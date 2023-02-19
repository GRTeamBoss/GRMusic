import requests, time


class YandexMusicParseIds:


    __URI = "https://music.yandex.ru/handlers/music-search.jsx?text={query}&type=all&ncrnd={digit}&clientNow={time}&lang=ru&external-domain=music.yandex.ru&overembed=false"


    def __init__(self, track_name=None, artist_name=None, album_name=None, playlist_name=None, track=None, artist=None, album=None, playlist=None) -> None:
        self.track_name = track_name
        self.artist_name = artist_name
        self.album_name = album_name
        self.playlist_name = playlist_name
        self._reverse_time = f"0.{''.join(time.time().__str__().split('.'))[::-1]}"[0:20]
        self._time = "".join(time.time().__str__().split("."))[0:14]


    def get_track_id(self):
        URI = self.__URI.format(query=self.track_name, digit=self._reverse_time, time=self._time)
        data = requests.get(URI)
        return data.json()['tracks']['items']


    def get_album_id(self):
        URI = self.__URI.format(query=self.album_name, digit=self._reverse_time, time=self._time)
        data = requests.get(URI)
        return data.json()['albums']['items']


    def get_artist_id(self):
        URI = self.__URI.format(query=self.artist_name, digit=self._reverse_time, time=self._time)
        data = requests.get(URI)
        return data.json()['artists']['items']


    def get_playlist_id(self):
        URI = self.__URI.format(query=self.playlist_name, digit=self._reverse_time, time=self._time)
        data = requests.get(URI)
        return data.json()['playlists']['items']
