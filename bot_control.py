from telegram import Update, ForceReply, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.utils import helpers
import time
# my libs
from lib import bot, last_update


def start(update: Update, _: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(f"Привет, {user.mention_markdown_v2()}\. "
                                     f"Чтобы подписаться на рассылку цен, напиши /connect\.")


def echo(update: Update, _: CallbackContext) -> None:
    """Reply to any user message."""
    update.message.reply_text(f'Напиши /connect, чтобы подписаться на рассылку цен.\n'
                              f'Напиши /when, чтобы узнать время последнего сканирования.')


def connect(update: Update, _: CallbackContext) -> None:
    # notifications.add_new_telegram_user(update.message.from_user.id)  TODO: переписать
    update.message.reply_text(f'Вы подписались на обновления.')


def when(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(f"Последнее сканирование {int((time.time() - last_update) // 60)} мин. назад.")


def send_message(user_id, message, bot=bot):
    return True if bot.send_message(chat_id=user_id,
                                    text=message,
                                    parse_mode='html',
                                    disable_web_page_preview=True) else False


def run():
    updater = Updater(use_context=True, bot=bot)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("connect", connect))
    dispatcher.add_handler(CommandHandler("when", when))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling()


if __name__ == '__main__':
    run()
