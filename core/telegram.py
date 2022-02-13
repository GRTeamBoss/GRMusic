import re, subprocess
from typing import Union

from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from core.token import bot
from core.yandex_parse_id import *
from core.yandex_parse_page import *


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
/trackid [value]
/albumid [number]
/artistid [number]
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
`/playlistid` yandex-best:88347328
-
`/trackurl` _https://music.yandex.ru/album/4274705/track/34648265_
domen is should be like _https://music.yandex.ru_
    """
    bot.send_message(message.chat.id, info)


def music_name(message: Message) -> None:
    funcs = {"/trackname": track,"/albumname": album,"/artistname": artist,"/playlistname": playlist,}
    funcs[message.text.split()[0]](message)

def music_id(message: Message) -> None:
    funcs = {"/trackid": track,"/albumid": album,"/artistid": artist,"/playlistid": playlist,}
    funcs[message.text.split()[0]](message, id=True)

def music_url(message: Message) -> None:
    funcs = {"/trackurl": track,"/albumurl": album,"/artisturl": artist,"/playlisturl": playlist,}
    funcs[message.text.split()[0]](message, url=True)

def music_callback(call: CallbackQuery) -> None:
    funcs = {"/trackid": track,"/albumid": album,}
    funcs[call.data.split()[0]](call, callback=True)


def track(method: Union[Message, CallbackQuery], url=False, id=False, callback=False) -> None:
    message = call = False
    if url is True or id is True or any((url, id, callback)) is False:
        message: Message = method
    elif callback is True:
        call: CallbackQuery = method
    if url:
        ref_album = re.findall(r"/album/[\d]+/track/[\d]+", message.text.split()[1])[0]
        _, _, album_id, _, track_id = ref_album.split("/")
        track = YandexParseMusic(track=track_id, album=album_id, ref_album=ref_album).getTrack()
    elif id:
        ref_album = YandexParseMusic(track=message.text.split()[1]).getRefAlbum()
        track = YandexParseMusic(track=message.text.split()[1], ref_album=ref_album).getTrack()
    elif callback:
        ref_album = YandexParseMusic(track=call.data.split()[1]).getRefAlbum()
        track = YandexParseMusic(track=call.data.split()[1], ref_album=ref_album).getTrack()
    else:
        track_id = ParseIDName(track_name=" ".join(message.text.split()[1:]), track=True).trackName()
        try:
            if len(track_id) > 1:
                track = None
                markup = InlineKeyboardMarkup(row_width=1)
                for item in track_id:
                    markup.add(InlineKeyboardButton(f"{item['name']} {item['artist']}", callback_data=f"/trackid {item['id']}"))
                bot.send_message(message.chat.id, "Please choose track:", reply_markup=markup)
            else:
                ref_album = YandexParseMusic(track=track_id[0]['id']).getRefAlbum()
                track = YandexParseMusic(track=track_id[0]['id'], ref_album=ref_album).getTrack()
        except Exception:
            track = False
    if track is False:
        if callback is True:
            bot.send_message(chat_id=call.message.chat.id, text="_Error!_", parse_mode="MARKDOWN")
        else:
            bot.send_message(message.chat.id, "_Error!_", parse_mode="MARKDOWN")
    elif track is None:
        pass
    else:
        file = open(track, "rb")
        mp3 = file.read()
        file.close()
        subprocess.run(f"if [ -e '{track}' ]; then rm '{track}'; else echo 'No'; fi", shell=True)
        if callback is True:
            bot.send_audio(call.message.chat.id, mp3)
        else:
            bot.send_audio(message.chat.id, mp3)


def album(method: Union[Message, CallbackQuery], url=False, id=False, callback=False) -> None:
    message = call = False
    if url is True or id is True or any((url, id, callback)) is False:
        message: Message = method
    elif callback is True:
        call: CallbackQuery = method
    if url:
        album_path = re.findall(r"/album/[\d]+", message.text.split()[1])[0]
        _, _, album_id = album_path.split("/")
        album = YandexParseMusic(album=album_id).getAlbum()
    elif id:
        album = YandexParseMusic(album=message.text.split()[1]).getAlbum()
    elif callback:
        album = YandexParseMusic(album=call.data.split()[1]).getAlbum()
    else:
        album_id = ParseIDName(album_name=" ".join(message.text.split()[1:]), album=True).albumName()
        try:
            if len(album_id) > 1:
                album = None
                markup = InlineKeyboardMarkup(row_width=1)
                for item in album_id:
                    markup.add(InlineKeyboardButton(f"{item['name']} {item['artist']}", callback_data=f"/albumid {item['id']}"))
                bot.send_message(message.chat.id, "Please choose album:", reply_markup=markup)
            else:
                album = YandexParseMusic(album=album_id[0]["id"]).getAlbum()
        except Exception:
            album = False
    if album is False:
        if callback:
            bot.send_message(call.message.chat.id, "_Error!_", parse_mode="MARKDOWN")
        else:
            bot.send_message(message.chat.id, "_Error!_", parse_mode="MARKDOWN")
    elif album is None:
        pass
    else:
        if callback is True:
            for track in album:
                file = open(track, "rb")
                mp3 = file.read()
                file.close()
                subprocess.run(f"if [ -e '{track}' ]; then rm '{track}'; else echo 'No'; fi", shell=True)
                bot.send_audio(call.message.chat.id, mp3)
        else:
            for track in album:
                file = open(track, "rb")
                mp3 = file.read()
                file.close()
                subprocess.run(f"if [ -e '{track}' ]; then rm '{track}'; else echo 'No'; fi", shell=True)
                bot.send_audio(message.chat.id, mp3)


def artist(message: Message, url=False, id=False) -> None:
    if url:
        artist_path = re.findall(r"/artist/[\d]+", message.text.split()[1])[0]
        _, _, artist_id = artist_path.split("/")
        artist = YandexParseMusic(artist=artist_id).getArtist()
    elif id:
        artist = YandexParseMusic(artist=message.text.split()[1]).getArtist()
    else:
        artist_id = ParseIDName(artist_name=" ".join(message.text.split()[1:]), artist=True).artistName()
        artist = YandexParseMusic(artist=artist_id).getArtist()
    if artist is False:
        bot.send_message(message.chat.id, "_Error!_", parse_mode="MARKDOWN")
    else:
        for album in artist:
            for track in album:
                file = open(track, "rb")
                mp3 = file.read()
                file.close()
                subprocess.run(f"if [ -e '{track}' ]; then rm '{track}'; else echo 'No'; fi", shell=True)
                bot.send_audio(message.chat.id, mp3)


def playlist(message: Message, url=False, id=False) -> None:
    if url:
        playlist_path = re.findall(r"/users/[\w\S]+/[\d]+", message.text.split()[1])[0]
        _, _, owner, _, kind = playlist_path.split("/")
        playlist = YandexParseMusic(playlist=dict(owner=owner, kinds=kind)).getPlaylist()
    elif id:
        owner, kind = message.text.split()[1].split(":")
        playlist = YandexParseMusic(playlist=dict(owner=owner, kinds=kind)).getPlaylist()
    else:
        owner, kind = ParseIDName(playlist_name=" ".join(message.text.split()[1:]), playlist=True).playlistName()
        playlist = YandexParseMusic(playlist=dict(owner=owner, kinds=kind)).getPlaylist()
    if playlist is False:
        bot.send_message(message.chat.id, "_Error!_", parse_mode="MARKDOWN")
    else:
        for track in playlist:
            file = open(track, "rb")
            mp3 = file.read()
            file.close()
            subprocess.run(f"if [ -e '{track}' ]; then rm '{track}'; else echo 'No'; fi", shell=True)
            bot.send_audio(message.chat.id, mp3)