#!/usr/bin/env python
#-*- coding:utf-8 -*-

import telebot
from telebot.types import Message

from grteammusicbot.core.filter import check_user_info, default_command, is_admin, music_command_id, music_command_name, music_command_url, user_registrated
from grteammusicbot.core.telegram import start, usage, registration, music_callback, music_id, music_name, music_url, session, send_log
from grteammusicbot.core.token import bot
from grteammusicbot.logger import logger


@bot.message_handler(func=lambda message: default_command(message) is True)
def bot_commands(message: Message):
    funcs = {
        "/start": start,
        "/help": usage
    }
    logger.info(f"{message.from_user.username} -> {message.text}")
    funcs[message.text](message)


@bot.message_handler(commands=['registration'])
def registration_user(message):
    logger.info(f"{message.from_user.username} -> {message.text}")
    registration(message)


@bot.message_handler(commands=['session_id'])
def session_user(message):
    logger.info(f"{message.from_user.username} -> {message.text}")
    session(message)

@bot.message_handler(commands=['log'], func=lambda message: is_admin(message) is True)
def log_user(message):
    logger.info(f"{message.from_user.username} -> {message.text}")
    send_log(message)


@bot.message_handler(func=lambda message: music_command_name(message) is True and user_registrated(message) is True and check_user_info(message) is True)
def parse_track_name(message):
    logger.info(f"{message.from_user.username} -> {message.text}")
    music_name(message)


@bot.message_handler(func=lambda message: music_command_id(message) is True and user_registrated(message) is True and check_user_info(message) is True)
def parse_track_id(message):
    logger.info(f"{message.from_user.username} -> {message.text}")
    music_id(message)


@bot.message_handler(func=lambda message: music_command_url(message) is True and user_registrated(message) is True and check_user_info(message) is True)
def parse_track_url(message):
    logger.info(f"{message.from_user.username} -> {message.text}")
    music_url(message)


@bot.callback_query_handler(func=lambda call: music_command_id(call, call=True) is True and user_registrated(call, call=True) is True and check_user_info(call, call=True) is True)
def parse_track_id_callback(call):
    logger.info(f"{call.message.from_user.username} -> {call.message.text}")
    music_callback(call)



if __name__ == "__main__":
    bot.polling(non_stop=True)
