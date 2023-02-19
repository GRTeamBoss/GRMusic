import os, sqlite3, time


class ParseCookies:


    def __init__(self) -> None:
        self.MOZILLA_DIRECTORY = "/home/user/.mozilla/firefox/y38kg56w.default-release"


    def parse_sql_cookies(self):
        result = ""
        _time = "".join(str(time.time())[0:14].split("."))
        os.system(f"cp {self.MOZILLA_DIRECTORY}/cookies.sqlite ./TEMP/cookies.sqlite")
        __COOKIES = {
            'yandexuid' : self.parse_sql_name_value('yandexuid'),
            '_yasc' : self.parse_sql_name_value('_yasc'),
            'i' : self.parse_sql_name_value('i'),
            'yuidss' : self.parse_sql_name_value('yuidss'),
            'ymex' : self.parse_sql_name_value('ymex'),
            'gdpr' : self.parse_sql_name_value('gdpr'),
            '_ym_uid' : self.parse_sql_name_value('_ym_uid'),
            '_ym_d' : self.parse_sql_name_value('_ym_d'),
            'is_gdpr' : self.parse_sql_name_value('is_gdpr'),
            'is_gdpr_b' : self.parse_sql_name_value('is_gdpr_b'),
            'Session_id' : self.parse_sql_name_value('Session_id'),
            'sessionid2' : self.parse_sql_name_value('sessionid2'),
            'L' : self.parse_sql_name_value('L'),
            'yandex_login' : self.parse_sql_name_value('yandex_login'),
            'lastVisitedPage' : "%7B%7D",
            'yashr' : self.parse_sql_name_value('yashr'),
            'device_id' : "a20e650936390ae7d90d8b61d9a232e8884d0239d",
            'active_browser_timestamp' : _time,
            '_ym_isad' : self.parse_sql_name_value('_ym_isad'),
            '_ym_visorc' : self.parse_sql_name_value('_ym_visorc')
        }
        for key, value in __COOKIES.items():
            if key == '_ym_visorc':
                result += f"{key}={value}"
            else:
                result += f"{key}={value}; "
        return result


    def parse_sql_name_value(self, name: str):
            database = sqlite3.connect("./TEMP/cookies.sqlite")
            content = list(database.execute(f"select max(id), name, value from moz_cookies where host='.yandex.ru' and name='{name}';"))
            database.close()
            if len(content) > 0:
                return content[0][2]
            else:
                return None


    def main(self):
        content = self.parse_sql_cookies()
        return content
