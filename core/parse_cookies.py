import os
import sqlite3


class ParseCookies:


    __PWD_TO_PACKAGE = '/home/user/git/GRMusic/'
    __PWD_TO_TEMP = f'{__PWD_TO_PACKAGE}TEMP/'
    __PWD_TO_DB = '/home/user/.mozilla/firefox/x8afeiud.default-release/'
    __NAME_DB = 'cookies.sqlite'


    def __init__(self) -> None:
        pass


    def cp(self) -> str:
        cmd = f'if [[ -e {self.__PWD_TO_DB}{self.__NAME_DB} ]]; then cp {self.__PWD_TO_DB}{self.__NAME_DB} {self.__PWD_TO_TEMP}; fi;'
        os.system(cmd)


    def read_db(self) -> str:
        data = str()
        db = sqlite3.connect("./TEMP/cookies.sqlite")
        cookies = list(db.cursor().execute('select * from moz_cookies where host GLOB ".yandex.ru"'))
        for row in cookies:
            data += f'{row[2]}={row[3]}; '
        db.close()
        return data


    def main(self) -> any:
        self.cp()
        content = self.read_db()
        return content