"""
Configures access to Adwords API and where to store results
"""
from datetime import date


def data_dir() -> str:
    """The directory where result data is written to"""
    return '/tmp/adwords'


def first_date() -> str:
    """The first day for which data is downloaded"""
    return '2015-01-01'


def client_customer_id() -> str:
    """The id of the manager account (MCC) that contains all the accounts for which data should be downloaded"""
    return '896-463-2775'


def developer_token() -> str:
    """The developer token that is used to access the Adwords API"""
    return '2a2K68DxyNWbPgMMKIfHdw'


def oauth2_client_id() -> str:
    """The Oauth client id obtained from the Adwords API center"""
    return '400397489470-f7drtoqfpe3oq181cf7nt74he643cuo0.apps.googleusercontent.com'


def oauth2_client_secret() -> str:
    """The Oauth client secret obtained from the Adwords API center"""
    return 'J9Uxui962FU4GuNRCT36bQTD'


def oauth2_refresh_token() -> str:
    """The Oauth refresh token returned from the adwords-downloader-refresh-oauth2-token script"""
    return '1/MMZf_PWTvoSNcr2pok7Na-Hto_bcIkKfdE6z_zjdmnk'

# 4/kYcOl8BN9r9gWxMsgkLFOZY3IewKGqc-FAIAMqCv6wE
def redownload_window() -> str:
    """The number of days for which the performance data will be redownloaded"""
    return '30'
