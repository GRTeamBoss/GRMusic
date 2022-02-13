import re


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
        try:
            _command, _value = message.data.split()[0:2]
            if _command in _commands and _value[1] != "":
                return True
        except Exception:
            return False
    else:
        try:
            _command, _value = message.text.split()[0:2]
            if message.text.split(" ")[0] in _commands and message.text.split(" ")[1] != "":
                return True
        except Exception:
            return False
    return False


def music_command_id(message, call=False):
    _commands = (
        '/trackid',
        '/albumid',
        '/artistid',
        '/playlistid'
    )
    if call is False:
        try:
            _command, _value = message.text.split()
            if _command in _commands and _value != "":
                if _command == "/playlistid" and _value.find(":") >= 0:
                    pass
                return True
        except Exception:
            return False
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
        if _command == "/playlisturl":
            try:
                _, users, owner, playlist, kinder = re.findall(r"/{1}[\w\W]{5}/{1}[\d]+/{1}[\w\W]{9}/{1}[\d]+", message.text.split()[1])[0].split("/")
                return True
            except Exception:
                return False
        elif _command == "/artisturl":
            try:
                _, artist, artist_id = re.findall(r"/{1}[\w\W]{6}/{1}[\d]+", message.text.split()[1])[0].split("/")
                return True
            except Exception:
                return False
        elif _command == "/albumurl":
            try:
                _, album, album_id = re.findall(r"/{1}[\w\W]{5}/{1}[\d]+", message.text.split()[1])[0].split("/")
                return True
            except Exception:
                return False
        elif _command == "/trackurl":
            try:
                _, album, album_id, track, track_id = re.findall(r"/{1}[\w\W]{5}/{1}[\d]+/{1}[\w\W]{5}/{1}[\d]+", message.text.split()[1])[0].split("/")
                return True
            except Exception:
                return False
    return False