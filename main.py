# USER GUIDE
# Script allows to collect music list of current VK user to local hard drive without API.

# SETTINGS
# Edit settings.json file. PATH_TO_SAVE_FILES is path for downloading (\\ instead \ in windows).

# USAGE
# 1) Start browser (better Chrome)
# 2) Login to vk.com
# 3) Start script


import os
import sys
import re
import json
import shutil
import requests
import browser_cookie3

global PATH_TO_SAVE_FILES, COOKIES


def to_correct_name(name):
    name = name.replace('*', '_').replace('|', '').replace('\\', '_')\
               .replace(':', '').replace('"', '`').replace('<', '')\
               .replace('>', '').replace('?', '').replace('/', '')
    return name


def get_settings():  # TODO make setting by console args
    with open('settings.json') as f:
        jf = json.load(f)
        global PATH_TO_SAVE_FILES
        PATH_TO_SAVE_FILES = jf['PATH_TO_SAVE_FILES']


def get_user_id():
    global COOKIES
    resp = requests.get('https://vk.com/', cookies=COOKIES)
    user_id = re.findall('vk_id=(\d*)&', resp.text)[0]

    return user_id


def collect_audio_links():
    global COOKIES
    user_id = get_user_id()
    audio_url = 'https://vk.com/audios%s' % user_id
    resp = requests.get(audio_url, cookies=COOKIES)
    audio_links = [link for link in re.findall('value="(https://.*mp3)', resp.text)]
    return audio_links


def download_by_links(audio_links):
    downloaded_files = [f for f in os.listdir(PATH_TO_SAVE_FILES)
                        if os.path.isfile(os.path.join(PATH_TO_SAVE_FILES, f))]

    for link in audio_links:
        name = link.split('/')[-1]  # TODO make naming from mp3 metada
        if name not in downloaded_files:
            print('-->    %s' % name)
            try:
                resp = requests.get(link, stream=True)
                if resp.status_code == 200:
                    path = os.path.join(PATH_TO_SAVE_FILES, name)
                    with open(path, 'wb') as f:
                        resp.raw.decode_content = True
                        shutil.copyfileobj(resp.raw, f)
            except Exception as e:
                print('ERROR:\n%s\n%s\n\n' % (name, e))


if __name__ == '__main__':
    global COOKIES
    COOKIES = browser_cookie3.load()

    get_settings()

    try:
        audio_links = collect_audio_links()
    except Exception as e:
        print('1) Restart browser\n2) Relogin to vk.com\n3) Restart script')
        sys.exit(-1)

    download_by_links(audio_links)
    print('DONE!')
