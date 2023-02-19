#!/usr/bin/env python
#-*- coding:utf-8 -*-

import flask, telebot
from flask import Flask, request

from core.filter import check_user_info, default_command, music_command_id, music_command_name, music_command_url, user_registrated
from core.telegram import start, usage, registration, music_callback, music_id, music_name, music_url, session
from core.token import bot


app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return {'status': True}

@app.route("/update", methods=["POST"])
def update():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


@bot.message_handler(func=lambda message: default_command(message) is True)
def bot_commands(message):
    funcs = {
        "/start": start,
        "/help": usage
    }
    funcs[message.text](message)


@bot.message_handler(commands=['registration'])
def registrate_user(message):
    registration(message)


@bot.message_handler(commands=['session_id'])
def session_user(message):
    session(message)


@bot.message_handler(func=lambda message: music_command_name(message) is True and user_registrated(message) is True and check_user_info(message) is True)
def parse_track_name(message):
    music_name(message)


@bot.message_handler(func=lambda message: music_command_id(message) is True and user_registrated(message) is True and check_user_info(message) is True)
def parse_track_id(message):
    music_id(message)


@bot.message_handler(func=lambda message: music_command_url(message) is True and user_registrated(message) is True and check_user_info(message) is True)
def parse_track_url(message):
    music_url(message)


@bot.callback_query_handler(func=lambda call: music_command_id(call, call=True) is True and user_registrated(call, call=True) is True and check_user_info(call, call=True) is True)
def parse_track_id_callback(call):
    music_callback(call)

if __name__ == "__main__":
    app.run("0.0.0.0", port=443)
