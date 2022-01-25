import subprocess


class Take_Music:


    def __init__(self) -> None:
        pass


    def __call__(self) -> None:
        __music_list = subprocess.check_output("ls ./Music/", stderr=subprocess.STDOUT, shell=True, encoding="utf-8").strip().split("\n")
        __html_music_list = ""
        for item in __music_list:
            __html_music_list += f"""<figure><figcaption>{item.split(".mp3")[0]}</figcaption><audio controls preload="metadata" src="./Music/{item}">This browser does not support the <code>audio</code> element.</audio></figure>"""
        with open("./web-music.html", "w+", encoding="utf-8") as file:
            file.write(f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Music</title></head><body>{__html_music_list}</body></html>""")


if __name__ == "__main__":
    Take_Music().__call__()