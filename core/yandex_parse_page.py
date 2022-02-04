import re
from typing import Union

import requests
from bs4 import BeautifulSoup

from core.parse_cookies import ParseCookies


class ParseIDName:


    def __init__(self, track_name=False, artist_name=False, album_name=False, playlist_name=False, track=False, artist=False, album=False, playlist=False) -> None:
        self.track_name = track_name
        self.artist_name = artist_name
        self.album_name = album_name
        self.playlist_name = playlist_name


    def parsePage(self, text_arg: str, type_arg: str):
        call_arg = {
            'track': 'tracks',
            'artist': 'artists',
            'album': 'albums',
            'playlist': 'playlists'
        }
        response = requests.get(f'https://music.yandex.ru/search?text={text_arg}&type={call_arg[type_arg]}')
        if response.status_code == 200:
            return response.text
        else:
            return False


    def trackName(self) -> any:
        print("* trackName")
        data = BeautifulSoup(self.parsePage(self.track_name, 'track'), 'lxml')
        if data:
            data_track_name = data.find_all('div', attrs={'class': 'd-track__name', 'title': self.track_name})
            if data_track_name:
                track_meta = []
                track_link = data.find_all('a', attrs={'class': ['d-track__title', 'deco-link', 'deco-link_stronger']}, text=f' {self.track_name} ')
                for item in track_link:
                    track_id = re.findall(r"href=\"[\w\W]*\"", item.__str__())[0].split('href=')[1].split('"')[1].split('/')[4]
                    meta = self.track_meta(track_id)
                    if meta:
                        track_meta.append(meta)
                    else:
                        continue
                return track_meta
        return False


    def artistName(self):
        print("* artistName")
        data = BeautifulSoup(self.parsePage(self.artist_name, 'artist'), 'lxml')
        if data:
            artist_link = data.find('div', attrs={'class': ['d-link', 'deco-link'], 'title': self.artist_name})
            if artist_link:
                artist_id = re.findall(r'href=\"[\w\W]*\"', artist_link.__str__())[0].split('href=')[1].split('"')[1].split('/')[2]
                return artist_id
        return False


    def albumName(self):
        print("* albumName")
        data = BeautifulSoup(self.parsePage(self.album_name, 'album'), 'lxml')
        if data:
            data_album_name = data.find_all('a', attrs={'class': ['d-link', 'deco-link', 'album__caption']}, text=self.album_name)
            if data_album_name:
                album_meta = []
                for item in data_album_name:
                    album_id = re.findall(r'href=\"[\w\W]*\"', data_album_name.__str__())[0].split('href=')[1].split('"')[1].split('/')[2]
                    meta = self.album_meta(album_id)
                    if meta:
                        album_meta.append(meta)
                    else:
                        continue
                return album_meta
        return False


    def playlistName(self) -> any:
        print("* playlistName")
        data = BeautifulSoup(self.parsePage(self.playlist_name, 'playlist'), 'lxml')
        if data:
            data_playlist_name = data.find('div', attrs={'class': ['playlist__title', 'deco-typo', 'typo-main'], 'title': self.playlist_name})
            if data_playlist_name:
                data_playlist_id = data.find('span', attrs={'class': ['d-link', 'deco-link', 'playlist__title-link']}, text=self.playlist_name)
                playlist_owner = re.findall(r'href=\"[\w\W]*\"', data_playlist_id.__str__())[0].split('href=')[1].split('"')[1].split('/')[2]
                playlist_kind = re.findall(r'href=\"[\w\W]*\"', data_playlist_id.__str__())[0].split('href=')[1].split('"')[1].split('/')[4]
                content = (playlist_owner, playlist_kind)
                return content
        return False


    def track_meta(self, id: Union[str, int]) -> dict:
        print("* track_meta")
        _HEADERS_JSX = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Cookie": ParseCookies().main(),
            'Host': "music.yandex.ru",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
        }
        page = requests.get(f"https://music.yandex.ru/handlers/track.jsx?track={id}",  headers=_HEADERS_JSX)
        if page.status_code == 200:
            meta = {}
            data = page.json()
            meta["name"] = data["track"]["title"]
            meta["id"] = data["track"]["id"]
            meta["album"] = data["track"]["albums"][0]["title"]
            meta["artist"] = data["track"]["artists"][0]["name"]
            return meta
        else:
            return False


    def album_meta(self, id: Union[str, int]) -> dict:
        print("* album_meta")
        _HEADERS_JSX = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Cookie": ParseCookies().main(),
            'Host': "music.yandex.ru",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
        }
        page = requests.get(f"https://music.yandex.ru/handlers/album.jsx?album={id}", headers=_HEADERS_JSX)
        if page.status_code == 200:
            meta = {}
            data = page.json()
            meta["name"] = data["title"]
            meta["id"] = data["id"]
            meta["artist"] = data["artists"][0]["name"]
            return meta
        else:
            return False
