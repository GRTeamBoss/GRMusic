import pathlib
import re

from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from core.token import bot
from core.yandex_music_download import YandexMusicAPI
from core.yandex_music_parse_id import YandexMusicParseIds


def start(message):
    intro = """
Hello, I am `GRSearch_BOT`
My tasks:
---
download music from `https://music.yandex.ru`
---
If you want too use this _bot_, you should will pay for this!
"""
    bot.send_message(message.chat.id, intro)


def usage(message):
    info = """
commands:
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
        track = YandexMusicAPI(track=obj.text.split()[1]).download_track()
        if track is None:
            bot.send_message(obj.chat.id, "Connection is lost!")
        else:
            file = pathlib.Path(track).read_bytes()
            bot.send_audio(obj.chat.id, file)
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
        track = YandexMusicAPI(track=track_id, album=album_id).download_track()
        if track is None:
            bot.send_message(obj.chat.id, "Connection is lost!")
        else:
            file = pathlib.Path(track).read_bytes()
            bot.send_audio(obj.chat.id, file)
    elif callback is True:
        track = YandexMusicAPI(track=obj.data.split()[1], album=obj.data.split()[2]).download_track()
        file = pathlib.Path(track).read_bytes()
        bot.send_audio(obj.message.chat.id, file)


def send_album(obj, identificator=None, name=None, url=None, callback=None) -> None:
    if identificator is True:
        album = YandexMusicAPI(album=obj.text.split()[1]).download_album()
        if album is None:
            bot.send_message(obj.chat.id, "Invalid value!")
        else:
            for track in album:
                file = pathlib.Path(track).read_bytes()
                bot.send_audio(obj.chat.id, file)
    elif name is True:
        album_id = YandexMusicParseIds(album_name=" ".join(obj.text.split()[1:])).get_album_id()
        album = None
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
        album = YandexMusicAPI(album=album_id).download_album()
        if album is None:
            bot.send_message(obj.chat.id, "Invalid value!")
        else:
            for track in album:
                file = pathlib.Path(track).read_bytes()
                bot.send_audio(obj.chat.id, file)
    elif callback is True:
        album = YandexMusicAPI(album=obj.data.split()[1]).download_album()
        if album is None:
            bot.send_message(obj.message.chat.id, "Connection is lost!")
        else:
            for track in album:
                file = pathlib.Path(track).read_bytes()
                bot.send_audio(obj.message.chat.id, file)


def send_artist(obj, identificator = None, name=None, url=None, callback=None) -> None:
    if identificator is True:
        artist = YandexMusicAPI(artist=obj.text.split()[1]).download_artist()
        if artist is None:
            bot.send_message(obj.chat.id, "Invalid value!")
        else:
            for album in artist:
                for track in album:
                    file = pathlib.Path(track).read_bytes()
                    bot.send_audio(obj.chat.id, file)
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
        artist = YandexMusicAPI(artist=artist_id).download_artist()
        if artist is None:
            bot.send_message(obj.chat.id, "Invalid value!")
        else:
            for album in artist:
                for track in album:
                    file = pathlib.Path(track).read_bytes()
                    bot.send_audio(obj.chat.id, file)
    elif callback is True:
        artist = YandexMusicAPI(artist=obj.data.split()[1]).download_artist()
        if artist is None:
            bot.send_message(obj.message.chat.id, "Connection is lost!")
        else:
            for album in artist:
                for track in album:
                    file = pathlib.Path(track).read_bytes()
                    bot.send_audio(obj.message.chat.id, file)


def send_playlist(obj, identificator=None, name=None, url=None, callback=None) -> None:
    if identificator is True:
        playlist = YandexMusicAPI(playlist=obj.text.split()[1]).download_playlist()
        if playlist is None:
            bot.send_message(obj.chat.id, "Connection is lost!")
        else:
            for track in playlist:
                file = pathlib.Path(track).read_bytes()
                bot.send_audio(obj.chat.id, file)
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
        playlist = YandexMusicAPI(playlist=f"{owner}:{kind}").download_playlist()
        if playlist is None:
            bot.send_message(obj.chat.id, "Connection is lost!")
        else:
            for track in playlist:
                file = pathlib.Path(track).read_bytes()
                bot.send_audio(obj.chat.id, file)
    elif callback is True:
        owner, kind = obj.data.split()[1].split(":")
        playlist = YandexMusicAPI(playlist=f"{owner}:{kind}").download_playlist()
        if playlist is None:
            bot.send_message(obj.message.chat.id, "Connection is lost!")
        else:
            for track in playlist:
                file = pathlib.Path(track).read_bytes()
                bot.send_audio(obj.message.chat.id, file)



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

