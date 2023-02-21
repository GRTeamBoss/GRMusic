import sqlite3

from grteammusicbot.core.yandex_music_download import YandexMusicAPI
from grteammusicbot.core.token import bot


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


def user_registrated(message, call=False):
    db = sqlite3.connect("./db.sqlite3")
    if call:
        content = list(db.execute(f"select yandex_login, Session_id from User where chat_id={message.message.chat.id};"))
        if len(content) == 0:
            return False
    else:
        content = list(db.execute(f"select yandex_login, Session_id from User where chat_id={message.chat.id};"))
        if len(content) == 0:
            return False
    db.close()
    if content[0][1] != None:
        return True
    return False


def check_user_info(message, call=False):
    user_info = YandexMusicAPI().get_user_info()
    if user_info['premium'] is False:
        if call is True:
            bot.send_message(message.message.chat.id, "[#] Sorry, you don\'t have a premium status, please send new <Session_id> or buy YandexPlus for refresh your <Session_id>.")
        else:
            bot.send_message(message.chat.id, "[#] Sorry, you don\'t have a premium status, please send new <Session_id> or buy YandexPlus for refresh your <Session_id>.")
        return False
    return True
