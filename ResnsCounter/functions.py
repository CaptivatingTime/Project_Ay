import asyncio  
from dotenv import load_dotenv 
import json
import random
import re
from openai import OpenAI, AsyncOpenAI
import time
from nltk.tokenize import word_tokenize 
from datetime import datetime
import pytz
import os
import nltk
from discord.ext import commands
import discord
import python_weather
from datetime import time

load_dotenv()
gpt_key               = os.getenv("GPT")
client_gpt = AsyncOpenAI(api_key=gpt_key)
addition_colltected = []
with open('testt.json', 'r') as file: #@#
    addition_colltected = json.load(file) 

async def get_threadID():
    utc_now = datetime.utcnow()
    local_timezone = pytz.timezone('Africa/Mbabane')
    local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    # Šodienas datums
    today = str(local_now.date())   
    with open("all_threads.json", "r") as file:
        thread_ids = json.load(file)

    if today not in thread_ids:
        thread = await client_gpt.beta.threads.create()
        new_entry = {
            f"{today}":{
                "thread_id": thread.id
                }
            }
        thread_ids.update(new_entry)
        with open("all_threads.json", "w") as file:
            json.dump(thread_ids, file, indent=4)  # You can adjust the indent for pretty printing
            file.write('\n')
    thread_id = thread_ids.get(str(today), {}).get("thread_id", "")
    print(thread_id)
    return thread_id    


def timeOfDay():
    now = datetime.now()
    # Check the time of day
    if now.hour  < 12:
        greeting = "Good morning"
    elif now.hour  < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good night"
    return greeting


def addPair(file_name, msg1, msg2): 
    if file_name == 'CB_pairs2addition.json':
        global addition
        addition.append([msg1,[msg2]])
        with open(file_name, 'w') as file:
            json.dump(addition,file)
        return addition
    else:
        global addition_colltected
        #addition_colltected = []
        addition_colltected.append([msg1,[msg2]])
        # with open(file_name, 'w') as file:
        #     json.dump(addition_colltected,file)
        return addition_colltected

def getDate():
    # Get the current date
    now = datetime.now()

    # Extract the day, month, and year from the datetime object
    day = now.day
    month = now.month
    year = now.year

    # Combine the day, month, and year into a formatted string
    date_string = f"{day}:{month}:{year}"

    return date_string

def getTime():
    # Get the current time
    now = datetime.now()

    # Extract the hour and minute from the datetime object
    hour = now.hour
    minute = now.minute

    # Combine the hour and minute into a formatted string
    time_string = f"{hour}:{minute}"

    return time_string

async def notify_nameday(channel):
    with open('namedays_showed.json', 'r', encoding='utf-8') as file:
        namedays_showed = json.load(file)
    today = datetime.now().strftime("%m-%d")
    with open('namedays.json', 'r', encoding='utf-8') as file:
        name_days = json.load(file)
    if today not in namedays_showed:
        if today in name_days:
            names = ", ".join(name_days[today])
            await channel.send(f"Šodien({today}) vārda dienu svin 🍄 : {names}")
        else:
            await channel.send(f"Šodien({today}) neviens nesvin vārda dienu.")


async def ElizabeteGPT(mind, tone):
    load_dotenv()
    gpt_key               = os.getenv("GPT")
    client_chat = OpenAI(api_key=gpt_key)    

    responsee = client_chat.chat.completions.create(
    model='gpt-4o',
    messages = [
    {"role": "system", "content": f'''Your name is "Elizabete". People also call you "mamma".Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. You were created 15.03.2023. You are insinde discord server "Asās resnās desiņas". Reply with short response in context. Use {tone} tone and respond only with one message with format as simple message without quotes. Do not mention which tone using. Sometimes use emojis'''},
    {"role": "user", "content": mind}
    ],
    max_tokens=700,
    n=1,
    stop=None,
    temperature=0.6,
    )
    response = responsee.choices[0].message.content
    return response    

async def notify_weather(channel):
    with open('namedays_showed.json', 'r', encoding='utf-8') as file:
        namedays_showed = json.load(file)   
    today = datetime.now().strftime("%m-%d")
    if today not in namedays_showed:  
        namedays_showed.append(today)
        with open('namedays_showed.json', 'w', encoding='utf-8') as file:
            json.dump(namedays_showed,file)          
        weather_today = ""
        i = 0
        # Define the start and end times
        start_time = time(6, 0)  # 6:00 AM
        end_time = time(6, 0)    # 6:00 AM next day

        async with python_weather.Client(unit=python_weather.METRIC) as client:
            weather = await client.get('Riga')
            
            # Current temperature
            weather_today += f"Current Temperature: {weather.temperature} °C\n"
            weather_today += "Today Forecasts:\n"
            
            # Loop through daily forecasts
            for daily in weather.daily_forecasts:
                if i == 0:
                    weather_today += f"Date: {daily.date}, Temperature: {daily.temperature}°C\n"
                    weather_today += "Hourly Forecasts:\n"
                    i = 1

                    # Loop through hourly forecasts and filter by time range
                    for hourly in daily.hourly_forecasts:
                        hourly_time = hourly.time  # Assuming this returns a datetime.time object
                        
                        # Include only times between 6:00 AM and 11:59 PM on the current day
                        if start_time <= hourly_time <= time(23, 59):
                            weather_today += (
                                f"  Time: {hourly.time}, Temperature: {hourly.temperature}°C, "
                                f"Description: {hourly.description}\n"
                            )
                
                # For the next day, include only times up to 6:00 AM
                else:
                    for hourly in daily.hourly_forecasts:
                        hourly_time = hourly.time  # Assuming this returns a datetime.time object
                        
                        # Include only times from 00:00 AM to 06:00 AM on the next day
                        if time(0, 0) <= hourly_time < end_time:
                            weather_today += (
                                f"  Time: {hourly.time}, Temperature: {hourly.temperature}°C, "
                                f"Description: {hourly.description}\n"
                            )
                    break  # Stop after getting the next day's early hours

        mind = f"Share your creatons Jānis link as just suggestion donation for coffee and support(put it in the end as plain link without brackets or parentheses): 'https://ko-fi.com/jaanisjc'. Mention todays date. Summer is over. In this autumn morning pretend you are weather teller. USE LATVIAN LANGUAGE Use emojies as bulletpoints. Give opinion on weather. In the end share short fun fact from history in today. inform people about todays weather using following data in Rīga.: {weather_today}"
        forecastMsg = await ElizabeteGPT(mind, "Emphases weather conditions")       
        await channel.send(forecastMsg)

def preprocess_message(msg):

    lv_stopwords = []
    with open('lv_stopwords.json', 'r', encoding="utf-8") as f:
       lv_stopwords = json.load(f)   
    # Remove parentheses and their contents using regex
    pattern_without_parentheses = re.sub(r'\([^)]*\)', ' ', msg)

    # Remove leading/trailing whitespace
    pattern_without_parentheses = pattern_without_parentheses.strip()

    # Convert to lowercase and remove stop words
    words = word_tokenize(pattern_without_parentheses.lower())
    pattern = [word for word in words if word not in lv_stopwords]

    # Return the preprocessed message as a string
    return "(?i).*" + re.escape(' '.join(pattern)) + ".*"

def replace_starting_phrase(sentence, starting_phrase, new_word):
    # Check if the sentence starts with the specified starting phrase
    if sentence.lower().startswith(starting_phrase.lower()):
        # Use regular expression to match the starting phrase at the beginning of the string
        pattern = r'\b' + re.escape(starting_phrase) + r'\b'
        
        # Replace the matched starting phrase with the new word
        new_sentence = re.sub(pattern, new_word, sentence, count=1, flags=re.IGNORECASE)
        
        return new_sentence
    else:
        return sentence



async def add_message_to_thread(client_gpt,thread_id, user_question):
    # Create a message inside the thread
    message = await client_gpt.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content= user_question
    )
    return message

async def scan_unsaved_msg(client, channel):
    with open("most_recent_saved_msg.json", "r") as file:
        latest_msg_ID = json.load(file)   

       

    messages = []
    
    msg1 = "None"
    msg2 = "None"
    msg1_temp = ""
    i = 0
    n = 0    
    
    gpt_key               = os.getenv("GPT")

    async for message in channel.history(limit=None, oldest_first=False):
        if message.id == latest_msg_ID["ID"]:
       # if message.id == 1205558165933133906: 
             break
        #if message.id == 1205541078363541546:
        #print(message)
        print(n)
        n = n+1
            #   break
            
        messages.append(message)
        #print(message)
    #print(latest_msg_ID["ID"])
    messages_rev = reversed(messages)

    with open("most_recent_saved_msg.json", "w") as file:
        json.dump(latest_msg_ID, file, indent=4)  # You can adjust the indent for pretty printing
    pattern = re.compile(r'\b(ay|ey|ou|au|mamma|mammu|aloha|mam|mamm|muterit|muterite|mutere|muter|mama|mammai|mammas)\b')
    for message in messages_rev:
                 reply_to_Elizabete = False
                 if message.reference:
                     if message.reference.resolved.author == client.user:
                         reply_to_Elizabete = True
                 if (pattern.search(message.content.lower()) or reply_to_Elizabete) and message.author != client.user:
                        user_content = ""
                        current_zina = message.content
                        if reply_to_Elizabete:
                            replied_message = await message.channel.fetch_message(message.reference.message_id)
                            user_content = f"Your previous messages was {replied_message}, user wrote in response '{current_zina}', give random short or medium  answer in context in latvian"
                        else: 
                            user_content = f"user wrote '{current_zina}' give random short or medium  answer in context in latvian"
                        current_zina = message.content
                        tones = ["sarcastic", "assertive", "sad", "cynical", "indignant", "contemplative", "witty", "persuasive", "rude", "angry", "romantic", "humorous", "adventurous", "creative", "friendly", "optimistic", "pessimistic", "nostalgic", "hopeful", "enthusiastic", "ambivalent", "descriptive", "suspenseful", "factual", "informative", "playful", "inspiring", "melancholic", "mysterious", "objective", "subjective", "sympathetic", "empathetic", "reflective", "confident", "satirical", "ironic", "sincere", "cautious", "credible", "informal", "formal", "professional", "scholarly", "inspirational", "controversial", "diplomatic", "nurturing", "authoritative", "didactic", "patronizing", "dismissive", "unemotional", "nihilistic"]

                        random.seed(time.time())
                        selected_tone = random.choice(tones)
                        #selected_tone = "evil joker"
                  
                        await channel.typing()

                     
                        client_chat = OpenAI(api_key=gpt_key)

                        responsee = client_chat.chat.completions.create(
                        model='gpt-4-1106-preview',
                        messages = [
                        {"role": "system", "content": f"'Your name is 'Elizabete'. People also call you 'mamma'. Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. You pretend that you have given response, recieved an answer from user and reply with compact random response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Sometimes use random emoji"},
                        {"role": "user", "content": user_content}
                        ],
                        max_tokens=700,
                        n=1,
                        stop=None,
                        temperature=0.6,
                        )                              
                        generated_text = responsee.choices[0].message.content
                        await message.reply(generated_text)


                 if msg1 != "None" and msg2 == "None":
                     msg2 = message.content
                     if message.attachments:
                         for att in message.attachments:
                              url = att.url 
                              msg2 = f"{msg2}\n{url}"
                 if msg1 == "None":
                     msg1 = message.content
                     #msg1_temp = msg1
                     msg1 = preprocess_message(msg1)
                     if  message.attachments:
                         for att in message.attachments:
                              url = att.url 
                              msg1 = f"{msg2}\n{url}"
                 if msg1 != "None" and msg2 != "None":
                    # temp = msg1
                   
                    if message.reference:
                       try:
                        if message.reference.resolved:
                            msg1 = message.reference.resolved.content
                        else:
                            
                            msg1_id = message.reference.message_id
                            
                            msg1_full = await channel.fetch_message(msg1_id)
                            

                           # replied_zina = replied_message.content
                            msg1 = msg1_full.content
                        if  message.reference.resolved is not None:
                            if  message.reference.resolved.attachments:
                              for att in message.attachments:
                                  url = att.url 
                                  msg1 = f"{msg1}\n{url}"
                                  msg1 = preprocess_message(msg1)
                        msg2 = message.content
                        if  message.attachments:
                          for att in message.attachments:
                              url = att.url 
                              msg2 = f"{msg2}\n{url}"
                       except:
                         print("ERROR")
                         created_at_utc = message.created_at.replace(tzinfo=pytz.utc)
                         desired_timezone = pytz.timezone("Africa/Bujumbura")
                         created_at_local = created_at_utc.astimezone(desired_timezone)
   
                         time_stamp = created_at_local.strftime('%d-%m %H:%M:%S')
                         name = message.author.name
                         new_message = f"{name}[{time_stamp}]:  '{message.content}'"
                         print(new_message)
                         if message.content != msg1:
                            msg2 = message.content
                            if  message.attachments:
                              for att in message.attachments:
                                  url = att.url 
                                  msg2 = f"{msg2}\n{url}"
                    else:
                     if message.content != msg1:
                        msg2 = message.content
                        if  message.attachments:
                          for att in message.attachments:
                              url = att.url 
                              msg2 = f"{msg2}\n{url}"
                    #print(f"msg1: {msg1}\nmsg2: {msg2}\n\n")

                    msg2 = replace_starting_phrase(msg2, "mammu", "pipsi")
                    msg2 = replace_starting_phrase(msg2, "ay gudrais", "pipsi")
                    msg2 = replace_starting_phrase(msg2, "ey gudrais", "pipsi")
                    addPair('testt.json', msg1, msg2)
                    msg1 = msg2
                    msg1 = preprocess_message(msg1)
                 i = i+1
                 name = message.author.name
                 if message.author.name == "Resnā mamma":
                    name = "Elizabete"
                 else: 
                   name = message.author.name

                 created_at_utc = message.created_at.replace(tzinfo=pytz.utc)
                 desired_timezone = pytz.timezone("Africa/Bujumbura")
                 created_at_local = created_at_utc.astimezone(desired_timezone)
   
                 time_stamp = created_at_local.strftime('%d-%m %H:%M:%S')
                 new_message = f"{name}[{time_stamp}]:  '{message.content}'"
                 thread_id = await get_threadID()
                 await add_message_to_thread(client_gpt, thread_id, new_message)
                 print(new_message)
                 if i == 57:
                    await asyncio.sleep(60)
             
                    #amount = amount + i
                    i = 0

    latest_msg_ID["ID"] = message.id
    with open("most_recent_saved_msg.json", "w") as file:
        json.dump(latest_msg_ID, file, indent=4)  # You can adjust the indent for pretty printing
    with open('testt.json', 'w') as file:
             json.dump(addition_colltected,file)