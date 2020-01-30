import configparser
import re
import requests
from telegram import bot
from telegram.ext import Updater, CommandHandler


def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url


def bop(bot, update):
    url = get_url()
    chat_id = update.message.chat_id
    print (chat_id)
    bot.send_photo(chat_id=chat_id, photo=url)


def sendtext(bot_message):
    config = configparser.ConfigParser()
    config.read("cfg/settings.ini")
    bot_token = config["INTEGRATION"]['telegramToken']
    bot_chatID = config["INTEGRATION"]['telegramChatID']
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()


def sendImage(file_location):
    config = configparser.ConfigParser()
    config.read("cfg/settings.ini")
    bot_token = config["INTEGRATION"]['telegramToken']
    bot_chatID = config["INTEGRATION"]['telegramChatID']
    bot.send_photo(bot_chatID, 'https://random.dog/woof.json')
    return response.json()


def main():
    config = configparser.ConfigParser()
    config.read("cfg/settings.ini")
    updater = Updater(config["INTEGRATION"]['telegramToken'])

    sendImage("this is a testsendtext")

    dp = updater.dispatcher
    t
    dp.add_handler(CommandHandler('bop', bop))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
