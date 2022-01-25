import re

from core.token import bot


def user_command(message, call=False):
    _commands = (
        "/start",
        "/help",
    )
    if message.text in _commands:
        return True
    else:
        return False


def apps_command_name(message, call=False):
    _commands = (
        '/trackname',
        '/albumname',
        '/artistname',
        '/playlistname',
    )
    if message.text.split(" ")[0] in _commands and message.text.split(" ")[1] != "":
        return True
    else:
        return False


def apps_command_id(message, call=False):
    _commands = (
        '/trackid',
        '/albumid',
        '/artistid',
        '/playlistid'
    )
    if call is False:
        if message.text.split(" ")[0] in _commands and message.text.split(" ")[1] != "":
            if message.text.split(" ")[0] == "/playlistid" and message.text.split(" ")[1].find(":") >= 0:
                return True
            return True
        else:
            return False
    else:
        if call.data.split()[0] in _commands:
            return True
        else:
            return False


def apps_command_url(message):
    _commands = (
        '/trackurl',
        '/albumurl',
        '/artisturl',
        '/playlisturl'
    )
    if message.text.split()[0] in _commands:
        if message.text.split()[0] == "/playlisturl":
            try:
                _, users, owner, playlist, kinder = re.findall(r"/{1}[\w\W]{5}/{1}[\d]+/{1}[\w\W]{9}/{1}[\d]+", message.text.split()[1])[0].split("/")
                return True
            except Exception:
                bot.send_message(message.chat.id, f"Invalid URI > {message.text.split()[1]}")
                return False
        elif message.text.split()[0] == "/artisturl":
            try:
                _, artist, artist_id = re.findall(r"/{1}[\w\W]{6}/{1}[\d]+", message.text.split()[1])[0].split("/")
                return True
            except Exception:
                bot.send_message(message.chat.id, f"Invalid URI > {message.text.split()[1]}")
                return False
        elif message.text.split()[0] == "/albumurl":
            try:
                _, album, album_id = re.findall(r"/{1}[\w\W]{5}/{1}[\d]+", message.text.split()[1])[0].split("/")
                return True
            except Exception:
                bot.send_message(message.chat.id, f"Invalid URI > {message.text.split()[1]}")
                return False
        elif message.text.split()[0] == "/trackurl":
            try:
                _, album, album_id, track, track_id = re.findall(r"/{1}[\w\W]{5}/{1}[\d]+/{1}[\w\W]{5}/{1}[\d]+", message.text.split()[1])[0].split("/")
                return True
            except Exception:
                bot.send_message(message.chat.id, f"Invalid URI > {message.text.split()[1]}")
                return False
    else:
        return False