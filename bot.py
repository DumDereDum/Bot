import telebot

bot = telebot.TeleBot('625199341:AAGuM7KLOKHGUHKv1Xo0-htS8pDu0IUedic')

@bot.message_handler(comands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Приветствую')	

bot.polling()
