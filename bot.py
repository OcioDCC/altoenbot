#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os

import requests
import sys
import telepot
import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from telepot.namedtuple import InlineQueryResultPhoto, InputTextMessageContent

bot = telepot.Bot(sys.argv[1])
answerer = telepot.helper.Answerer(bot)
FONT = "opensans.ttf"
SIZES = [9,17,24]
POSITIONS2 = [80,100]
POSITIONS3 = [70,90,120]
POSITIONS_DOWN = [190,200]
MAX_CHARS_TEXT = [16,12,12]
MAX_CHARS_DOWN = [18,18]
SERV_ROOT = "/var/www/bots/altoenbot/imgs/"
SERV_URL = "http://45.55.157.236/bots/altoenbot/imgs/"

def get_text_array(text,max_chars):
    text = text.strip()
    arr_tmp = text.split(" ")
    arr_pos = 0;
    arr = []
    first = True
    for maxchars in max_chars:
        act_txt = ""
        if arr_pos >= len(arr_tmp):
            break
        count = maxchars+1
        while count >= 0 and arr_pos < len(arr_tmp):
            if arr_pos == len(arr_tmp)-1 and first:
                first = False
                break # Para tener texto en los cuadros grandes si queda solo una palabra
            if (len(arr_tmp[arr_pos])+1 <= count):
                act_txt += " " + arr_tmp[arr_pos]
                count -= len(arr_tmp[arr_pos])
                arr_pos += 1
            else:
                break
        first = False
        arr.append(act_txt[1:])
    return arr


def add_text_to_center(im,draw,text,height,size):
    font = ImageFont.truetype(FONT, SIZES[size])
    text_size = draw.textsize(text, font)
    return draw.text(
        ((im.size[0] - text_size[0]) / 2, height),
        text, font=font, fill=(255,255,255,255))


def create_image(id, text):
    im = Image.open('altoen.png', 'r').copy()
    draw = ImageDraw.Draw(im)
    arr_dos = text.split("#",1)
    arr = get_text_array(arr_dos[0], MAX_CHARS_TEXT)
    if "#" in text:
        arr_down = get_text_array(arr_dos[1],MAX_CHARS_DOWN)
    else:
        arr_down = ["CREADO CON","ALTOENBOT"]
    for i in range(0,len(arr)):
        size = 1 if i==0 else 2
        positions = POSITIONS2 if len(arr) == 2 else POSITIONS3
        add_text_to_center(im,draw,arr[i],positions[i],size)
    for i in range(0,len(arr_down)):
        size = 0
        positions = POSITIONS_DOWN
        add_text_to_center(im,draw,arr_down[i],positions[i],size)
    imgname = str(id)+".png"
    imgpath = SERV_ROOT + imgname
    im.save(imgpath)
    #r = requests.post('http://uploads.im/api', files={'img': open(imgname, 'rb')})
    #reqpost = json.loads(r.text)["data"]
    reqpost = get_img_metadata(imgname,imgpath)
    #os.remove(imgname)
    return reqpost

def get_img_metadata(imgname, imgpath):
    meta = {};
    with Image.open(imgpath) as im:
        thumbname = "thumb."+imgname;
        im.thumbnail((128,128), Image.ANTIALIAS)
        im.save(SERV_ROOT + thumbname, "JPEG")
        meta['img_width'], meta['img_height'] = im.size;
        meta['img_url'] = SERV_URL + imgname;
        meta['thumb_url'] = SERV_URL + thumbname;
        meta['name'] = imgname[0:len(imgname)-4];
    return meta;

def on_inline_query(msg):
    def compute():
        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        print ('Inline Query:', query_id, from_id, query_string)
        reqpost = create_image(query_id,query_string)
        articles = [InlineQueryResultPhoto(
                        id=reqpost["name"][0:64],
                        title='AltoEnBot',
                        photo_url = reqpost["img_url"],
                        thumb_url = reqpost["thumb_url"],
                        photo_width = reqpost["img_width"],
                        photo_height= reqpost["img_height"],
                        caption = "Creado con @altoenbot"
                       )]
        return articles

    answerer.answer(msg, compute)

def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print ('Chosen Inline Result:', result_id, from_id, query_string)

def default_handler(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    bot.sendMessage(chat_id, "Hola, debes usarme en modo inline o no funciono.")

bot.message_loop({'chat':default_handler,
                  'inline_query': on_inline_query,
                  'chosen_inline_result': on_chosen_inline_result},
                 run_forever='Listening ...')
