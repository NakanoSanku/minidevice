from minidevice import config


def str2byte(content):
    """compile str to byte"""
    return content.encode(config.DEFAULT_CHARSET)
