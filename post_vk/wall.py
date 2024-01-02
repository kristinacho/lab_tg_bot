import requests
import os
from dotenv import load_dotenv

load_dotenv()


user_token = os.environ.get('VK_TOKEN')

def wallPost(post):

    params = {
        'owner_id': post['link_group'],#id группы,куда будет производиться публикация поста
        'from_group': '1',  #флаг, указывающий, что пост будет опубликован от имени группы.
        'message': post['post'],  #текст публикуемого сообщения 
        'access_token': user_token,    
        'v': '5.131',  # Версия VK API
    }
    response = requests.post('https://api.vk.com/method/wall.post', data=params)
    data=response.json()
    return data['response']

def wallPostDelete(post):

    params = {
        'owner_id': post['link_group'],#id группы,куда будет производиться публикация поста
        'post_id': post['id_vk'],  #флаг, указывающий, что пост будет опубликован от имени группы. 
        'access_token': user_token,    
        'v': '5.131',  # Версия VK API
    }
    requests.post('https://api.vk.com/method/wall.delete', data=params)


