import telebot
import re
import subprocess
import sys
from telebot import apihelper
import time, timelib
from datetime import datetime
import sqlite3

def replace_all(t, d):
    """Общая функция для подмены переменных"""
    for i, j in d.items():
        t = t.replace(i, j, 1)
    return t

def get_datex(text):
    """Извлекает из текста дату и подстроку с датой, которую нужно удалить"""
    whatdate = ''
    delwhatdate = ''
    datex = re.findall(r'\d{2}[.,-]\d{2}[.,-]\d{4}|\d{1}[.,-]\d{2}[.,-]\d{4}',text) # ищем дату в формате 19.08.2014 или 19-08-2014 или 19,08,2014
    if datex:
        date = datex[0].replace('-','.').replace(',','.') # преобразуем дату в формат 19.08.2014
        whatdate = date
        delwhatdate = datex[0]+' '
    return whatdate, delwhatdate

def get_day(text):
    """Извлекает из текста день недели и подстроку, которую нужно удалить"""
    when = ''
    delday = ''

    day = re.findall('завтра|Завтра|в понедельник|во вторник|в среду|в четверг|в пятницу|в субботу|в воскресенье',text)
    daywithoutin = re.findall('понедельник|вторник|среда|четверг|пятница|суббота|воскресенье',text)
    if day:
        ind = {'завтра':'tomorrow', 'Завтра':'tomorrow', 'в понедельник':'mon', 'во вторник':'tue', 'в среду':'wed', 'в четверг':'thu', 'в пятницу':'fri', 'в субботу':'sat', 'в воскресенье':'sun'}
        when = replace_all(day[0], ind)
        delday = day[0]+' '
    elif daywithoutin:
        ind = {'понедельник':'mon', 'вторник':'tue', 'среда':'wed', 'четверг':'thu', 'пятница':'fri', 'суббота':'sat', 'воскресенье':'sun'}
        when = replace_all(daywithoutin[0], ind)
        delday = daywithoutin[0]+' '
    return (when, delday)

def get_clock(text):
    """Извлекает из текста время и подстроку, которую нужно удалить"""
    how = ''
    delclock = ''
    clock = re.findall('минуты |часа |дня |минуту |часов |день |минут |час |дней ',text)
    if clock: # смотрим, есть ли указание на часы, минуты, дни
        clockbank = {'минут ':'min', 'час ':'hour', 'дней ':'days', 'минуту ':'min', 'часа ':'hours', 'дня ':'days', 'минуты ':'min', 'часов ':'hours', 'день ':'days'}
        how = replace_all(clock[0], clockbank)
        delclock = clock[0]
    return (how, delclock)

def add_task(out, x, chat):
    #print (x)
    with sqlite3.connect("reminders.db") as con:
        cursor = con.cursor()
        if 'now' in x:
            cursor.execute("INSERT INTO tasks VALUES (?, ?, ?)", (out, timelib.strtotime(x.encode('utf-8')), chat))
        else:
            cursor.execute("INSERT INTO tasks VALUES (?, ?, ?)", (out, timelib.strtotime(x.encode('utf-8'))-10800, chat))
        con.commit()
    
def checkTasks (chat):
    deleteOldReminders()
    with sqlite3.connect("reminders.db") as con:
        cursor = con.cursor()
        data = ""
        for row in cursor.execute("SELECT * FROM tasks WHERE id="+str(chat)):
            data += "\n" + row[0] + "в " + datetime.fromtimestamp(row [1]).strftime('%Y-%m-%d %H:%M:%S')
        if data:
            return data
        else:
            return "ничего"

def deleteOldReminders():
     with sqlite3.connect("reminders.db") as con:
        cursor = con.cursor()
        cursor.execute("DELETE FROM tasks WHERE date<"+str(time.time()))


#apihelper.proxy = {'https':'socks5h://45.55.106.89:80'}
conn = sqlite3.connect("reminders.db")


bot = telebot.TeleBot('625199341:AAGuM7KLOKHGUHKv1Xo0-htS8pDu0IUedic')

@bot.message_handler(comands=['start'])
def start_message(message):
		bot.send_message(message.chat.id, 'Приветствую')
@bot.message_handler(content_types=['text'])
def send_text(message):
        if message.text.lower() == 'привет': 
            bot.send_message(message.chat.id, 'Привет, мой господин') 
        elif message.text.lower() == 'пока': 
            bot.send_message(message.chat.id, 'Прощай, господин')
        elif message.text.lower() == 'че напомнишь?':
            bot.send_message(message.chat.id, checkTasks(message.chat.id))	
        elif 'ты сука' in message.text.lower(): 
                bot.send_photo(message.chat.id, open('mem.jpg', 'rb') )
        elif 'напомни' in message.text.lower():
                get = message.text # получаем текст
                text = get+' ' # добавляем в конец пробел, чтобы отрабатывать уведомления типа "напомнить мне через 10 минут". Если бы пробела не было, параметр clock был бы пуст. В параметре clock после слова "час" тоже стоит пробел, чтобы различать поиск "час" и "часов".
                find = re.findall('ерез [0-9]+|В [0-9:-]+|в [0-9:-]+|ерез час',text)
                if get: # убеждаемся, заполнено ли поле ввода
                        if find: # убеждаемся, указано ли время напоминания
                                what = find[0].split()
                                timex = what[1].replace('-',':').replace('час','1')
								
                                if len(timex) > 2: # заменяет выражения типа "в 10" на "в 10:00"
                                        time = timex
                                else:
                                        time = timex+':00'	
                
                                whatdate, delwhatdate = get_datex(text)
                                when, delday = get_day(text)
                                how, delclock = get_clock(text)

                                reps = {'ерез':'now + %s %s' % (timex,how),'В':'%s %s %s' % (when, time,whatdate),'в':'%s %s %s' % (when, time, whatdate)}
                                wors = {'Через %s %s' % (what[1],delclock):'','через %s %s' % (what[1],delclock):'','В %s ' % what[1]:'','в %s ' % what[1]:'', '%s' % delday:'', 'Через час':'', 'через час':'', '%s' % delwhatdate:'',} # какие слова мы будем удалять
                                x = replace_all(what[0], reps) # это время, на которое запланировано появление напоминания
                                out = replace_all(text, wors) # это текст напоминания
                                try:
                                    add_task(out, x, message.chat.id)
                                    bot.send_message(message.chat.id, "Окей")
                                except:
                                    bot.send_message(message.chat.id,"Не получилось")
                        else:
                            bot.send_message(message.chat.id,"Время указано как-то не так")
                else:
                    bot.send_message(message.chat.id,"Что-то не то")
        else:
            bot.send_message(message.chat.id,"Не знаю, что на это ответить")


bot.polling()

