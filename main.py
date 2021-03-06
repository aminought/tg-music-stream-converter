import logging
import os
import re

import requests
from bs4 import BeautifulSoup
from dotenv import find_dotenv, load_dotenv
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi. I\'m waiting for your links.')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Just send me a link to Yandex Music or Google Play Music song.')


def yandex_to_google(yandex_link):
    r = requests.get(yandex_link)
    soup = BeautifulSoup(r.text, 'html.parser')
    html_title = soup.find('title').text
    pattern = r'^(.*) — (.*)\. Слушать онлайн на Яндекс.Музыке$'
    title, artist = re.findall(pattern, html_title)[0]
    title_encoded = title.replace(' ', '+')
    artist_encoded = artist.replace(' ', '+')
    url = f'https://play.google.com/music/listen#/sr/{title_encoded}+{artist_encoded}'
    return url


def google_to_yandex(google_link):
    title, artist = google_link.split('?t=')[1].replace('_', ' ').split(' - ')
    url = f'https://music.yandex.ru/search?text={title} {artist}'.replace(' ', '%20')
    return url


def convert(bot, update):
    try:
        link = update.message.text
        logger.info(link)
        if 'music.yandex.ru' in link:
            reply = yandex_to_google(link)
        elif 'play.google.com/music' in link:
            reply = google_to_yandex(link)
        else:
            reply = 'Unknown link.'

        update.message.reply_text(reply)
    except Exception as e:
        logger.exception(e)
        update.message.reply_text('Unknown error.')
    

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    REQUEST_KWARGS = {
        'proxy_url': os.environ.get('PROXY_URL')
    }

    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(os.environ.get('TG_TOKEN'),
                      request_kwargs=REQUEST_KWARGS)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(MessageHandler(Filters.text, convert))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    main()
