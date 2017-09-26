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


def redownload_window() -> str:
    """The number of days for which the performance data will be redownloaded"""
    return '30'
