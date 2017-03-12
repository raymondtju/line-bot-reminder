# -*- coding: utf-8 -*-

import os
import sys
reload(sys)     
sys.setdefaultencoding("utf-8")

from flask import Flask, render_template, request, redirect, url_for

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from bo import EventBO
from message import send_text_message

app = Flask(__name__)

channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')


###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)
    print("Request body: %s" % body)

    # parse webhook body
    try:
        events = handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if hasattr(event.source, "user_id"):
        user_id = event.source.user_id
        # print("user_id: %s" % event.source.user_id)
    
    text = event.message.text
    bo = EventBO()

    if text.startswith("/add"):
        result = bo.handle_add_command(user_id, command_parser(text[4:]))
    elif text.startswith("/remove"):
        result = bo.handle_remove_command(user_id, command_parser(text[7:]))
    elif text.startswith("/reset"):
        result = bo.handle_reset_command(user_id, command_parser(text[6:]))

    if result:
        send_text_message(user_id, "OK!")

def command_parser(input):
    import getopt
    args, long_options = getopt.getopt(input.split(), "n:t:")
    return args

if __name__ == '__main__':
    app.run(debug=True)
