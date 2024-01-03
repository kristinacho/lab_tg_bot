import telebot
from telebot import types
import json
from metodhs_json import *
import uuid
from post_vk.wall import *
import os
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.environ.get('TG_BOT_TOKEN'))

def mainWindow():
    markup = types.InlineKeyboardMarkup(row_width=2)
    item = types.InlineKeyboardButton("Создать пост", callback_data="item_1")
    item3 = types.InlineKeyboardButton("Мои посты", callback_data="my_posts")
    markup.add(item, item3)
    return markup

def myPostsWindow():
    posts = getPostsFromFile('posts.json')
    markup = types.InlineKeyboardMarkup(row_width=2)
    for post in posts:
        item = types.InlineKeyboardButton(post['name'], callback_data=("post_" + str(post['id'])))
        markup.add(item)
    itemBack = types.InlineKeyboardButton("Вернуться назад", callback_data="back_main")
    markup.add(itemBack)
    return markup

def myPostWindow(postId):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item = types.InlineKeyboardButton("Опубликовать пост", callback_data="to_publish_{}".format(postId))
    item2 = types.InlineKeyboardButton("Удалить пост", callback_data="removePost_{}".format(postId))
    itemBack = types.InlineKeyboardButton("Вернуться назад", callback_data="back_my_posts")
    markup.add(item, itemBack,item2)
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    markup = mainWindow()
    bot.send_message(message.chat.id, "Привет, это Телеграм Бот, который поможет тебе опубликовать запись в сообществе Вконтакте!  Выберите действие: ", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == "item_1":
            bot.edit_message_text(
                chat_id=call.message.chat.id, message_id=call.message.id, text = "Напиши название для публикуемой записи. "
            )
        
        elif call.data == "my_posts" or call.data == "back_my_posts":
            markup = myPostsWindow()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text = "Мои посты", reply_markup=markup)
        
        elif call.data == "back_main":
            markup = mainWindow()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id = call.message.id, text = "Выберите действие:", reply_markup=markup)
        
        elif "post_" in call.data:
            postId = call.data.split("_")[1]
            post = getPostById('posts.json' , postId)
            markup = myPostWindow(postId)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text = "Пост: {}".format(post['name']), reply_markup=markup)
        
        elif "to_publish_" in call.data:
            postId = call.data.split("_")[2]
            post = getPostById('posts.json' , postId)
            vkPostIdPrev = post['id_vk']
            if (vkPostIdPrev != ""):
                wallPostDelete(post)
            response=wallPost(post)
            if 'post_id' in response:
                vkPostIdNew=response['post_id']
                post['id_vk'] = vkPostIdNew
                changePostById('posts.json', post)
                markup = myPostsWindow()
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text = "Пост успешно опубликован в группу вк. \n\nМои посты:", reply_markup=markup)
            else:
                markup = myPostsWindow()
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text = "Произошла ошибка при публикации поста в группу вк. \n\nМои посты:", reply_markup=markup)

        elif "removePost_" in call.data:
            postId = call.data.split("_")[1]
            post = getPostById('posts.json' , postId)
            vkPostIdPrev = post['id_vk']
            if (vkPostIdPrev != ""):
                response = wallPostDelete(post)
                if response == 1:
                    deletePostById('posts.json' , postId)
                    markup = myPostsWindow()
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text = "Пост успешно удален. \n\nМои посты:", reply_markup=markup)
                else:
                    markup = myPostsWindow()
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text = "Произошла ошибка при удалении поста с группы вк. \n\nМои посты:", reply_markup=markup)
                    


user_state = {}
post = {}


@bot.message_handler(content_types=["text"])
def info(message):
    chat_id = message.chat.id
    if chat_id not in user_state:
        user_state[chat_id] = "waiting_for_first_message"
        post["id"] = str(uuid.uuid4())
        post["name"] = message.text
        bot.reply_to(message, "Отлично, теперь напиши текст для записи.")
    else:
        if user_state[chat_id] == "waiting_for_first_message":
            post["post"] = message.text
            bot.reply_to(
                message,
                "Спасибо за текст. Теперь пришли мне id группы Вконтакте, в которой ты хотел бы опубликовать запись.",
            )
            user_state[chat_id] = "waiting_for_second_message"
        elif user_state[chat_id] == "waiting_for_second_message":
            post["link_group"] = message.text
            post['id_vk'] = ""
            savePostInFile("posts.json", post)
            markup = mainWindow()
            bot.send_message(
                message.chat.id, "Ты успешно создал пост!", reply_markup=markup
            )
            del user_state[chat_id]

        else:
            bot.reply_to(
                message, "Произошла ошибка,попробуйте заново. Для этого введите: /start"
            )
            user_state[chat_id] = "waiting_for_fourth_message"

if __name__ == "__main__":
    print("Bot started...")
    bot.polling()
