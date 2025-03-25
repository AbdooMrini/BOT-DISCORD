from flask import Flask
from threading import Thread
import logging

# Disable Flask's default logging to avoid cluttering the console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('')

@app.route('/')
def home():
    return "Bot is online! 🤖"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Create and start a web server in a separate thread to keep the bot alive"""
    t = Thread(target=run)
    t.daemon = True  # This thread won't prevent program exit
    t.start()
    print("Keep alive server started at http://0.0.0.0:8080/")
    return t 