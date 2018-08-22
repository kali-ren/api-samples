#!/usr/bin/env python3

"""
Telegram bot to integrate Qradar API Samples

Bot get number of offenses and assorted events(not implemeted yet) via text or voice command(speech_recognition and ffmpy are required) 

"""

from pprint import pprint
import telepot, speech_recognition as sr
import time, os, sys
from telepot.loop import MessageLoop
import ffmpy
import requests
from telepot.namedtuple import ReplyKeyboardMarkup
import importlib

sys.path.append(os.path.realpath('siem'))
sys.path.append(os.path.realpath('modules'))

api = 'your_token'
siem_module = importlib.import_module('scratch')

def action(acao):
	acao = acao.lower()
	
	if acao == 'ofensas dia'
		return siem_module.get_offenses(1)

	elif acao == 'ofensas semana':	
		return siem_module.get_offenses(7)

	elif acao == 'ofensas mes':
		return siem_module.get_offenses(30)

	else:
		return 'command not found!'

def speech2text(novo):
    harvard = sr.AudioFile(novo)
    r = sr.Recognizer()
			
    with harvard as source:
        audio = r.record(source)
        print (type(audio))
        r = r.recognize_google(audio,language='pt')

    return action(r)

def extract_audio(msg):
    file_id = msg['voice']['file_id']
    file_name = 'comando_novo.ogg'
    bot.download_file(file_id,file_name)
  
    ff = ffmpy.FFmpeg(
        inputs={file_name : '-loglevel quiet'},
        outputs={'output.wav' : None}
        )
    ff.run()

    return 'output.wav'

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print (content_type, chat_type, chat_id)#debug
	#bot.sendMessage(chat_id,'Aguarde')	

    if content_type == 'text':
        #bot.sendMessage(chat_id, msg['text'])
        if msg['text'].startswith('/help'):
            keyboard = ReplyKeyboardMarkup(keyboard=[['ofensas dia','ofensas semana','ofensas mes']],resize_keyboard=True)
            bot.sendMessage(chat_id, 'Choice options', reply_markup=keyboard)			
        else:
            print (msg['text'])
            bot.sendMessage(chat_id,action(msg['text']))

    elif content_type == 'voice':
        print (msg['voice']['file_id'])
        #bot.sendMessage(chat_id, bot.getUpdates())
        command = speech2text(extract_audio(msg))
        bot.sendMessage(chat_id,command)
        try:
            os.remove('output.wav')
            os.remove('comando_novo.ogg')
        except Exception as e:
            print (e)

bot = telepot.Bot(api)
MessageLoop(bot, handle).run_as_thread()
print ('listening ...')

while 1:
    time.sleep(10)

