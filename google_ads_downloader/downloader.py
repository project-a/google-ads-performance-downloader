import datetime
import errno
import gzip
import http
import csv
import logging
import re
import shutil
import sys
import io
import tempfile
import json
import time
from enum import Enum
from pathlib import Path

from google_ads_downloader import config
from googleads import adwords, oauth2, errors

from google_auth_oauthlib.flow import InstalledAppFlow
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError


class PerformanceReportType(Enum):
    """ A Google performance report type
    https://developers.google.com/adwords/api/docs/appendix/reports/ad-performance-report
    https://developers.google.com/adwords/api/docs/appendix/reports/adgroup-performance-report
    https://developers.google.com/adwords/api/docs/appendix/reports/campaign-performance-report
    https://developers.google.com/adwords/api/docs/appendix/reports/account-performance-report
    """
    AD_PERFORMANCE_REPORT = 'ad-performance'
    ADGROUP_PERFORMANCE_REPORT = 'adgroup-performance'
    CAMPAIGN_PERFORMANCE_REPORT = 'campaign-performance'
    ACCOUNT_PERFORMANCE_REPORT = 'account-performance'


class AdWordsApiClient(adwords.AdWordsClient):
    """A client for downloading data from the Google AdWords API"""

    def __init__(self):

        self.client = super(AdWordsApiClient, self).__init__(
            developer_token=config.developer_token(),
            oauth2_client=oauth2.GoogleRefreshTokenClient(
                client_id=config.oauth2_client_id(),
                client_secret=config.oauth2_client_secret(),
                refresh_token=config.oauth2_refresh_token()),
            client_customer_id=config.client_customer_id())
        self.client_customers = self._fetch_client_customers()

    def _fetch_managed_customer_page(self):
        """Fetches the data from the ManagedCustomerService containing the customer information
        https://developers.google.com/adwords/api/docs/reference/v201609/ManagedCustomerService.ManagedCustomerPage

        Returns: ManagedCustomerPage

        """
        service = self.GetService(service_name='ManagedCustomerService')
        return service.get({'fields': ['CustomerId', 'Name', 'CanManageClients', 'AccountLabels', 'CurrencyCode']})

    def _fetch_client_customers(self):
        """Fetches the client customers, including their names and account labels, from
         the Google Ads API

        Returns:
            A dictionary of client_customers with
            {customer_id: {'Name': account_name, 'Labels': account_labels}}

        """
        managed_customer_page = self._fetch_managed_customer_page()
        client_customers = {}
        for managed_customer in managed_customer_page.entries:
            # Exclude manager customers
            # https://support.google.com/adwords/answer/6139186?hl=en
            if not managed_customer.canManageClients:
                account_labels = []
                if hasattr(managed_customer, 'accountLabels'):
                    account_labels = [x.name for x in managed_customer.accountLabels]
                client_customers[managed_customer.customerId] = {
                    'Name': managed_customer.name,
                    'Labels': account_labels,
                    'Currency Code': managed_customer.currencyCode}
        return client_customers


def download_data():
    """Creates an AdWordsApiClient and downloads the data"""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logging.info('Adwords API version: '+str(config.api_version()))

    api_client = AdWordsApiClient()
    download_data_sets(api_client)


def download_data_sets(api_client: AdWordsApiClient):
    """Downloads the account structure and the AdWords ad performance

    Args:
        api_client: AdWordsApiClient

    """

    predicates = [{'field': 'Status',
                   'operator': 'IN',
                   'values': ['ENABLED',
                              'PAUSED',
                              'DISABLED']
                   }, {
                      'field': 'Impressions',
                      'operator': 'GREATER_THAN',
                      'values': [0]
                  }]

    if config.ignore_removed_campaigns():
        predicates.append({
            'field': 'CampaignStatus',
            'operator': 'NOT_EQUALS',
            'values': 'REMOVED'
        })

    download_performance(api_client,
                         PerformanceReportType.AD_PERFORMANCE_REPORT,
                         fields=['Date', 'Id', 'AdGroupId', 'Device', 'AdNetworkType2',
                                 'ActiveViewImpressions', 'AveragePosition',
                                 'Clicks', 'Conversions', 'ConversionValue',
                                 'Cost', 'Impressions'],
                         predicates=predicates
                         )

    download_account_structure(api_client)


def download_performance(api_client: AdWordsApiClient,
                         performance_report_type: PerformanceReportType,
                         fields: [str],
                         predicates: [{}]):
    """Download the Google Ads performance and saves them as zipped json files to disk

    Args:
        api_client: An AdWordsApiClient
        performance_report_type: A PerformanceReportType object
        fields: A list of fields to be included in the report
        predicates: A list of filters for the report
    """
    client_customer_ids = api_client.client_customers.keys()

    first_date = datetime.datetime.strptime(config.first_date(), '%Y-%m-%d')
    last_date = datetime.datetime.now() - datetime.timedelta(days=1)
    current_date = last_date
    while current_date >= first_date:
        relative_filepath = Path('{date:%Y/%m/%d}/google-ads/{filename}_{version}.json.gz'.format(
            date=current_date,
            filename=performance_report_type.value,
            version=config.output_file_version()))
        filepath = ensure_data_directory(relative_filepath)

        if (not filepath.is_file()
                or (last_date - current_date).days <= int(config.redownload_window())):
            report_list = get_performance_for_single_day(api_client,
                                                         client_customer_ids,
                                                         current_date,
                                                         performance_report_type,
                                                         fields,
                                                         predicates)

            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_filepath = Path(tmp_dir, relative_filepath)
                tmp_filepath.parent.mkdir(exist_ok=True, parents=True)
                with gzip.open(str(tmp_filepath), 'wt') as tmp_ad_performance_file:
                    tmp_ad_performance_file.write(json.dumps(report_list))
                shutil.move(str(tmp_filepath), str(filepath))
        current_date += datetime.timedelta(days=-1)


def get_performance_for_single_day(api_client: AdWordsApiClient,
                                   client_customer_ids: [int],
                                   single_date: datetime,
                                   report_type: PerformanceReportType,
                                   fields: [],
                                   predicates: []) -> [{}]:
    """Downloads the performance for a list of clients for a given day

    Args:
        api_client: An AdWordsApiClient
        client_customer_ids: A list of client ids
        single_date: A single date as a datetime object
        report_type: A PerformanceReportType object
        fields: A list of fields to be included in the report
        predicates: A list of filters for the report

    Returns:
        A list containing dictionaries with the performance from the report
    """
    report_list = []
    logging.info(
        'download google ads {} for {}'.format(report_type.value, single_date.strftime('%Y-%m-%d')))
    for client_customer_id in client_customer_ids:
        api_client.SetClientCustomerId(client_customer_id)
        report = _download_adwords_report(api_client,
                                          current_date=single_date,
                                          report_type=report_type.name,
                                          fields=fields,
                                          predicates=predicates,
                                          )
        report_list.extend(list(report))
    return report_list


def download_account_structure(api_client: AdWordsApiClient):
    """Downloads the Google Ads account structure as saves it as a zipped csv file.

    Args:
        api_client: An AdWordsApiClient

    """
    filename = Path('google-ads-account-structure_{}.csv.gz'.format(config.output_file_version()))
    filepath = ensure_data_directory(filename)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_filepath = Path(tmp_dir, filename)
        with gzip.open(str(tmp_filepath), 'wt') as tmp_campaign_structure_file:
            header = ['Ad Id', 'Ad', 'Ad Group Id', 'Ad Group', 'Campaign Id',
                      'Campaign', 'Customer Id', 'Customer Name', 'Attributes', 'Currency Code']
            writer = csv.writer(tmp_campaign_structure_file, delimiter="\t")
            writer.writerow(header)
            for client_customer_id, client_customer in api_client.client_customers.items():
                labels = json.dumps(client_customer['Labels'])
                client_customer_attributes = parse_labels(labels)
                client_customer_name = client_customer['Name']

                campaign_attributes = get_campaign_attributes(api_client, client_customer_id)
                ad_group_attributes = get_ad_group_attributes(api_client, client_customer_id)
                ad_data = get_ad_data(api_client, client_customer_id)

                for ad_data_dict in ad_data:
                    ad_id = ad_data_dict['Ad ID']
                    campaign_id = ad_data_dict['Campaign ID']
                    ad_group_id = ad_data_dict['Ad group ID']
                    currency_code = client_customer['Currency Code']
                    attributes = {**client_customer_attributes,
                                  **campaign_attributes.get(campaign_id, {}),
                                  **ad_group_attributes.get(ad_group_id, {}),
                                  **ad_data_dict['attributes']}

                    ad = [str(ad_id),
                          ad_data_dict['Ad'],
                          str(ad_group_id),
                          ad_data_dict['Ad group'],
                          str(campaign_id),
                          ad_data_dict['Campaign'],
                          str(client_customer_id),
                          client_customer_name,
                          json.dumps(attributes),
                          currency_code
                          ]

                    writer.writerow(ad)

        shutil.move(str(tmp_filepath), str(filepath))


def get_campaign_attributes(api_client: AdWordsApiClient, client_customer_id: int) -> {}:
    """Downloads the campaign attributes from the Google Ads API
    https://developers.google.com/adwords/api/docs/appendix/reports/campaign-performance-report

    Args:
        api_client: An AdWordsApiClient
        client_customer_id: A client customer id

    Returns:
        A dictionaries mapping campaign attributes to campaign ids
    """
    logging.info('get campaign attributes for account {}'.format(client_customer_id))
    api_client.SetClientCustomerId(client_customer_id)
    report = _download_adwords_report(api_client,
                                      report_type='CAMPAIGN_PERFORMANCE_REPORT',
                                      fields=['CampaignId', 'Labels'],
                                      predicates={'field': 'CampaignStatus',
                                                  'operator': 'IN',
                                                  'values': ['ENABLED',
                                                             'PAUSED',
                                                             'REMOVED']
                                                  })
    return {row['Campaign ID']: parse_labels(row['Labels']) for row in report}


def get_ad_group_attributes(api_client: AdWordsApiClient, client_customer_id: int) -> {}:
    """Downloads the ad group attributes from the Google AdWords API
    https://developers.google.com/adwords/api/docs/appendix/reports/adgroup-performance-report

    Args:
        api_client: An AdWordsApiClient
        client_customer_id: A client customer id

    Returns:
        A dictionaries mapping ad group attributes to ad group ids
    """
    logging.info('get ad group attributes for account {}'.format(client_customer_id))
    api_client.SetClientCustomerId(client_customer_id)
    report = _download_adwords_report(api_client,
                                      report_type='ADGROUP_PERFORMANCE_REPORT',
                                      fields=['AdGroupId', 'Labels'],
                                      predicates={'field': 'AdGroupStatus',
                                                  'operator': 'IN',
                                                  'values': ['ENABLED',
                                                             'PAUSED',
                                                             'REMOVED']
                                                  })

    return {row['Ad group ID']: parse_labels(row['Labels']) for row in report}


def get_ad_data(api_client: AdWordsApiClient, client_customer_id: int) -> [{}]:
    """Downloads the ad data from the Google AdWords API for a given client_customer_id
    https://developers.google.com/adwords/api/docs/appendix/reports/ad-performance-report

    Args:
        api_client: An AdWordsApiClient
        client_customer_id: A client customer id

    Returns:
        A dictionary of the form {ad_id: {key: value}}
    """
    logging.info('get ad data for account {}'.format(client_customer_id))

    api_client.SetClientCustomerId(client_customer_id)

    predicates = [
        {
            'field': 'Status',
            'operator': 'IN',
            'values': ['ENABLED',
                       'PAUSED',
                       'DISABLED']
        }
    ]

    if config.ignore_removed_campaigns():
        predicates.append({
            'field': 'CampaignStatus',
            'operator': 'NOT_EQUALS',
            'values': 'REMOVED'
        })

    report = _download_adwords_report(api_client,
                                      report_type='AD_PERFORMANCE_REPORT',
                                      fields=['Id', 'AdGroupId', 'AdGroupName',
                                              'CampaignId', 'CampaignName',
                                              'Labels', 'Headline', 'AdType',
                                              'Status'],
                                      predicates=predicates)

    ad_data = []
    for row in report:
        attributes = parse_labels(row['Labels'])
        if row['Ad type'] is not None:
            attributes = {**attributes, 'Ad type': row['Ad type']}
        if row['Ad state'] is not None:
            attributes = {**attributes, 'Ad state': row['Ad state']}
        ad_data.append({**row, 'attributes': attributes})

    return ad_data


def _download_adwords_report(api_client: AdWordsApiClient,
                             report_type: str,
                             fields: [str],
                             predicates: {},
                             current_date: datetime = None) -> csv.DictReader:
    """Downloads an Google Ads report from the Google Ads API

    Args:
        api_client: An AdWordsApiClients
        report_type: The report type
            https://developers.google.com/adwords/api/docs/appendix/reports
        fields: The selector fields
            https://developers.google.com/adwords/api/docs/appendix/selectorfields
        predicates: The predicate to filter by
            https://developers.google.com/adwords/api/docs/reference/v201609/CampaignService.Predicate
        current_date: datetime (optional), if none is specified today's date is assumed

    Returns:
        A Google Ads report as a string

    """
    report_filter = {
        'reportName': '{}_#'.format(report_type),
        'dateRangeType': 'CUSTOM_DATE',
        'reportType': report_type,
        'downloadFormat': 'CSV',
        'selector': {
            'fields': fields,
            'predicates': predicates
        }
    }

    if current_date is not None:
        date_str = current_date.strftime('%Y%m%d')
        report_filter['selector']['dateRange'] = {
            'min': date_str,
            'max': date_str
        }
    else:
        report_filter['dateRangeType'] = 'TODAY'

    report_downloader = api_client.GetReportDownloader(version=config.api_version())

    retry_count = 0
    while True:
        retry_count += 1
        try:
            report = io.StringIO()
            report_downloader.DownloadReport(report_filter,
                                             output=report,
                                             skip_report_header=True,
                                             skip_column_header=False,
                                             skip_report_summary=True)
            report.seek(0)
            return csv.DictReader(report)
        except errors.AdWordsReportError as e:
            if retry_count < config.max_retries():

                logging.warning(('Error HTTP #{e.code} Failed attempt #{retry_count} for report with settings:\n'
                                 '{report_filter}\n'
                                 'Retrying...').format(e=e, retry_count=retry_count,
                                                       report_filter=report_filter))
                time.sleep(retry_count * config.retry_backoff_factor())
            else:
                raise e
        except http.client.RemoteDisconnected as e:
            if retry_count < config.max_retries():
                logging.warning(('Network error during attempt #{retry_count} for report with settings:\n'
                                 '{report_filter}\n'
                                 'Retrying...').format(retry_count=retry_count,
                                                       report_filter=report_filter))
                time.sleep(retry_count * config.retry_backoff_factor())
            else:
                raise e


class ClientConfigBuilder(object):
    """Helper class used to build a client config dict used in the OAuth 2.0 flow."""

    _DEFAULT_AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    _DEFAULT_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    CLIENT_TYPE_WEB = 'web'
    CLIENT_TYPE_INSTALLED_APP = 'installed'

    def __init__(self, client_type=None, client_id=None, client_secret=None,
                 auth_uri=_DEFAULT_AUTH_URI, token_uri=_DEFAULT_TOKEN_URI):
        self.client_type = client_type
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_uri = auth_uri
        self.token_uri = token_uri

    def build(self):
        """Builds a client config dictionary used in the OAuth 2.0 flow."""
        if all((self.client_type, self.client_id, self.client_secret,
                self.auth_uri, self.token_uri)):
            client_config = {
                self.client_type: {
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'auth_uri': self.auth_uri,
                    'token_uri': self.token_uri
                }
            }
        else:
            raise ValueError('Required field is missing.')

        return client_config


def refresh_oauth_token():
    """Retrieve and display the access and refresh token."""

    client_config = ClientConfigBuilder(
        client_type=ClientConfigBuilder.CLIENT_TYPE_WEB, client_id=config.oauth2_client_id(),
        client_secret=config.oauth2_client_secret())
    flow = InstalledAppFlow.from_client_config(client_config.build(),
                                               scopes=['https://www.googleapis.com/auth/adwords'])
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    authorize_url, _ = flow.authorization_url(prompt='consent')

    print('Log into the Google Account you use to access your Google Ads account '
          'and go to the following URL: \n%s\n' % authorize_url)
    print('After approving the token enter the verification code (if specified).')
    code = input('Code: ').strip()
    try:
        flow.fetch_token(code=code)
    except InvalidGrantError as ex:
        print('Authentication has failed: %s' % ex)
        sys.exit(1)

    print('Access token: %s' % flow.credentials.token)
    print('Refresh token: %s' % flow.credentials.refresh_token)


def parse_labels(labels: str) -> {str: str}:
    """Extracts labels from a string

    Args:
        labels: Labels as an json encoded array of strings '["{key_1=value_1}","{key_2=value_2}]", ..]'

    Returns:
            A dictionary of labels with {key_1 : value_1, ...} format

    """
    matches = re.findall("{([^=]+)=([^=]+)}", labels)
    labels = {x[0].strip().lower().title(): x[1].strip() for x in matches}
    return labels


def ensure_data_directory(relative_path: Path = None) -> Path:
    """Checks if a directory in the data dir path exists. Creates it if necessary

    Args:
        relative_path: A Path object pointing to a file relative to the data directory

    Returns:
        The absolute path Path object

    """
    if relative_path is None:
        return Path(config.data_dir())
    try:
        path = Path(config.data_dir(), relative_path)
        # if path points to a file, create parent directory instead
        if path.suffix:
            if not path.parent.exists():
                path.parent.mkdir(exist_ok=True, parents=True)
        else:
            if not path.exists():
                path.mkdir(exist_ok=True, parents=True)
        return path
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
