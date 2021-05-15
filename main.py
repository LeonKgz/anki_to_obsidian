import os
import math
import numpy
import time

import json
import urllib.request

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']

# decks = ['Also sprach Zarathustra', 'Enten-eller', 'Horus Heresy', 'QI', 'Автостопом', 'Афоризмы житейской мудрости', 'Болезнь к Смерти','Великий и Могучий', 'Герои и героини (INACTIVE)', 'Главные вопросы', 'Греция - Рим (INACTIVE)', 'Евангелие страданий', 'Закат Европы', 'Критика чистого разума (INACTIVE)', 'Мир как воля и представление (INACTIVE)', 'По ту сторону Добра и Зла', 'Полевая лилия и птица небесная', 'Понятие страха', 'Философия Канке (Вопросы)', '詩', 'Учитель', ]
         
decks = invoke('deckNames')

from datetime import datetime
import string
import base64

todo = len(decks)

def retrieve_media(decks, file_extension=".jpg"):
    
    # Iterate through all decks
    for deck in decks:
       cards = invoke('findCards', query=f"deck:\"{deck}\"")
       infos = invoke('cardsInfo', cards=cards)

       # Iterate through all cards within a deck 
       for info in infos:
           
           # get the front (assuming that the front is a question/description)
           # and remove punctuation, since cannot have punctuation in obsidian 
           # file names
           front = info["fields"]["Вопрос"]["value"]
           front = front.translate(str.maketrans('', '', string.punctuation))
           
           back = info["fields"]["Ответ"]["value"]
            
           if (file_extension in back):

               # If there are any media files in the back side of the card, 
               # get the file name from "<img src='file_name'>" and replace
               # with ![[file_name]] (this is how you access files in Obsidian)
               if ("src=\'" in back):
                   back_file_name = back.split("<img src=\'")[1].split("\'/>")[0]
                   to_replace = "<img src=\'" + back_file_name + "\'/>"
               if ("src=\"" in back):
                   back_file_name = back.split("<img src=\"")[1].split("\"/>")[0]
                   to_replace = "<img src=\"" + back_file_name + "\"/>"

               back = back.replace(to_replace, f"![[{back_file_name}]]")
               
               # print(back_file_name)

               # Save the contents of media file locally
               # (this particular implementation) works for jpg files
               data = invoke('retrieveMediaFile', filename=back_file_name)
               data = base64.b64decode(data)
               with open(f"obsidian/images/{back_file_name}", 'wb') as f:
                   f.write(data)

               # Produce the resulting contents of a markdown file and save  
               result = front + " — " + back
               file_name = front
               try:
                   with open("obsidian/" + front + ".md", 'w', encoding='utf-8') as f:
                       now = datetime.now()
                       current_time = now.strftime("%H%M")
                       code = "2120210430" + str(current_time)
                       contents = f"{code}\nTags: #type_unfinished_anki \n---\n# {str(front)}\n\n{str(back)}\n\n---\n### Zero-Links\n- [[00 {deck}]]\n---\n### Links\n-"
                       f.write(str(contents))
                       f.close()
               except OSError as err:
                   print(f"deck {deck}; card {front} FAILED")
            
           else:
               # same as above but without media contents (only text based)
               result = front + " — " + back
               file_name = front
               try:
                   with open("obsidian/" + front + ".md", 'w', encoding='utf-8') as f:
                       now = datetime.now()
                       current_time = now.strftime("%H%M")
                       code = "2120210430" + str(current_time)
                       contents = f"{code}\nTags: #type_unfinished_anki \n---\n# {str(front)}\n\n{str(back)}\n\n---\n### Zero-Links\n- [[00 {deck}]]\n---\n### Links\n-"
                       f.write(str(contents))
                       f.close()
               except OSError as err:
                   print(f"deck {deck}; card {front} FAILED")

       print(f"{deck} is done ({len(infos)} cards), {todo} decks are left!")

# same as above but without media contents (only text based)
def retrieve_text(decks):
    for deck in decks:
        cards = invoke('findCards', query=f"deck:\"{deck}\"")
        infos = invoke('cardsInfo', cards=cards)
        for info in infos:
            # print(info)
            front = info["fields"]["Вопрос"]["value"]
            front = front.translate(str.maketrans('', '', string.punctuation))

            back = info["fields"]["Ответ"]["value"]
            result = front + " — " + back
            file_name = front
            try:
                with open("obsidian/" + front + ".md", 'w', encoding='utf-8') as f:
                    now = datetime.now()
                    current_time = now.strftime("%H%M")
                    code = "2120210430" + str(current_time)
                    contents = f"{code}\nTags: #type_unfinished_anki \n---\n# {str(front)}\n\n{str(back)}\n\n---\n### Zero-Links\n- [[00 {deck}]]\n---\n### Links\n-"
                    f.write(str(contents))
                    f.close()
            except OSError as err:
                print(f"deck {deck}; card {front} FAILED")


        todo -= 1
        print(f"{deck} is done ({len(infos)} cards), {todo} decks are left!")

# retrieve_media(decks)
