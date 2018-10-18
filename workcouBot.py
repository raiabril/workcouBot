import json
import requests
import time
import urllib
import os
import random
import yaml
import mysql.connector

SESSION_ID = random.randint(0,1000000)
TOKEN = os.getenv('BOT_TOKEN',"784190639:AAEFGEHszyKPRhgNUD4vzs9FeqjvHxx1n2U")
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
keyboard_wait = ["Entro","Salgo"]

def getDB(query):
    cnx = mysql.connector.connect(user='root', database='workcouBot', passwd='J4v5f7o3', host='localhost')
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
            first_name = update["message"]["from"]["first_name"]
            last_name = update["message"]["from"]["last_name"]
            username = update["message"]["from"]["username"]
            is_bot = update["message"]["from"]["is_bot"]
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            date = update["message"]["date"]

        except Exception as e:
            print(e)
        try:
            if text == 'Entro':
                keyboard = build_keyboard(keyboard_wait)
                send_message("Recibido {}! A por ellos!".format(username), chat,keyboard)
            if text == 'Salgo':
                keyboard = build_keyboard(keyboard_wait)
                send_message("Recibido {}! A descansar!".format(username), chat,keyboard)
        except Exception as e:
            print(e)
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
