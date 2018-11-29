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
# This is a comment

start_1 = "08:30"
start_2 = "09:00"
start_3 = "08:00"
start_4 = "07:00"
start_5 = "08:00"
finish_1 = "18:00"
finish_2 = "18:00"
finish_3 = "18:00"
finish_4 = "15:00"
finish_5 = "15:00"
break_start_1 = "13:30"
break_start_2 = "14:00"
break_start_3 = "13:00"
break_finish_1 = "14:30"
break_finish_2 = "15:00"
break_finish_3 = "14:00"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

def insertLog(update):
    cnx = mysql.connector.connect(user='root', database='workcouBot', passwd='', host='localhost')
    cursor = cnx.cursor()
    sql = "INSERT INTO logs (creation_datetime, log_text) VALUES (%s, %s)"
    val = (str(datetime.now()), update)
    cursor.execute(sql, val)
    cnx.commit()
    print("{} - Log inserted".format(str(datetime.now())))
    cursor.close()
    cnx.close()

def insertMessage(update_id, update_date, chat_id, username, text):
    cnx = mysql.connector.connect(user='root', database='workcouBot', passwd='', host='localhost')
    cursor = cnx.cursor()
    sql = "INSERT INTO messagesLog (id, creation_datetime, chat_id, username, message_text) VALUES (%s, %s, %s, %s, %s)"
    val = (update_id, update_date, chat_id, username, text)
    cursor.execute(sql, val)
    cnx.commit()
    print("{} - Record inserted by {}: {}".format(update_date, chat_id, text))
    cursor.close()
    cnx.close()

def insertMode(update_id, chat_id, schedule_mode, start_time, stop_time, break_start_time, break_stop_time, update_date):
    cnx = mysql.connector.connect(user='root', database='workcouBot', passwd='J4v5f7o3', host='localhost')
    cursor = cnx.cursor()
    sql = "INSERT INTO userInfo (id, chat_id, schedule_mode, start_time, stop_time, break_start_time, break_stop_time, setup_datetime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (update_id, chat_id, schedule_mode, start_time, stop_time, break_start_time, break_stop_time, update_date)
    cursor.execute(sql, val)
    cnx.commit()
    print("{} - Setup inserted by {}".format(update_date, chat_id))
    cursor.close()
    cnx.close()

def runQuery(query):
    cnx = mysql.connector.connect(user='root', database='workcouBot', passwd='', host='localhost')
    cursor = cnx.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    names = cursor.column_names
    cursor.close()
    cnx.close()
    return names,data


def prepareCSV(chat_id,username):
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
    bot.send_message(chat_id=update.message.chat_id, text="Would you mind sharing your location and contact with me?", reply_markup=reply_markup)

def send_image(bot, chat_id, path):
    bot.send_photo(chat_id=chat_id, photo=open(path, 'rb'))

def send_file(bot, chat_id, path):
    bot.send_document(chat_id=chat_id, document=open(path, 'rb'))

custom_keyboard = [["Start","Stop", "My data!"]]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

begin_keyboard = [["/setup", "Exit"]]
begin_markup = telegram.ReplyKeyboardMarkup(begin_keyboard)

setup_keyboard = [["Mode 1","Mode 2", "Mode 3", "Mode 4", "Mode 5", "Exit"]]
setup_markup = telegram.ReplyKeyboardMarkup(setup_keyboard)

# ==========
def start(bot, update):
    insertLog(str(update))
    bot.send_message(chat_id=update.message.chat_id, text="Hi! I'm a Bot designed to help you control your working or studying hours. Keep track of the time you spend in the office by sending me Begin or Finish. You can download your data whenever you want by sending My data!. For more info /help. You can also configure your calendar with /setup. Thanks!!", reply_markup=begin_markup)

def help(bot, update):
    insertLog(str(update))
    bot.send_message(chat_id=update.message.chat_id,
    text="This bot does not analyze or share your personal data.", reply_markup=reply_markup)

def setup_user(bot, update):
    insertLog(str(update))
    try:
        column, data = runQuery("SELECT schedule_mode FROM workcouBot.userInfo where chat_id = {} order by id DESC limit 1;".format(update.message.chat_id))
        current_mode = data[0][0]
    except:
        print("No mode")
        current_mode = 1
        insertMode(update.message.message_id, update.message.chat_id, 1, start_1, finish_1, break_start_1, break_finish_1, update.message.date)
        
    
    bot.send_message(chat_id=update.message.chat_id,
    text="This is your current work schedule: Mode {}".format(current_mode), reply_markup=setup_markup)
    bot.send_message(chat_id=update.message.chat_id, 
    text="Available modes:")
    bot.send_message(chat_id=update.message.chat_id,
    text="Mode 1: {}-{} and {}-{}".format(start_1,break_start_1,break_finish_1,finish_1))
    bot.send_message(chat_id=update.message.chat_id,
    text="Mode 2: {}-{} and {}-{}".format(start_2,break_start_2,break_finish_2,finish_2))
    bot.send_message(chat_id=update.message.chat_id,
    text="Mode 3: {}-{} and {}-{}".format(start_3,break_start_3,break_finish_2,finish_3))
    bot.send_message(chat_id=update.message.chat_id,
    text="Mode 4: {}-{}".format(start_4,finish_4))
    bot.send_message(chat_id=update.message.chat_id,
    text="Mode 5: {}-{}".format(start_5,finish_5))


def unknown(bot, update):
    insertLog(str(update))
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.", reply_markup=reply_markup)

def error(bot, update, error):
    insertLog(str(update))
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def message_handler(bot, update):
    insertLog(str(update))

    update_id = update.message.message_id
    chat_id = update.message.chat_id
    text = update.message.text
    update_date = update.message.date
    #last_name = update.message.from_user.last_name
    #first_name = update.message.from_user.first_name
    username= update.message.from_user.username
    insertMessage(update_id, update_date, chat_id, username, text)

    if text == "Start":
        bot.send_message(chat_id=update.message.chat_id, text="Received {}! Go get them!".format(username), parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)

    elif text == "Stop":
        bot.send_message(chat_id=update.message.chat_id, text="Awesome! Time to chill!", parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)

    elif text == "My data!":
        bot.send_message(chat_id=update.message.chat_id, text="<b>Stats for {}</b>".format(chat_id), parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)
        
        column_names, data = prepareCSV(chat_id,username)
        send_file(bot, chat_id=update.message.chat_id, path="{}.csv".format(chat_id))

    elif text == "Exit":
        bot.send_message(chat_id=update.message.chat_id, text="Ok, you can setup your workschedule when you want", parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)

    elif text == "Mode 1":
        bot.send_message(chat_id=update.message.chat_id, text="Correctly saved your settings", parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)
        insertMode(update_id, chat_id, 1, start_1, finish_1, break_start_1, break_finish_1, update_date)

    elif text == "Mode 2":
        bot.send_message(chat_id=update.message.chat_id, text="Correctly saved your settings", parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)
        insertMode(update_id, chat_id, 2, start_2, finish_2, break_start_2, break_finish_2, update_date)

    elif text == "Mode 3":
        bot.send_message(chat_id=update.message.chat_id, text="Correctly saved your settings", parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)
        insertMode(update_id, chat_id, 3, start_3, finish_3, break_start_3, break_finish_3, update_date)

    elif text == "Mode 4":
        bot.send_message(chat_id=update.message.chat_id, text="Correctly saved your settings", parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)
        insertMode(update_id, chat_id, 4, start_4, finish_4, "NULL", "NULL", update_date)

    elif text == "Mode 5":
        bot.send_message(chat_id=update.message.chat_id, text="Correctly saved your settings", parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)
        insertMode(update_id, chat_id, 5, start_1, finish_1, "NULL", "NULL", update_date)

    else:
        bot.send_message(chat_id=update.message.chat_id, text="Ups! I didn't get that!", parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)

        #bot.send_message(chat_id=update.message.chat_id, text="There it goes!", parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)

    #bot.send_message(chat_id=update.message.chat_id, text=update.message.text, parse_mode=telegram.ParseMode.HTML)
    #bot.send_message(chat_id=update.message.chat_id, text="<b>Texto</b>", parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)
    #send_file(bot, chat_id=update.message.chat_id, path="/Users/raimundoabrillopez/Documents/aleman.txt")

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("setup", setup_user))
    dp.add_handler(MessageHandler(Filters.command, unknown))
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
