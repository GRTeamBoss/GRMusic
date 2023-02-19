def default_command(message, call=False):
    _commands = (
        "/start",
        "/help",
    )
    if call is True:
        if message.data in _commands:
            return True
    else:
        if message.text in _commands:
            return True
    return False


def music_command_name(message, call=False):
    _commands = (
        '/trackname',
        '/albumname',
        '/artistname',
        '/playlistname',
    )
    if call is True:
        _command = message.data.split()[0]
        if _command in _commands:
            return True
    else:
        _command = message.text.split()[0]
        if _command in _commands:
            return True
    return False


def music_command_id(message, call=False):
    _commands = (
        '/trackid',
        '/albumid',
        '/artistid',
        '/playlistid'
    )
    if call is False:
        _command = message.text.split()[0]
        if _command in _commands:
            return True
    else:
        if message.data.split()[0] in _commands:
            return True
    return False


def music_command_url(message):
    _commands = (
        '/trackurl',
        '/albumurl',
        '/artisturl',
        '/playlisturl'
    )
    _command = message.text.split()[0]
    if _command in _commands:
        return True
    return False
