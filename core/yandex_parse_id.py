import hashlib
import sqlite3
import time

import requests
from mutagen.id3 import ID3, COMM, TALB, TPE1, TDRC, TIT2, USLT
from mutagen.mp3 import MP3

from core.parse_cookies import ParseCookies


class YandexParseMusic:

    __HOST = 'music.yandex.ru'


    def __init__(self, track=False, artist=False, album=False, ref_album=False,  playlist=False) -> None:
        self.track = track
        self.artist = artist
        self.album = album
        self.ref_album = ref_album
        self.playlist = playlist
        self.__HOST_API = False
        self._HEADERS_MDS = False
        self._HEADER_API = False
        self._HEADER_MPEG = False
        self._HEADERS_JSX = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Cookie": ParseCookies().main(),
            'Host': self.__HOST,
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
        }


    def trackDownloadedMeta(self, artist: str, title: str, album: str, track_text: str, year: str) -> dict:
        print("* trackDownloadedMeta")
        content = dict(artist=artist, album=album, title=title, track_text=track_text, year=year)
        return content


    def trackDownloadedInfo(self, codec: str, bitrate: int, src: str, gain: bool, preview: bool) -> dict:
        print("* trackDownloadedInfo")
        content = {
            'codec': codec,
            'bitrate': bitrate,
            'src': src,
            'gain': gain,
            'preview': preview,
        }
        return content


    def fileDownloadedInfo(self, s: str, ts: str, path: str, host: str) -> dict:
        print("* fileDownloadedInfo")
        content = {
            's': s,
            'ts': ts,
            'path': path,
            'host': host,
        }
        return content


    def getObject(self, type=False, path=False, header=False) -> any:
        print("* getObject")
        if path:
            url = 'https://' + path
        else: 
            return ValueError(path)
        if header:
            response = requests.get(url, headers=header)
        else:
            response = requests.get(url)
        print("response.status_code > ", response.status_code)
        if response.status_code == 200:
            if type == 'text':
                response.encoding = 'utf-8'
                return response.text
            elif type == 'json':
                return response.json()
        else:
            return f'status_code -> {response.status_code}'


    def getRefAlbum(self) -> str:
        print("* getRefAlbum")
        resp = self.getObject(type='json', path=f'{self.__HOST}/handlers/track.jsx?track={self.track}')
        if isinstance(resp, str):
            return "FAIL"
        album_id = resp['track']['albums'][0]['id']
        ref_album = f'/album/{album_id}/track/{self.track}'
        return ref_album


    def getTrack(self) -> str:
        print("* getTrack")
        resp = self.getTrackLink()
        return resp


    def getAlbum(self) -> list:
        print("* getAlbum")
        response = self.getObject(type='json', path='{}/handlers/album.jsx?album={}'.format(self.__HOST, self.album), header=self._HEADERS_JSX)
        if isinstance(response, str):
            return "FAIL"
        data = list()
        for disk in range(len(response['volumes'])):
            for num in range(len(response['volumes'][disk])):
                track_id = response['volumes'][disk][num]['id']
                temp_path = YandexParseMusic(track=track_id, ref_album=self.ref_album).getTrackLink()
                data.append(temp_path)
        return data


    def getArtist(self) -> dict:
        print("* getArtist")
        response = self.getObject(type='json', path='{}/handlers/artist.jsx?artist={}'.format(self.__HOST, self.artist), header=self._HEADERS_JSX)
        if isinstance(response, str):
            return "FAIL"
        albums = response['count']['directAlbums']
        data = dict()
        for num in albums:
            album_id = response['albums'][num]['id']
            ref_album = '/album/{}'.format(album_id)
            album_name = response['albums'][num]['title']
            album_path = YandexParseMusic(album=album_id, ref_album=ref_album).getAlbum()
            data[album_name] = album_path
        return data


    def getPlaylist(self) -> list:
        print("* getPlaylist")
        response = self.getObject(type='json', path='{}/handlers/playlist.jsx?owner={}&kinds={}'.format(self.__HOST, self.playlist['owner'], self.playlist['kinds']), header=self._HEADERS_JSX)
        if isinstance(response, str):
            return "FAIL"
        track_count = response['playlist']['trackCount']
        data = list()
        for num in range(track_count):
            track_id = response['playlist']['tracks'][num]['id']
            album_id = response['playlist']['tracks'][num]['albums'][0]['id']
            ref_album = '/album/{}'.format(album_id)
            track_path = YandexParseMusic(track=track_id, ref_album=ref_album).getTrackLink()
            data.append(track_path)
        return data



    def getTrackMeta(self) -> dict:
        print("* getTrackMeta")
        response = self.getObject(type='json', path='{}/handlers/track.jsx?track={}'.format(self.__HOST, self.track), header=self._HEADERS_JSX)
        data = dict()
        artist = response['track']['artists'][0]['name']
        album = response['track']['albums'][0]['title']
        title = response['track']['title']
        year = str(response['track']['albums'][0]['year'])
        if response['lyric']:
            track_text = response['lyric'][0]['fullLyrics']
        else:
            track_text = ''
        meta_content = dict(artist=artist, album=album, title=title, track_text=track_text, year=year)
        data[f'{title}_track_meta'] = meta_content
        return data


    def getAlbumMeta(self) -> dict:
        print("* getAlbumMeta")
        response = self.getObject(type='json', path='{}/handlers/album.jsx?album={}'.format(self.__HOST, self.album), header=self._HEADERS_JSX)
        data = dict()
        meta_content = dict()
        album_name = response['title']
        for num in range(response['trackCount']):
            track_id = response['volumes'][0][num]['id']
            track_name = response['volumes'][0][num]['title']
            time.sleep(1)
            temp = YandexParseMusic(track=track_id).getTrackMeta()
            meta_content['{}_track_meta'.format(track_name)] = temp['{}_track_meta'.format(track_name)]
        data['tracks'] = meta_content
        data['{}_album_meta'.format(album_name)] = {
            'album': response['title'],
            'year': response['year'],
            'artist': response['artists'][0]['name'],
            'genre': response['genre'],
            'tracks': response['trackCount'],
        }
        return data


    def getArtistMeta(self) -> dict:
        print("* getArtistMeta")
        response = self.getObject(type='json', path='{}/handlers/artist.jsx?artist={}'.format(self.__HOST, self.artist), header=self._HEADERS_JSX)
        data = dict()
        artist = response['artist']['name']
        genres = response['artist']['genres'] or False
        albums = response['count']['directAlbums']
        tracks = response['count']['tracks']
        meta_content = dict()
        for num in albums:
            album_id = response['albums'][num]['id']
            album_name = response['albums'][num]['title']
            time.sleep(1)
            temp = YandexParseMusic(album=album_id).getAlbumMeta()
            meta_content['{}_tracks'.format(album_name)] = temp['tracks']
            meta_content['{}_album_meta'.format(album_name)] = temp['{}_album_meta'.format(album_name)]
        data['albums'] = meta_content
        data['{}_artist_meta'.format(artist)] = {
            'artist': artist, 
            'genres': genres,
            'albums': albums,
            'tracks': tracks,
        }
        return data


    def getPlaylistMeta(self) -> dict:
        print("* getPlaylistMeta")
        response = self.getObject(type='json', path='{}/handlers/playlist.jsx?owner={}&kinds={}'.format(self.__HOST, self.playlist['owner'], self.playlist['kinds']), header=self._HEADERS_JSX)
        data = dict()
        meta_content = dict()
        playlist_name = response['playlist']['title']
        track_count = response['playlist']['trackCount']
        playlist_duration = response['playlist']['duration']
        for num in range(response['playlist']['trackCount']):
            track_id = response['playlist']['tracks'][num]['id']
            track_name = response['playlist']['tracks'][num]['title']
            time.sleep(1)
            temp = YandexParseMusic(track=track_id).getTrackMeta()
            meta_content['{}_track_meta'.format(track_name)] = temp['{}_track_meta'.format(track_name)]
        data['{}_tracks'.format(playlist_name)] = meta_content
        data['{}_playlist_meta'] = {
            'playlist': playlist_name,
            'tracks': track_count,
            'duration': playlist_duration,
        }
        return data


    def getTrackLink(self) -> str:
        print("* getTrackLink")
        url = self.getHostAPI()
        temp_api_header = self.get_HEADER_API()
        track_name = list(self.getTrackMeta().values())[0]['title']
        time.sleep(1)
        response_track = self.getObject(type='json', path='{}{}'.format(self.__HOST, url), header=temp_api_header)
        trackInfo = self.trackDownloadedInfo(codec=response_track['codec'], bitrate=response_track['bitrate'], src=response_track['src'], gain=response_track['gain'], preview=response_track['preview'])
        time.sleep(1)
        response_file = self.getObject(type='json', path='{}&format=json&external-domain={}&overembed=no&t_={}'.format(trackInfo['src'][2::], self.__HOST, ''.join(time.time().__str__()[0:14].split('.'))), header=self._HEADERS_MDS)
        fileInfo = self.fileDownloadedInfo(s=response_file['s'], ts=response_file['ts'], path=response_file['path'], host=response_file['host'])
        temp = 'XGRlBW9FXlekgbPrRHuSiA{}{}'.format(fileInfo['path'][1::], fileInfo['s'])
        md5hash = hashlib.md5(temp.encode())
        path = '/get-mp3/{}/{}{}?track-id={}'.format(md5hash.hexdigest(), fileInfo['ts'], fileInfo['path'], self.track)
        track_link = 'https://{}{}'.format(fileInfo['host'], path)
        temp_header = self.get_HEADER_MPEG(host=fileInfo['host'])
        time.sleep(1)
        content = requests.get(track_link, headers=temp_header)
        with open('./Music/{}.mp3'.format(track_name), 'wb') as file:
            file.write(content.content)
        track_path = './Music/{}.mp3'.format(track_name)
        track_meta = self.getTrackMeta()['{}_track_meta'.format(track_name)]
        audio = MP3(track_path)
        audio.add_tags()
        audio.save()
        mp3 = ID3(track_path)
        mp3.add(TIT2(encoding=3, text=track_meta['title']))
        mp3.add(TALB(encoding=3, text=track_meta['album']))
        mp3.add(TPE1(encoding=3, text=track_meta['artist']))
        mp3.add(TDRC(encoding=3, text=track_meta['year']))
        mp3.add(COMM(encoding=3, desc='Telegram', text='Parsed with @GRSearch_Bot!'))
        mp3.add(USLT(encoding=3, desc='lyrics', text=track_meta['track_text']))
        mp3.save()
        self.set_meta_in_db()
        return track_path


    def getCoverLink(self, uri: str, size: int) -> any:
        print("* getCoverLink")
        return 'https://{}{}x{}'.format(uri[::-2], size, size)



    def getHostAPI(self) -> str:
        print("* getHostAPI")
        self.__HOST_API = (
            f'/api/v2.1/handlers/track/{self.track}:{self.ref_album.split("/")[2]}/' +
            'web-album-track-track-main/download/m?' +
            f'hq=0&external-domain={self.__HOST}&' +
            f"overembed=no&__t={''.join(time.time_ns().__str__()[:14])}"
        )
        return self.__HOST_API


    def get_HEADER_MPEG(self, host=False) -> str:
        print("* get_HEADER_MPEG")
        self._HEADER_MPEG = {
            'Host': host,
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
            'Accept': 'audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5',
            'Referer': 'https://{}{}'.format(self.__HOST, self.ref_album),
            'Range': 'bytes=0-',
            'Origin': 'https://{}'.format(self.__HOST),
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'audio',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
        }
        return self._HEADER_MPEG


    def get_HEADER_MDS(self) -> str:
        print("* get_HEADER_MDS")
        self._HEADERS_MDS = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
            'Host': 'storage.mds.yandex.net',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://{}{}'.format(self.__HOST, self.ref_album),
            'Origin': 'https://{}'.format(self.__HOST),
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'TE': 'trailers',
        }
        return self._HEADERS_MDS


    def get_HEADER_API(self) -> str:
        print("* get_HEADER_API")
        self._HEADER_API = {
            'Host': self.__HOST,
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            'Accept-Encoding': 'gzip, deflate, br',
            "Accept-Language": "en-US,en;q=0.5",
            'Referer': f'https://{self.__HOST}{self.ref_album}',
            'X-Retpath-Y': f'https%3A%2F%2F{self.__HOST}%2Falbum%2F{self.ref_album[7::]}',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            "Cookie": ParseCookies().main(),
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            "Sec-Fetch-Dest": "empty",
            "Upgrade-Insecure-Requests": "1",
        }
        return self._HEADER_API


    def set_meta_in_db(self):
        print("* set_meta_in_db")
        meta = self.getObject(type='json', path='{}/handlers/track.jsx?track={}'.format(self.__HOST, self.track), header=self._HEADERS_JSX)
        track_name = meta['track']['title']
        track_id = meta["track"]["id"]
        album_id = meta["track"]["albums"][0]["id"]
        artist_id = meta["track"]["artists"][0]["id"]
        db = sqlite3.connect("bot.db")
        db.cursor().execute(
            "insert into Music (TRACK_NAME, TRACK_ID, ALBUM_ID, ARTIST_ID)" +
            f"values ('{track_name}', {track_id}, {album_id}, {artist_id})"
        )
        db.commit()
        db.close()


    def __str__(self) -> str:
        content = dict(track_id=self.track, artist_id=self.artist, album_id=self.artist, playlist=self.playlist)
        return content.__str__()


    def __sizeof__(self) -> int:
        count = 0
        if self.track:
            count += 1
        if self.album:
            count += 3
        if self.artist:
            count += 5
        if self.playlist:
            count += 7
        return count