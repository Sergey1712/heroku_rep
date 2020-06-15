import random
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests, vk_api
from time import sleep
import os
from urllib.parse import unquote
from PIL import Image
from docx import Document
from docx.shared import Cm

login = 'voronin_1922@mail.ru'
password = 'Iphone11IchLibenDu'
group = '196003084'


def auth():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1200,40000")
    options.add_argument("--start-maximized")
    options.add_argument("--start-fullscreen")

    chrome_profile = webdriver.ChromeOptions()
    profile = {"download.default_directory": "C:\\",
               "download.prompt_for_download": False,
               "download.directory_upgrade": True,
               "plugins.plugins_disabled": ["Chrome PDF Viewer"]}
    chrome_profile.add_experimental_option("prefs", profile)

    geckodriver = 'C:\\geckodriver\\chromedriver.exe'
    browser = webdriver.Chrome(options=options, executable_path=geckodriver)
    browser.get('https://umschool.net/accounts/login/')
    browser.find_element_by_id('check1').send_keys(login)
    browser.find_element_by_id('pswd').send_keys(password)
    browser.find_element_by_class_name('button').click()
    sleep(2)
    return browser


def auth_handler():
    key = input("Введите код: ")
    remember_device = True
    return key, remember_device


browser = auth()
# link = input("Ссылка на мг:")
browser.get('https://umschool.net/course/540/lessons/')
sleep(2)
browser.find_element_by_class_name('btn-orange').click()
sleep(2)
youtube = browser.find_element_by_tag_name('iframe').get_attribute('src')
youtube = youtube[:youtube.find('?')]
if 'youtube' in youtube:
    youtube = youtube.replace('/embed/', '/watch?v=')
else:
    youtube = youtube.replace('/embed', '')
print(youtube)
title = ''
tmp = browser.find_element_by_tag_name('h1').text
browser.back()
sleep(2)
try:
    tmp2 = browser.find_element_by_css_selector('div.description').text
    title = f"{tmp}\n\n{tmp2}"
except Exception as e:
    print(e)
    title = tmp

link = []
lol = browser.find_element_by_class_name('lesson-content').find_elements_by_class_name('ml-2')
for x in lol:
    a = x.find_element_by_tag_name('a').get_attribute('href')
    if a:
        link.append(a)
print(link)
print(youtube)

name_files = []
for x in link:
    pdf_resp = requests.get(x)
    ran = random.randint(1, 10000000)
    with open(f"{ran}.pdf", "wb") as f:
        f.write(pdf_resp.content)
    name_file = str(unquote(x[x.rfind('/') + 1:]))
    os.rename(f'{ran}.pdf', name_file)
    name_files.append(name_file)
    sleep(3)

login, password = '89205474557', 'SergeyApox51s42'

vk_session = vk_api.VkApi(
    login, password,
    auth_handler=auth_handler
)
try:
    vk_session.auth(token_only=True)
except vk_api.AuthError as error_msg:
    print(error_msg)
vk = vk_session.get_api()
doc_link = []
for x in name_files:
    sleep(3)
    post_url = vk.docs.getWallUploadServer(group_id=group)['upload_url']
    sleep(3)
    resp = requests.post(post_url, files={'file': open(x, 'rb')}).json()
    try:
        doc = vk.docs.save(file=resp['file'],
                           title=f"{x.replace('.pdf', '').replace('.docx', '')}_" +
                                 title.split('\n')[0])
        print(doc)
        doc_link.append(f"doc{doc['doc']['owner_id']}_{doc['doc']['id']}")
    except vk_api.exceptions.Captcha as captcha:
        key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
        captcha.try_again(key)
        doc = vk.docs.save(file=resp['file'],
                           title=f"{x.replace('.pdf', '').replace('.docx', '')}_" +
                                 title.split('\n')[0])
        print(doc)
        doc_link.append(f"doc{doc['doc']['owner_id']}_{doc['doc']['id']}")

vk = vk_session.get_api()
res = vk.wall.post(owner_id='-' + group,
                   from_group=1,
                   message=title + '\n\n' + youtube,
                   attachments=f"{','.join(doc_link)}")
print(res)
for x in name_files:
    os.remove(x)
sleep(30)
