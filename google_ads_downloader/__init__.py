
def MARA_CONFIG_MODULES():
    from . import config, cli
    return [config]

def MARA_CLICK_COMMANDS():
    from . import config, cli
    return [cli.download_data, cli.refresh_oauth2_token]