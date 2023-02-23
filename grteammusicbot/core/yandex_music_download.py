import requests, time

from hashlib import md5


from grteammusicbot.core.parse_cookies import *
from grteammusicbot.core.token import bot
from grteammusicbot.logger import logger


class YandexMusicAPI:


    def __init__(self, chat_id, track=None, artist=None, album=None, playlist=None) -> None:
        self.chat_id = chat_id
        self.track_id = track
        self.album_id = album
        self.artist_id = artist
        self.playlist_id = playlist
        self._time = "".join(time.time().__str__().split("."))[0:13]
        self._reverse_time = f"0.{''.join(time.time().__str__().split('.'))[::-1]}"[0:20]



    def download_playlist(self):
        playlist_info = self.get_playlist_info()
        if playlist_info is None:
            pass
        else:
            tracks = playlist_info['playlist']['trackIds']
            for track in tracks:
                self.track_id = str(track).split(":")[0]
                self.download_track()


    def download_artist(self):
        artist_info = self.get_artist_info()
        if artist_info is None:
            pass
        else:
            albums = artist_info['albums']
            for album in albums:
                self.album_id = album['id']
                self.download_album()


    def download_album(self):
        album_info = self.get_album_info()
        if album_info is None:
            pass
        else:
            volumes = album_info['volumes'][0]
            for item in volumes:
                self.track_id = item['id']
                self.download_track()


    def download_track(self):
        download_link = self.get_download_link()
        track_info = self.get_track_info()
        if download_link is None or track_info is None:
            return None
        _sign = md5(f"XGRlBW9FXlekgbPrRHuSiA{download_link['path'][1::]}{download_link['s']}".encode('utf-8')).hexdigest()
        URI = f"https://{download_link['host']}/get-mp3/{_sign}/{download_link['ts']}{download_link['path']}?track_id={self.track_id}&play=false"
        data = requests.get(URI)
        if data.status_code == 200:
            track_meta = track_info['track']
            bot.send_audio(self.chat_id, data.content, title=track_meta['title'], performer=track_meta['artists'][0]['name'])
        else:
            bot.send_message(self.chat_id, f"{track_info['track']['title']} не скачался.\nID={self.track_id}")
            logger.info(f"[{data.url} -> {data.status_code}]")



    def get_download_link(self):
        """
        return object:
            s : str,
            ts : str,
            path : str,
            host : str,
        """
        download_info = self.get_download_info()
        if download_info is None:
            return None
        URI = f"https:{download_info['src']}&format=json&external-domain=music.yandex.ru&overembed=no&__t={self._time}"
        data = requests.get(URI)
        if data.status_code == 200:
            return data.json()
        else:
            bot.send_message(self.chat_id, f"Ссылка для скачивания не получена.")
            logger.info(f"[{data.url} -> {data.status_code}]")
            return None




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
        if user_info is None or track_info is None:
            return None
        HEADER['X-Current-UID'] = user_info['uid']
        URI = f"https://music.yandex.ru/api/v2.1/handlers/track/{track_info['track']['id']}/web-home_new-auto-playlist_of_the_day-playlist-saved/download/m?hq=1&external-domain=music.yandex.ru&overembed=no&__t={self._time}"
        data = requests.get(URI, headers=HEADER)
        if data.status_code == 200:
            return data.json()
        else:
            bot.send_message(self.chat_id, f"Не удалось получить информацию для получения ссылки для скачивания.")
            logger.info(f"[{data.url} -> {data.status_code}]")
            return None



    def get_playlist_info(self):
        owner, kind = str(self.playlist_id).split(":")
        user_info = self.get_user_info()
        if user_info is None:
            return None
        HEADER = self.get_header()
        HEADER["X-Current-UID"] = user_info['uid']
        URI = f"https://music.yandex.ru/handlers/playlist.jsx?owner={owner}&kinds={kind}&light=true&madeFor=&withLikesCount=true&forceLogin=true&lang=ru&external-domain=music.yandex.ru&overembed=false&ncrnd={self._reverse_time}"
        data = requests.get(URI, headers=HEADER)
        if data.status_code == 200:
            return data.json()
        else:
            bot.send_message(self.chat_id, "Не удалось получить мета-информацию плейлиста.")
            logger.info(f"[{data.url} -> {data.status_code}]")
            return None



    def get_artist_info(self):
        user_info = self.get_user_info()
        if user_info is None:
            return None
        HEADER = self.get_header()
        HEADER["X-Current-UID"] = user_info['uid']
        URI = f"https://music.yandex.ru/handlers/artist.jsx?artist={self.artist_id}&lang=ru&external-domain=music.yandex.ru&overembed=false&ncrnd={self._reverse_time}"
        data = requests.get(URI, headers=HEADER)
        if data.status_code == 200:
            return data.json()
        else:
            bot.send_message(self.chat_id, "Не удалось получить мета-информацию артиста.")
            logger.info(f"[{data.url} -> {data.status_code}]")
            return None



    def get_album_info(self):
        user_info = self.get_user_info()
        if user_info is None:
            return None
        HEADER = self.get_header()
        HEADER["X-Current-UID"] = user_info["uid"]
        URI = f"https://music.yandex.ru/handlers/album.jsx?album={self.album_id}&lang=ru&external-domain=music.yandex.ru&overembed=false&ncrnd={self._reverse_time}"
        data = requests.get(URI, headers=HEADER)
        if data.status_code == 200:
            return data.json()
        else:
            bot.send_message(self.chat_id, "Не удалось получить мета-информацию альбома.")
            logger.info(f"[{data.url} -> {data.status_code}]")
            return None


    def get_track_info(self):
        user_info = self.get_user_info()
        if user_info is None:
            return None
        HEADER = self.get_header()
        HEADER["X-Current-UID"] = user_info["uid"]
        URI = f"https://music.yandex.ru/handlers/track.jsx?track={self.track_id}&lang=ru&external-domain=music.yandex.ru&overembed=false&ncrnd={self._reverse_time}"
        data = requests.get(URI, headers=HEADER)
        if data.status_code == 200:
            return data.json()
        else:
            bot.send_message(self.chat_id, "Не удалось получить мета-информацию трека.")
            logger.info(f"[{data.url} -> {data.status_code}]")
            return None



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
        else:
            bot.send_message(self.chat_id, "Не удалось получить мета-информацию пользователя.")
            logger.info(f"[{data.url} -> {data.status_code}]")
            return None



    def get_header(self):
        HEADER = {
            "Accept" : "application/json; q=1.0, text/*; q=0.8, */*; q=0.1",
            "Accept-Encoding" : "gzip, deflate, br",
            "Accept-Language" : "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection" : "keep-alive",
            "Cookie" : ParseCookies(chat_id=self.chat_id).main(),
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

