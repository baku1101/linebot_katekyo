# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals

import errno
import os
import sys
import tempfile

from argparse import ArgumentParser

from flask import Flask, request, abort, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)

import mydatabase
import datetime

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 普通のメッセージを受け取った時の動作記述
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    profile = line_bot_api.get_profile(event.source.user_id)
    usrname = 'user_' + profile.display_name
    if text.split()[0] == 'insert':
        startTime = text.split()[1] + ' ' + text.split()[2]
        finishTime = text.split()[3] + ' ' + text.split()[4]
        mydatabase.InsertRow(usrname, startTime, finishTime)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='inserted row'))
    elif text == 'help':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='insert format: Y/m/d H:M'))
    else:
        buttons_template = ButtonsTemplate(
            title='My buttons sample', text='Hello, my buttons', actions=[
                # startというデータのpostbackeventを発行
                PostbackAction(label='start', data='start'),
                PostbackAction(label='finish', data='finish'),
                DatetimePickerAction(label='show', data='show', mode='date'),
                PostbackAction(label='del', data='del'),
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)

@handler.add(PostbackEvent)
def handle_postback(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    usrname = 'user_' + profile.display_name
    data = event.postback.data
    if data == 'start':
        messageStart = 'start timer' if mydatabase.Start(usrname) else 'already started'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=messageStart))
    elif data == 'finish':
        messageFinish = 'finish timer' if mydatabase.Finish(usrname) else 'not start yet'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=messageFinish))
    elif data == 'show':
        date_str = event.postback.params['date']
        year, month, day = date_str.split('-')
        rowList = mydatabase.GetTableByMonth(usrname, year, month)
        output = "record of {}-{}\n".format(year, month)
        for row in rowList:
            start = datetime.datetime.strftime(row[2], "%d日 %H:%M")
            finish = datetime.datetime.strftime(row[3], "%H:%M")
            output += start + ' - ' + finish + '\n'
        sumStr = str(mydatabase.GetSumOfMonth(usrname, year, month))
        output += "sum: " + sumStr
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=output))
    elif data == 'del':
        mydatabase.DeleteRow(usrname)

# 友達登録された時の挙動(ここで新規テーブル作ると良い)
@handler.add(FollowEvent)
def handle_follow(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    usrname = 'user_' + profile.display_name
    mydatabase.CreateTable(usrname)
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))

# ここでテーブル削除すると良い
@handler.add(UnfollowEvent)
def handle_unfollow():
    profile = line_bot_api.get_profile(event.source.user_id)
    usrname = 'user_' + profile.display_name
    mydatabase.CreateTable(usrname)
    app.logger.info("Got Unfollow event")

@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Joined this ' + event.source.type))

@handler.add(LeaveEvent)
def handle_leave():
    app.logger.info("Got leave event")

@app.route('/static/<path:path>')
def send_static_content(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
