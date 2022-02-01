import re, subprocess

from telebot import types

from core.token import bot
from core.yandex_parse_id import YandexParseMusic
from core.yandex_parse_page import ParseIDName


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


def track(message, id=False, url=False, call=False):
    if call is True:
        ref_album = YandexParseMusic(track=message.data.split()[1]).getRefAlbum()
        if ref_album == "FAIL":
            bot.edit_message_text(chat_id=message.message.chat.id, text="Your request not finded, try another id!",
                message_id=message.message.message_id
            )
        else:
            tracks = YandexParseMusic(track=message.data.split()[1], ref_album=ref_album).getTrack()
            bot.send_message(message.message.chat.id, f"Track {tracks.split('/')[-1]} Loading...")
            mp3 = open(tracks, 'rb')
            music = mp3.read()
            mp3.close()
            subprocess.run(f"if [[ -e ./Music/{tracks} ]]; then rm ./Music/{tracks}; fi", shell=True)
            bot.send_audio(message.message.chat.id, music)
    else:
        if id is True:
            ref_album = YandexParseMusic(track=message.text.split()[1]).getRefAlbum()
            if ref_album == "FAIL":
                bot.send_message(message.chat.id, "Your request not finded, try another id!")
            else:
                tracks = YandexParseMusic(track=message.text.split()[1], ref_album=ref_album).getTrack()
                bot.send_message(message.chat.id, f"Track {tracks.split('/')[-1]} Loading...")
                mp3 = open(tracks, 'rb')
                music = mp3.read()
                mp3.close()
                subprocess.run(f"if [[ -e ./Music/{tracks} ]]; then rm ./Music/{tracks}; fi", shell=True)
                bot.send_audio(message.chat.id, music)
        elif url is True:
            uri = re.findall(r"/{1}[\w\W]{5}/{1}[\d]+/{1}[\w\W]{5}/{1}[\d]+", message.text.split()[1])[0]
            _, album, album_id, track, track_id = uri.split("/")
            try:
                tracks = YandexParseMusic(track=track_id, ref_album=uri).getTrack()
                bot.send_message(message.chat.id, f"Track `{tracks.split('/')[-1]}` Loading...")
                mp3 = open(tracks, 'rb')
                music = mp3.read()
                mp3.close()
                subprocess.run(f"if [[ -e ./Music/{tracks} ]]; then rm ./Music/{tracks}; fi", shell=True)
                bot.send_audio(message.chat.id, music)
            except Exception:
                bot.send_message(message.chat.id, "Your URI is invalid, try again!")
        else:
            resp_name = ParseIDName(track=True, track_name=message.text.split(" ", 1)[1]).trackName()
            if resp_name is False:
                bot.send_message(message.chat.id, 'Your request not finded, try another name!')
            else:
                markup = types.InlineKeyboardMarkup(row_width=1)
                for item in resp_name:
                    markup.add(types.InlineKeyboardButton(f"{item['album']} {item['artist']}", callback_data=f"/trackid {item['id']}"))
                bot.send_message(message.chat.id, "Album\tArtist\nPlease choose correct `track` from albums:", reply_markup=markup)


def playlist(message, id=False, url=False):
    if id is True:
        temp = message.text.split(' ')[1].split(":")
        tracks = YandexParseMusic(playlist={'owner': temp[0], 'kinds': temp[1]}).getPlaylist()
        if tracks == "FAIL":
            bot.send_message(message.chat.id, "Your request not finded, try another id!")
        else:
            bot.send_message(message.chat.id, 'Playlist Loading...')
            for item in tracks:
                mp3 = open(item, 'rb')
                music = mp3.read()
                mp3.close()
                subprocess.run(f"if [[ -e ./Music/{item} ]]; then rm ./Music/{item}; fi", shell=True)
                bot.send_audio(message.chat.id, music)
    elif url is True:
        uri = re.findall(r"/{1}[\w\W]{5}/{1}[\d]+/{1}[\w\W]{9}/{1}[\d]+", message.text.split()[1])[0]
        _, users, owner, playlist, kinder = uri.split("/")
        tracks = YandexParseMusic(playlist={"owner": owner, "kinds": kinder}).getPlaylist()
        if tracks == "FAIL":
            bot.send_message(message.chat.id, "Your URI is invalid, try again!")
        else:
            bot.send_message(message.chat.id, 'Playlist Loading...')
            for item in tracks:
                mp3 = open(item, 'rb')
                music = mp3.read()
                mp3.close()
                subprocess.run(f"if [[ -e ./Music/{item} ]]; then rm ./Music/{item}; fi", shell=True)
                bot.send_audio(message.chat.id, music)
    else:
        resp_name = ParseIDName(playlist=True, playlist_name=message.text.split(" ", 1)[1]).playlistName()
        if resp_name is False:
            bot.send_message(message.chat.id, 'Your request not finded, try another name!')
        else:
            tracks = YandexParseMusic(playlist={'owner': resp_name[0], 'kinds': resp_name[1]}).getPlaylist()
            bot.send_message(message.chat.id, f'Playlist `{message.text.split(" ")[1]}` Loading...')
            for item in tracks:
                mp3 = open(item, 'rb')
                music = mp3.read()
                mp3.close()
                subprocess.run(f"if [[ -e ./Music/{item} ]]; then rm ./Music/{item}; fi", shell=True)
                bot.send_audio(message.chat.id, music)


def artist(message, id=False, url=False):
    if id is True:
        tracks = YandexParseMusic(artist=message.text.split()[1]).getArtist()
        if tracks == "FAIL":
            bot.send_message(message.chat.id, "Your request not finded, try another id!")
        else:
            bot.send_message(message.chat.id, "Artist Loading...")
            for key, val in tracks.items():
                bot.send_message(message.chat.id, f'Album {key} Loading...')
                for item in val:
                    mp3 = open(item, 'rb')
                    music = mp3.read()
                    mp3.close()
                    subprocess.run(f"if [[ -e ./Music/{item} ]]; then rm ./Music/{item}; fi", shell=True)
                    bot.send_audio(message.chat.id, music)
    elif url is True:
        uri = re.findall(r"/{1}[\w\W]{6}/{1}[\d]+", message.text.split()[1])[0]
        _, artist, artist_id = uri.split("/")
        tracks = YandexParseMusic(artist=artist_id).getArtist()
        if tracks == "FAIL":
            bot.send_message(message.chat.id, "Your URI is invalid, try again!")
        else:
            bot.send_message(message.chat.id, "Artist Loading...")
            for key, val in tracks.items():
                bot.send_message(message.chat.id, f'Album {key} Loading...')
                for item in val:
                    mp3 = open(item, 'rb')
                    music = mp3.read()
                    mp3.close()
                    subprocess.run(f"if [[ -e ./Music/{item} ]]; then rm ./Music/{item}; fi", shell=True)
                    bot.send_audio(message.chat.id, music)
    else:
        resp_name = ParseIDName(artist=True, artist_name=message.text.split(" ", 1)[1]).artistName()
        if resp_name is False:
            bot.send_message(message.chat.id, 'Your request not finded, try another name!')
        else:
            tracks = YandexParseMusic(artist=resp_name).getArtist()
            bot.send_message(message.chat.id, f'Artist `{message.text.split(" ", 1)[1]}` Loading...')
            for key, value in tracks.items():
                bot.send_message(message.chat.id, f'Album `{key}` Loading...')
                for item in value:
                    mp3 = open(item, 'rb')
                    music = mp3.read()
                    mp3.close()
                    subprocess.run(f"if [[ -e ./Music/{item} ]]; then rm ./Music/{item}; fi", shell=True)
                    bot.send_audio(message.chat.id, music)


def album(message, id=False, url=False, call=False):
    if call is True:
        ref_album = '/album/{}'.format(message.data.split()[1])
        tracks = YandexParseMusic(album=message.data.split()[1], ref_album=ref_album).getAlbum()
        if tracks == "FAIL":
            bot.send_message(message.message.chat.id, "Your request not finded, try another id!")
        else:
            bot.send_message(message.message.chat.id, 'Album Loading...')
            for item in tracks:
                mp3 = open(item, 'rb')
                music = mp3.read()
                mp3.close()
                subprocess.run(f"if [[ -e ./Music/{item} ]]; then rm ./Music/{item}; fi", shell=True)
                bot.send_audio(message.message.chat.id, music)
    else:
        if id is True:
            ref_album = '/album/{}'.format(message.text.split()[1])
            tracks = YandexParseMusic(album=message.text.split()[1], ref_album=ref_album).getAlbum()
            if tracks == "FAIL":
                bot.send_message(message.chat.id, "Your request not finded, try another id!")
            else:
                bot.send_message(message.chat.id, 'Album Loading...')
                for item in tracks:
                    mp3 = open(item, 'rb')
                    music = mp3.read()
                    mp3.close()
                    subprocess.run(f"if [[ -e ./Music/{item} ]]; then rm ./Music/{item}; fi", shell=True)
                    bot.send_audio(message.chat.id, music)
        elif url is True:
            uri= re.findall(r"/{1}[\w\W]{5}/{1}[\d]+", message.text.split()[1])[0]
            _, album, album_id = uri.split("/")
            tracks = YandexParseMusic(album=album_id, ref_album=uri).getAlbum()
            if tracks == "FAIL":
                bot.send_message(message.chat.id, "Your URI is invalid, try again!")
            else:
                bot.send_message(message.chat.id, 'Album Loading...')
                for item in tracks:
                    mp3 = open(item, 'rb')
                    music = mp3.read()
                    mp3.close()
                    subprocess.run(f"if [[ -e ./Music/{item} ]]; then rm ./Music/{item}; fi", shell=True)
                    bot.send_audio(message.chat.id, music)
        else:
            resp_name = ParseIDName(album=True, album_name=message.text.split(" ", 1)[1]).albumName()
            if resp_name is False:
                bot.send_message(message.chat.id, 'Your request not finded, try another name!')
            else:
                markup = types.InlineKeyboardMarkup(row_width=1)
                for item in resp_name:
                    markup.add(types.InlineKeyboardButton(f"{item['artist']}", callback_data=f"/albumid {item['id']}"))
                bot.send_message(message.chat.id, "Artist\nPlease choose correct `album` from artists:", reply_markup=markup)