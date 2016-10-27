#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import requests
import telepot
import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from telepot.namedtuple import InlineQueryResultPhoto, InputTextMessageContent

bot = telepot.Bot("281070738:AAFzojC-b9O3kQtLcFIlue7xKBevW4xqKzg")
answerer = telepot.helper.Answerer(bot)
FONT = "opensans.ttf"
SIZES = [9,18,24]
POSITIONS2 = [80,100]
POSITIONS3 = [70,90,120]
POSITIONS_DOWN = [190,200]
MAX_CHARS_TEXT = [16,12,12]
MAX_CHARS_DOWN = [18,18]


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
    arr_dos = text.split("#",2)
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
    im.save(imgname)
    r = requests.post('http://uploads.im/api', files={'img': open(imgname, 'rb')})
    reqpost = json.loads(r.text)["data"]
    return reqpost


def on_inline_query(msg):
    def compute():
        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        print ('Inline Query:', query_id, from_id, query_string)
        reqpost = create_image(query_id,query_string)
        articles = [InlineQueryResultPhoto(
                        id=reqpost["img_url"][0:64],
                        title='AltoEnBot',
                        photo_url = reqpost["img_url"],
                        thumb_url = reqpost["thumb_url"],
                        photo_width = int(reqpost["img_width"]),
                        photo_width= int(reqpost["img_height"]),
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