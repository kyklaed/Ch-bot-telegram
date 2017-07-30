# -*- coding: utf-8 -*-

import config
import telebot
import datetime
import dbconnect
import time


bot = telebot.TeleBot(config.token)

new = {} #стейт для добавление новости
admin_cnf ={} #стейт для получения новости
blockuser={} #стейт для черного списка

usertext={} #списко для храения текста
userphoto={} #список для хранения ссылок на фото
usertext_str= {} #для хранения текста из списка как строки
userphoto_str= {} #для хранения текста из списка как строки
content_u = {} #хранится контент из бд для выдачи

chk_black_list={} #тут хранится айди юзера из бд для проверки на состоит ли в черном списке

start_n= {}  # стейт для работы с функциями перемещения между записями и постинга

chat_id=[]



""" 
Бот для каналов телеграма, юзеры могут отправлять через бота новости итд
"""

"""
Основной функционал для юзера , кнопка начать, послее нажатия юзер должен ввести текст и/или прикрепить фото 
после того как он все ввел он должен нажать кнопку закончить. Что приведет к сохранению в БД
"""

@bot.message_handler(commands=["start", "help"])
def start(message):
    # print("start")
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    btn1 = telebot.types.InlineKeyboardButton(text="начать")
    btn2 = telebot.types.InlineKeyboardButton(text="закончить")
    keyboard.add(btn1,btn2)
    bot.send_message(message.from_user.id,
"""Здравстуйте! Чтобы предложить новость на канал @chenal нажмите на кнопку "НАЧАТЬ", после этого введите текст Вашего сообщения и прикрепите фотографии. Затем нажмите кнопку "ЗАКОНЧИТЬ". Обратите внимание, что каждая новая новость должна начинаться с нажатия кнопки "НАЧАТЬ", если Вы хотите предложить несколько новостей, то каждая новость это отдельный пост.""",reply_markup=keyboard)

"""
Фнкция проверки по черному списку
при каждом запросе к фнкциям юзера. проверяет id юзера из ТГ по бд 
"""
def check_black_list(message):
    dbase = dbconnect.Check_blacklist('chnews', 'blockuser')
    dbase.addtable()
    chk_black_list[message.chat.id] = dbase.chk_list(message.chat.id)
    if chk_black_list[message.chat.id] == []:
        chk_black_list[message.chat.id] = [(0,)]

"""
Тут объявляются необходимые переменные для дальнейшей записи в них полученной от юзера информации
и проверка по черному списку
"""
@bot.message_handler(func=lambda message: message.text in ['начать'])
def start_new(message):
    print("начать")
    check_black_list(message)
    if message.chat.id not in chk_black_list[message.chat.id][0]:
        bot.send_message(message.from_user.id,"Введите текст новости и прикрепите фотографии. По окончанию нажмите кнопку 'закончить'.")
        usertext[message.chat.id]=[]
        userphoto[message.chat.id]=[]
        usertext_str[message.chat.id] = None
        userphoto_str[message.chat.id] = None
        new[message.chat.id] = 0
        chk_black_list[message.chat.id] = None
    else:
        bot.send_message(message.from_user.id, "Вы заблокированы")
        chk_black_list[message.chat.id] = None


"""
Функция непосредственного сохранения переданной информации от юзера, длинна текста ограниченна 1000 символов, 
если юзер ввле два текстовых сообщения то они сохраняются через запятую, тут вероятно есть дырка связанная с размером сообщений
БД держит 1000 символов на поле а пользователь за одну сессию может попытаться несколькими сообщениями записать больше символов, что вызовет падение!!

После каждой сессии все поля обруляются.
"""


@bot.message_handler(func=lambda message: message.chat.id in new.keys() and message.text not in ['начать','админ',
                                                                                                 'загрузить','следующий',
                                                                                                 'в_черный_список',
                                                                                                 'состояние','1','0','ИНФО_отпр',
                                                                                                 'ВКЛ_уведомления']
                                                                                        and True,content_types=['photo','text'])
def save_news(message):
    print("save news")
    print(new[message.chat.id])
    if new[message.chat.id] == 0 and message.text not in ['начать','админ','активация','в_черный_список','состояние','1','0']:
        print("v cikle!")
        if message.text != None and message.photo == None and message.text not in ['закончить']:
            # print('pole = text')
            if len(message.text) <= 1000:
                usertext[message.chat.id].append(message.text)
            else:
                bot.send_message(message.from_user.id, "Вы отправили слишком длинный текст")
            print("______________________________________________________")
            print(usertext[message.chat.id])
            print("______________________________________________________")
        elif message.text == None and message.photo != None and message.text not in ['закончить']:
            print('pole = photo')
            if len(message.photo) <= 1000:
                userphoto[message.chat.id].append(message.photo[len(message.photo)-1].file_id)
            else:
                bot.send_message(message.from_user.id, "Вы отправили слишком много фотографий")
            print("______________________________________________________")
            print(userphoto[message.chat.id])
            print("______________________________________________________")
        elif new[message.chat.id] == 0 and message.text in ['закончить']:
            print('pole = stop')
            if usertext[message.chat.id] == [] and userphoto[message.chat.id] == []:
                bot.send_message(message.from_user.id, "Вы ничего не отправили")
                new[message.chat.id] = 1
                usertext[message.chat.id].clear()
                userphoto[message.chat.id].clear()
                usertext_str[message.chat.id] = None
                userphoto_str[message.chat.id] = None

            else:
                usertext_str[message.chat.id] = ','.join(usertext[message.chat.id])
                userphoto_str[message.chat.id] =','.join(userphoto[message.chat.id])
                new[message.chat.id] = 1
                dbase = dbconnect.Add_new_news('chnews', 'newnews')
                dbase.addtable()
                date_u=datetime.date.today()
                dbase.add_news(message.chat.id,message.chat.username,usertext_str[message.chat.id],userphoto_str[message.chat.id],date_u)
                if chat_id !=[]: #and message.chat.id in [int('id_admin'),int('id_admin')]:
                    for idd in chat_id:
                        bot.send_message(idd, 'Новая запись в БД')
                usertext[message.chat.id].clear()
                userphoto[message.chat.id].clear()
                usertext_str[message.chat.id] = None
                userphoto_str[message.chat.id] = None
                bot.send_message(message.from_user.id, "Спасибо! Ваша новость отправлена на премодерацию.")


"""
Админка.

Что бы вызвать админ панель необходимо напечатать в чат "админ"

Кнопка  "загрузить" - загружает посты из БД для работы просомтра и работы с ними 
        "выход" - обнуляет все переменные задейтсвованные для админских функций
        "состояние" - показывает пост с который сейчас считается активным для вас
        "в_черный_список" - вызывает функцию добавления в ЧС
        "1" - отправляет выбранный пост в канал и помечает как обработанный
        "0" - не отправлет пост, а просто помечает как обработанный 
        "ИНФО_отпр" - отправляет информационное сообщение в канал
        "следующий" - показывет следущее сообщение из БД, зацикленно. то есть пока есть посты они будут показываться по кругу
"""
@bot.message_handler(func=lambda message: message.chat.id in [int('25725314'),int('65012501')] and message.text in ["админ"])
def admin(message):
    print("админ панель")
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    btn1 = telebot.types.InlineKeyboardButton(text="загрузить")
    btn2 = telebot.types.InlineKeyboardButton(text="выход")
    btn3 = telebot.types.InlineKeyboardButton(text="состояние")
    btn4 = telebot.types.InlineKeyboardButton(text="в_черный_список")
    btn5 = telebot.types.InlineKeyboardButton(text="1")
    btn6 = telebot.types.InlineKeyboardButton(text="0")
    btn7 = telebot.types.InlineKeyboardButton(text="ИНФО_отпр")
    btn8 = telebot.types.InlineKeyboardButton(text="следующий")
    btn9 = telebot.types.InlineKeyboardButton(text='ВКЛ_уведомления')
    keyboard.add(btn1, btn2,btn3)
    keyboard.add(btn4, btn5, btn6)
    keyboard.add(btn7,btn8,btn9)

    bot.send_message(message.from_user.id,"Привет админ",reply_markup=keyboard)


"""
Основная фнкция которая получает посты с фото и без из БД
1. подключение с БД
2. берем актуальную дату
3.по дате смотрим в БД и выбираем посты за сегодня
4. если посты есть, то вызываем generator_post()
5.если постов нет то , меняет стейт на не активный и работа заканчивается
"""
@bot.message_handler(func=lambda message: message.chat.id in [int('25725314'),int('65012501')] and message.text in ['загрузить'])
def reload_post(message):
    start_n[message.chat.id] = 0
    print("start pos = ",start_n[message.chat.id])
    dbase = dbconnect.Add_new_news('chnews', 'newnews')
    date_u = datetime.date.today()
    content_u[message.chat.id] = dbase.select_news(date_u)
    print("content = ",content_u[message.chat.id])
    if content_u[message.chat.id] != []:
        admin_cnf[message.chat.id] = 0
        generator_post(message)
        print("Новые записи найдены!")
    else:
        admin_cnf[message.chat.id] = 1
        print("Новых записей нет!")
        bot.send_message(message.from_user.id, "Новостей больше нет")


"""
получнный данных из reload_post обрабатываются тут!

1. проверяется не пустой ли список
2. проверить нужна ли эта строка start_n[message.chat.id] != len(content_u[message.chat.id])
3. данные отправляются в чат для админа
4.проверяется есть ли фото и если есть то отправляютя в след
5. если список с данными полученными из админки пуст то вызываем функцию закгрузки данных и пробуем загрузить еще из БД
"""
def generator_post(message):
    if content_u[message.chat.id] != [] and start_n[message.chat.id] != len(content_u[message.chat.id]):
        bot.send_message(message.from_user.id, content_u[message.chat.id][start_n[message.chat.id]][2]
                         + """\n\nАвтор: @{0} """.format(content_u[message.chat.id][start_n[message.chat.id]][4]))
        try:
            for photo in content_u[message.chat.id][start_n[message.chat.id]][3].split(','):
                bot.send_photo(message.from_user.id, photo)
            return content_u[message.chat.id]
        except Exception as error:
            print(error)
    else:
        print("reload")
        print("start_n gen = ",start_n[message.chat.id])
        reload_post(message)


"""
Функция обработки комманд

особенность этой функции что при обращении к определенной команде мы получаем изменение состояния ключа.  если команда следуюзий задействуется
то мы получаем +1 к счетчику и следущий пост из БД, "1" и "0"  выполняют ранее описанные функции и так же мзменяютс состояние счетчика и состояния в БД,
после каждой комманды следует генерация нового поста с помощью вызова функции generator_post
"""
@bot.message_handler(func=lambda message: message.chat.id in [int('id_admin'),int('id_admin')] and message.text in ['1','0','состояние','следующий']
                                           and message.chat.id in admin_cnf.keys())
def state_menu_for_post(message):

    if message.text == 'состояние' and admin_cnf[message.chat.id] == 0:
        generator_post(message)

    elif message.text == 'следующий' and admin_cnf[message.chat.id] == 0:
        start_n[message.chat.id]+=1
        generator_post(message)
        print("sosto9nie = ",start_n[message.chat.id])

    elif message.text == '1' and admin_cnf[message.chat.id] == 0:
        try:
            for photo in content_u[message.chat.id][start_n[message.chat.id]][3].split(','):
                bot.send_photo(config.id_ch, photo)
        except Exception as error:
            print(error)

        bot.send_message(config.id_ch,
                         content_u[message.chat.id][start_n[message.chat.id]][2] + """\n\nАвтор новости: @{0}\nДобавлено через бота: @bot"""
                         .format(content_u[message.chat.id][start_n[message.chat.id]][4]))

        dbase = dbconnect.Add_new_news('chnews', 'newnews')
        dbase.update_checkpost(1,content_u[message.chat.id][start_n[message.chat.id]][0])
        bot.send_message(message.from_user.id, "Новость опубликована!")
        start_n[message.chat.id] += 1
        generator_post(message)


    elif message.text == '0' and admin_cnf[message.chat.id] == 0:
        dbase = dbconnect.Add_new_news('chnews', 'newnews')
        dbase.update_checkpost(0,content_u[message.chat.id][start_n[message.chat.id]][0])
        bot.send_message(message.from_user.id, "Новость не опубликована!")
        start_n[message.chat.id] += 1
        generator_post(message)

"""
Функция добавления в черный список,
берет id юзера , настоящее время, и записывает в бд 
"""
@bot.message_handler(func=lambda message: message.chat.id in [int('id_admin'),int('id_admin'] and message.text in ['в_черный_список'])
def state_blacklis(message):
    print("tyt1")
    bot.send_message(message.from_user.id, "Введите id юзера для его блокировки!")
    if message.chat.id not in new.keys():
        blockuser[message.chat.id]=0
    else:
        new.pop(message.chat.id)
        blockuser[message.chat.id] = 0

@bot.message_handler(func=lambda message: message.chat.id in [int('id_admin'),int('id_admin')] and message.chat.id in blockuser.keys()
                                          and message.text not in ['начать','админ','активация','в_черный_список','состояние','1','0','ИНФО_отпр','выход','ВКЛ_уведомления'])
def add_blacklist(message):
    print("tyt2")
    if blockuser[message.chat.id]== 0 and message.text not in ['начать','админ','активация','в_черный_список','состояние','1','0','ИНФО_отпр','выход','ВКЛ_уведомления']:
        # print("0")
        dbase = dbconnect.Check_blacklist('chnews', 'blockuser')
        # print("1")
        dbase.addtable()
        # print("2")
        if message.text.isdigit():
            time_block = datetime.datetime.now()
            # print("3")
            dbase.add_to_blacklist(message.text,time_block)
            bot.send_message(message.from_user.id, "Юзер заблокирован!")
            blockuser[message.chat.id] = 1
        else:
            bot.send_message(message.from_user.id, "Вы ввели не верный id")
            blockuser[message.chat] = 1


@bot.message_handler(func=lambda message: message.chat.id in [int('id_admin'),int('id_admin')] and message.text in ['ИНФО_отпр'])
def info_messages(message):
    text = "Вы можете предложить свою новость на канал. Для этого напишите боту @bot."
    bot.send_message(config.id_ch, text)

@bot.message_handler(func=lambda message: message.chat.id in [int('id_admin'),int('id_admin'] and message.text in ['ВКЛ_уведомления'])
def notification_message(message):
    if message.from_user.id not in chat_id:
        chat_id.append(message.from_user.id)
        print("chaid_ init = ",chat_id)
    else:
        bot.send_message(message.from_user.id, "Уведомления уже включены!")

"""
def notification_message_func(message,count_news):
    time.sleep(2)
    if chat_id != []:
        dbase = dbconnect.Add_new_news('chnews', 'newnews')
        date_u = datetime.date.today()
        check_mes= dbase.select_news(date_u)
        coun_new = dbase.c_news(date_u)
        print("xy9k= ",check_mes)
        print("count = ",coun_new)
        if chat_id !=[] and check_mes != [] and int(coun_new[0]) > count_news:
            print("chat_id = ",chat_id)
            for idd in chat_id:
                print(idd)
                bot.send_message(idd, 'Новые записи')
            if count_news != 0:
                count_news += 1
            else:
                count_news += int(coun_new[0])

            time.sleep(2)
            notification_message_func(message,count_news)
        else:
            time.sleep(2)
            notification_message_func(message,count_news)
"""

@bot.message_handler(func=lambda message: message.chat.id in [int('id_admin'),int('id_admin'] and message.text in ['выход'])
def stop(message):
    # print("выход")
    if message.text in ["выход"]:
        admin_cnf[message.chat] = None
        content_u[message.chat.id] = None
        blockuser[message.chat] = None
        print("do end = ",chat_id)
        if message.from_user.id in chat_id:
            chat_id.remove(message.from_user.id)
        print("posle end = ",chat_id)
        bot.send_message(message.from_user.id, "Досвидания админчег")

bot.polling(none_stop=True)
