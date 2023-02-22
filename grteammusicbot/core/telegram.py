import re, sqlite3

from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from grteammusibot.core.token import bot
from grteammusibot.core.yandex_music_download import YandexMusicAPI
from grteammusibot.core.yandex_music_parse_id import YandexMusicParseIds


def start(message):
    intro = """
Hello, I am `GRSearch_BOT`
My tasks:
---
download music from `https://music.yandex.ru`
---
If you want too use this _bot_, you should will pay for this!
"""
    db = sqlite3.connect("./db.sqlite3")
    db.execute(f"insert into User (chat_id) values ({message.chat.id});")
    db.commit()
    db.close()
    bot.send_message(message.chat.id, intro)


def usage(message):
    info = """
commands:
/registration [yandex_login]
/session_id [Session_id]
---
/trackid [id]
/albumid [id]
/artistid [id]
/playlistid [owner:kinds]
---
/trackname [name]
/albumname [name]
/artistname [name]
/playlistname [name]
----
/trackurl [URI]
/albumurl [URI]
/artisturl [URI]
/playlisturl [URI]
-------
Example:
`/registrate` account
'/session_id' Session_id
Session_id you find in cookies your browser
--
`/trackid` 123213213
`/playlistid` yandex-best:123213213
--
`/trackname` Phonk
`/trackname` Phonk Hard
--
`/trackurl` https://music.yandex.ru/album/23326838/track/106799856
`/trackurl` 23326838:106799856
`/trackurl` 23326838/106799856
`/albumurl` https://music.yandex.ru/album/24217929
`/albumurl` 24217929
`/artisturl` https://music.yandex.ru/artist/4545156
`/artisturl` 4545156
`/playlisturl` https://music.yandex.ru/users/yamusic-daily/playlists/110900658
`/playlisturl` yamusic-daily/110900658
`/playlisturl` yamusic-daily:110900658
-
"""
    bot.send_message(message.chat.id, info)

def music_id(message: Message):
    __funcs[message.text.split()[0]](message, identificator=True)

def music_name(message: Message):
    __funcs[message.text.split()[0]](message, name=True)

def music_url(message: Message):
    __funcs[message.text.split()[0]](message, url=True)

def music_callback(call: CallbackQuery):
    __funcs[call.data.split()[0]](call, callback=True)


def send_track(obj, identificator=None, name=None, url=None, callback=None):
    track_id = []
    if identificator is True:
        YandexMusicAPI(chat_id=obj.chat.id, track=obj.text.split()[1]).download_track()
    elif name is True:
        track_id = YandexMusicParseIds(track_name="".join(obj.text.split()[1:])).get_track_id()
        markup = InlineKeyboardMarkup(row_width=1)
        for item in track_id:
            markup.add(InlineKeyboardButton(f"{item['title']} {item['artists'][0]['name']}", callback_data=f"/trackid {item['id']} {item['albums'][0]['id']}"))
        bot.send_message(obj.chat.id, "Please choose track:", reply_markup=markup)
    elif url is True:
        track_url = re.findall(r"/album/[\d]*/track/[\d]*", obj.text.split()[1])
        album_id = track_id = None
        if len(track_url) == 0:
            track_match = obj.text.split()[1].split(':')
            if len(track_match) == 1:
                track_match = obj.text.split()[1].split('/')
            else:
                album_id, track_id = track_match[::]
                if len(track_match) == 1:
                    bot.send_message(obj.chat.id, "Invalid value!")
                else:
                    album_id, track_id = track_match[::]
        else:
            _, _, album_id, _, track_id = track_url[0].split('/')
        YandexMusicAPI(chat_id=obj.chat.id, track=track_id, album=album_id).download_track()
    elif callback is True:
        YandexMusicAPI(chat_id=obj.message.chat.id, track=obj.data.split()[1], album=obj.data.split()[2]).download_track()


def send_album(obj, identificator=None, name=None, url=None, callback=None) -> None:
    if identificator is True:
        YandexMusicAPI(chat_id=obj.chat.id, album=obj.text.split()[1]).download_album()
    elif name is True:
        album_id = YandexMusicParseIds(album_name=" ".join(obj.text.split()[1:])).get_album_id()
        markup = InlineKeyboardMarkup(row_width=1)
        for item in album_id:
            markup.add(InlineKeyboardButton(f"{item['title']} {item['artists'][0]['name']}", callback_data=f"/albumid {item['id']}"))
        bot.send_message(obj.chat.id, "Please choose album:", reply_markup=markup)
    elif url is True:
        album_url = re.findall(r"/album/[\d]+", obj.text.split()[1])
        if len(album_url) == 0:
            album_id = obj.text.split()[1]
        else:
            _, _, album_id = album_url[0].split("/")
        YandexMusicAPI(chat_id=obj.chat.id, album=album_id).download_album()
    elif callback is True:
        YandexMusicAPI(chat_id=obj.message.chat.id, album=obj.data.split()[1]).download_album()


def send_artist(obj, identificator = None, name=None, url=None, callback=None) -> None:
    if identificator is True:
        YandexMusicAPI(chat_id=obj.chat.id, artist=obj.text.split()[1]).download_artist()
    elif name is True:
        artist_id = YandexMusicParseIds(artist_name=" ".join(obj.text.split()[1:])).get_artist_id()
        markup = InlineKeyboardMarkup(row_width=1)
        for item in artist_id:
            markup.add(InlineKeyboardButton(f"{item[0]['name']}", callback_data=f"/artistid {item[0]['id']}"))
        bot.send_message(obj.chat.id, "Please choose artist:", reply_markup=markup)
    elif url is True:
        artist_url = re.findall(r"/artist/[\d]+", obj.text.split()[1])
        if len(artist_url) == 0:
            artist_id = obj.text.split()[1]
        else:
            _, _, artist_id = artist_url[0].split("/")
        YandexMusicAPI(chat_id=obj.chat.id, artist=artist_id).download_artist()
    elif callback is True:
        YandexMusicAPI(chat_id=obj.message.chat.id, artist=obj.data.split()[1]).download_artist()


def send_playlist(obj, identificator=None, name=None, url=None, callback=None) -> None:
    if identificator is True:
        YandexMusicAPI(chat_id=obj.chat.id, playlist=obj.text.split()[1]).download_playlist()
    elif name is True:
        playlist_id = YandexMusicParseIds(playlist_name=" ".join(obj.text.split()[1:])).get_playlist_id()
        markup = InlineKeyboardMarkup(row_width=1)
        for item in playlist_id:
            markup.add(InlineKeyboardButton(f"{item['owner']['name']} {item['title']} {item['trackCount']}", callback_data=f"/playlistid {item['owner']['login']}:{item['kind']}"))
        bot.send_message(obj.chat.id, "Please choose playlist: ", reply_markup=markup)
    elif url is True:
        playlist_url = re.findall(r"/users/[\w\S]+/[\d]+", obj.text.split()[1])
        if len(playlist_url) == 0:
            owner, kind = obj.text.split()[1].split(':')
        else:
            _, _, owner, _, kind = playlist_url[0].split("/")
        YandexMusicAPI(chat_id=obj.chat.id, playlist=f"{owner}:{kind}").download_playlist()
    elif callback is True:
        owner, kind = obj.data.split()[1].split(":")
        YandexMusicAPI(chat_id=obj.message.chat.id, playlist=f"{owner}:{kind}").download_playlist()


def registration(obj):
    db = sqlite3.connect("./db.sqlite3")
    db.execute(f"update User yandex_login='{obj.text.split()[1]}';")
    db.commit()
    db.close()
    bot.send_message(obj.chat.id, f"Your login -> {obj.text.split()[1]}.")


def session(obj):
    db = sqlite3.connect("./db.sqlite3")
    db.execute(f"update User set Session_id='{obj.text.split()[1]}';")
    db.commit()
    db.close()
    bot.send_message(obj.chat.id, f"Your Session_id -> {obj.text.split()[1]}")



__funcs = {
        "/trackname": send_track,
        "/albumname": send_album,
        "/artistname": send_artist,
        "/playlistname": send_playlist,
        "/trackurl": send_track,
        "/albumurl": send_album,
        "/artisturl": send_artist,
        "/playlisturl": send_playlist,
        "/trackid": send_track,
        "/albumid": send_album,
        "/artistid": send_artist,
        "/playlistid": send_playlist
}

