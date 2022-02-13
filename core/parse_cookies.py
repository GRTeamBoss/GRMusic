import os
import sqlite3


class ParseCookies:


    __PWD_TO_PACKAGE = '/home/user/git/GRMusic/'
    __PWD_TO_TEMP = f'{__PWD_TO_PACKAGE}TEMP/'
    __PWD_TO_DB = '/home/user/.mozilla/firefox/zp0farnc.default-esr/'
    __NAME_DB = 'cookies.sqlite'


    def __init__(self) -> None:
        pass


    def cp(self) -> str:
        print("* cp")
        cmd = f'if [ -e {self.__PWD_TO_DB}{self.__NAME_DB} ]; then cp {self.__PWD_TO_DB}{self.__NAME_DB} {self.__PWD_TO_TEMP}; fi'
        os.system(cmd)


    def read_db(self) -> str:
        print("* read_db")
        data = str()
        db = sqlite3.connect(f"./TEMP/{self.__NAME_DB}")
        cookies = list(db.cursor().execute('select name, value from moz_cookies where host GLOB ".yandex.ru"'))
        for row in cookies:
            data += f'{row[0]}={row[1]}; '
        db.close()
        return data


    def main(self) -> any:
        print("* main")
        self.cp()
        content = self.read_db()
        return content
