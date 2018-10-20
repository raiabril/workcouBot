import json
import requests
import time
from datetime import datetime
import urllib
import os
import random
import mysql.connector
import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

def insertLog(date, update):
    cnx = mysql.connector.connect(user='root', database='workcouBot', passwd='J4v5f7o3', host='localhost')
    cursor = cnx.cursor()
    sql = "INSERT INTO logs (creation_epoch, log_text) VALUES (%s, %s)"
    val = (date, update)
    cursor.execute(sql, val)
    cnx.commit()
    print("{} - Log inserted".format(str(datetime.now())))
    cursor.close()
    cnx.close()

def insertMessage(id, date, chat_id, username, text):
    cnx = mysql.connector.connect(user='root', database='workcouBot', passwd='J4v5f7o3', host='localhost')
    cursor = cnx.cursor()
    sql = "INSERT INTO messagesLog (id, creation_datetime, chat_id, username, message_text) VALUES (%s, %s, %s, %s, %s)"
    val = (id, date, chat_id, username, text)
    cursor.execute(sql, val)
    cnx.commit()
    print("{} - Record inserted by {}: {}".format(date, username, text))
    cursor.close()
    cnx.close()

def runQuery(query):
    cnx = mysql.connector.connect(user='root', database='workcouBot', passwd='J4v5f7o3', host='localhost')
    cursor = cnx.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    names = cursor.column_names
    cursor.close()
    cnx.close()
    return names,data


def prepareCSV(chat_id):
    column_names, data = runQuery(query = ("SELECT creation_datetime,message_text FROM workcouBot.messagesLog WHERE chat_id = {}".format(chat_id)))
    with open("{}.csv".format(chat_id), "w") as myfile:
        myfile.write("{},{}\n".format("Date", "Message"))
        for row in data:
            myfile.write("{},{}\n".format(row[0], row[1]))
    print("{} - Document prepared {}.csv".format(str(datetime.now()),chat_id))
    return column_names, data

def askQuestion(bot, update):
    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                 InlineKeyboardButton("Option 2", callback_data='2')],
                [InlineKeyboardButton("Option 3", callback_data='3')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=update.message.chat_id, text="What option??", reply_markup=reply_markup)

def request_location(bot,update):
    location_keyboard = telegram.KeyboardButton(text="send_location", request_location=True)
    contact_keyboard = telegram.KeyboardButton(text="send_contact", request_contact=True)
    custom_keyboard = [[ location_keyboard, contact_keyboard ]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text="Would you mind sharing your location and contact with me?", reply_markup=reply_markup)

def send_image(bot, chat_id, path):
    bot.send_photo(chat_id=chat_id, photo=open(path, 'rb'))

def send_file(bot, chat_id, path):
    bot.send_document(chat_id=chat_id, document=open(path, 'rb'))

custom_keyboard = [["Begin","Finish", "My data!"]]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

# ==========
def start(bot, update):
    insertLog(time.time(), str(update))
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

def help(bot, update):
    insertLog(time.time(), str(update))
    bot.send_message(chat_id=update.message.chat_id, text="this is help!")

def unknown(bot, update):
    insertLog(time.time(), str(update))
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

def error(bot, update, error):
    insertLog(time.time(), str(update))
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def message_handler(bot, update):
    insertLog(time.time(), str(update))

    id = update.message.message_id
    chat_id = update.message.chat_id
    text = update.message.text
    date = update.message.date
    last_name = update.message.from_user.last_name
    last_name = update.message.from_user.first_name
    username= update.message.from_user.username

    insertMessage(id, date, chat_id, username, text)

    if text == "Begin":
        bot.send_message(chat_id=update.message.chat_id, text="Received {}! Go get them!".format(username), parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)

    if text == "Finish":
        bot.send_message(chat_id=update.message.chat_id, text="Awesome! Time to chill!", parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)

    if text == "My data!":
        bot.send_message(chat_id=update.message.chat_id, text="<b>Stats for {}</b>".format(username), parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)
        column_names, data = prepareCSV(chat_id)
        send_file(bot, chat_id=update.message.chat_id, path="{}.csv".format(chat_id))
        #bot.send_message(chat_id=update.message.chat_id, text="There it goes!", parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)

    #bot.send_message(chat_id=update.message.chat_id, text=update.message.text, parse_mode=telegram.ParseMode.HTML)
    #bot.send_message(chat_id=update.message.chat_id, text="<b>Texto</b>", parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)
    #send_file(bot, chat_id=update.message.chat_id, path="/Users/raimundoabrillopez/Documents/aleman.txt")

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("784190639:AAHJPD_XK9iLKFq-idZ6zT5Xacp19anVbJI")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("help", unknown))
    dp.add_handler(MessageHandler(Filters.text, message_handler))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()