#!/usr/bin/env python
#-*- coding:utf-8 -*-


from core.filter import *
from core.telegram import *
from core.token import bot



@bot.message_handler(func=lambda message: user_command(message) is True)
def bot_commands(message):
    funcs = {
        "/start": start,
        "/help": usage
    }
    funcs[message.text](message)


@bot.message_handler(func=lambda message: apps_command_name(message) is True)
def parse_track_name(message):
    funcs = {
        "/trackname": track,
        "/albumname": album,
        "/artistname": artist,
        "/playlistname": playlist,
    }
    funcs[message.text.split()[0]](message)


@bot.message_handler(func=lambda message: apps_command_id(message) is True)
def parse_track_id(message):
    funcs = {
        "/trackid": track,
        "/albumid": album,
        "/artistid": artist,
        "/playlistid": playlist,
    }
    funcs[message.text.split()[0]](message, id=True)


@bot.message_handler(func=lambda message: apps_command_url(message) is True)
def parse_track_url(message):
    funcs = {
        "/trackurl": track,
        "/albumurl": album,
        "/artisturl": artist,
        "/playlisturl": playlist,
    }
    funcs[message.text.split()[0]](message, url=True)

@bot.inline_handler(func=lambda call: apps_command_id(call.data, call=True) is True)
def parse_track_id_callback(call):
    funcs = {
        "/trackid": track,
        "/albumid": album,
    }
    funcs[call.data.split()[0]](call, call=True)


if __name__ == "__main__":
    bot.polling(non_stop=True)
