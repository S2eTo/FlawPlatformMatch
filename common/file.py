def get_original_filename(filename) -> str:
    """
    获取原始文件名
    """

    if filename == '' or filename is None:
        return ''

    unixSep = filename.rfind('/')
    winSep = filename.rfind('\\')
    pos = winSep if winSep > unixSep else unixSep

    return filename[pos + 1:] if pos != -1 else filename


def get_extension(filename) -> str:
    """
    获取文件扩展名
    """

    if filename == '' or filename is None:
        return ''

    pos = filename.rfind('.')

    return filename[pos + 1:] if pos != -1 else filename
