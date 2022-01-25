def ParseEXCEPTION(header, title) -> str:
    call_arg = {
        'track': trackException,
        'album': albumException,
        'artist': artistException,
        'playlist': playlistException,
    }
    resp = call_arg[header](title)
    print(resp)
    return 'FAIL'


def trackException(title) -> str:
    err = 'Your track -> {}, not finded, please try again with another word!'.format(title)
    return err


def artistException(title) -> str:
    err = 'Your artist -> {}, not finded, please try again with another word!'.format(title)
    return err


def albumException(title) -> str:
    err = 'Your album -> {}, not finded, please try again with another words'.format(title)
    return err


def playlistException(title) -> str:
    err = 'Your playlists -> {}, not finded, please try again with another words!'.format(title)
    return err