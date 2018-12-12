#!/usr/bin/env python3

"""
Telegram bot to integrate Qradar API Samples

Bot gets number of offenses and assorted events(not implemeted yet) via text or voice command(speech_recognition and ffmpy are required) 

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
db_model = importlib.import_module('banco')#import database

logfile = 'yourpath'

def save_log(contact):#save bot new interactions 
	with open(logfile,'a') as f:
		f.write(contact+'\n\n')

# This function receveid a command and returns a friendly message for specified client with the number
# of offenses found(if any).
def action_offenses(acao,client_id):
	acao = acao.lower()
	
	if acao == 'ofensas hoje' or acao == '/ofensas_hoje':
		return siem_module.get_offenses(0,client_id)

	elif acao == 'ofensas dia' or acao == '/ofensas_ontem':
		return siem_module.get_offenses(1,client_id)

	elif acao == 'ofensas semana' or acao == '/ofensas_semana':	
		return siem_module.get_offenses(7,client_id)

	elif acao == 'ofensas mes' or acao == '/ofensas_mes':
		return siem_module.get_offenses(30,client_id)
	
	else:
		return 'command not found!'


# This function convert audio message for text.
# The message is send to action_offenses.
def speech2text(novo, client_id):
    harvard = sr.AudioFile(novo)
    r = sr.Recognizer()
			
    with harvard as source:
        audio = r.record(source)
        print (type(audio))
        r = r.recognize_google(audio,language='pt')

    return action_offenses(r,client_id)


# This function download the audio file from chat.
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


# This function handles the messages and manages responses.
def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print (content_type, chat_type, chat_id)#debug purposes
	chat_id = str(chat_id) 
    contact = bot.getUpdates()
    pprint(contact)
    
    #authenticated client using a database
    if(db_model.fetch(str(chat_id))):
        client_id = str(db_model.get_domain_id(str(chat_id)))

        if content_type == 'text':
	        if msg['text'].startswith('/help'):
	            keyboard = ReplyKeyboardMarkup(keyboard=[['ofensas hoje','ofensas dia','ofensas semana','ofensas mes']],resize_keyboard=True)
	            bot.sendMessage(chat_id, 'Choice options', reply_markup=keyboard)				        
	        else:
                print(msg['text'])
                answer = action_offenses(msg['text'],client_id)
                bot.sendMessage(chat_id,answer)

                if answer == 'command not found.':
                	pass

                else:
                    with open('/path/teste.png','rb') as f:#fig. path to send.
                        bot.sendPhoto(chat_id,f)	    
	    
	    elif content_type == 'voice':
	        print (msg['voice']['file_id'])
	        answer = speech2text(extract_audio(msg), client_id)
			
			if answer == 'command not found':
				pass
			
			else:
				bot.sendMessage(chat_id,answer)
				with open('/home/renan/Desktop/golimar/1teste.png','rb') as f:
                	bot.sendPhoto(chat_id,f)
	        try:
	            os.remove('output.wav')
	            os.remove('comando_novo.ogg')
	        except Exception as e:
	            print (e)
    else:
        save_log(str(contact))
        bot.sendMessage(chat_id,'bot test')		            


bot = telepot.Bot(api)
MessageLoop(bot, handle).run_as_thread()
print ('listening ...')

while 1:
    time.sleep(10)
