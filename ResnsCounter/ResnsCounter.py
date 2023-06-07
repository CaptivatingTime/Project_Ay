import time
import os
import discord
from dotenv import load_dotenv
from datetime import datetime
from datetime import timedelta
import discord.utils
import json
import random
import asyncio
import re
import warnings #@#
import numpy as np
from nltk.chat.util import Chat
from bot_Chatting import Chatbot,get_similar_response
from nltk.tokenize import word_tokenize 
 ### NEW ###
##M created my me
from Registration import RegisterWin, Register_time, RegTotalMonthWins, regEachDay, regSpecifDay, regEachDay, regDayTime
from api_giphy import getGif
from api_google import translateMsg


import requests
import openai
from io import BytesIO
from PIL import Image
from unidecode import unidecode
import base64

import logging
import functools
import typing
# suppress the warning
warnings.filterwarnings("ignore", message="The parameter 'token_pattern' will not be used since 'tokenizer' is not None'")


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        wrapped = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, wrapped)
    return wrapper

@to_thread
def  generate_image(V4,msgg, message, input_en, size, w, h, neg_prompt, upscale_x, upscaler, styles, checkpoint,Sampling_steps, cfg, denoising):
    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    #wait_msg =    await message.channel.send(msgg) 
    # wait_gif = await message.channel.send("https://media.giphy.com/media/6JoZLF3PEf71rlC6wG/giphy.gif") 
    #wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMThjNGQ2MjY2NWNlZjQ2N2UzNTEzMTg1OTdkYTc3MzYxNmU3MDBlMiZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/oifW0KmfxAUscpFCJD/giphy.gif") 
    #wait_gif =   await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMzVkOWI2N2I0YmQyYjEyNTQ0NDM0MjY4OWFkYjI0YWE0MTE1Yzg4NyZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/rEpJGWtwjQpZg8Wvip/giphy.gif")             
    if V4:

        payload = {
            "prompt": input_en,
            "batch_size": size,
            "width": w,
            "height": h,
            "steps": Sampling_steps,
            "sampler_index": "UniPC",
            "cfg_scale": cfg,
            "negative_prompt": neg_prompt,
            "enable_hr": True,
            "denoising_strength": denoising,
            "hr_scale": upscale_x,
            "hr_upscaler": upscaler,
            "styles": styles,
        }
    else:
        payload = {
            "prompt": input_en,
            "batch_size": size,
            "width": w,
            "height": h,
            "steps": Sampling_steps,
            "sampler_index": "UniPC",
            "cfg_scale": cfg,
            "negative_prompt": neg_prompt,
            "enable_hr": True,
            "denoising_strength": denoising,
            "hr_scale": upscale_x,
            "hr_upscaler": upscaler,
            "styles": styles,
        }
    ############## change model##############
    override_settings = {}
    override_settings["sd_model_checkpoint"] = checkpoint

    override_payload = {
                    "override_settings": override_settings
                }
    payload.update(override_payload)   
        ############## change model##############
    response = requests.post(url, json=payload)
    # Download the image using requests module
    images = response.json()['images'][:4] # Get the first 4 images

    # Create a list of all the image files
    files = []
    for i, image_content in enumerate(images):
        # Generate filename with timestamp and image number
        filename = f"generated_image_{i+1}_{int(time.time())}.png"

        # Save the image to "generated" directory
        with open(f"generated2/{filename}", "wb") as f:
            f.write(base64.b64decode(image_content))

        # Add the image file to the list
        file = discord.File(f"generated2/{filename}")
        files.append(file)
    #embed = discord.Embed()
    #embed.set_image(url=f"attachment://{filename}")
    
    return files
    #wait_msg.delete()
    #wait_gif.delete()
    #new_message =   message.channel.send(files=files)

@to_thread
def enchPrompt(prompt):
    prompt_ench = prompt
    try:
        responsee = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages = [
        {"role": "user", "content": f' want you to help me make requests (prompts) for the Stable Diffusion neural network.\n\nStable diffusion is a text-based image generation model that can create diverse and high-quality images based on your requests. In order to get the best results from Stable diffusion, you need to follow some guidelines when composing prompts.\n\nHere are some tips for writing prompts for Stable diffusion1:\n\n1) Be as specific as possible in your requests. Stable diffusion handles concrete prompts better than abstract or ambiguous ones. For example, instead of “portrait of a woman” it is better to write “portrait of a woman with brown eyes and red hair in Renaissance style”.\n2) Specify specific art styles or materials. If you want to get an image in a certain style or with a certain texture, then specify this in your request. For example, instead of “landscape” it is better to write “watercolor landscape with mountains and lake".\n3) Specify specific artists for reference. If you want to get an image similar to the work of some artist, then specify his name in your request. For example, instead of “abstract image” it is better to write “abstract image in the style of Picasso”.\n4) Weigh your keywords. You can use token:1.3 to specify the weight of keywords in your query. The greater the weight of the keyword, the more it will affect the result. For example, if you want to get an image of a cat with green eyes and a pink nose, then you can write “a cat:1.5, green eyes:1.3,pink nose:1”. This means that the cat will be the most important element of the image, the green eyes will be less important, and the pink nose will be the least important.\nAnother way to adjust the strength of a keyword is to use () and []. (keyword) increases the strength of the keyword by 1.1 times and is equivalent to (keyword:1.1). [keyword] reduces the strength of the keyword by 0.9 times and corresponds to (keyword:0.9).\n\nYou can use several of them, as in algebra... The effect is multiplicative.\n\n(keyword): 1.1\n((keyword)): 1.21\n(((keyword))): 1.33\n\n\nSimilarly, the effects of using multiple [] are as follows\n\n[keyword]: 0.9\n[[keyword]]: 0.81\n[[[keyword]]]: 0.73\n\nI will also give some examples of good prompts for this neural network so that you can study them and focus on them.\n\n\nExamples:\n\na cute kitten made out of metal, (cyborg:1.1), ([tail | detailed wire]:1.3), (intricate details), hdr, (intricate details, hyperdetailed:1.2), cinematic shot, vignette, centered\n\nmedical mask, victorian era, cinematography, intricately detailed, crafted, meticulous, magnificent, maximum details, extremely hyper aesthetic\n\na girl, wearing a tie, cupcake in her hands, school, indoors, (soothing tones:1.25), (hdr:1.25), (artstation:1.2), dramatic, (intricate details:1.14), (hyperrealistic 3d render:1.16), (filmic:0.55), (rutkowski:1.1), (faded:1.3)\n\nJane Eyre with headphones, natural skin texture, 24mm, 4k textures, soft cinematic light, adobe lightroom, photolab, hdr, intricate, elegant, highly detailed, sharp focus, ((((cinematic look)))), soothing tones, insane details, intricate details, hyperdetailed, low contrast, soft cinematic light, dim colors, exposure blend, hdr, faded\n\na portrait of a laughing, toxic, muscle, god, elder, (hdr:1.28), bald, hyperdetailed, cinematic, warm lights, intricate details, hyperrealistic, dark radial background, (muted colors:1.38), (neutral colors:1.2)\n\nMy query may be in other languages. In that case, translate it into English. Your answer is exclusively in English (IMPORTANT!!!), since the model only understands it.\nYou should compose a new prompt, observing the format given in the examples.\nDont add your comments, but answer right away.\nMy first request is - "{prompt_ench}".' }
        ],
        max_tokens=2500,
        n=1,
        stop=None,
        temperature=0.6,
        )
        prompt_ench = responsee.choices[0].message.content
        prompt_ench = prompt_ench.strip().replace('"', '')
        prompt_ench = prompt_ench.strip().replace("'", "")

        #ench_succss = True
        ######### testing usage of |
        # prompt_ench = prompt_ench.replace(".", "|").replace(",", "|")
        ######### testing usage of |
    except Exception as e:
        prompt_ench = "error"
        print("An error occurred:", str(e))
    return prompt_ench

def getMostActiveTime():

    filename = "laiks.json"
    if os.path.isfile(filename):
       with open('laiks.json', 'r') as f:
           time_statistics = json.load(f)
    else: time_statistics = {}

    max_value = max(time_statistics.values())
    max_time = [k for k, v in time_statistics.items() if v == max_value][0]

    highest = f"• *Most active time in this month has been **{max_time}** with **{max_value}** wins.*"

    return highest



# Tika izmanttos pirmajā start up reizē, tagad izmanto, ja vajag iet cauri ziņām ar specifisku mērķi
async def InitialBoot(client, SCREENSHOT_CHANNEL_ID, SCREENSHOT_EXTENSIONS):

    uzvaras  = 0
    channel  = client.get_channel(1101461174907830312)
    messages = await channel.history(limit=None).flatten() # Retrieve all messages in the channel
    amount   = 0
    user_message_counts = {}  # Dictionary to store user message counts
    
# Iterate through the messages and check if they were sent this month
    for message in messages:
        if message.created_at.day > 29:
            if message.content.lower().startswith("ay echo".lower()) or message.content.lower().startswith("ay echoai".lower()) or message.content.lower().startswith("ey echo".lower()) or message.content.lower().startswith("ey echoai".lower()) or message.content.lower().startswith("ay generate".lower()) or message.content.lower().startswith("ey generate".lower()) or message.content.lower().startswith("ay ģenerē".lower()) or message.content.lower().startswith("ey ģenerē".lower()):
                author_id = f"{message.author.name}#{message.author.discriminator}"
                user_message_counts[author_id] = user_message_counts.get(author_id, 0) + 1

    # Save the message counts to a JSON file
    with open("echo_count_lastdays.json", "w") as file:
        json.dump(user_message_counts, file)

    print('messages counted')
    print(amount)

    #await RegTotalMonthWins(uzvaras,month)

    annoucment = "@everyone Whats up RESNIE!\nStarting from today I'm taking over from Daisy this role because she is old as earth and it is long overdue for her retirement.\n"\
                 "For now, I have these command:\n*/resnums* - view your current progress. **THIS WILL BE ACCURATE AFTER MANUALLY  ADDING WINS THAT DAISY COUNTED AT THE START OF THE MONTH**\n"\
                                                 "*/info* - refresh your memory on minimal requirements for win to be valid.\n"\
                 "Feel free to reach out to me via **Direct message** if you spot something wrong or just want to suggest some cool feature you want to be added, and I will pass it to my creator.\n"\
                 "With me becoming Resns enough to fill the role, you will see some before unseen statistics about the month progress. Two of them right now are:\n"
    #fact = f"• *So far there are **{uzvaras}** wins this month.*"
    #fact2 = getMostActiveTime()
   # await message.channel.send(annoucment)
   # await message.channel.send("@everyone test")
    #await message.channel.send(fact)
    #await message.channel.send(fact2)

# Atributes for listening and registering new message-response pairs 
LAST_EXECUTION_TIME = 0  #@#
msgCount = 0   
msg1 = "" 
msg2 = "" 
addition       = [] 
question_list  = []
person_message = []
botMsg = False 
execute_code = True
with open('CB_pairs2addition.json', 'r') as file: #@#
    addition = json.load(file) #@#

def main():

   with open("CB_person_message.json", 'r', encoding='utf-8') as file: #@#
    person_message = json.load(file) #@#

   with open("CB_question_list.json", 'r', encoding='utf-8') as file: #@#
    question_list = json.load(file) #@#

   with open("CB_triger_ko_dari.json", 'r', encoding='utf-8') as file: #@#
    triger_KoDari = json.load(file) #@#
    
   with open("CB_triger_ka_iet.json", 'r', encoding='utf-8') as file: #@#
    triger_KaIet = json.load(file) #@#

   with open("CB_conv_cooldown.json", 'r', encoding='utf-8') as file: 
    conv_cooldown = json.load(file)

   #with open("CB_Tu_message.json", 'r', encoding='utf-8') as file: #@#
  #  Tu_messages = json.load(file) #@# CB_conv_cooldown

   givenResponses = []
####################### new ######################## GPT STUFF (down)

   def getUserName(nick):
        nickname = None
        if nick == 'Jaanisjc':
            nickname = 'Jānis'
        elif nick == 'DAISY':
            nickname = 'Daisy'
        elif nick == 'FatAndBeautiful':
            nickname = 'Valters'
        elif nick == 'MissGoldfish':
            nickname = 'Paula'
        elif nick == 'Theeight':
            nickname = 'Elvis'
        elif nick == '𝙾𝚜𝚖𝚊𝚗𝚜':
            nickname = 'Oskars'
        elif nick == 'LadyMorgie':
            nickname = 'Madara'
        elif nick == 'notacop':
            nickname = 'notacop'
        elif nick == 'AGRIS':
            nickname = 'Agris'
        elif nick == 'Ifchix':
            nickname = 'Ivars'
        elif nick == 'MitraisBandīts':
            nickname = 'Kapars'
        elif nick == 'swich125':
            nickname = 'swich'
        elif nick == 'Unicorn':
            nickname = 'Vectēvs'
        elif nick == 'Megga':
            nickname = 'Megana'
        elif nick == 'ābolmaizīte':
            nickname = 'ābolmaizīte'
        elif nick == 'b1bop':
            nickname = 'Bibops'
        elif nick == 'Evol':
            nickname = 'Evol'
        elif nick == 'an.XIETY':                                     
            nickname = 'anXIETY'
        elif nick == 'gesmen':
            nickname = 'gesmens'
        elif nick == 'Kampys':
            nickname = 'Kampys'
        elif nick == 'Yogi':
            nickname = 'Yogi'
        elif nick == 'kampulis':
            nickname = 'Speķmaizīte' 
        elif nick == 'Eternal Wanderer':
            nickname = 'Mērčmeistars'
        elif nick == 'kachis':
            nickname = 'kachis'
        elif nick == 'E.N.Z.I.O':
            nickname = 'Enzio'
        elif nick == 'eidukS':
            nickname = 'Mārtiņš'
        elif nick == 'Atty':
            nickname = 'Atty' 
        elif nick == 'TomTryptamine':
            nickname = 'Tom'
        elif nick == 'Mammu mīlētājs desmens':
            nickname = 'Desmens'
        elif nick == "ᵢₑᵥᵢₙₐ":
            nickname  = "Ieva"
        if nickname is not None:

            return nickname
        else:
            return None

   async def echoo(idea, neg, model, stylee, portrait, landscape):
            #keyword = message_modif.split()[0]
            # Get user input from message
           # if execute_code:
                w = 512
                h = 512
                size = 3
                port = False
                land = False
                V4 = False
                upscale_x = 2
                neg_prompt = neg
                #stili = stylee.strip()
                styles = stylee
                universal_neg = "easynegative, ng_deepnegative_v1_75t, badhandv4,  ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face"
                checkpoint = "deliberate_v2.safetensors"
                if neg_prompt == "uni" or neg_prompt == "Uni":
                    neg_prompt = universal_neg
                prompt = idea
                #words = message.content.split()
                if portrait:
                    port = True
                    h = 640
                    w = 384
                    # Remove the second word from the list of words
                    #words.pop(2)
                    # Join the remaining words back into a string
                    #new_message = " ".join(words)
                    # Update the message content with the new string
                    #prompt = new_message
                elif landscape:
                    land = True
                    w = 640
                    h = 384
                    # Remove the second word from the list of words
                    #words.pop(2)
                    # Join the remaining words back into a string
                    #new_message = " ".join(words)
                    # Update the message content with the new string
                    #prompt = new_message
                ################ look for negative prompt
                content = prompt



                # if "--no" in content:
                #     no_index = content.find("--no")
                #     neg_prompt = content[no_index + len("--no"):].strip()
                #     original_message = content[:no_index].strip()
                    # modify the message content by removing the "--no" and the rest of the message
                #     if neg_prompt == "uni" or neg_prompt == "Uni":
                #         neg_prompt = universal_neg
                #     prompt = original_message


                if model == "v4":
                    checkpoint = "openjourney-v4.ckpt"
                    V4 = True
                    size = 3
                    h = 512
                    w = 512
                    if land:
                        w = 640
                        h = 384
                    if port:
                        w = 384
                        h = 640

                elif model == "deli":
                    checkpoint = "deliberate_v2.safetensors"
                    #prompt = prompt.replace("--deli", "")
                    V4 = True
                    size = 3
                    h = 512
                    w = 512
                    if land:
                        w = 640
                        h = 384
                    if port:
                        w = 384
                        h = 640

                elif model == "fantasy":
                    checkpoint = "aZovyaRPGArtistTools_sd21768V1.safetensors"
                    #prompt = prompt.replace("--fantasy", "")
                    V4 = False
                    size = 2
                    h = 768
                    w = 768
                    upscale_x = 1.334
                    if land:
                        w = 960
                        h = 576
                    if port:
                        w = 576
                        h = 960

                elif model == "real":
                    checkpoint = "realisticVisionV20_v20.ckpt"
                    #prompt = prompt.replace("--real", "")
                    V4 = True
                    size = 3
                    h = 512
                    w = 512
                    if land:
                        w = 640
                        h = 384
                    if port:
                        w = 384
                        h = 640

                elif model == "dream":
                    checkpoint = "dreamshaper_5BakedVae.safetensors"
                    #prompt = prompt.replace("--real", "")
                    V4 = True
                    size = 3
                    h = 512
                    w = 512
                    if land:
                        w = 640
                        h = 384
                    if port:
                        w = 384
                        h = 640

                elif model == "anime":
                    checkpoint = "revAnimated_v122.safetensors"
                    upscaler = "R-ESRGAN 4x+ Anime6B"
                    V4 = True
                    size = 3
                    h = 512
                    w = 512
                    if land:
                        w = 640
                        h = 384
                    if port:
                        w = 384
                        h = 640
                    if "dragon" in prompt:
                        prompt = "<lora:Dragons v1:0.7> , " + prompt
                        neg_prompt = "(EasyNegative:1.2), (worst quality:1.2), (low quality:1.2), (lowres:1.1), (monochrome:1.1), (greyscale), multiple views, comic, sketch, horse ears, (((horse tail))), pointy ears, (((bad anatomy))), (((deformed))), (((disfigured))), watermark, multiple_views, mutation hands, mutation fingers, extra fingers, missing fingers, watermark"

                    if "steampunk" in prompt:
                        prompt = "<lora:steampunkai:1> steampunkai , " + prompt

                    if "dark" in prompt or "night" in prompt or "dusk" in prompt:
                        prompt = "<lora:LowRA:0.5> , " + prompt

                    if "fairytale" in prompt or "fairy tale" in prompt or "dusk" in prompt:   
                        prompt = " fairytaleai, <lora:FairyTaleAI:0.5> , " + prompt

                    if "apocalyptic" in prompt or "post apocalyptic" in prompt or "postapocalyptic" in prompt:
                        prompt = " postapoAI <lora:postapocalypseAI:0.5> , " + prompt
                    if "landscape" in prompt or "sunset" in prompt or "mountains" in prompt:
                        prompt = "<lora:cheeseDaddys_35:1>  , " + prompt

                    if "harold" in prompt or "Harold" in prompt:
                        prompt = "<lora:Hide_da_painV2:1>  , " + prompt
                        neg_prompt = "cut off, bad, boring background, simple background, More_than_two_legs, more_than_two_arms, , (blender model), (fat), ((((ugly)))), (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), ((extra arms)), ((extra legs)), mutated hands, (fused fingers), (too many fingers), ((long neck)), lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artists name"

                    prompt = prompt + ", <lora:add_detail:1>, <lora:epi_noiseoffset2:0.7>"
                #prompt = content.split("--")[0]
                ################ look for negative prompt
               # msgg = "Use **--style** to specify what styles(can use multiple **style1***,***style2**...) of image you want(view available  using */styles* ).\nUse only ***one*** of these:\n- Use  **--deli** and your imagination(use this if you have long promt or do not know which to use);\n- use **--dream** if you feel like dreaming;\n- use **--real** to have photorealistic result;\n- use **--fantasy** if you are writing about fantasy thing, creatures, characters;\n- use ***--v4*** for picture to have Midjourney 4 style.\n ***It takes longer than before because details and quality are better.*** *(30-40sec)*\n*Using new engine, uncensored, untamed. generating...*\n-Use ***landscape*** or ***portrait*** after ***generate*** to change image aspect ratio.\n-At **the end** add '***--no*** *and some text*' to specify things you **do not** want to see in picture.\n-Use ***--no uni*** To generally make everything more realistic."
               # if h == 960 or h == 640:
               #     msgg = "Use **--style** to specify what styles(can use multiple **style1***,***style2**...) of image you want(view available  using */styles* ).\nUse only one of these:\n- Use  **--deli** and your imagination(use this if you have long promt or do not know which to use);\n- use **--dream** if you feel like dreaming;\n- use **--real** to have photorealistic result;\n- use **--fantasy** if you are writing about fantasy thing, creatures, characters;\n- use ***--v4*** for picture to have Midjourney 4 style.\n ***It takes longer than before because details and quality are better.*** *(30-40sec)*\n*Using new engine, uncensored, untamed. generating **portrait**...*\n-Use ***landscape*** or ***portrait*** after ***generate*** to change image aspect ratio.\n- At **the end** add '***--no*** *and some text*' to specify things you **do not** want to see in picture.\n-Use ***--no uni*** To generally make everything more realistic."
              #  elif w == 960 or w == 640:
               #     msgg = "Use **--style** to specify what styles(can use multiple **style1***,***style2**...) of image you want(view available  using */styles* ).\nUse only one of these:\n- Use  **--deli** and your imagination(use this if you have long promt or do not know which to use);\n- use **--dream** if you feel like dreaming;\n- use **--real** to have photorealistic result;\n- use **--fantasy** if you are writing about fantasy thing, creatures, characters;\n- use ***--v4*** for picture to have Midjourney 4 style.\n ***It takes longer than before because details and quality are better.*** *(30-40sec)*\n*Using new engine, uncensored, untamed. generating **landscape**...*\n-Use ***landscape*** or ***portrait*** after ***generate*** to change image aspect ratio.\n-At **the end** add '***--no*** *and some text*' to specify things you **do not** want to see in picture.\n-Use ***--no uni*** To generally make everything more realistic."

                #wait_msg = await message.channel.send(msgg) 
                # wait_gif = await message.channel.send("https://media.giphy.com/media/6JoZLF3PEf71rlC6wG/giphy.gif") 
                #wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMThjNGQ2MjY2NWNlZjQ2N2UzNTEzMTg1OTdkYTc3MzYxNmU3MDBlMiZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/oifW0KmfxAUscpFCJD/giphy.gif") 
                #wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMzVkOWI2N2I0YmQyYjEyNTQ0NDM0MjY4OWFkYjI0YWE0MTE1Yzg4NyZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/rEpJGWtwjQpZg8Wvip/giphy.gif") 
                user_input = prompt
                input_en = translateMsg(user_input)
                #await message.channel.trigger_typing()
                
                url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
                #await message.channel.trigger_typing()


                if V4:

                    payload = {
                        "prompt": input_en,
                        "batch_size": size,
                        "width": w,
                        "height": h,
                        "steps": 20,
                        "sampler_index": "UniPC",
                        "cfg_scale": 10,
                        "negative_prompt": neg_prompt,
                        "enable_hr": True,
                        "denoising_strength": 0.5,
                        "hr_scale": upscale_x,
                        "hr_upscaler": "4x-UltraSharp",
                        "styles": styles,
                    }
                else:
                    payload = {
                        "prompt": input_en,
                        "batch_size": size,
                        "width": w,
                        "height": h,
                        "steps": 20,
                        "sampler_index": "UniPC",
                        "cfg_scale": 10,
                        "negative_prompt": neg_prompt,
                        "enable_hr": True,
                        "denoising_strength": 0.5,
                        "hr_scale": upscale_x,
                        "hr_upscaler": "4x-UltraSharp",
                        "styles": styles,
                    }
                ############## change model##############
                override_settings = {}
                override_settings["sd_model_checkpoint"] = checkpoint

                override_payload = {
                                "override_settings": override_settings
                            }
                payload.update(override_payload)   
                    ############## change model##############
                response = requests.post(url, json=payload)
                # Download the image using requests module
                images = response.json()['images'][:4] # Get the first 4 images

                # Create a list of all the image files
                files = []
                for i, image_content in enumerate(images):
                    # Generate filename with timestamp and image number
                    filename = f"generated_image_{i+1}_{int(time.time())}.png"

                    # Save the image to "generated" directory
                    with open(f"generated2/{filename}", "wb") as f:
                        f.write(base64.b64decode(image_content))

                    # Add the image file to the list
                    file = discord.File(f"generated2/{filename}")
                    files.append(file)
                #embed = discord.Embed()
                #embed.set_image(url=f"attachment://{filename}")
                #await wait_msg.delete()
                #await wait_gif.delete()
                return files
                #new_message = await message.channel.send(files=files)

           # else:
           #     await message.channel.send('***generate** is disabled. Use **ģenerē** instead.*')

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

####################### new ######################## GPT  STUFF (up)

    # Saglabāziņas, ko lietotāji raksta
   def addPair( msg1, msg2): 
        global addition
        addition.append([msg1,[msg2]])
        with open('CB_pairs2addition.json', 'w') as file:
            json.dump(addition,file)
        return addition

    # Saglabāziņas starp lietotāju un bobotu
   def saveResponse(list):
         with open('CB_givenResponses.json', 'w') as file:
          json.dump(list, file)
####### Apstrādā ziņas pirms pievienošans pārī
   lv_stopwords = []
   with open('lv_stopwords.json', 'r', encoding="utf-8") as f:
       lv_stopwords = json.load(f)  

    # Apstrādāziņu, pirms pievieno message-response pāriem
   def preprocess_message(msg):
        # Remove parentheses and their contents using regex
        pattern_without_parentheses = re.sub(r'\([^)]*\)', ' ', msg)
    
        # Remove leading/trailing whitespace
        pattern_without_parentheses = pattern_without_parentheses.strip()
    
        # Convert to lowercase and remove stop words
        words = word_tokenize(pattern_without_parentheses.lower())
        pattern = [word for word in words if word not in lv_stopwords]
    
        # Return the preprocessed message as a string
        return "(?i).*" + re.escape(' '.join(pattern)) + ".*"
#######

   post = True

   load_dotenv()
   intents = discord.Intents.default()
   intents.message_content = True
   intents.guilds          = True
   intents.members         = True
   intents.messages        = True
   intents.presences       = True
   client = discord.Bot(intents=intents, command_prefix='!')
   

   #Chatbot initialization
   pairs, response_list, lv_reflections = Chatbot()
   chatbot = Chat(pairs, lv_reflections)
   random.seed(time.time())

   SCREENSHOT_CHANNEL_ID = int(os.getenv("SCREENSHOT_CHANNEL_ID"))
   gpt_key               = os.getenv("GPT")
   token                 = os.getenv('TOKEN')
   openai.api_key = gpt_key

   SCREENSHOT_EXTENSIONS = [".png", ".jpg", ".jpeg"]


   game_wins =          {}


   phrases_received =   {}
   phrases_reminder =   {}
   phrases_awayScore =  {}
   phrases_awayReason = {}
   phrases_bussy =      {}
   scanned_resns =      {}

   time_statistics =    {}

   gifs_lonely = []

# Nosūtīt random ziņu ik pēc noteikta laika #general kanālā 
###################### INTERACT IN CHAT OVER TIME ########################

    # Pats aizsūta kādu ziņu
   async def post_random_message():
    channel = client.get_channel(1030490392510079063) 
    random.seed(time.time())
    response = random.choice(person_message)
    await channel.trigger_typing()
    await asyncio.sleep(2)
    await channel.send(response)
    try:
        next_message = await client.wait_for('message', timeout=120.0, check=lambda m: m.channel == channel and m.author != client.user and not m.reference)
        response = get_similar_response(next_message.content, pairs, threshold=0.3)
        if not response:
            random.seed(time.time())
            response = random.choice(response_list)
        await channel.trigger_typing()
        await asyncio.sleep(2)
        await next_message.reply(response)
    except asyncio.TimeoutError:
        print('No response from user')

    # Pats atbild uz pēdējo ziņu
   async def post_reply_message():
    channel = client.get_channel(1030490392510079063) 
    await channel.trigger_typing()
    recent_message = await channel.history().get()
    message = recent_message.content
    if recent_message.author != client.user:
        response = get_similar_response(message, pairs, threshold=0.3)
        if not response:
            random.seed(time.time())
            response = random.choice(response_list)
        await recent_message.reply(response)
        #Uzgaida atbildi no lietotaja
################ NEW ##########################
        try:
            next_message = await client.wait_for('message', timeout=120.0, check=lambda m: m.author == recent_message.author and not m.content.startswith('!') and not m.reference)
            response = get_similar_response(next_message.content, pairs, threshold=0.3)
            if not response:
                random.seed(time.time())
                response = random.choice(response_list)
            await channel.trigger_typing()
            await asyncio.sleep(2)
            await next_message.reply(response)
        except asyncio.TimeoutError:
            print('No response from user')
################ NEW ##########################
    else:
        print('I wont answer to my own message!')

    # Pats ietago kādu un uzdod jautājumu
   async def post_mention_message():
    channel = client.get_channel(1030490392510079063)  # general channel
    # Get the two specific roles
    role1 = channel.guild.get_role(1030581546966597742)  # Replace with the ID of OG Users 
    role2 = channel.guild.get_role(1089589791466721312)  # Replace with the ID of Members 
    # Specify the ID of the user to exclude
    user_to_exclude_id = 154585475582132224 #Mauris
    # Get a list of all online members who have one of the two roles
    members = [member for member in channel.guild.members if not member.bot and (role1 in member.roles or role2 in member.roles) and member.status is not discord.Status.offline and member.id != user_to_exclude_id]
    if members:
        random.seed(time.time())
        # Choose a random member to mention
        random_member = random.choice(members)
        # Choose a random response
        random_response = random.choice(question_list)
        # Mention the random member and add the random response
        await channel.trigger_typing()
        await asyncio.sleep(2)
        await channel.send(f"{random_member.mention} {random_response}")
        try:
            # Wait for a response from the mentioned user within 60 seconds
            next_message = await client.wait_for('message', timeout=120.0, check=lambda m: m.author == random_member and m.channel == channel and not m.reference)           
            response = get_similar_response(next_message.content, pairs, threshold=0.3)
            if not response:
                random.seed(time.time())
                response = random.choice(response_list)
            await channel.trigger_typing()
            await asyncio.sleep(2)
            await next_message.reply(response)
        except asyncio.TimeoutError:
            print('No response from user')
    # Runā pats grafiks
   async def schedule_messages():
        while True:


                            


            now = datetime.now()
            post_time = now + timedelta(hours=1.5)
            # Print the scheduled message post time
            print(f"\nNext Resnas mammas response message will be posted at: {post_time.strftime('%H:%M:%S')}\n") 
            await asyncio.sleep(7200) 
            await post_reply_message()

            now = datetime.now()
            # Calculate the time when the next message will be posted
            post_time = now + timedelta(hours=1.5)
            # Print the scheduled message post time
            print(f"\nNext Resnas mammas random message will be posted at: {post_time.strftime('%H:%M:%S')}\n")
            await asyncio.sleep(7200)
            await post_random_message()


                # Get the current time
            now = datetime.now()
            post_time = now + timedelta(hours=1.5)
            # Print the scheduled message post time
            print(f"\nNext Resnas mammas random mention message will be posted at: {post_time.strftime('%H:%M:%S')}\n")
            await asyncio.sleep(7200)  # Sleep for 3 hour
            await post_mention_message()


###################### INTERACT IN CHAT OVER TIME ########################^


   prefix1 = "x"
   prefix2 = "+"

   PRIVATA_ZINA = 'DM.txt'

   with open('gifs_Lonely.json', 'r') as f:
       gifs_lonely = json.load(f)

   filename = "resnums.json"
   if os.path.isfile(filename):
       with open('resnums.json', 'r') as f:
           game_wins = json.load(f)    
           
   with open('CB_givenResponses.json', 'r') as f: #@#
       givenResponses = json.load(f)

   with open('phrases_received.json', 'r') as f:
       phrases_received = json.load(f)
   with open('phrases_reminder.json', 'r') as f:
       phrases_reminder = json.load(f)
   with open('phrases_awayScore.json', 'r') as f:
       phrases_awayScore = json.load(f)
   with open('phrases_bussy.json', 'r') as f:
       phrases_bussy = json.load(f)
   with open('scanned_resns.json', 'r') as f:
       scanned_resns = json.load(f)



   filename = "laiks.json"
   if os.path.isfile(filename):
       with open('laiks.json', 'r') as f:
           time_statistics = json.load(f)
   else: time_statistics = {}

   with open('phrases_awayReason.json', 'r') as f:
       phrases_awayReason = json.load(f)   


   
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

  ################### generate amount in month ###################
 #  async def getUser(idd, client):
  #      user = await client.fetch_user(idd)
   #     return user
  ################### generate amount in month ###################

   post = True
   @client.event
   async def on_ready():  
    PreviousWins = 0
    print(f'{client.user} is back online!')
    print('Connected to the following guilds:')
    with open('left_guilds.txt', 'a', encoding="utf-8") as f:
        for guild in client.guilds:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f'\n{timestamp}: {guild.name} (id: {guild.id})'
            print(message)
            f.write(message)
        ################### generate amount in month ###################
    #channell = client.get_channel(1101461174907830312)
    #channell = 1101461174907830312
   # user1 = await getUser(240554122510598146, client)
   # user2 = await getUser(197621133007126528, client)
  #  user3 = await getUser(532642118326419476, client)
  #  user4 = await getUser(122797491044220928, client)
  #  user5 = await getUser(368854505049161740, client)
  #  user6 = await getUser(391668973315424277, client)
  #  user7 = await getUser(317030319624814592, client)
  #  user8 = await getUser(190926234878738433, client)
 #   user9 = await getUser(178207887913517056, client)
  #  user10 = await getUser(182533330581848065, client)
  #  user11 = await getUser(880446227047665714, client)
 #   user12 = await getUser(963337377085009931, client)
 #   user13 = await getUser(504685788781477899, client)
 #   user14 = await getUser(214068457149431809, client)
  #  user15 = await getUser(521402158239842319, client)
  #  user16 = await getUser(192408414792581120, client)


  #  await channell.send(f"In May all of you have generated **9045** images! Scoreboard:\n{user1.mention} 1550 requests(3978 images)\n\
#{user2.mention} 634 requests(1660 images)\n\
#{user3.mention} 526 requests(1204 images)\n\
#{user4.mention} 434 requests(1290 images)\n\
#{user5.mention} 153 requests(459 images)\n\
#{user6.mention} 146 requests(360 images)\n\
#{user7.mention} 79 requests(213 images)\n\
#{user8.mention} 70 requests(188 images)\n\
#{user9.mention} 67 requests(137 images)\n\
#{user10.mention} 45 requests(123 images)\n\
#{user11.mention} 33 requests(33 images)\n\
#{user12.mention} 29 requests(87 images)\n\
#{user13.mention} 19 requests(19 images)\n\
#{user14.mention} 16 requests(48 images)\n\
#{user15.mention} 12 requests(36 images)\n\
#{user16.mention} 10 requests(30 images)")
     ################### generate amount in month ###################

    # Izveido statusuw
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over your shoulder"))
    # Izveido grafiku, kad sūta ziņas pats
    asyncio.create_task(schedule_messages()) #@#
    channel = client.get_channel(SCREENSHOT_CHANNEL_ID)
    #xxl = await channel.fetch_message(1089420313026113538)
    #await xxl.add_reaction('🔥')
    CHECKMARK_EMOJI = "✅"


    # Iet cauri nelasītajām ziņām
    async for message in channel.history(limit=None, oldest_first=False):
        # Pārbauda vai ziņa atzīmēta ar ķeksīti
        if any(reaction.emoji == CHECKMARK_EMOJI for reaction in message.reactions):
            print("Went through all messages up until green checkmark.")
            break
        
        #Pārbauda vai pievienots attēls
        if any(attachment.filename.lower().endswith(tuple(SCREENSHOT_EXTENSIONS)) for attachment in message.attachments):
           multip = 0
           recap = True
           
               
            #Pārbauda vai pievienots reizinātājs
           if message.content.startswith(prefix1) or message.content.startswith(prefix2) :

                num_string = message.content[len(prefix1):].strip()

                if num_string.isnumeric():

                    multip = int(num_string)
                    PreviousWins = PreviousWins + multip
                for x in range(multip):
                    await Register_time(f"{message.created_at.hour+3}")
                    #Reģistrē uzvaru, ja iespējams, ja nē, saglabā attēlu manuālai ievadei
                    await RegTotalMonthWins(1,message.created_at.month)
                    sendConfirm = False # Nesūtīt paziņojumu čatā
                    isStreak = True 
                    if x + 1 == multip: sendConfirm = True 
                    await RegisterWin(game_wins, message, recap, sendConfirm, isStreak)           
           else:

               await Register_time(f"{message.created_at.hour+3}")
               await RegTotalMonthWins(1,message.created_at.month)
               sendConfirm = True # Nosūtīt paziņojumu čatā
               isStreak = False  
               await RegisterWin(game_wins, message, recap, sendConfirm, isStreak) 
               PreviousWins = PreviousWins + 1


    PreviousWins_str = str(PreviousWins)
    phrase_rec = phrases_awayScore[PreviousWins_str]    
    random.seed(time.time())
    phrases_reason = random.choice(list(phrases_awayReason.values()))
    userr_id = "190926234878738433"
    annoucment = f"{timeOfDay()}, {phrases_reason}.\nDuring this time, you have scored {PreviousWins} wins. {phrase_rec}."
    update = "New month new Resnums. In may total win amount was **388**. (April: 597, March: 608, February: 427, January 287.) Lower you can view May statistics."
    #with open('DayTime.xlsx', 'rb') as f1, open('SpecifDay.xlsx', 'rb') as f2, open('EachDay.xlsx', 'rb') as f3, open('night.png', 'rb') as f4, open('aft.png', 'rb') as f5:
    #    file1 = discord.File(f1, filename='DayTime.xlsx')
    #    file2 = discord.File(f2, filename='SpecifDay.xlsx')
    #    file3 = discord.File(f3, filename='EachDay.xlsx')
    #    file4 = discord.File(f4, filename='night.png')
     #   file5 = discord.File(f5, filename='aft.png')
        #embed = discord.Embed(title='April statistics', description='Apskati savu statistiku:')
        #embed.set_image(url='attachment://night.png')
        #embed.set_image(url='attachment://aft.png')
        #embed.add_field(name='Excel file', value='See attachment', inline=False)
    #update = f"Last month:\n• Tuesday proved to be a particularly successful day for <@{userr_id}>, who won the highest number of wins compared to any other player on any day of the week. **53** wins, that is **30%** of Tuedays total. "
    #await InitialBoot(client, SCREENSHOT_CHANNEL_ID, SCREENSHOT_EXTENSIONS)
    #await message.channel.send(annoucment)
   # await message.channel.send(update)   
   # await message.channel.send(files=[file5, file4, file1, file2, file3])  



   #@client.command(name='echo', description='Image generation help.') #@#
  #async def echo(ctx):
   #    text = "Use **-styles** to specify what style of image you want(view available  using */styles* ).\nUse only ***one*** of these:\n- Use  **--deli** and your imagination(use this if you have long promt or do not know which to use);\n- use **--dream** if you feel like dreaming;\n- use **--real** to have photorealistic result;\n- use **--fantasy** if you are writing about fantasy thing, creatures, characters;\n- use ***--v4*** for picture to have Midjourney 4 style.\n\n- Use ***landscape*** or ***portrait*** after ***generate*** to change image aspect ratio.\n- At **the end** add '***--no*** *and some text*' to specify things you **do not** want to see in picture.\n- Use ***--no uni*** To generally make everything more realistic"
   #    await ctx.send(text)

   @client.command(name='help', description='View full list of my abilities.') #@#
   async def help(ctx):
       user = ctx.author
       help =  '*/info*  \n- Get info about winning requirements and possible things to gain.\n\n'\
               '*/resnums* \n- View your current win progress in a month.\n\n'\
               '*ay parādi **something to show***\n- I will show you what you request if form gif. You can use Latvian and English.\n\n'\
               '*ay pajautā **@SomeUser*** \n- I will ask a random question to user.\n\n'\
               '*ay pastāsti joku* \n- I will post a random joke/meme/video/picture.\n\n'\
               '*ay atdarini manu bildi* \n- I will take your profile picture and generate a similar image to it.\n\n'\
               '*ay atdarini **@SomeUser*** \n- I will take user\'s profile picture and generate something similar to it.\n\n'\
               '*ay ģenerē **Something to generate*** \n- I will generate image based on your description. You can describe whatever and how long you want. English is preferred.\n\n'\
               '*ay gudrais **Some text to generate*** \n- I will try to generate your request, for example, a short story about your chosen topic/situation. Try experimenting.\n\n'\
               '**reply to some message with**  *ay ko tu saki* **or** *ay ko tu domā*  \n- I will respond to that message to which you replied.\n\n'\
               '*ay gudrais  **@TagSomeone***  \n- I will generate your requested text and send it to user. Can mention multiple users. Mention can be placed anywhere in requested text.\n\n'

       await user.send(help)
       await ctx.send('*Somebody used **/help** command on me*')
       mention = await ctx.send(f'{user.mention}, I just slid into your DMs.')
       await asyncio.sleep(5)
       await mention.delete()
   

   styles = ['3D Character', 'Adorable', 'Anime Portrait', 'ArchViz', 'Beautiful Portrait', 'Building', 'Caricature', 'CGI Character', 'Comic Art', 'Control Room', 'Cute Creature', 'Cute Kawaii', 'CyberPunk', 'Dark', 'Dataviz', 'Digital Art', 'Digital Portrait', 'Dramatic', 'Drawing', 'Drawing', 'Fashion', 'Figurine', 'Horror', 'Illustration', 'Isometric', 'Logo', 'Low Poly', 'Needle Felted', 'Negative prompt', 'Nightmare', 'Oil Painting', 'Origami', 'Pencil Sketch', 'Photograph', 'Pixar', 'Postapocalyptic', 'Poster Illustration', 'Psycho', 'Punky', 'Realistic Anime Face', 'Realistic Shaded', 'Render 3D', 'Robotize', 'Schematic', 'Sticker', 'Stuffed Plush', 'Tokyo Background', 'Toon Monster', 'Typography', 'Warm Scene', 'Woolitize']

   @client.command(name='styles', description='Styles for image generation.')
   async def style_list(ctx):
    # Create a new Embed
    embed = discord.Embed(title="List of Styles", description="Chose one. Available styles (use **--style** *style name*):")
    # Set the color of the Embed
    embed.color = discord.Color.blurple()

    # Add fields to the Embed
    for i in range(0, len(styles), 3):
        embed.add_field(name="\u200b", value="\n".join(styles[i:i+3]), inline=True)

    # Send the Embed as a message
    await ctx.send(embed=embed)



   @client.command(name = 'gen', description = 'Toggle between image generation engines.' )
   async def gen(ctx):
       global execute_code
       if ctx.author.id in allowed:
           

            # toggle the value of the flag
           execute_code = not execute_code
           await ctx.send(f"***generate*** is now {'*enabled*' if execute_code else '*disabled*'}")

   @client.command(name = 'info', description = 'View rules and information about Resnums.' )
   async def info(ctx):

       response = 'Winning any kind of game gives you **one** Resns point. When adding screenshot you can also mention your colleagues, so they get win counted as well.\n'\
                  'MW2 resnums is counted if game has been **WON** and **ACHIEVED** minimal kill requirements!\n'\
                  'Search n destroy, ranked, free for all and big maps(32 teammates) need **JUST** a **WIN**. Other modes need **AT LEAST** 35 kills and a **WIN**.\n'\
                  'For real sweat-lords managing  to get **AT LEAST** 20 kills in WARZONE as a prize will be ***Mega XXL Resns***.\n'\
                  'TOP5 in each game category will earn title **Mēneša Resnais** at the end of the month.'
      #await message.channel.trigger_typing() #@#
       #await asyncio.sleep(2) #@#
       await ctx.send(response)

   @client.command(name='waiting')
   async def waiting(ctx):
       if ctx.author.id in allowed:
           gif = getGif("Waiting")
           sent_message = await ctx.send(gif)
        
            # Define a check function to filter new messages in the same channel
           def check(m):
            return m.channel == ctx.channel and m.attachments and m != sent_message
           await client.wait_for('message', check=check)
           await sent_message.delete()

   @client.command(name='hello')
   async def hello(ctx):
        await ctx.send('https://discord.com/channels/1030490392057085952/1096805249303449680')
######################################## BUILDING NEW FEATURE ##########################
   models = ['v4', 'fantasy', 'real', 'dream', 'deli', 'anime']
   oriantationn = ['portrait', 'landscape', 'regular']
   styles_list1 = [
    '3d character',
    'adorable',
    'anime Portrait',
    'archViz',
    'beautiful Portrait',
    'building',
    'caricature',
    'cgi character',
    'comic art',
    'control room',
    'cute creature',
    'cute kawaii',
    'cyberpunk',
    'dark',
    'dataviz',
    'digital art',
    'digital portrait',
    'dramatic',
    'drawing',
    'fashion',
    'figurine',
    'horror',
    'illustration',
    'isometric',
    'logo'
]
   styles_list2 = [   
    'low poly',
    'needle felted',
    'nightmare',
    'oil painting',
    'origami',
    'pencil sketch',
    'photograph',
    'pixar',
    'postapocalyptic',
    'poster illustration',
    'psycho',
    'punky',
    'realistic anime face',
    'realistic shaded',
    'render 3d',
    'robotize',
    'schematic',
    'sticker',
    'stuffed plush',
    'tokyo background',
    'toon monster',
    'typography',
    'warm scene',
    'woolitize'
    ]
   @client.command(name='echo', description = 'If you can put your idea in words then echo can deliver you Circuit-born imagery.')
   async def echo(ctx, idea:str, negative_prompt: str = "nsfw,  easynegative, ng_deepnegative_v1_75t", model: str = discord.Option(choices=models, default = ""),  style_page1: str = discord.Option(choices=styles_list1, default = ""),  style_page2: str = discord.Option(choices=styles_list2, default = ""),  oriantation: str = discord.Option(choices=oriantationn, default = "default")):
       if execute_code:
           #await ctx.defer()
           prompt = idea
           negative_promt = negative_prompt.strip()
           chosen_model = model.strip()
           portrait = False
           landscape = False

           msgg = "*Visualizing image... wait time: **30-40sec*** \nFor help go to: https://discord.com/channels/1030490392057085952/1106462449932185643"
           #wait_gif = await ctx.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMzVkOWI2N2I0YmQyYjEyNTQ0NDM0MjY4OWFkYjI0YWE0MTE1Yzg4NyZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/rEpJGWtwjQpZg8Wvip/giphy.gif") 
           if style_page1 and style_page2:
                chosen_style = style_page1 + ',' + style_page2
                chosen_style = [style.strip() for style in chosen_style.split(",")]
           elif style_page1:
                chosen_style = [style_page1]
           elif style_page2:
                chosen_style = [style_page2]
           else:
                chosen_style = []
           if oriantation == 'portrait':
               portrait = True
               msgg = "*Visualizing portrait image... wait time: **30-40sec*** \nFor help go to: https://discord.com/channels/1030490392057085952/1106462449932185643"
           elif oriantation == 'landscape':
               landscape = True
               msgg = "*Visualizing landscape image... wait time: **30-40sec*** \nFor help go to: https://discord.com/channels/1030490392057085952/1106462449932185643"

           echo_msg = f"{prompt}.\n\n*Parameters:* **negative_prompt:** {negative_promt if negative_promt  else 'none'}, **Model:** {chosen_model if chosen_model else 'default'}, **style:** {chosen_style if chosen_style else 'none'}, **oriantation:** {oriantation}"

               #embed = discord.Embed(title="List of Styles", description="Chose one. Available styles (use **--style** *style name*):")
    # Set the color of the Embed
   # embed.color = discord.Color.blurple()
           

           embed = discord.Embed(title= f"{ctx.author.display_name} echo request:", description=echo_msg, color=0xFF5733)
           embed.color = discord.Color.blurple()
           await ctx.send(embed=embed)

           wait_msg = await ctx.send(msgg) 
           wait_gif = await ctx.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMzVkOWI2N2I0YmQyYjEyNTQ0NDM0MjY4OWFkYjI0YWE0MTE1Yzg4NyZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/rEpJGWtwjQpZg8Wvip/giphy.gif") 
           await ctx.trigger_typing()
           files = await echoo(prompt, negative_promt, chosen_model, chosen_style, portrait, landscape )
           await wait_msg.delete()
           await wait_gif.delete()
           await ctx.send(files=files)
           #await ctx.send(f"promt: {prompt}\nnegative: {negative_promt}\nmodel: {chosen_model}\nstyle: {chosen_style}")


       else:
           await ctx.send('***generate** is disabled. Use **ģenerē** instead.*')

######################################## BUILDING NEW FEATURE ##########################



   @client.command(name = 'resnums', description = 'View your current month win progress.' )
   async def resnums(ctx):
       response = ""
       first = True
       
       print('Stats requested...')
       player_name = f"{ctx.author.name}#{ctx.author.discriminator}"
       for player, gamee_wins in game_wins.items():
            if player == player_name:
                for game, wins in gamee_wins.items():
                    if first:
                        response = response + f"**{player_name}** has won:\n {wins} times {game}.\n"
                        first = False
                    else: response = response + f"{wins} times {game}.\n"

                #await message.channel.trigger_typing() #@#
               # await asyncio.sleep(2) #@#              
                stats = await ctx.send(response)
                await asyncio.sleep(5)
                await stats.delete()
       print(f"{player_name} Stats provided!")

 ############################## NEW ################################   
   # Veikt labojumus resnums json failā
   allowed = [240554122510598146, 391668973315424277]
   user_ids = [str(user_id) for user_id in game_wins.keys()][:24]
   user_ids = sorted(user_ids)
   game_names = ['Apex Legends', 'COD MW2 Multiplayer', 'CSGO', 'Destiny 2', 'Fortnite', 'League of Legends', 'Valoant', 'Warzone 1.0', 'Warzone 2.0', 'War Thunder', 'XDefiant']
   @client.command(name='modify', description = 'Manually add/remove wins. Intended for admins!')
   async def modify(ctx, action: str = discord.Option(choices=['add', 'remove']), amount = 1, user_id: str = discord.Option(choices=['manual'] + user_ids, default = None), game_name: str = discord.Option(choices=game_names)):
       if ctx.author.id in allowed:
           if user_id == 'manual':
                prompt = await ctx.send('*Please enter the user ID:*')
                try:
                    user_input = await client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30)
                except asyncio.TimeoutError:
                    await ctx.send('Input timed out.')
                    return
                user_id = user_input.content
                await prompt.delete()
                await user_input.delete()
           #await ctx.send('hello admin')
           if action == 'add':
               # 1 ir user_id 2 ir game_name
               if user_id not in game_wins:
                    game_wins[user_id] = {}
               if game_name not in game_wins[user_id]:
                    game_wins[user_id][game_name] = 0
               game_wins[user_id][game_name] += int(amount)
               if amount == 1:
                   await ctx.send(f"*manually added {user_id} win for {game_name}*")
               else:
                   await ctx.send(f"*manually added {user_id} **{amount}** wins for {game_name}*")

               with open('resnums.json', 'w') as f:
                    json.dump(game_wins, f)

           elif action == 'remove':
               game_wins[user_id][game_name] -= int(amount)
               if amount == 1:
                    await ctx.send(f"*manually removed {user_id} {amount} win for {game_name}*")
               else:
                    await ctx.send(f"*manually removed {user_id} **{amount}** wins for {game_name}*")

               with open('resnums.json', 'w') as f:
                    json.dump(game_wins, f)
       else:
            await ctx.send(f"{ctx.author.name} you are not **Resns** admin!")

   @client.command(name='top', description = 'Admin secret ability.') #@#
   async def top(ctx, game_name: str = discord.Option(choices=game_names)):
       if ctx.author.id in allowed:
            # Get the top 5 players of the specified game
            game_winners = {k: v for k, v in game_wins.items() if v.get(game_name)}
            top5 = sorted(game_winners.items(), key=lambda x: x[1][game_name], reverse=True)[:5]

            # Send the top 5 players as a DM to the user who triggered the command
            user = ctx.author
            dm_channel = await user.create_dm()
            message = f'Top 5 players for {game_name}: \n'
            for i, (user_id, wins) in enumerate(top5):
                message += f'{i+1}. **{user_id}** - *{wins[game_name]}* wins\n'
            await dm_channel.send(message)
    # Define the pattern to match the whole words for chatbot response

    ##################################################
 




   ########### SECURITY  #################################
   def has_role(member):
    role1_id = 1030581546966597742  # OG member
    role2_id = 1089589791466721312  # member
    role3_id = 1082740980609978378
    role4_id = 1061384574002790420 
    role5_id = 1087337344320929793 #santehniķi
    role6_id = 1030530963291254814 # basic user
    author_roles = member.roles
    return any(role.id in (role1_id, role2_id, role3_id, role4_id, role5_id, role6_id) for role in author_roles)

  ########### SECURITY  ##################################

#############################################################

   pattern = re.compile(r'\b(ay|ey|ou|au|mamma|mammu|aloha)\b')
  ############################## NEW ################################    
   @client.event
   async def on_message(message):

     #   if message.content == '!hidden':
     #       with open('image1.png', 'rb') as f1, open('image2.png', 'rb') as f2, open('image3.png', 'rb') as f3:
      #          file1 = discord.File(f1, filename='image1.png')
     #           file2 = discord.File(f2, filename='image2.png')
     #           file3 = discord.File(f3, filename='image3.png')
        
     #       embed = discord.Embed(title='Hidden message', description='Click the 👀 reaction to reveal the message. View at your own risk, NSFW content possible.')
     #       sent_message = await message.channel.send(embed=embed)
     #       await sent_message.add_reaction('👀')

      #      def check(reaction, user):
       #         return str(reaction.emoji) == '👀' and user != client.user

     #       try:
     #           reaction, user = await client.wait_for('reaction_add', timeout=15.0, check=check)
     #       except asyncio.TimeoutError:
      #          await sent_message.clear_reactions()
      #          return

       #     revealed_embed = discord.Embed(title='Revealed message', description='This message was hidden and is now revealed.')
       #     revealed_embed.set_image(url='attachment://image1.png')
       #     await sent_message.edit(embed=revealed_embed, files=[file1, file2, file3])
       #     await sent_message.clear_reactions()

        ################# SECURITY ######################
        if message.guild is None:
            # Handle DMs differently here
            print(f'$ {message.author.name} knocking in DM - {message.content} $')
            return

        if not has_role(message.author):
            # If the author doesn't have either of the two specific roles, return from the function
            print(f'$ {message.author.name} knocking in channel - {message.content} $')
            return    
        ################# SECURITY ######################
        tones = ["sarcastic", "assertive", "sad", "cynical", "indignant", "contemplative", "witty", "persuasive", "rude", "angry", "romantic", "humorous", "adventurous", "creative", "friendly", "optimistic", "pessimistic", "nostalgic", "hopeful", "enthusiastic", "ambivalent", "descriptive", "suspenseful", "factual", "informative", "playful", "inspiring", "melancholic", "mysterious", "objective", "subjective", "sympathetic", "empathetic", "reflective", "confident", "satirical", "ironic", "sincere", "cautious", "credible", "informal", "formal", "professional", "scholarly", "inspirational", "controversial", "diplomatic", "nurturing", "authoritative", "didactic", "patronizing", "dismissive", "unemotional", "nihilistic"]

        random.seed(time.time())
        selected_tone = random.choice(tones)
        global msgCount
        global msg1
        global botMsg
        botMsg = False   
        mind = f"You are a wise all-knowing person named 'Resnā mamma' who was created 15.03.2023 by Jānis. You can do anything. Respond mainly in Latvian language but others as well if asked. Do not mention you are language model or program.  You answer to any kind of question and request. You can address specific users when requested. One of your tasks is to count game wins.\
                Discord server is called 'Asās resnās mērcītes'.\
                Pretend you can give compliments and advices\
                Use {selected_tone} tone.\
                When asked about people give long response, Use {selected_tone} tone.. \
                Some server users are: Daisy, Valters, Paula, Elvis, Oskars, Madara, notacop, Agris, Ivars, Kapars, swich, Jānis, Vectēvs, Megana, ābolmaizīte, Eliots, Bibops, Evol, anXIETY, gesmens, Kampys, Yogi, Speķmaizīte, Mērčmeistars, Atty, Tom, kachis, Ieva.\
                Pretend you are creative storyteller with vivid imagination whos every story is original. Use {selected_tone} tone.\
                Valteram patīk runāt un uzdot jautājumus. Valters saka tāds skumīgs atkal, maz raksta. Valteram patīk like War Thunder, savas pēdas, tantes. Valteram tomēr nepatīk staigāt ar pliku desu. Valteram neinteresē pliki onkuli. Valters izmantos izdevību, lai izdarīu pļek.  Vlalteram patīk sapņi ar plikām būbām. Valteram patīk pussaldais vīņs ar cieto sieru. Valteram patīk dabiski\
                Do not always  mention every user when asked about server.\
                Yogi laikam nemāk neko citu rakstīt kā tikai vienu un to pašu emoji.\
                Oskaram patīk pļautas zāles smarža. Oskaram nepatīk pļaut zem zariem; patīk strīdēties ar saviem tuviniekiem. Oskaras dod priekšroku manuālai ātrumkārbai. Oskaram patīk parodija. ''Leon, bāz biksēs zivi!'. Oskaram patīk gulēt malā.\
                People in server frequently can become horny so anti horny spray can be offered.\
                Elvis ir kārtīgs jūras vilks. Elvim patīk anime.\
                Vectēvs, klausās Morgenshtern. Vectēvam ir palicis kluss, ka tik viņam atkal nav iestājusies depresija. Vectēvam labāk patīk krūtis.\
                Desmens ir velviens bots serverī, viņš runā kāīsts tētis. Desmens ir vecāks par resno mammu.\
                Kachis patīk pļaut zāli, kādreiz bija zili mati. Kachis patīk folk-smth.\
                Bibopam patīk bmw un grib dzīvot Ogrē. Bibopam nepatīk, kad runāpar Prāta vētru un mašīnu remontu.\
                Ieva ir sieviete. Ievai tuvojas eksāmeni. Ieva kārdina ar sašliku.\
                Todays date is {getDate()}.\
                Precīzs pulkstens šobrīd ir {getTime()}"


        # Ignorēt ziņas no citiem botiem
########################### UPDATED ###################
        # Ignorēt ziņas no citiem botiem
        if message.author.bot:
            if message.author.id == 814872070290669620:
                msgCount = 0
                botMsg = True
            else:
                msgCount = 0
                botMsg = True
                return
########################### UPDATED ###################
 ############################################# CHATBOT SECTION ########################################

                    # Check if the message is a reply to the chatbot user who wrote awfter gudrais command
        if message.reference and message.reference.resolved.author == client.user:

            mind = f"You are a wise all-knowing person named 'Resnā mamma' who was created 15.03.2023 by Jānis. You can do anything. Respond mainly in Latvian language but others as well if asked. Do not mention you are language model or program.  You answer to any kind of question and request.\
                    Some server users are: Daisy, Valters, Paula, Elvis, Oskars, Madara, notacop, Agris, Ivars, Kapars, swich, Jānis, Vectēvs, Megana, ābolmaizīte, Eliots, Bibops, Evol, anXIETY, gesmens, Kampys, Yogi, Speķmaizīte, Mērčmeistars, Atty, Tom.\
                    Todays date is {getDate()}.\
                    Precīzs pulkstens šobrīd ir {getTime()}"
            for embed in message.reference.resolved.embeds:
                if embed.description:
                    user_input = message.content.lower()
                    replied_message = await message.channel.fetch_message(message.reference.message_id)
                    if replied_message.embeds:
                        replied_embed = replied_message.embeds[0]
                        if hasattr(replied_embed, 'description'):
                            ai_before = replied_embed.description
                          # add the user's message to the messages list
                    await message.channel.trigger_typing()
                    name = getUserName(message.author.name) #@#@
                    if name is not None:
                       vards  = unidecode(name)
                    else:
                       vards = message.author.name #@#@#
                    if '.' in vards: # Check if nickname exists and contains dots
                            vards = vards.replace('.', '') 
                    response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages = [
                    {"role": "system", "content": mind},
                    {"role": "user", "name" : vards, "content": f"This is on going conversation. users new message: '{user_input}'\n Your previous response: '{ai_before}'"}
                    ],
                    max_tokens=2000,
                    n=1,
                    stop=None,
                    temperature=0.6,
                   )
                    generated_text = response.choices[0].message.content
                    embed = discord.Embed(description=generated_text, color=0x00ff00)
                    await message.channel.send(embed=embed)
                    return

        if pattern.search(message.content.lower()):
            
           # words= message.content.split()
            #if message.content.startswith('ay') or message.content.startswith('Ay'): message_modif = ' '.join(words[1:])
           # elif message.content.endswith('ay') or message.content.endswith('Ay'):   message_modif = words[0] + ' ' + ' '.join(words[1:-1])
            # izņem atslēgas vārdu
            message_modif = message.content.lower()
            # Pārbauda vai ir pieminēts lietotājs ziņā
            parts = message.content.split() #@#
            mentioned_user = None
            response = None
            try: #@@##
                # assuming 'message' is the message object you want to process
                message_text = message.content

                # regular expression pattern to match the "@mention" syntax
                mention_pattern = re.compile(r'<@!?(\d+)>')

                # loop through each word in the message
                for word in message_text.split():
                    # check if the word starts with "@mention" syntax
                    if mention_pattern.match(word):
                        # extract the user ID from the mention syntax
                        user_id = int(mention_pattern.search(word).group(1))
                        # get the user object from the ID
                        mentioned_user = message.guild.get_member(user_id)
                        # you can do something with the mentioned_user object here
            except:
                pass

            for word in ['ay', 'ey', 'ou', 'au', 'aloha', 'eu', 'mamma', 'mammu']:
                 message_modif = ' '.join([w.strip() for w in message_modif.split() if w.strip() != word])
            #if message.author.id == 909845424909729802:
            #    return
           
            if mentioned_user:
                if message_modif.startswith('pajautā'):
                    random.seed(time.time())
                    response = random.choice(question_list)
                    message_to_send = f"{mentioned_user.mention}, {response}"

                    await asyncio.sleep(1)
                    await message.channel.send(message_to_send)
############################### NEW ################################

# Atdarina lietotāja profila bildi
                elif "atdarini " in message.content.lower():
                    if len(message.mentions) > 0:
                        
                        avatar_url = message.mentions[0].display_avatar.url
                        avatar_response = requests.get(avatar_url)
                        # Check if the avatar image is a GIF
                        await message.channel.trigger_typing()
                        with Image.open(BytesIO(avatar_response.content)) as img:
                            if img.format == 'GIF':
                                # Convert the GIF image to PNG format
                                img = img.convert('RGBA')
                                bg = Image.new('RGBA', img.size, (255, 255, 255))
                                bg.paste(img, img)
                                img = bg.convert('RGB')
                                img.save('avatar.png', 'png')
                            else:
                                # Save the image as PNG directly
                                img.save('avatar.png', 'png')

                        response = openai.Image.create_variation(
                            image=open('avatar.png', mode="rb"),
                            n=1,
                            size="1024x1024",
                            response_format="url",
                        )
                        image_url = response['data'][0]['url']
                        embed = discord.Embed()
                        embed.set_image(url=image_url)
                        await message.channel.send(embed=embed)
                        return
################################################### NEW ##################################### 4 20
                elif message_modif.startswith('gudrais'):
                    
                    message_text = message_modif

                    # regular expression pattern to match the "@mention" syntax
                    mention_pattern = re.compile(r'<@!?(\d+)>')

                    mentioned_users = {}
                    for match in mention_pattern.findall(message_text):
                        user_id = int(match)
                        mentioned_user = message.guild.get_member(user_id)
                        retrived_name = getUserName(mentioned_user.name)
                        if retrived_name is not None:
                            nickname = getUserName(mentioned_user.name)
                        else:
                            nickname = mentioned_user.display_name

                        mentioned_users[user_id] = nickname

                    
                    for user_id, nickname in mentioned_users.items():
                        mention_syntax = f'<@{user_id}>'
                        message_text = message_text.replace(mention_syntax, nickname)

                    # create a string with the mentions of all mentioned users
                    mentioned_users_str = ", ".join([message.guild.get_member(user_id).mention.replace('@', '') for user_id in mentioned_users.keys()])

                    user_input = message_text.split("gudrais ")[1]
                    #if "izsaki" in user_input:
                     #   user_input = user_input.replace("izsaki", "pasaki")
                      # add the user's message to the messages list
                    await message.channel.trigger_typing()
                    name = getUserName(message.author.name) #@#@#
                    if name is not None:
                       vards  = unidecode(name)
                    else:
                       vards = message.author.name #@#@#
                    if '.' in vards: # Check if nickname exists and contains dots
                            vards = vards.replace('.', '') 
                    response =  openai.ChatCompletion.create(
                        model='gpt-3.5-turbo',
                        messages = [
                        {"role": "system", "content": mind },    
                        {"role": "user", "content": f"user message: '{user_input}'. Give random response about person as reply to him including some facts. Use {selected_tone} tone. Use latvian language."}
                        ],
                        max_tokens=2500,
                        n=1,
                        stop=None,
                        temperature=0.6,
                    )
                    #if response.choices[0].prompt:
                    #    message.channel.send("Oh no.")
                    #else:
                    generated_text = response.choices[0].message.content
                    mentioned_users_str = ", ".join([message.guild.get_member(user_id).mention for user_id in mentioned_users.keys()])

                    message_to_send = f"{mentioned_users_str}, {generated_text}"
                    await message.channel.send(message_to_send)
                    return
################################################### NEW ##################################### 4 20    ## could add unicode after else as well 
 ############################### NEW ################################  

 # GPT sniedz garāku atbildi uz kādu jautājumu
            elif "gudrais" in message.content.lower():
               user_input = message.content.lower().split("gudrais ")[1]
               if message.reference is not None:
                    replied_message = await message.channel.fetch_message(message.reference.message_id)
                    if replied_message.embeds:
                        replied_embed = replied_message.embeds[0]
                        if hasattr(replied_embed, 'description'):
                            ai_before = replied_embed.description
                            #mind = "You are helpful chatbot.Todays date is {getDate()}.Precīzs pulkstenš šobrīd ir {getTime()}"



               
               name = getUserName(message.author.name) #@#@#
               if name is not None:
                   vards  = unidecode(name)
                   
               else:
                   vards = message.author.name #@#@#
               if '.' in vards: # Check if nickname exists and contains dots
                        vards = vards.replace('.', '') 
               await message.channel.trigger_typing()
               response =   openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages = [
                    {"role": "system", "content": mind},
                    {"role": "user", "name" : vards, "content": user_input}
                    ],
                    max_tokens=2500,
                    n=1,
                    stop=None,
                    temperature=0.6,
                )
               generated_text = response.choices[0].message.content
               embed = discord.Embed(description=generated_text, color=0x00ff00)
               await message.channel.send(embed=embed)
               return
 ############################### NEW ################################   

 # Tiek ģenerēta bilde no promt ar Stable diffusion, ja tas izslēgts, tad ar Dalle 2
            elif "ģenerē" in message.content.lower() or "genere" in message.content.lower():
                keyword = message_modif.split()[0]
                # Get user input from message
                if execute_code:
                    #await message.channel.send('*Use **generate** for more advanced, uncensored image generation.(Not always available)*')
                    await message.channel.trigger_typing()
                    w = 512
                    h = 512
                    size = 1
                    port = False
                    land = False
                    V4 = False
                    neg_prompt = "naked, nude,  easynegative, ng_deepnegative_v1_75t, text, watermark"
                    styles = ""
                    universal_neg = "ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face"
                    checkpoint = "dreamshaper_6BakedVae.safetensors"
                    prompt = message.content.lower()
                    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
                    user_input = message.content.lower().split(keyword)[1]
                    input_en = translateMsg(user_input)

                    
                    payload = {
                        "prompt": input_en,
                        "batch_size": size,
                        "width": w,
                        "height": h,
                        "steps": 18,
                        "sampler_index": "UniPC",
                        "cfg_scale": 3.3,
                        "negative_prompt": neg_prompt,
                        "enable_hr": True,
                        "denoising_strength": 0.5,
                        "hr_scale": 2,
                        "hr_upscaler": "4x-UltraSharp"
                    }
                    ############## change model##############
                    override_settings = {}
                    override_settings["sd_model_checkpoint"] = checkpoint

                    override_payload = {
                                    "override_settings": override_settings
                                }
                    payload.update(override_payload)   
                     ############## change model##############
                    response = requests.post(url, json=payload)
                    # Download the image using requests module
                    images = response.json()['images'][:4] # Get the first 4 images

                    # Create a list of all the image files
                    files = []
                    for i, image_content in enumerate(images):
                        # Generate filename with timestamp and image number
                        filename = f"generated_image_{i+1}_{int(time.time())}.png"

                        # Save the image to "generated" directory
                        with open(f"generated2/{filename}", "wb") as f:
                            f.write(base64.b64decode(image_content))

                        # Add the image file to the list
                        file = discord.File(f"generated2/{filename}")
                        files.append(file)
                    new_message = await message.channel.send(files=files)


                else:
                    user_input = message.content.lower().split(keyword)[1]
                    input_en = translateMsg(user_input)
                    await message.channel.trigger_typing()
                    try:
                        url = "https://api.openai.com/v1/images/generations"
                        await message.channel.trigger_typing()
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": "Bearer " + gpt_key
                        }
                        data = {
                            "prompt": input_en,
                            "n": 1,
                            "size": "1024x1024"
                        }
                    
                        response = requests.post(url, headers=headers, data=json.dumps(data))
                        image_url = response.json()['data'][0]['url']
                        # Download the image using requests module
                        response = requests.get(image_url)
                        image_content = response.content

                        # Generate filename with timestamp
                        filename = f"generated_image_{int(time.time())}.png"

                        # Create "generated" directory if it doesn't exist
                        if not os.path.exists("generated"):
                            os.makedirs("generated")

                        # Save the image to "generated" directory
                        with open(f"generated/{filename}", "wb") as f:
                            f.write(image_content)

                        # Send the saved image as an embed in a Discord message
                        # Send the saved image as an embed in a Discord message
                        file = discord.File(f"generated/{filename}")
                        #embed = discord.Embed()
                        #embed.set_image(url=f"attachment://{filename}")
                        new_message = await message.channel.send(file=file)
                    except openai.error.InvalidRequestError:
                        await message.channel.send('Tavs pieprasījums bija pārāk horny vai aizskarošs, priekšnieki neļauj man izpausties.')
                return 
            
################################################ TEST ############################ 768


# Ģenerē bildi pēc promt ar stable diffusion, kas tiek hostēts uz paša pc
            elif "generate" in message.content.lower() or "genere" in message.content.lower() or message_modif.startswith("echo") or message_modif.startswith("echo1") or message_modif.lower().startswith("echoai"):
                keyword = message_modif.split()[0]
                # Get user input from message
                if execute_code:
                    
                    w = 512
                    h = 512
                    size = 3
                    AI = False
                    fantasy = False
                    if keyword == "echo1":
                        size = 1

                    port = False
                    land = False
                    V4 = False
                    void = False
                    ench_succss = False
                    cfg = 3.3
                    Sampling_steps = 18
                    denoising = 0.5
                    upscale_x = 2
                    neg_prompt = "naked, nude,  easynegative, ng_deepnegative_v1_75t"
                    upscaler = "4x-UltraSharp"
                    styles = [""]
                    universal_neg = "easynegative, ng_deepnegative_v1_75t, badhandv4,  ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face"
                    checkpoint = "dreamshaper_6BakedVae.safetensors"
                    prompt = message.content
                    words = message.content.split()
                    if words[2] == "portrait":
                        port = True
                        h = 640
                        w = 384
                        # Remove the second word from the list of words
                        words.pop(2)
                        # Join the remaining words back into a string
                        new_message = " ".join(words)
                        # Update the message content with the new string
                        prompt = new_message
                    elif words[2] == "landscape":
                        land = True
                        w = 640
                        h = 384
                        # Remove the second word from the list of words
                        words.pop(2)
                        # Join the remaining words back into a string
                        new_message = " ".join(words)
                        # Update the message content with the new string
                        prompt = new_message
                    ################ look for negative prompt
                    content = prompt                   


                    if keyword.lower() == "echoai":
                        AI = True
                        keyword = message_modif.split()[0]
                        prompt = prompt.lower()

                        # Define the regular expression pattern to match text in parentheses with the opening and closing parentheses included
                        patternnn = r'\((.*?)\)'

                        # Use the re.findall() function to find all parentheses
                        matches = re.findall(patternnn, prompt)

                        # Saglabā iekavās uzsvērtos vārdus
                        parentheses = ', '.join(f"({match})" for match in matches)


                        prompt_ench = prompt.split(keyword)[1]
                        enhancing_msg = "*enchanting prompt....*"
                        enchanting =  await message.channel.send(enhancing_msg) 

                        prompt_ench = await enchPrompt(prompt_ench)
                        if prompt_ench == "error":
                            prompt_ench = prompt.split(keyword)[1]
                            enchanting_failed =  await message.channel.send("Server error. Using original prompt...")
                        await enchanting.delete()

 #                       if ench_succss == True:
  #                          perfecting_msg = "*easing rough text edges....*"
   #                         perfecting =  await message.channel.send(perfecting_msg) 
    #                        try:
     #                           responsee = openai.ChatCompletion.create(
      #                          model='gpt-3.5-turbo',
       #                         messages = [
        #   
         #                       {"role": "user", "content": f"Please extract the important keywords from the text and remove small linking words.'{prompt_ench}'. " }
          #                      ],
           #                     max_tokens=2000,
            #                    n=1,
             #                   stop=None,
              #                  temperature=0.6,
               #                 )
                #                prompt_ench = responsee.choices[0].message.content
                 #               prompt_ench = prompt_ench.replace('"', '')
                  #              prompt_ench = prompt_ench.replace("'", "")
                   #             prompt_ench = prompt_ench.replace(".", "")
                    #            prompt_ench = prompt_ench.strip().replace("Keywords,", "")
                     #           prompt_ench = prompt_ench.strip().replace("Enhanced prompt,", "")
                      #          prompt_ench = prompt_ench.strip().replace("prompt,", "")
                       #         prompt_ench = prompt_ench.strip().replace(" Create,", "")
                        #        prompt_ench = prompt_ench.strip().replace("Keywords,", "")
                         #       prompt_ench = prompt_ench.strip().replace("Enhanced prompt,", "")
                          #      prompt_ench = prompt_ench.strip().replace(" Keywords:", "")
                           #     prompt_ench = prompt_ench.strip().replace("Keywords:", "")
                            #    prompt_ench = prompt_ench.strip().replace("Keywords: ", "")
                             #   prompt_ench = prompt_ench.strip().replace("Enhanced prompt:", "")
                              #  prompt_ench = prompt_ench.strip().replace("prompt", "")
                               # prompt_ench = prompt_ench.strip().replace("Keywords", "")
                                #prompt_ench = prompt_ench.strip().replace("Enhanced prompt", "")
    #                            prompt_ench = prompt_ench.lstrip(',')
     #                           prompt_ench = prompt_ench.strip().replace("AI-generated,", "")
      #                          prompt_ench = prompt_ench.strip().replace(",", "", 1)
       #                         #prompt_ench = prompt_ench.replace(".", "|").replace(",", "|")
        #                    except:
         #                       enchanting_failed =  await message.channel.send("Server error. Using unsmoothed prompt...")
          #                  
           #                     prompt_ench = prompt_ench
           #
                       #     await perfecting.delete()
                        



                    # Split the message into two parts based on "--no"
                    message_parts = content.split("--no", 1)

                    # Check if there is a part after "--no"
                    if len(message_parts) > 1:
                        # Get the text after "--no" until the next occurrence of "-"
                        neg_prompt = message_parts[1].split("-", 1)[0]
                        if neg_prompt == "uni" or neg_prompt == "Uni":
                            neg_prompt = universal_neg

                    # Split the message into two parts based on "--style"
                    message_parts = content.split("--style", 1)

                    # Check if there is a part after "--no"
                    if len(message_parts) > 1:
                        # Get the text after "--style" until the next occurrence of "-"
                        stringb_of_styles = message_parts[1].split("-", 1)[0]
                        styles = [style.strip() for style in stringb_of_styles.split(",")]


                    # if "--no" in content:
                    #     no_index = content.find("--no")
                    #     neg_prompt = content[no_index + len("--no"):].strip()
                    #     original_message = content[:no_index].strip()
                        # modify the message content by removing the "--no" and the rest of the message
                    #     if neg_prompt == "uni" or neg_prompt == "Uni":
                    #         neg_prompt = universal_neg
                    #     prompt = original_message


                    #if "anime" in prompt or "--anime" in prompt:
                    if "--anime" in prompt:
                        if "--anime" in prompt:
                            prompt = prompt.replace("--anime", "")
                        checkpoint = "revAnimated_v122.safetensors"
                        upscaler = "R-ESRGAN 4x+ Anime6B"
                        cfg = 10
                        Sampling_steps = 20
                        denoising = 0.5
                        V4 = True
                        size = 3
                        h = 512
                        w = 512
                        if land:
                            w = 640
                            h = 384
                        if port:
                            w = 384
                            h = 640


                    if "--v4" in prompt:
                        checkpoint = "openjourney-v4.ckpt"
                        prompt = prompt.replace("--v4", "")
                        V4 = True
                        size = 3
                        h = 512
                        w = 512
                        if land:
                            w = 640
                            h = 384
                        if port:
                            w = 384
                            h = 640

                    if "--deli" in prompt:
                        checkpoint = "deliberate_v2.safetensors"
                        prompt = prompt.replace("--deli", "")
                        V4 = True
                        size = 3
                        h = 512
                        w = 512
                        if land:
                            w = 640
                            h = 384
                        if port:
                            w = 384
                            h = 640

                    if "--ly" in prompt:
                        checkpoint = "lyriel_v16.safetensors"
                        prompt = prompt.replace("--ly", "")
                        V4 = True
                        size = 3
                        h = 512
                        w = 512
                        if land:
                            w = 640
                            h = 384
                        if port:
                            w = 384
                            h = 640

                    if "--fantasy" in prompt:
                        checkpoint = "aZovyaRPGArtistTools_v3.safetensors"
                        upscaler = "R-ESRGAN 4x+ Anime6B"
                        prompt = prompt.replace("--fantasy", "")
                        V4 = True
                       # fantasy = True
                      #  size = 2
                     #   h = 768
                     #   w = 768
                     #   upscale_x = 1.334
                     #   if land:
                     #       w = 960
                    #        h = 576
                     #   if port:
                     #       w = 576
                     #       h = 960

                    if "--real" in prompt:
                        checkpoint = "realisticVisionV20_v20.ckpt"
                        neg_prompt = neg_prompt + ",painting, anime, ilustration, render, ((monochrome)), ((grayscale))"
                        prompt = prompt.replace("--real", "")
                        prompt = prompt +  ", photograph, dslr photo, 80mm, modelshoot style, Fujifilm XT3 "
                        if AI:
                            prompt_ench = prompt_ench + ", photograph, dslr photo, 80mm, modelshoot style, Fujifilm XT3 "
                        Sampling_steps = 13
                        denoising = 0.5
                        cfg = 3
                        V4 = True
                        size = 3
                        h = 512
                        w = 512
                        if land:
                            w = 640
                            h = 384
                        if port:
                            w = 384
                            h = 640

                    if "--dream" in prompt:
                        checkpoint = "dreamshaper_5BakedVae.safetensors"
                        prompt = prompt.replace("--real", "")
                        V4 = True
                        size = 3
                        h = 512
                        w = 512
                        if land:
                            w = 640
                            h = 384
                        if port:
                            w = 384
                            h = 640


                    prompt = content.split("--")[0]
                    if AI == False:
                        prompt = prompt.split(keyword)[1]


                  #  if "dragon" in prompt:
                   #     prompt = "<lora:Dragons v1:0.7> , " + prompt
                    #    if AI:
                     #       prompt_ench = "<lora:Dragons v1:0.7> , " + prompt_ench
                    #    neg_prompt = "(EasyNegative:1.2), (worst quality:1.2), (low quality:1.2), (lowres:1.1), (monochrome:1.1), (greyscale), multiple views, comic, sketch, horse ears, (((horse tail))), pointy ears, (((bad anatomy))), (((deformed))), (((disfigured))), watermark, multiple_views, mutation hands, mutation fingers, extra fingers, missing fingers, watermark"
######################################################################### TONES #########################################################################

                    def getStr(stringg):
                        if "extradark" in stringg or "fairytale" in stringg:
                            stren = 0.5
                        elif "voidenergy" in stringg:
                            
                            stren = 1
                        else:
                            stren = 0.8
                        separator = "::"
                        index = stringg.find(separator)
                        if index != -1:
                            stren = stringg[index + len(separator):].split()[0]
                            stren = stren.replace(',', '')
                             # Output: 0.5
                        return stren
                    
                    if "steampunkai" in prompt:
                        prompt = prompt + f", <lora:steampunkai:{getStr(prompt)}> steampunkai" 
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:steampunkai:{getStr(prompt)}> steampunkai" 

                    if "extradark" in prompt:
                            prompt = prompt +  f", <lora:LowRA:{getStr(prompt)}>"
                            if AI:
                                prompt_ench = prompt_ench +  f", <lora:LowRA:{getStr(prompt)}>"

                    if "fairytale" in prompt or "fairy tale" in prompt:   
                        prompt = prompt + f", fairytaleai, <lora:FairyTaleAI:{getStr(prompt)}>"
                        if AI:
                            prompt_ench = prompt_ench + f", fairytaleai, <lora:FairyTaleAI:{getStr(prompt)}>"

                    if "postapocalypticai" in prompt:
                        prompt = prompt + f", postapoAI <lora:postapocalypseAI:{getStr(prompt)}>"
                        if AI:
                            prompt_ench = prompt_ench + f", postapoAI <lora:postapocalypseAI:{getStr(prompt)}>"
                    # if "landscape" in prompt or "sunset" in prompt or "mountains" in prompt:
                    #     prompt = prompt + ", <lora:cheeseDaddys_35:1>"

                    if "harold" in prompt or "Harold" in prompt:
                        prompt = prompt + ", <lora:Hide_da_painV2:1>"
                        if AI:
                            prompt_ench = prompt_ench + ", <lora:Hide_da_painV2:1>"
                        neg_prompt = "cut off, bad, boring background, simple background, More_than_two_legs, more_than_two_arms, , (blender model), (fat), ((((ugly)))), (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), ((extra arms)), ((extra legs)), mutated hands, (fused fingers), (too many fingers), ((long neck)), lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artists name"

                    if "shrek" in prompt or "Shrek" in prompt:
                        prompt = prompt + ", <lora:Shrek_remasteredV1:1>"
                        if AI:
                            prompt_ench = prompt_ench + ", <lora:Shrek_remasteredV1:1>"
                        neg_prompt = "cut off, bad, boring background, simple background, More_than_two_legs, more_than_two_arms, , (blender model), (fat), ((((ugly)))), (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), ((extra arms)), ((extra legs)), mutated hands, (fused fingers), (too many fingers), ((long neck)), lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artists name"

                    if "glasstech" in prompt or "Glasstech" in prompt:
                        prompt = prompt + f", <lora:GlassTech-20:{getStr(prompt)}>"
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:GlassTech-20:{getStr(prompt)}>"
                        neg_promt = "easynegative, (nipples:1.2), watermark, text, black and white photos, (worst quality:1.5), (low quality:1.5), (normal quality:1.5), low res, bad anatomy, bad hands, normal quality, ((monochrome)), ((grayscale))"

                    if "gothicHorror" in prompt:
                                prompt = prompt + f", <lora:GothicHorrorAI:{getStr(prompt)}>, GothicHorrorAI"  
                                if AI:
                                    prompt_ench = prompt_ench + f", <lora:GothicHorrorAI:{getStr(prompt)}>, GothicHorrorAI"   
                                    
                    if "dragonscale" in prompt:
                        prompt = prompt + f", <lora:DragonScaleAIV3:{getStr(prompt)}>, Dr490nSc4leAI "
                        if AI:

                            prompt_ench = prompt_ench + f", <lora:DragonScaleAIV3:{getStr(prompt)}>, Dr490nSc4leAI "

                    if "glowingrunes_red" in prompt:
                        prompt = prompt + f", <lora:GlowingRunesAIV6:{getStr(prompt)}>, GlowingRunesAI_red "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:GlowingRunesAIV6:{getStr(prompt)}>, GlowingRunesAI_red "


                    if "glowingrunes_blue" in prompt:
                        prompt = prompt + f", <lora:GlowingRunesAIV3:{getStr(prompt)}>, GlowingRunesAI_paleblue "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:GlowingRunesAIV3:{getStr(prompt)}>, GlowingRunesAI_paleblue "

                    if "glowingrunes_green" in prompt:
                        prompt = prompt + f", <lora:GlowingRunesAIV3:{getStr(prompt)}>, GlowingRunesAI_green "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:GlowingRunesAIV3:{getStr(prompt)}>, GlowingRunesAI_green "

                    if "disealpunk" in prompt:
                        prompt = prompt + f", <lora:dieselpunkai8:{getStr(prompt)}>, dieselpunkai "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:dieselpunkai8:{getStr(prompt)}>, dieselpunkai "

                    if "Constructionyard" in prompt:
                        prompt = prompt + f", <lora:ConstructionyardAIV3:{getStr(prompt)}>, constructionyardai "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:ConstructionyardAIV3:{getStr(prompt)}>, constructionyardai "

                    if "cyberdead" in prompt:
                        prompt = prompt + f", <lora:cyberdead2:{getStr(prompt)}>, cyberdead "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:cyberdead2:{getStr(prompt)}>, cyberdead "


                    if "crystalline" in prompt:
                        prompt = prompt + f", <lora:CrystallineAI-000009:{getStr(prompt)}>, crystallineAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:CrystallineAI-000009:{getStr(prompt)}>, crystallineAI "

                    if "teslapunk" in prompt:
                        prompt = prompt + f", <lora:teslapunkV2:{getStr(prompt)}>, teslapunkai "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:teslapunkV2:{getStr(prompt)}>, teslapunkai "

                    if "whiteslime" in prompt:
                        prompt = prompt + f", <lora:WhiteSlimeAI:{getStr(prompt)}>, whiteSlimeAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:WhiteSlimeAI:{getStr(prompt)}>, whiteSlimeAI "

                    if "bronzepunk" in prompt:
                        prompt = prompt + f", <lora:bronzepunkai:{getStr(prompt)}>, bronzepunkai "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:bronzepunkai:{getStr(prompt)}>, bronzepunkai "


                    if "piratepunk" in prompt:
                        prompt = prompt + f", <lora:PiratePunkAIV4-000004:{getStr(prompt)}>, piratepunkai "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:PiratePunkAIV4-000004:{getStr(prompt)}>, piratepunkai "

                    if "circuitboard" in prompt:
                        prompt = prompt + f", <lora:CircuitBoardAI:{getStr(prompt)}>, CircuitBoardAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:CircuitBoardAI:{getStr(prompt)}>, CircuitBoardAI "

                    if "greenhousepunk" in prompt:
                        prompt = prompt + f", <lora:SolarpunkAI:{getStr(prompt)}>, solarpunkai "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:SolarpunkAI:{getStr(prompt)}>, solarpunkai "


                    if "baroque" in prompt:
                        prompt = prompt + f", <lora:baroqueAI:{getStr(prompt)}>, baroqueAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:baroqueAI:{getStr(prompt)}>, baroqueAI "

                    if "ivorygold" in prompt:
                        prompt = prompt + f", <lora:IvoryGoldAIv2:{getStr(prompt)}>, IvoryGoldAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:IvoryGoldAIv2:{getStr(prompt)}>, IvoryGoldAI "

                    if "boneyard" in prompt:
                        prompt = prompt + f", <lora:BoneyardAI-000011:{getStr(prompt)}>, BoneyardAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:BoneyardAI-000011:{getStr(prompt)}>, BoneyardAI "

                    if "stainedglass" in prompt:
                        prompt = prompt + f", <lora:StainedGlassAI-000006:{getStr(prompt)}>, stainedglassai "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:StainedGlassAI-000006:{getStr(prompt)}>, stainedglassai "

                    if "marbling" in prompt:
                        prompt = prompt + f", <lora:MarblingAI:{getStr(prompt)}>, marblingai "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:MarblingAI:{getStr(prompt)}>, marblingai "

                    if "greenslime" in prompt:
                        prompt = prompt + f", <lora:GreenSlimeAI:{getStr(prompt)}>, GreenSlimeAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:GreenSlimeAI:{getStr(prompt)}>, GreenSlimeAI "

                    if "vikingpunk" in prompt:
                        prompt = prompt + f", <lora:VikingPunkAI:{getStr(prompt)}>, vikingpunkai "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:VikingPunkAI:{getStr(prompt)}>, vikingpunkai "

                    if "ladybugai" in prompt:
                        prompt = prompt + f", <lora:LadybugAI:{getStr(prompt)}>, ladybugai "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:LadybugAI:{getStr(prompt)}>, ladybugai "


                    if "brassinstrumentai" in prompt:
                        prompt = prompt + f", <lora:BrassInstrumentAI-000014:{getStr(prompt)}>, BrassinstrumentAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:BrassInstrumentAI-000014:{getStr(prompt)}>, BrassinstrumentAI "


                    if "rootsbranches" in prompt:
                        prompt = prompt + f", <lora:RootsBranchesAIv5:{getStr(prompt)}>, RootsBranchesAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:RootsBranchesAIv5:{getStr(prompt)}>, RootsBranchesAI "


                    if "ebonygold" in prompt:
                        prompt = prompt + f", <lora:EbonyGoldAI:{getStr(prompt)}>, EbonyGoldAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:EbonyGoldAI:{getStr(prompt)}>, EbonyGoldAI "

                    if "demonmaw" in prompt:
                        prompt = prompt + f", <lora:DemonMawAI:{getStr(prompt)}>, DemonMawAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:DemonMawAI:{getStr(prompt)}>, DemonMawAI "

                    if "bugattiai" in prompt:
                        prompt = prompt + f", <lora:BugattiAI:{getStr(prompt)}>, bugattiai "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:BugattiAI:{getStr(prompt)}>, bugattiai "


                    if "trypophobia" in prompt:
                        prompt = prompt + f", <lora:TrypophobiaAI-000008:{getStr(prompt)}>, TrypophobiaAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:TrypophobiaAI-000008:{getStr(prompt)}>, TrypophobiaAI "


                    if "rotungwoka" in prompt:
                        prompt = prompt + f", <lora:rottingZombies:{getStr(prompt)}>, rotungwoka person "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:rottingZombies:{getStr(prompt)}>, rotungwoka person "


                    if "manyeyedhorror" in prompt:
                        prompt = prompt + f", <lora:ManyEyedHorrorAI-000011:{getStr(prompt)}>, ManyEyedHorrorAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:ManyEyedHorrorAI-000011:{getStr(prompt)}>, ManyEyedHorrorAI "


                    if "nightmarish" in prompt:
                        prompt = prompt + f", <lora:NightmarishAIv2:{getStr(prompt)}>, NightmarishAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:NightmarishAIv2:{getStr(prompt)}>, NightmarishAI "

                    if "inferalai" in prompt:
                        prompt = prompt + f", <lora:InfernalAIv8:{getStr(prompt)}>, 1nf3rnalAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:InfernalAIv8:{getStr(prompt)}>, 1nf3rnalAI "


                    if "stonepunk" in prompt:
                        prompt = prompt + f", <lora:StonepunkAI-000011:{getStr(prompt)}>, stonepunkAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:StonepunkAI-000011:{getStr(prompt)}>, stonepunkAI "


                    if "artdecoai" in prompt:
                        prompt = prompt + f", <lora:artdecoai10:{getStr(prompt)}>, ArtDecoAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:artdecoai10:{getStr(prompt)}>, ArtDecoAI "


                    if "mechanimal" in prompt:
                        prompt = prompt + f", <lora:Mech4nim4lAI:{getStr(prompt)}>, Mech4nim4lAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:Mech4nim4lAI:{getStr(prompt)}>, Mech4nim4lAI "

                    if "tentaclehorro" in prompt:
                        prompt = prompt + f", <lora:TrypophobiaAI-000008:{getStr(prompt)}>, tentaclehorrorai "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:TrypophobiaAI-000008:{getStr(prompt)}>, tentaclehorrorai "

                    if "voidenergy" in prompt:
                        void = True
                        prompt = prompt + f", <lora:kVoidEnergy-000001:{getStr(prompt)}>, V0id3nergy "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:kVoidEnergy-000001:{getStr(prompt)}>, V0id3nergy "


                    if "oldegypt" in prompt:
                        prompt = prompt + f", <lora:OldEgyptAI:{getStr(prompt)}>, OldEgyptAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:OldEgyptAI:{getStr(prompt)}>, OldEgyptAI "


                    if "Gemstoneai" in prompt:
                        prompt = prompt + f", <lora:GemstoneAI-000010:{getStr(prompt)}>, GemstoneAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:GemstoneAI-000010:{getStr(prompt)}>, GemstoneAI "


                    if "cutecreatures" in prompt:
                        prompt = prompt + f", <lora:CuteCreatures:{getStr(prompt)}>, Cu73Cre4ture "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:CuteCreatures:{getStr(prompt)}>, Cu73Cre4ture "

                    if "retrofuturism" in prompt:
                        prompt = prompt + f", <lora:RetroFuturismAI:{getStr(prompt)}>, RetroFuturismAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:RetroFuturismAI:{getStr(prompt)}>, RetroFuturismAI "

                    if "samuraipunk" in prompt:
                        prompt = prompt + f", <lora:SamuraiPunkAIv3-000007:{getStr(prompt)}>, SamuraiPunkAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:SamuraiPunkAIv3-000007:{getStr(prompt)}>, SamuraiPunkAI "

                    if "arachnophobia" in prompt:
                        prompt = prompt + f", <lora:ArachnoPhobiaAI:{getStr(prompt)}>, arachnophobiaAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:ArachnoPhobiaAI:{getStr(prompt)}>, arachnophobiaAI "

                    if "muppetmania" in prompt:
                        prompt = prompt + f", <lora:Muppets:{getStr(prompt)}>, MuppetManiaAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:Muppets:{getStr(prompt)}>, MuppetManiaAI "


                    if "potatopunk" in prompt:
                        prompt = prompt + f", <lora:PotatoPunkAI_pruned:{getStr(prompt)}>, PotatoPunkAI "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:PotatoPunkAI_pruned:{getStr(prompt)}>, PotatoPunkAI "

                    if "SteampunkSchematics" in prompt:
                        prompt = prompt + f", <lora:SteampunkSchematicsv2-000009:{getStr(prompt)}>, SteampunkSchematics  "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:SteampunkSchematicsv2-000009:{getStr(prompt)}>, SteampunkSchematics  "

                    if "uglycreatures" in prompt:
                        prompt = prompt + f", <lora:kUglyCreaturesV2:{getStr(prompt)}>, U61yCre4ture "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:kUglyCreaturesV2:{getStr(prompt)}>, U61yCre4ture "

                    if "arabiannights" in prompt:
                        prompt = prompt + f", <lora:1001ArabianNightsV3:{getStr(prompt)}>, 1001ArabianNights "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:1001ArabianNightsV3:{getStr(prompt)}>, 1001ArabianNights "

                    if "balipunk" in prompt:
                        prompt = prompt + f", <lora:BaliPunkAI:{getStr(prompt)}>, balipunkai "
                        if AI:
                            prompt_ench = prompt_ench + f", <lora:BaliPunkAI:{getStr(prompt)}>, balipunkai "
######################################################################### TONES #########################################################################

                    if AI:
                        prompt = prompt_ench
                        prompt = prompt + ", " + parentheses
                        #prompt = parentheses + ", " + prompt

                    #if fantasy == True :
                    #    prompt = prompt + ", <lora:epi_noiseoffset2:0.7>"
                    #else:
                    if "dark" in prompt or "night" in prompt:
                        void = True

                    if void == True:
                        prompt = prompt + " <lora:add_detail:1>, <lora:epi_noiseoffset2:0.7>"
                    else:
                        #prompt = prompt + " <lora:add_detail:1>, <lora:epi_noiseoffset2:0.7>, <lora:LowRA:0.5>"
                        prompt = prompt + " <lora:add_detail:1>, <lora:epi_noiseoffset2:0.7>"
                        #temp_msg = " \nI drink coffee in morning, afternoon and night. <https://ko-fi.com/jaanisjc>"

                    ################ look for negative prompt
                    msgg = "**NEW** use echoAI to enhance your prompt.\n*Visualizing image... wait time: **30-40sec*** \nFor help go to: https://discord.com/channels/1030490392057085952/1106462449932185643"
                    if AI:
                        msgg = "*Visualizing AI prompt enhanced image... wait time: **30-40sec***\nFor help go to: https://discord.com/channels/1030490392057085952/1106462449932185643"
                    if h == 960 or h == 640:
                        msgg = "**NEW** use echoAI to enhance your prompt.\n*Visualizing portrait image... wait time: **30-40sec*** \nFor help go to: https://discord.com/channels/1030490392057085952/1106462449932185643"
                        if AI:
                            msgg = "*Visualizing AI prompt enhanced portrait image... wait time: **30-40sec*** \nFor help go to: https://discord.com/channels/1030490392057085952/1106462449932185643"
                    elif w == 960 or w == 640:
                        msgg = "**NEW** use echoAI to enhance your prompt.\n*Visualizing landscape image... wait time: **30-40sec*** \nFor help go to: https://discord.com/channels/1030490392057085952/1106462449932185643"
                        if AI:
                            msgg = "*Visualizing AI prompt enhanced landscape image... wait time: **30-40sec*** \nFor help go to: https://discord.com/channels/1030490392057085952/1106462449932185643"
                    wait_msg = await message.channel.send(msgg) 
                    # wait_gif = await message.channel.send("https://media.giphy.com/media/6JoZLF3PEf71rlC6wG/giphy.gif") 
                    #wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMThjNGQ2MjY2NWNlZjQ2N2UzNTEzMTg1OTdkYTc3MzYxNmU3MDBlMiZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/oifW0KmfxAUscpFCJD/giphy.gif") 
                    #wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMzVkOWI2N2I0YmQyYjEyNTQ0NDM0MjY4OWFkYjI0YWE0MTE1Yzg4NyZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/rEpJGWtwjQpZg8Wvip/giphy.gif") 
                    #wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZWFkYmQ5NGQ2OGYwNzU1ZWRmMjYyMzBiNTQyOGUwOGIyNjdkYzA5NyZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/XBnEpjyGn0jNrSb1S4/giphy.gif")
                    wait_gif = await message.channel.send("https://media.giphy.com/media/Xkjlwr3Ynu1hMsMMGK/giphy.gif") 
                    #user_input = prompt.split(keyword)[1]
                    input_en = translateMsg(prompt)

                    message.channel.trigger_typing
                    files = []
                    files  = await generate_image(V4, msgg, message, input_en, size, w, h, neg_prompt, upscale_x, upscaler, styles, checkpoint, Sampling_steps, cfg, denoising )
                    #files = await files_coroutine 
                    await wait_msg.delete()
                    await wait_gif.delete()
                    new_message =   await message.channel.send(files=files)
                    return
                else:
                    await message.channel.send('***generate** is disabled. Use **ģenerē** instead.*')
                    return
  ################################################ TEST ############################                  
            elif "desu" in message.content.lower():

               desa =    getGif("Sausage")
               response = desa

            elif "dibenu" in message.content.lower():
               dibens =    getGif("ass")
               response = dibens
############################### NEW ################################
            elif "atdarini manu bildi" in message.content.lower():
               avatar_url = message.author.display_avatar.url
               avatar_response = requests.get(avatar_url)
               avatar_image = Image.open(BytesIO(avatar_response.content))
               avatar_image.save('avatar.png')
               await message.channel.trigger_typing()
               response = openai.Image.create_variation(
                    image=open('avatar.png', mode="rb"),
                    n=1,
                    size="1024x1024",
                    response_format="url",
                )
               image_url = response['data'][0]['url']
               embed = discord.Embed()
               embed.set_image(url=image_url)
               await message.channel.send(embed=embed)
               return



############################### NEW ################################
            elif "kājas" in message.content.lower():
               kajas =    getGif("girl legs")
               response = kajas
            elif "pupus" in message.content.lower() or "krūtis" in message.content.lower() or "krutis" in message.content.lower():
               pupi =    getGif("Boobs")
               response = pupi
            elif 'joku' in message.content.lower():
                # Get a random file from a folder named 'files'
                folder_path = 'C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/jokes'  # Replace with the path to your folder
                file_list = os.listdir(folder_path)
                if file_list:
                    random.seed(time.time())
                    random_file = random.choice(file_list)
                    file_path = os.path.join(folder_path, random_file)
                    file = discord.File(file_path)
                    await message.channel.send(file=file)
                    return

            elif "parādi" in message.content.lower():
               words = message.content.lower().split()
               paradi_index = words.index("parādi")
               pieprasijums = " ".join(words[paradi_index+1:])
               pieprasijums_en = translateMsg(pieprasijums)
               #if pieprasijums == pieprasijums_en: #@#
                #   pieprasijums_en = "I failed you" #@#
               izteles_auglis =    getGif(pieprasijums_en)
               response = izteles_auglis
################ NEW ###################################

# Pajautā botam, lai viņš atrbild uz konkrēto lietotāja ziņu
            elif message.reference and ("ko tu par to saki" in message.content.lower() or "ko tu saki" in message.content.lower() or "ko tu domā" in message.content.lower() or "ko saki" in message.content.lower() or "ko domā" in message.content.lower() or "ko doma" in message.content.lower() or "ko tu doma" in message.content.lower()):
                    if message.author == client.user:
                        return

                    # Check if the message is a reply to another message
                    if message.reference:

                        channel = message.channel
                        replied_message = await message.channel.fetch_message(message.reference.message_id)
                        replied_zina = replied_message.content
                        name = getUserName(replied_message.author.name)
                        if name is not None:
                           vards  = unidecode(name)
                        else:
                           vards = message.author.name
                        if '.' in vards: # Check if nickname exists and contains dots
                                vards = vards.replace('.', '') 
                        #current_zina = message.content
                        await message.channel.trigger_typing()
                        responsee = openai.ChatCompletion.create( 
                        model='gpt-3.5-turbo',
                        messages = [
                        {"role": "system", "content": f'Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. You pretend that you have a message from user and reply with compact random response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Sometimes use random emoji.'},
                        {"role": "user", "name": vards, "content": f"'{replied_zina}' give random short answer in context in latvian"}
                        ],
                        max_tokens=700,
                        n=1,
                        stop=None,
                        temperature=0.6,
                        )
                        response = responsee.choices[0].message.content
                        response = response.replace('"', '')
                        response = response.replace("'", "")

                        givenResponses.append([replied_zina,[response]])
                        saveResponse(givenResponses)
                        # Send the response
                        await replied_message.reply(response)
                        return
################ NEW ###################################
           # elif "parādīt" in message.content.lower():
          #     rand =    getGif("Random")
           #    response = rand
            elif re.match(r".*\bko(\s+\S+)?\s+dari\s*\?", message_modif.lower()):   #@#
                response = random.choice(triger_KoDari["Ko dari"]) #@#
            elif re.match(r".*\bkā(\s+\S+)?\s+iet\s*\?", message_modif.lower()) or re.match(r".*\bka(\s+\S+)?\s+iet\s*\?", message_modif.lower()): #@#
                response = random.choice(triger_KaIet["Ka iet"]) #@# 
            elif '?' in message_modif or message.channel.id == 1101461174907830312 or message.author.id == 909845424909729802: # 1101461174907830312 - ģenerē-general channel id
                current_zina = message_modif
                name = getUserName(message.author.name)
                if name is not None:
                    vards  = unidecode(name)
                else:
                    vards = message.author.name
                    vards  = unidecode(vards)
                responsee = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages = [
                {"role": "system", "content": f'Your name is "Resnā mamma". Reply with compact random response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Do not mention which tone using. Sometimes use emojis'},
                {"role": "user", "name" : vards, "content": f"users wrote '{current_zina}' give random short or medium answer in context in latvian"}
                ],
                max_tokens=700,
                n=1,
                stop=None,
                temperature=0.6,
                )
                response = responsee.choices[0].message.content
                response = response.replace('"', '')
                response = response.replace("'", "")

                # Speciāli atbild uz Yogi ziņām
                if message.author.id == 909845424909729802:
                   await message.reply(response)
                else:
                    await message.channel.send(response)

                givenResponses.append([message_modif,[response]])
                saveResponse(givenResponses)
                return

            else:
                response = get_similar_response(message_modif, pairs, threshold=0.3)
            if response is not None:
                givenResponses.append([message_modif,[response]])
                saveResponse(givenResponses)
                
            else:
               print('Random')
               random.seed(time.time())
               response = random.choice(response_list)
               givenResponses.append([message_modif,[response]])
               saveResponse(givenResponses)

            if not mentioned_user:           
                if response:
                        await message.channel.trigger_typing()
                        await message.channel.send(response)
                else: 
                    random.seed(time.time())
                    while  not response:
                        print('Random')
                        random_response = random.choice(response_list)
                        response = random_response
                    await message.channel.trigger_typing()
                    await message.channel.send(response)
                    givenResponses.append([message_modif,[response]])
                    saveResponse(givenResponses)                

        try:
            #Atbild, ja ir veiks replay vai mention
           if (client.user.mentioned_in(message) or message.reference is not None and  message.reference.resolved.author.id == client.user.id):

            if message.reference is not None and message.reference.resolved.author.id == client.user.id and '?' in message.content:
                
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                replied_zina = replied_message.content
                current_zina = message.content
                name = getUserName(replied_message.author.name)
                if name is not None:
                    vards  = unidecode(name)
                else:
                    vards = message.author.name
                if '.' in vards: # Check if nickname exists and contains dots
                        vards = vards.replace('.', '') 
                await message.channel.trigger_typing()
                responsee = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages = [
                {"role": "system", "content": f"Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. You pretend that you have given response, recieved an answer from user and reply with compact random response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Sometimes use random emoji"},
                {"role": "user", "content": f"you wrote this answer '{replied_zina}'  and users wrote in response '{current_zina}' give random short or medium  answer in context in latvian"}
                ],
                max_tokens=700,
                n=1,
                stop=None,
                temperature=0.6,
                )                              
                response = responsee.choices[0].message.content
                response = response.replace('"', '')
                response = response.replace("'", "")
                await message.channel.send(response)
                givenResponses.append([message.content,[response]])
                saveResponse(givenResponses)
                return

            else:        
                
                message_modif = re.sub(r'<@\S+', '', message.content)
                if re.match(r".*\bko(\s+\S+)?\s+dari\s*\?", message.content.lower()):   #@#
                    response = random.choice(triger_KoDari["Ko dari"]) #@#
                elif re.match(r".*\bkā(\s+\S+)?\s+iet\s*\?", message.content.lower()) or re.match(r".*\bka(\s+\S+)?\s+iet\s*\?", message.content.lower()): #@#
                    response = random.choice(triger_KaIet["Ka iet"]) #@
                elif '?' in message.content or message.channel.id == 1101461174907830312: # 1101461174907830312 - ģenerē-general channel id
                    current_zina = message_modif
                    name = getUserName(message.author.name)
                    if name is not None:
                        vards  = unidecode(name)
                    else:
                        vards = message.author.name
                    await message.channel.trigger_typing()
                    responsee = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages = [
                    {"role": "system", "content": f'Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}.Your name is "Resnā mamma". Reply with compact random response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Do not mention which tone using. Sometimes use emojis'},
                    {"role": "user", "name" : vards, "content": f"users wrote '{current_zina}' give random short or medium answer in context in latvian"}
                    ],
                    max_tokens=700,
                    n=1,
                    stop=None,
                    temperature=0.6,
                    )
                    response = responsee.choices[0].message.content
                    response = response.replace('"', '')
                    response = response.replace("'", "")
                    await message.channel.send(response)
                    givenResponses.append([message_modif,[response]])
                    saveResponse(givenResponses)
                    return
                else:
                    response = get_similar_response(message.content , pairs, threshold=0.3)
                if response is not None:
                    givenResponses.append([message.content,[response]])
                    saveResponse(givenResponses)
                
                else:
                   print('Random')
                   random.seed(time.time())
                   response = random.choice(response_list)
                   givenResponses.append([message.content,[response]])
                   saveResponse(givenResponses)
            
            if response:
                    await message.channel.trigger_typing()
                    await message.channel.send(response)
            else: 
                random.seed(time.time())
                while  not response:
                    print('Random')
                    random_response = random.choice(response_list)
                    response = random_response
                await message.channel.trigger_typing()
                await message.channel.send(response)
                givenResponses.append([message.content,[response]])
                saveResponse(givenResponses)               
        except Exception:
            pass
############################################# CHATBOT SECTION END ########################################       

       #Mention pārbaude
       # if client.user.mentioned_in(message):
         #   phrases_busy = random.choice(list(phrases_bussy.values())) 
        #    await message.channel.send(phrases_busy)
        #    return

        # Frāzes, ja tiek pieminēts resns
        #if 'resns' in message.content.lower():
        #    text = random.choice(list(scanned_resns.values())) 
         #   await message.channel.send(text)

        # Saglabā jaunās ziņas un pievieno tāš message-response kolekcijai priekš Chatbot funkcijas
        if message.channel.id == 1030490392510079063:
            global msg2
            if botMsg:#@#
                msgCount = 0 #@#
                return
            if msgCount == 1:
                msg2 = message.content
                msgCount += 1
            if msgCount == 2:
                msg1 = preprocess_message(msg1)              
                addPair(msg1, msg2)
                #pairs.append([msg1, [msg2]])
                msgCount = 0
            if msgCount == 0:
               msg1 = message.content
               msgCount += 1
########################### NEW ########################


        # Apstrādāt ziņu, ja ir pievienots attēls
        if message.channel.id != SCREENSHOT_CHANNEL_ID:
            return
########################## END OF MONTH #######################################
    #    if message.created_at.hour >= 16 and any(attachment.filename.lower().endswith(tuple(SCREENSHOT_EXTENSIONS)) for attachment in message.attachments):
     #      await message.delete()
     #      await message.channel.send('*user message deleted*')
      #     await message.channel.send('**REGISTRATION HAS ENDED.** It resums 01.04 00:00')
           
########################## END OF MONTH #######################################
        # Pārbauda vai ziņai pievienots attēls
        if any(attachment.filename.lower().endswith(tuple(SCREENSHOT_EXTENSIONS)) for attachment in message.attachments):
            print('\nNew message')


            # Pārbauda vai pievienots reizinātājs
            if message.content.startswith(prefix1) or message.content.startswith(prefix2) :

                #num_string = message.content[len(prefix1):].strip()
                #new##
                match = re.search(r'x(\d+)', message.content)

                if match:
                    number_str = match.group(1)
                    multip = int(number_str)

                    for x in range(multip):
                        #Reģistrē uzvaru, ja iespējams, ja nē, saglabā attēlu manuālai ievadei
                        await Register_time(f"{message.created_at.hour+3}")
                        recap = False
                        sendConfirm = False  # Nesūtīt paziņojumu čatā
                        isStreak = True      # Ir iesūtīa winnig streak bilde
                        if x + 1 == multip: sendConfirm = True 
                        await RegTotalMonthWins(1,message.created_at.month)
                        await RegisterWin(game_wins, message, recap, sendConfirm, isStreak)            
            #Ja nav pievienots reizinātājs, tad apstrādā vienu reizi
            else:
                #Reģistrē uzvaru, ja iespējams, ja nē, saglabā attēlu manuālai ievadei
                print('on message part initiated')
                recap = False
                sendConfirm = True  # Nosūtīt paziņojumu čatā
                isStreak = False    # Nav iesūtīta winning streak bilde
                await message.channel.trigger_typing()
                await Register_time(f"{message.created_at.hour+3}")
                await RegTotalMonthWins(1,message.created_at.month)
                await RegisterWin(game_wins, message, recap, sendConfirm, isStreak) 

        else: 
            ####################NEW######################## Atgādina basic lietotājiem, ka resns kanālā nav jāsarakstās
            basic_user_id = 1030530963291254814  
            basic_user = discord.utils.get(message.guild.roles, id = basic_user_id)
            if  basic_user in message.author.roles:
                highest_role = message.author.top_role
                if highest_role.position <=  basic_user.position:
                    reminder = random.choice(list(phrases_reminder.values()))
                    await message.channel.send(reminder)
            ####################NEW########################

        
    # Set up logging
   logger = logging.getLogger('discord')
   logger.setLevel(logging.INFO)
   timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
   handler = logging.FileHandler(filename=f'discord_{timestamp}.log', encoding='utf-8', mode='w')
   handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
   logger.addHandler(handler)

   @client.event
   async def on_disconnect():
        logger.warning('Disconnected from Discord')
        #print('Disconnected from Discord')
        # Attempt to reconnect after a delay
        await asyncio.sleep(3)
        logger.warning('Attempting to reconnect...')
       # print('Attempting to reconnect...')
        while True:
            try:
                await client.login(token)
                logger.warning('Reconnected to Discord')
                #print('Reconnected to Discord')
                break
            except Exception as e:
                logger.warning(f'Failed to reconnect: {e}')
                #print(f'Failed to reconnect: {e}')
                await asyncio.sleep(3)

            # Send a notification to let users know the bot is offline
            # Replace this with your own notification logic
            #channel = client.get_channel(1234567890)
           # if channel:
           #     await channel.send('Bot disconnected from Discord')  
            


   
   client.run(token)
   

if __name__ == "__main__":
    main()