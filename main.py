#!/usr/bin/env python
#-*- coding:utf-8 -*-


from core.filter import default_command, music_command_id, music_command_name, music_command_url
from core.telegram import start, usage, music_callback, music_id, music_name, music_url
from core.token import bot



@bot.message_handler(func=lambda message: default_command(message) is True)
def bot_commands(message):
    funcs = {
        "/start": start,
        "/help": usage
    }
    funcs[message.text](message)


@bot.message_handler(func=lambda message: music_command_name(message) is True)
def parse_track_name(message):
    music_name(message)


@bot.message_handler(func=lambda message: music_command_id(message) is True)
def parse_track_id(message):
    music_id(message)


@bot.message_handler(func=lambda message: music_command_url(message) is True)
def parse_track_url(message):
    music_url(message)


@bot.callback_query_handler(func=lambda call: music_command_id(call, call=True) is True)
def parse_track_id_callback(call):
    music_callback(call)

if __name__ == "__main__":
    bot.polling(non_stop=True)
