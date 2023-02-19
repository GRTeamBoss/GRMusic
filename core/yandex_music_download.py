import requests, sqlite3, time, pathlib

from hashlib import md5

from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.id3._frames import TIT2, TALB, TPE1, TDRC, COMM, USLT, APIC

from core.parse_cookies import *


class YandexMusicAPI:


    def __init__(self, track=None, artist=None, album=None, playlist=None) -> None:
        self.track_id = track
        self.album_id = album
        self.artist_id = artist
        self.playlist_id = playlist
        self._time = "".join(time.time().__str__().split("."))[::13]
        self._reverse_time = f"0.{''.join(time.time().__str__().split('.'))[::-1]}"[0:20]



    def download_playlist(self):
        playlist_info = self.get_playlist_info()
        tracks = playlist_info['playlist']['trackIds']
        _tmp = []
        for track in tracks:
            self.track_id = track[0].split(":")[0]
            _tmp.append(self.download_track())
        return _tmp




    def download_artist(self):
        artist_info = self.get_artist_info()
        albums = artist_info['albums']
        _tmp = []
        for album in albums:
            self.album_id = album['id']
            _tmp.append(self.download_album())
        return _tmp



    def download_album(self):
        album_info = self.get_album_info()
        volumes = album_info['volumes'][0]
        _tmp = []
        for item in volumes:
            self.track_id = item['id']
            _tmp.append(self.download_track())
        return _tmp


    def download_track(self):
        track_in_memory = self.check_track_in_db()
        if track_in_memory is True:
            filename = self.get_meta_from_db()
            return f"./Music/{filename}.mp3"
        download_link = self.get_download_link()
        track_info = self.get_track_info()
        _sign = md5(f"XGRlBW9FXlekgbPrRHuSiA{download_link['path'][1::]}{download_link['s']}".encode('utf-8')).hexdigest()
        URI = f"https://{download_link['host']}/get-mp3/{_sign}/{download_link['ts']}{download_link['path']}?track_id={self.track_id}&play=false"
        data = requests.get(URI)
        if data.status_code == 200:
            track_meta = track_info['track']
            filename = "_".join(track_info['track']['title'].split(" "))
            pathlib.Path(f"./Music/{filename}.mp3").touch()
            pathlib.Path(f"./Music/{filename}.mp3").write_bytes(data.content)
            mp3 = MP3(f"./Music/{filename}.mp3")
            mp3.add_tags()
            mp3.save()
            id3 = ID3(f"./Music/{filename}.mp3")
            id3.add(TIT2(encoding=3, text=track_meta['title']))
            id3.add(TALB(encoding=3, text=track_meta['albums'][0]['title']))
            id3.add(TPE1(encoding=3, text=track_meta['artists'][0]['name']))
            id3.add(TDRC(encoding=3, text=str(track_meta['albums'][0]['year'])))
            id3.add(COMM(encoding=3, desc='Telegram', text='Parsed with @gr_team_music_bot'))
            if track_info['lyricsAvailable'] is True:
                id3.add(USLT(encoding=3, desc='lyrics', text=track_info['lyric'][0]['fullLyrics']))
            album_cover = requests.get("https://"+track_meta['albums'][0]['ogImage'][0:-2]+"200x200")
            id3.add(APIC(mime="image/jpeg", type=3, data=album_cover.content))
            id3.save()
            self.set_meta_in_db(track_info)
            return f"./Music/{filename}.mp3"
        return None



    def get_download_link(self):
        """
        return object:
            s : str,
            ts : str,
            path : str,
            host : str,
        """
        download_info = self.get_download_info()
        URI = f"https:{download_info['src']}&format=json&external-domain=music.yandex.ru&overembed=no&__t={self._time}"
        data = requests.get(URI)
        if data.status_code == 200:
            return data.json()




    def get_download_info(self):
        """
        return object:
            codec : str,
            bitrate : int,
            src : str,
            gain : bool,
            preview : bool
        """
        HEADER = self.get_header()
        user_info = self.get_user_info()
        track_info = self.get_track_info()
        HEADER['X-Current-UID'] = user_info['uid']
        URI = f"https://music.yandex.ru/api/v2.1/handlers/track/{track_info['track']['id']}/web-home_new-auto-playlist_of_the_day-playlist-saved/download/m?hq=1&external-domain=music.yandex.ru&overembed=no&__t={self._time}"
        data = requests.get(URI, headers=HEADER)
        if data.status_code == 200:
            return data.json()



    def get_playlist_info(self):
        owner, kind = self.playlist_id.split(":")
        user_info = self.get_user_info()
        HEADER = self.get_header()
        HEADER["X-Current-UID"] = user_info['uid']
        URI = f"https://music.yandex.ru/handlers/playlist.jsx?owner={owner}&kinds={kind}&light=true&madeFor=&withLikesCount=true&forceLogin=true&lang=ru&external-domain=music.yandex.ru&overembed=false&ncrnd={self._reverse_time}"
        data = requests.get(URI, headers=HEADER)
        if data.status_code == 200:
            return data.json()



    def get_artist_info(self):
        user_info = self.get_user_info()
        HEADER = self.get_header()
        HEADER["X-Current-UID"] = user_info['uid']
        URI = f"https://music.yandex.ru/handlers/artist.jsx?artist={self.artist_id}&lang=ru&external-domain=music.yandex.ru&overembed=false&ncrnd={self._reverse_time}"
        data = requests.get(URI, headers=HEADER)
        if data.status_code == 200:
            return data.json()



    def get_album_info(self):
        user_info = self.get_user_info()
        HEADER = self.get_header()
        HEADER["X-Current-UID"] = user_info["uid"]
        URI = f"https://music.yandex.ru/handlers/album.jsx?album={self.album_id}&lang=ru&external-domain=music.yandex.ru&overembed=false&ncrnd={self._reverse_time}"
        data = requests.get(URI, headers=HEADER)
        if data.status_code == 200:
            return data.json()


    def get_track_info(self):
        user_info = self.get_user_info()
        HEADER = self.get_header()
        HEADER["X-Current-UID"] = user_info["uid"]
        URI = f"https://music.yandex.ru/handlers/track.jsx?track={self.track_id}&lang=ru&external-domain=music.yandex.ru&overembed=false&ncrnd={self._reverse_time}"
        data = requests.get(URI, headers=HEADER)
        if data.status_code == 200:
            return data.json()



    def get_user_info(self):
        """
        return object:
            csrf : str,
            isCIS : bool,
            freshCsrf : str,
            uid : str,
            login : str,
            yandexuid : str,
            logged : bool,
            premium : bool,
            lang : str,
            timestamp : int,
            experiments : {...},
            badRegion : bool,
            notFree : bool,
            device_id : str

        """
        HEADER = self.get_header()
        URI = f"https://music.yandex.ru/api/v2.1/handlers/auth?external-domain=music.yandex.ru&overembed=no&__t={self._time}"
        data = requests.get(URI, headers=HEADER)
        if data.status_code == 200:
            return data.json()



    def get_header(self):
        HEADER = {
            "Accept" : "application/json; q=1.0, text/*; q=0.8, */*; q=0.1",
            "Accept-Encoding" : "gzip, deflate, br",
            "Accept-Language" : "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection" : "keep-alive",
            "Cookie" : ParseCookies().main(),
            "Host" : "music.yandex.ru",
            "Referer" : "https://music.yandex.ru/home",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
            "X-Requested-With" : "XMLHttpRequest",
            "X-Retpath-Y" : "https%3A%2F%2Fmusic.yandex.ru%2Fhome",
            "X-Yandex-Music-Client" : "YandexMusicAPI"
        }
        return HEADER


    def set_meta_in_db(self, meta):
        track_name = meta['track']['title']
        track_id = meta["track"]["id"]
        album_id = meta["track"]["albums"][0]["id"]
        artist_id = meta["track"]["artists"][0]["id"]
        db = sqlite3.connect("./bot.db")
        db.execute(
            "insert into Music (TRACK_NAME, TRACK_ID, ALBUM_ID, ARTIST_ID)" +
            f"values ('{track_name}', {track_id}, {album_id}, {artist_id})"
        )
        db.commit()
        db.close()


    def get_meta_from_db(self):
        db = sqlite3.connect("./bot.db")
        content = list(db.execute(f"select TRACK_NAME from Music where TRACK_ID={self.track_id};"))
        db.close()
        return content[0][0]


    def check_track_in_db(self):
        db = sqlite3.connect("./bot.db")
        content = list(db.execute(f"select * from Music where TRACK_ID={self.track_id};"))
        db.close()
        if len(content) > 0:
            return True
        return False
