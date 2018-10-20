import json
import requests
import time
import urllib
import os
import random
import mysql.connector

SESSION_ID = random.randint(0,1000000)
TOKEN = os.getenv('BOT_TOKEN',"")
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
keyboard_wait = ["Starting now!","Out!","My data!"]

def getDB(query):
    cnx = mysql.connector.connect(user='root', database='workcouBot', passwd='', host='localhost')
    cursor = cnx.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    names = cursor.column_names
    cursor.close()
    cnx.close()
    return names,data

def setMessageDB(id, date, chat, username, text):
    cnx = mysql.connector.connect(user='root', database='workcouBot', passwd='', host='localhost')
    cursor = cnx.cursor()
    sql = "INSERT INTO messagesLog (id, creation_epoch, chat_id, username, message_text) VALUES (%s, %s, %s, %s, %s)"
    val = (id, date, chat, username, text)
    cursor.execute(sql, val)
    cnx.commit()
    print(cursor.rowcount, "record inserted by {}.".format(username))
    cursor.close()
    cnx.close()

def sendLogDB(date, update):
    cnx = mysql.connector.connect(user='root', database='workcouBot', passwd='', host='localhost')
    cursor = cnx.cursor()
    sql = "INSERT INTO logs (creation_epoch, log_text) VALUES (%s, %s)"
    val = (date, update)
    cursor.execute(sql, val)
    cnx.commit()
    print("log inserted")
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

def send_document(chat_id, path, reply_markup=None):
    path = urllib.parse.quote_plus(path)
    url = URL + "sendDocument?chat_id={}&document={}".format(chat_id, path)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def send_messageHTML(text, chat_id, reply_markup=None):
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=html".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def handle_updates(updates):
    for update in updates["result"]:
        try:
            sendLogDB(time.time(), json.dumps(update))
        except Exception as e:
            print(e)

        try:
            id = update["message"]["message_id"]
            text = update["message"]["text"]
            chat_id = update["message"]["chat"]["id"]
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
            if text == '/start':
                keyboard = build_keyboard(keyboard_wait)
                send_message("Hi! I'm a Bot designed to help you control your working or studying hours. Keep track of the time you spend in the office by sending me Begin or Finish", chat_id,keyboard)

            if text == keyboard_wait[0]:
                keyboard = build_keyboard(keyboard_wait)
                send_message("Good morning {}! Go get them!".format(username), chat_id,keyboard)

            if text == keyboard_wait[1]:
                keyboard = build_keyboard(keyboard_wait)
                send_message("Great! Time to chill!", chat_id,keyboard)

            if text == keyboard_wait[2]:
                keyboard = build_keyboard(keyboard_wait)
                send_message("Let's see what we have here!", chat_id,keyboard)
                query = ("SELECT FROM_UNIXTIME(creation_epoch) as creation_datetime,message_text FROM workcouBot.messagesLog WHERE chat_id = {}".format(chat_id))
                columns, data = getDB(query)
                send_document(chat_id,"http://www.mercasa.es/files/multimedios/1470593606_Cincuenta_anos_de_alimentacion_en_Espana.pdf")

        except Exception as e:
            if text != '':
                keyboard = build_keyboard(keyboard_wait)
                send_message("Ups! I did not understand", chat_id,keyboard)
            print(e)
            print(text)

        try:
            setMessageDB(id, date, chat_id, username, text)

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
