"""Command line interface for adwords downloader"""

import click
from google_ads_downloader import config
from functools import partial


def config_option(config_function, **kwargs):
    """Helper decorator that turns an option function into a cli option"""

    def decorator(function):
        default = kwargs.pop('default', None)
        if default is None:
            default = config_function()
        if kwargs.get('multiple'):
            default = [default]
        return click.option('--' + config_function.__name__,
                            help=config_function.__doc__ + '. Default: "' + str(default) + '"',
                            **kwargs)(function)

    return decorator


def apply_options(kwargs):
    """Applies passed cli parameters to config.py"""
    for key, value in kwargs.items():
        if key == 'accounts':
            if value !=():
                setattr(config, key, partial(lambda v: [config.AdwordsAccount(*args) for args in v], value))
        else:
            if value: setattr(config, key, partial(lambda v: v, value))


@click.command()
@config_option(config.accounts, type=(str, str, str, str, str, str), multiple=True,
               default=('name', 'client_customer_id', 'developer_token', 'oauth2_client_id', 'oauth2_client_secret', 'oauth2_refresh_token'))

def refresh_oauth2_token(**kwargs):
    """
    Creates a new OAuth2 token.
    When options are not specified, then the defaults from config.py are used.
    """
    apply_options(kwargs)

    from google_ads_downloader import downloader
    downloader.refresh_oauth_token()


@click.command()
@config_option(config.accounts, type=(str, str, str, str, str, str), multiple=True,
               default=('name', 'client_customer_id', 'developer_token', 'oauth2_client_id', 'oauth2_client_secret', 'oauth2_refresh_token'))
@config_option(config.data_dir)
@config_option(config.first_date)
@config_option(config.redownload_window)
@config_option(config.output_file_version)
@config_option(config.max_retries)
@config_option(config.retry_backoff_factor)
def download_data(**kwargs):
    """
    Downloads data.
    When options are not specified, then the defaults from config.py are used.
    """
    apply_options(kwargs)
    from google_ads_downloader import downloader
    downloader.download_data()
