import json
import requests
import time
import urllib
import os
import random
import yaml
import mysql.connector

SESSION_ID = random.randint(0,1000000)
TOKEN = os.getenv('BOT_TOKEN',"Starting now!")
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
keyboard_wait = ["Starting now!","Out!"]

def getDB(query):
    cnx = mysql.connector.connect(user='root', database='workcouBot', passwd='', host='localhost')
    cursor = cnx.cursor()
    query = ("SELECT * from messagesLog")
    cursor.execute(query)
    data = cursor.fetchall()
    names = cursor.column_names
    cursor.close()
    cnx.close()
    return names,data

def setMessageDB(id, date, chat, username, text):
    cnx = mysql.connector.connect(user='root', database='workcouBot', passwd='J4v5f7o3', host='localhost')
    cursor = cnx.cursor()
    sql = "INSERT INTO messagesLog (id, date, chat_id, username, text) VALUES (%s, %s, %s, %s, %s)"
    val = (id, date, chat, username, text)
    cursor.execute(sql, val)
    cnx.commit()
    print(cursor.rowcount, "record inserted by {}.".format(username))
    cursor.close()
    cnx.close()


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def handle_updates(updates):
    for update in updates["result"]:
        try:
            id = update["message"]["message_id"]
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            date = update["message"]["date"]
        except Exception as e:
            print(e)
        try:
            first_name = update["message"]["from"]["first_name"]
        except Exception as e:
            print(e)
            first_name = "NULL"
        try:
            last_name = update["message"]["from"]["last_name"]
        except Exception as e:
            print(e)
            last_name = "NULL"
        try:
            username = update["message"]["from"]["username"]
        except Exception as e:
            print(e)
            username = "NULL"

        try:
            if text == keyboard_wait[0]:
                keyboard = build_keyboard(keyboard_wait)
                send_message("Good morning {}! Go get them!".format(username), chat,keyboard)

            if text == keyboard_wait[1]:
                keyboard = build_keyboard(keyboard_wait)
                send_message("Great! Time to chill!", chat,keyboard)

            if text == '/start':
                keyboard = build_keyboard(keyboard_wait)
                send_message("Hi! I'm a Bot designed to help you control your working or studying hours. Keep track of the time you spend in the office by sending me In! or Out!", chat,keyboard)

        except Exception as e:
            if text != '':
                keyboard = build_keyboard(keyboard_wait)
                send_message("Ups! I did not understand", chat,keyboard)
            print(e)
            print(text)
        try:
            setMessageDB(id, date, chat, username, text)

        except Exception as e:
            print(e)

def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def main():
    last_update_id = None
    pwd = os.getcwd()

    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
