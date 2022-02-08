import random
import requests
import os
from dotenv import load_dotenv


def check_vk_api_response(decoded_response):
    if 'error' in decoded_response:
        raise requests.HTTPError(decoded_response['error'])


def get_last_comic_num():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()

    return response.json()['num']


def load_random_comic(filename, last_comic_num):
    comic_num = random.randint(1, last_comic_num)

    url = f'https://xkcd.com/{comic_num}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    decoded_response = response.json()

    img_url = decoded_response['img']
    img_response = requests.get(img_url)
    img_response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(img_response.content)

    comment = decoded_response['alt']
    return comment


def get_upload_url(access_token, group_id):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payload = {
        'v': '5.131',
        'access_token': access_token
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    decoded_response = response.json()
    check_vk_api_response(decoded_response)

    return decoded_response['response']['upload_url']


def upload_photo(access_token, group_id, filename):
    with open(f'./{filename}', 'rb') as file:
        url = get_upload_url(access_token, group_id)
        files = {
            'photo': file
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
        decoded_response = response.json()
    check_vk_api_response(decoded_response)

    return decoded_response.values()


def save_photo_on_server(access_token, group_id, filename, server, photo, hash):
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
    decoded_response = response.json()
    check_vk_api_response(decoded_response)

    return decoded_response['response'][0]


def post_photo_in_vk(access_token, group_id, filename, comment, saved_photo):
    url = 'https://api.vk.com/method/wall.post'
    payload = {
        'v': '5.131',
        'access_token': access_token,
        'owner_id': group_id,
        'from_group': 1,
        'message': comment,
        'attachments': 'photo{}_{}'.format(saved_photo['owner_id'], saved_photo['id'])
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    check_vk_api_response(response.json())


def main():
    load_dotenv()
    vk_access_token = os.getenv('VK_ACCESS_TOKEN')
    vk_group_id = os.getenv('VK_GROUP_ID')
    filename = 'comic.png'

    last_comic_num = get_last_comic_num()
    comment = load_random_comic(filename, last_comic_num)
    try:
        server, photo, hash = upload_photo(vk_access_token, vk_group_id, filename)
        saved_photo = save_photo_on_server(vk_access_token, vk_group_id, filename, server, photo, hash)
        post_photo_in_vk(vk_access_token, vk_group_id, filename, comment, saved_photo)
    finally:
        os.remove(filename)


if __name__ == '__main__':
    main()
