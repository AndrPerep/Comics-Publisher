import random
import requests
import os
from dotenv import load_dotenv


def get_last_comic_num():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()

    return response.json()['num']


def load_comic(filename):
    comic_num = random.randint(1, get_last_comic_num())

    url = f'https://xkcd.com/{comic_num}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()

    img_url = response.json()['img']
    img_response = requests.get(img_url)
    img_response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(img_response.content)

    comment = response.json()['alt']
    return comment


def get_upload_url(access_token, group_id):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payload = {
        'v': '5.131',
        'access_token': access_token
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()

    decoded_response = response.json()['response']
    return decoded_response['upload_url']


def upload_photo(access_token, group_id, filename):
    with open(f'./{filename}', 'rb') as file:
        url = get_upload_url(access_token, group_id)
        files = {
            'photo': file
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
    decoded_response = response.json()
    return decoded_response.values()


def save_photo(access_token, group_id, filename):
    server, photo, hash = upload_photo(access_token, group_id, filename)
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    payload = {
        'v': '5.131',
        'access_token': access_token,
        'hash': hash,
        'photo': photo,
        'server': server
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()

    return response.json()['response'][0]


def post_photo(access_token, group_id, filename):
    comment = load_comic(filename)
    photo = save_photo(access_token, group_id, filename)

    url = 'https://api.vk.com/method/wall.post'
    payload = {
        'v': '5.131',
        'access_token': access_token,
        'owner_id': group_id,
        'from_group': 1,
        'message': comment,
        'attachments': 'photo{}_{}'.format(photo['owner_id'], photo['id'])
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    os.remove(filename)


def main():
    load_dotenv()
    vk_access_token = os.getenv('VK_ACCESS_TOKEN')
    vk_group_id = os.getenv('VK_GROUP_ID')
    filename = 'comic.png'

    post_photo(vk_access_token, vk_group_id, filename)


if __name__ == '__main__':
    main()
