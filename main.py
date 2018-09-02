import logging
import os

from dotenv import find_dotenv, load_dotenv
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
import requests
from bs4 import BeautifulSoup
import re

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Just send a link to Yandex Music song.')


def convert(bot, update):
    link = update.message.text
    r = requests.get(link)
    soup = BeautifulSoup(r.text, 'html.parser')
    html_title = soup.find('title').text
    pattern = r'^(.*) — (.*)\. Слушать онлайн на Яндекс.Музыке$'
    title, artist = re.findall(pattern, html_title)[0]
    title_encoded = title.replace(' ', '+')
    artist_encoded = artist.replace(' ', '+')
    url = f'https://play.google.com/music/listen#/sr/{title_encoded}+{artist_encoded}'
    update.message.reply_text(url)


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
