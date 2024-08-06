# webserver.py

from flask import Flask
from threading import Thread
import requests
import time

app = Flask('')
@app.route('/')
def home():
    return "DISCORD BOT OKAY"

def run():
    app.run(host = '0.0.0.0', port = 8080)


def keep_alive():
    def ping():
        while True:
            try:
                requests.get('https://discord-bot-6mzo.onrender.com')
                print("Pinged bot to keep alive.")
            except Exception as e:
                print(f"Error keeping bot alive: {e}")
            time.sleep(900) 
    
    t1 = Thread(target=run)
    t2 = Thread(target=ping)
    t1.start()
    t2.start()
    