"""
Configures access to Adwords API and where to store results
"""
from datetime import date

class AdwordsAccount:
    """A Adwords account"""

    def __init__(self, name: str, client_customer_id: str, developer_token: str, oauth2_client_id: str, oauth2_client_secret: str, oauth2_refresh_token: str):
        self.name = name
        self.client_customer_id = client_customer_id
        self.developer_token = developer_token
        self.oauth2_client_id = oauth2_client_id
        self.oauth2_client_secret = oauth2_client_secret
        self.oauth2_refresh_token = oauth2_refresh_token

    def __repr__(self) -> str:
        """A self representation of the account"""
        return '<{name} {client_customer_id} {oauth2_client_id} {oauth2_client_secret} {oauth2_refresh_token}>'.format(name = self.name,
                                                                      client_customer_id=self.client_customer_id,
                                                                      oauth2_client_id=self.oauth2_client_id,
                                                                      oauth2_client_secret=self.oauth2_client_secret,
                                                                      oauth2_refresh_token=self.oauth2_refresh_token)

    def __str__(self) -> str:
        """A human-readable representation of the account"""
        return 'AdwordsAccount: ' + self.name

def accounts() -> [AdwordsAccount]:
    """A list of Adwords accounts provided by <client_customer_id developer_token oauth2_client_id oauth2_client_secret oauth2_refresh_token> Accepts multiple accounts"""
    return [AdwordsAccount('name', 'client_customer_id', 'developer_token', 'oauth2_client_id', 'oauth2_client_secret', 'oauth2_refresh_token')]

def data_dir() -> str:
    """The directory where result data is written to"""
    return '/tmp/adwords'


def first_date() -> str:
    """The first day for which data is downloaded"""
    return '2015-01-01'


def client_customer_id() -> str:
    """The id of the manager account (MCC) that contains all the accounts for which data should be downloaded"""
    return '123-456-7890'


def developer_token() -> str:
    """The developer token that is used to access the Adwords API"""
    return 'ABCDEFEGHIJKL'


def oauth2_client_id() -> str:
    """The Oauth client id obtained from the Adwords API center"""
    return '123456789-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com'


def oauth2_client_secret() -> str:
    """The Oauth client secret obtained from the Adwords API center"""
    return 'aBcDeFg'


def oauth2_refresh_token() -> str:
    """The Oauth refresh token returned from the adwords-downloader-refresh-oauth2-token script"""
    return '1/acbd-efghijklmnopqrstuvwxyz'


def api_version() -> str:
    """Which Adwords API version should be called"""
    return 'v201809'


def redownload_window() -> str:
    """The number of days for which the performance data will be redownloaded"""
    return '30'


def output_file_version() -> str:
    """A suffix that is added to output files, denoting a version of the data format"""
    return 'v4'


def max_retries() -> int:
    """How often try retry at max in case of 500 errors"""
    return 5


def retry_backoff_factor() -> int:
    """How many seconds to wait between retries (is multiplied with retry count)"""
    return 5
