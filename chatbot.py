from telegram import Update
from telegram.ext import (Updater, MessageHandler, Filters, CommandHandler, CallbackContext)
from ChatGPT_HKBU import HKBU_ChatGPT
import configparser
import logging
import redis

def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=config['TELEGRAM']['ACCESS_TOKEN'], use_context=True)
    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(host = (config['REDIS']['HOST']),
                password = (config['REDIS']['PASSWORD']),
                port = (config['REDIS']['REDISPORT']),
                decode_responses = (config['REDIS']['DECODE_RESPONSE']),
                username = (config['REDIS']['USER_NAME']))
    
    # Dispatcher for ChatGPT
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)
    
    # You can set this logging module, 
    # so you will know when (and why) things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # Register a dispatcher to handle commands
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))  # Added hello command handler
    
    # To start the bot:
    updater.start_polling()
    updater.idle()

def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said '+ msg +' for '+ redis1.get(msg) +' times.')
    
    except(IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def hello(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /hello <name> is issued."""
    try:
        name = context.args[0]
        update.message.reply_text(f'Good day, {name}!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <name>')

if __name__ == '__main__':
    main()
