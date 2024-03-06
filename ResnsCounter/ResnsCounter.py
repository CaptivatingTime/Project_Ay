import time
import os
import discord
from dotenv import load_dotenv
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import discord.utils
from discord.ext import commands
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

from pathlib import Path
import requests
#import openai

import openai
from openai import OpenAI, AsyncOpenAI
from io import BytesIO
import io
from PIL import Image
from unidecode import unidecode
import base64

import logging
import functools
import typing
import pytz

from urllib import request, parse
# suppress the warning
warnings.filterwarnings("ignore", message="The parameter 'token_pattern' will not be used since 'tokenizer' is not None'")

import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse

from colorama import Fore

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.get_event_loop()
        wrapped = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, wrapped)
    return wrapper


# Ctrl + K, then Ctrl + U if you’re on Windows
@to_thread
def  generate_gif(promptt, image_name, PingPong):

    server_address = "127.0.0.1:8188"
    client_id = str(uuid.uuid4())

    def queue_prompt(prompt):
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
            return response.read()

    def get_history(prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
            return json.loads(response.read())

    def get_images(ws, prompt):
        prompt_id = queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue #previews are binary data

        history = get_history(prompt_id)[prompt_id]
        for o in history['outputs']:
            for node_id in history['outputs']:
                node_output = history['outputs'][node_id]
                if 'gifs' in node_output:
                    images_output = []
                    for image in node_output['gifs']:
                        image_data = get_image(image['filename'], image['subfolder'], image['type'])
                        images_output.append(image_data)
                output_images[node_id] = images_output

        return output_images


    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    V4 = True
    prompt_text = """
{
  "8": {
    "inputs": {
      "samples": [
        "38",
        0
      ],
      "vae": [
        "15",
        2
      ]
    },
    "class_type": "VAEDecode"
  },
  "12": {
    "inputs": {
      "width": 1024,
      "height": 576,
      "video_frames": 25,
      "motion_bucket_id": 40,
      "fps": 6,
      "augmentation_level": 0.04,
      "clip_vision": [
        "15",
        1
      ],
      "init_image": [
        "23",
        0
      ],
      "vae": [
        "15",
        2
      ]
    },
    "class_type": "SVD_img2vid_Conditioning"
  },
  "14": {
    "inputs": {
      "min_cfg": 1,
      "model": [
        "15",
        0
      ]
    },
    "class_type": "VideoLinearCFGGuidance"
  },
  "15": {
    "inputs": {
      "ckpt_name": "svd_xt_1_1.safetensors"
    },
    "class_type": "ImageOnlyCheckpointLoader"
  },
  "23": {
    "inputs": {
      "image": "SVD-1st-_00037.png",
      "choose file to upload": "image"
    },
    "class_type": "LoadImage"
  },
  "26": {
    "inputs": {
      "frame_rate": 20,
      "loop_count": 0,
      "filename_prefix": "SVD-1st-",
      "format": "image/gif",
      "pingpong": false,
      "save_image": true,
      "crf": 20,
      "save_metadata": false,
      "audio_file": "",
      "videopreview": {
        "hidden": false,
        "paused": false,
        "params": {
          "filename": "SVD-1st-_00053.mp4",
          "subfolder": "",
          "type": "output",
          "format": "image/gif"
        }
      },
      "images": [
        "75",
        0
      ]
    },
    "class_type": "VHS_VideoCombine"
  },
  "36": {
    "inputs": {
      "b1": 1.3,
      "b2": 1.4,
      "s1": 0.9,
      "s2": 0.2,
      "model": [
        "14",
        0
      ]
    },
    "class_type": "FreeU_V2"
  },
  "38": {
    "inputs": {
      "seed": [
        "40",
        0
      ],
      "steps": 20,
      "cfg": 2.5,
      "sampler_name": "euler",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "36",
        0
      ],
      "positive": [
        "12",
        0
      ],
      "negative": [
        "12",
        1
      ],
      "latent_image": [
        "12",
        2
      ]
    },
    "class_type": "KSampler"
  },
  "40": {
    "inputs": {
      "seed": 124580278781504
    },
    "class_type": "Seed (rgthree)"
  },
  "74": {
    "inputs": {
      "ckpt_name": "rife40.pth",
      "clear_cache_after_n_frames": 10,
      "multiplier": 2,
      "fast_mode": true,
      "ensemble": true,
      "scale_factor": 1
    },
    "class_type": "RIFE VFI"
  },
  "75": {
    "inputs": {
      "ckpt_name": "film_net_fp32.pt",
      "clear_cache_after_n_frames": 10,
      "multiplier": 2,
      "frames": [
        "8",
        0
      ]
    },
    "class_type": "FILM VFI"
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)

    source_image = f"S:/comfy/ComfyUI_windows_portable/ComfyUI/output/{image_name}_00001_.png"
    filename = f"echo_{int(time.time())}_high_res"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    prompt = json.loads(prompt_text)

    if PingPong:
        prompt["26"]["inputs"]["pingpong"] = "true"
    #set the text prompt for our positive CLIPTextEncode 
   # if format == "mp4":

    prompt["23"]["inputs"]["image"] = source_image
    prompt["40"]["inputs"]["seed"] = formatted_number
    #prompt["15"]["inputs"]["seed"] = formatted_number 
    #prompt["15"]["inputs"]["frame_number"] = frame_amount 
    #if frame_amount == 24:
    #    prompt["20"]["inputs"]["batch_size"] = 16



       # prompt["8"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["217"]["inputs"]["vae"] = 240
        #prompt["217"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["218"]["inputs"]["vae"] = 240
       # prompt["218"]["inputs"]["vae"][1] = 0
    #    prompt["8"]["inputs"]["vae"] = ["240", 0]
    #set the seed for our KSampler node
    #prompt["3"]["inputs"]["seed"] = 5

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)
    ws.close()
   # queue_prompt(prompt)

    filename = f"{filename}"

    # Create a list of all the image files
    files = []
  #  for i, image_content in enumerate(images):
        # Generate filename with timestamp and image number
  #      filename = f"generated_image_{i+1}_{int(time.time())}.png"

        # Save the image to "generated" directory
  #      with open(f"generated2/{filename}", "wb") as f:
  #          f.write(base64.b64decode(image_content))

    # Add the image file to the list
    files = []
   # asyncio.sleep(40)
  #  file = discord.File(f"F:/ComfyUI_windows_portable/ComfyUI/output/ProjectAy/{filename}")
  #  files.append(file)
    #embed = discord.Embed()
    #embed.set_image(url=f"attachment://{filename}")

    i=0
    for node_id in images:     
         for image_data in images[node_id]:
             i=i+1
             filename = f"echo_{i}_{int(time.time())}.gif"

             #from PIL import Image
             #import io
            # Save the image to "generated" directory
        #     if i == 4 or i == 5 or i == 6:

             if i == 2 or i == 1:
                with open(f"generatedNewAge/{filename}", "wb") as f:              
                        f.write(image_data)
        # Add the image file to the list
                file = discord.File(f"generatedNewAge/{filename}")
                files.append(file)
           #  if i == 7:
            #    files.append(file)
             #image = Image.open(io.BytesIO(image_data))
             #image.show()



    return files
    #wait_msg.delete()
    #wait_gif.delete()
    #new_message =   message.channel.send(files=files)

############# gudrais ######################
# Function to load data from JSON file

def load_data_from_json(file_name):
    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {}

# Function to save data to JSON file
def save_data_to_json(data, file_name):
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

# Function to update most recent message ID and thread ID in the dictionary
def update_message_data(msg_id, thread_id, file_name):
    data = load_data_from_json(file_name)
    data[msg_id] = thread_id  # Update or create the 'msg_id' key with the new thread_id
    save_data_to_json(data, file_name)


############# gudrais ######################
@to_thread
def  generate_image_turbo_upscale(V4, promptt, neg_prompt,w, h, keyw, model, three, vae, lora, support, seed, upscale):

    server_address = "127.0.0.1:8188"
    client_id = str(uuid.uuid4())

    def queue_prompt(prompt):
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
            return response.read()

    def get_history(prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
            return json.loads(response.read())

    def get_images(ws, prompt):
        prompt_id = queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue #previews are binary data

        history = get_history(prompt_id)[prompt_id]
        for o in history['outputs']:
            for node_id in history['outputs']:
                node_output = history['outputs'][node_id]
                if 'images' in node_output:
                    images_output = []
                    for image in node_output['images']:
                        image_data = get_image(image['filename'], image['subfolder'], image['type'])
                        images_output.append(image_data)
                output_images[node_id] = images_output

        return output_images


    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    V4 = True
    prompt_text = """
{
  "5": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage"
  },
  "6": {
    "inputs": {
      "text": "cinematic portrait photo of old man staring into camera and smiling with teeth, wearing oversized glasses, snowy forest in background",
      "clip": [
        "20",
        1
      ]
    },
    "class_type": "CLIPTextEncode"
  },
  "7": {
    "inputs": {
      "text": "text, watermark",
      "clip": [
        "20",
        1
      ]
    },
    "class_type": "CLIPTextEncode"
  },
  "14": {
    "inputs": {
      "sampler_name": "euler_ancestral"
    },
    "class_type": "KSamplerSelect"
  },
  "20": {
    "inputs": {
      "ckpt_name": "turbo_pixelwaveturbo_01.safetensors"
    },
    "class_type": "CheckpointLoaderSimple"
  },
  "22": {
    "inputs": {
      "steps": 3
    },
    "class_type": "SDTurboScheduler"
  },
  "25": {
    "inputs": {
      "images": [
        "42",
        0
      ]
    },
    "class_type": "PreviewImage"
  },
  "35": {
    "inputs": {
      "model_name": "4x_NMKD-Siax_200k.pth"
    },
    "class_type": "UpscaleModelLoader"
  },
  "36": {
    "inputs": {
      "upscale_model": [
        "35",
        0
      ],
      "image": [
        "42",
        0
      ]
    },
    "class_type": "ImageUpscaleWithModel"
  },
  "37": {
    "inputs": {
      "upscale_method": "area",
      "scale_by": 0.5,
      "image": [
        "36",
        0
      ]
    },
    "class_type": "ImageScaleBy"
  },
  "38": {
    "inputs": {
      "pixels": [
        "37",
        0
      ],
      "vae": [
        "20",
        2
      ]
    },
    "class_type": "VAEEncode"
  },
  "42": {
    "inputs": {
      "samples": [
        "51",
        0
      ],
      "vae": [
        "20",
        2
      ]
    },
    "class_type": "VAEDecode"
  },
  "44": {
    "inputs": {
      "add_noise": "enable",
      "noise_seed": 1053975616190790,
      "steps": 30,
      "cfg": 2,
      "sampler_name": "dpmpp_3m_sde_gpu",
      "scheduler": "karras",
      "start_at_step": 20,
      "end_at_step": 1000,
      "return_with_leftover_noise": "disable",
      "model": [
        "20",
        0
      ],
      "positive": [
        "6",
        0
      ],
      "negative": [
        "7",
        0
      ],
      "latent_image": [
        "38",
        0
      ]
    },
    "class_type": "KSamplerAdvanced"
  },
  "45": {
    "inputs": {
      "samples": [
        "44",
        0
      ],
      "vae": [
        "20",
        2
      ]
    },
    "class_type": "VAEDecode"
  },
  "46": {
    "inputs": {
      "blend_factor": 0.225,
      "blend_mode": "overlay",
      "image1": [
        "45",
        0
      ],
      "image2": [
        "45",
        0
      ]
    },
    "class_type": "ImageBlend"
  },
  "47": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "46",
        0
      ]
    },
    "class_type": "SaveImage"
  },
  "51": {
    "inputs": {
      "add_noise": "enable",
      "noise_seed": 1053975616190790,
      "steps": 5,
      "cfg": 2,
      "sampler_name": "dpmpp_sde_gpu",
      "scheduler": "karras",
      "start_at_step": 0,
      "end_at_step": 10000,
      "return_with_leftover_noise": "disable",
      "model": [
        "20",
        0
      ],
      "positive": [
        "6",
        0
      ],
      "negative": [
        "7",
        0
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSamplerAdvanced"
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"echo_{int(time.time())}_high_res"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    prompt = json.loads(prompt_text)


    #set the text prompt for our positive CLIPTextEncode 
    prompt["6"]["inputs"]["text"] = promptt
    prompt["37"]["inputs"]["scale_by"] = upscale
   # prompt["75"]["inputs"]["text_l"] = support
   # prompt["120"]["inputs"]["text"] = promptt
    prompt["7"]["inputs"]["text"] = neg_prompt
    #prompt["82"]["inputs"]["text_l"] = neg_prompt
   # prompt["81"]["inputs"]["text"] = neg_prompt
    prompt["47"]["inputs"]["filename_prefix"] = filename_h
    #prompt["201"]["inputs"]["filename_prefix"] = filename_l
    prompt["51"]["inputs"]["noise_seed"] = seed 
    #prompt["22"]["inputs"]["noise_seed"] = formatted_number
    #prompt["216"]["inputs"]["noise_seed"] = formatted_number 
    prompt["5"]["inputs"]["width"] = w
    prompt["5"]["inputs"]["height"] = h
    prompt["20"]["inputs"]["ckpt_name"] = model
   # if three:
   #     prompt["60"]["inputs"]["batch_size"] = 3
   # if vae:
  #      prompt["8"]["inputs"]["vae"][0] = "240"
  #      prompt["8"]["inputs"]["vae"][1] = 0
  #      prompt["217"]["inputs"]["vae"][0] = "240"
  #      prompt["217"]["inputs"]["vae"][1] = 0
  #      prompt["218"]["inputs"]["vae"][0] = "240"
  #      prompt["218"]["inputs"]["vae"][1] = 0
 #   if lora:
 #       prompt["22"]["inputs"]["model"][0] = "241"
  #      prompt["75"]["inputs"]["clip"][0] = "241"
  #      prompt["82"]["inputs"]["clip"][0] = "241"
   #     prompt["216"]["inputs"]["model"][0] = "241"


       # prompt["8"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["217"]["inputs"]["vae"] = 240
        #prompt["217"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["218"]["inputs"]["vae"] = 240
       # prompt["218"]["inputs"]["vae"][1] = 0
    #    prompt["8"]["inputs"]["vae"] = ["240", 0]
    #set the seed for our KSampler node
    #prompt["3"]["inputs"]["seed"] = 5

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)
    ws.close()
   # queue_prompt(prompt)

    filename = f"{filename}"
    if keyw.lower() == "echoais":
        filename = f"SPOILER_{filename}"
    # Create a list of all the image files
    files = []
  #  for i, image_content in enumerate(images):
        # Generate filename with timestamp and image number
  #      filename = f"generated_image_{i+1}_{int(time.time())}.png"

        # Save the image to "generated" directory
  #      with open(f"generated2/{filename}", "wb") as f:
  #          f.write(base64.b64decode(image_content))

    # Add the image file to the list
    files = []
   # asyncio.sleep(40)
  #  file = discord.File(f"F:/ComfyUI_windows_portable/ComfyUI/output/ProjectAy/{filename}")
  #  files.append(file)
    #embed = discord.Embed()
    #embed.set_image(url=f"attachment://{filename}")

    i=0
    for node_id in images:     
         for image_data in images[node_id]:
             i=i+1
             filename = f"echo_{i}_{int(time.time())}.png"
             if keyw.lower() == "echoais":
                filename = f"SPOILER_{filename}"
             #from PIL import Image
             #import io
            # Save the image to "generated" directory
        #     if i == 4 or i == 5 or i == 6:
             if three:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
             else:
                 if i == 2:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
           #  if i == 7:
            #    files.append(file)
             #image = Image.open(io.BytesIO(image_data))
             #image.show()



    return files, filename_h
    #wait_msg.delete()
    #wait_gif.delete()
    #new_message =   message.channel.send(files=files)

@to_thread
def  generate_image_turbo(V4, promptt, neg_prompt,w, h, keyw, model, three, vae, lora, support):

    server_address = "127.0.0.1:8188"
    client_id = str(uuid.uuid4())

    def queue_prompt(prompt):
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
            return response.read()

    def get_history(prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
            return json.loads(response.read())

    def get_images(ws, prompt):
        prompt_id = queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue #previews are binary data

        history = get_history(prompt_id)[prompt_id]
        for o in history['outputs']:
            for node_id in history['outputs']:
                node_output = history['outputs'][node_id]
                if 'images' in node_output:
                    images_output = []
                    for image in node_output['images']:
                        image_data = get_image(image['filename'], image['subfolder'], image['type'])
                        images_output.append(image_data)
                output_images[node_id] = images_output

        return output_images


    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    V4 = True
    prompt_text = """
{
  "20": {
    "inputs": {
      "ckpt_name": "turbo_pixelwaveturbo_01.safetensors"
    },
    "class_type": "CheckpointLoaderSimple"
  },
  "44": {
    "inputs": {
      "add_noise": "enable",
      "noise_seed": 134312246023121,
      "steps": 5,
      "cfg": 2,
      "sampler_name": "dpmpp_sde_gpu",
      "scheduler": "karras",
      "start_at_step": 0,
      "end_at_step": 10000,
      "return_with_leftover_noise": "disable",
      "model": [
        "20",
        0
      ],
      "positive": [
        "57",
        0
      ],
      "negative": [
        "58",
        0
      ],
      "latent_image": [
        "60",
        0
      ]
    },
    "class_type": "KSamplerAdvanced"
  },
  "49": {
    "inputs": {
      "samples": [
        "44",
        0
      ],
      "vae": [
        "20",
        2
      ]
    },
    "class_type": "VAEDecode"
  },
  "57": {
    "inputs": {
      "text": "afro donald trump shooting gun",
      "clip": [
        "20",
        1
      ]
    },
    "class_type": "CLIPTextEncode"
  },
  "58": {
    "inputs": {
      "text": "",
      "clip": [
        "20",
        1
      ]
    },
    "class_type": "CLIPTextEncode"
  },
  "60": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage"
  },
  "61": {
    "inputs": {
      "filename_prefix": "Turbo",
      "images": [
        "49",
        0
      ]
    },
    "class_type": "SaveImage"
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"echo_{int(time.time())}_high_res"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    prompt = json.loads(prompt_text)


    #set the text prompt for our positive CLIPTextEncode 
    prompt["57"]["inputs"]["text"] = promptt
   # prompt["75"]["inputs"]["text_l"] = support
   # prompt["120"]["inputs"]["text"] = promptt
    prompt["58"]["inputs"]["text"] = neg_prompt
    #prompt["82"]["inputs"]["text_l"] = neg_prompt
   # prompt["81"]["inputs"]["text"] = neg_prompt
    prompt["61"]["inputs"]["filename_prefix"] = filename_h
    #prompt["201"]["inputs"]["filename_prefix"] = filename_l
    prompt["44"]["inputs"]["noise_seed"] = formatted_number 
    #prompt["22"]["inputs"]["noise_seed"] = formatted_number
    #prompt["216"]["inputs"]["noise_seed"] = formatted_number 
    prompt["60"]["inputs"]["width"] = w
    prompt["60"]["inputs"]["height"] = h
    prompt["20"]["inputs"]["ckpt_name"] = model
    if three:
        prompt["60"]["inputs"]["batch_size"] = 3
   # if vae:
  #      prompt["8"]["inputs"]["vae"][0] = "240"
  #      prompt["8"]["inputs"]["vae"][1] = 0
  #      prompt["217"]["inputs"]["vae"][0] = "240"
  #      prompt["217"]["inputs"]["vae"][1] = 0
  #      prompt["218"]["inputs"]["vae"][0] = "240"
  #      prompt["218"]["inputs"]["vae"][1] = 0
 #   if lora:
 #       prompt["22"]["inputs"]["model"][0] = "241"
  #      prompt["75"]["inputs"]["clip"][0] = "241"
  #      prompt["82"]["inputs"]["clip"][0] = "241"
   #     prompt["216"]["inputs"]["model"][0] = "241"


       # prompt["8"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["217"]["inputs"]["vae"] = 240
        #prompt["217"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["218"]["inputs"]["vae"] = 240
       # prompt["218"]["inputs"]["vae"][1] = 0
    #    prompt["8"]["inputs"]["vae"] = ["240", 0]
    #set the seed for our KSampler node
    #prompt["3"]["inputs"]["seed"] = 5

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)
    ws.close()
   # queue_prompt(prompt)

    filename = f"{filename}"
    if keyw.lower() == "echoais":
        filename = f"SPOILER_{filename}"
    # Create a list of all the image files
    files = []
  #  for i, image_content in enumerate(images):
        # Generate filename with timestamp and image number
  #      filename = f"generated_image_{i+1}_{int(time.time())}.png"

        # Save the image to "generated" directory
  #      with open(f"generated2/{filename}", "wb") as f:
  #          f.write(base64.b64decode(image_content))

    # Add the image file to the list
    files = []
   # asyncio.sleep(40)
  #  file = discord.File(f"F:/ComfyUI_windows_portable/ComfyUI/output/ProjectAy/{filename}")
  #  files.append(file)
    #embed = discord.Embed()
    #embed.set_image(url=f"attachment://{filename}")

    i=0
    for node_id in images:     
         for image_data in images[node_id]:
             i=i+1
             filename = f"echo_{i}_{int(time.time())}.png"
             if keyw.lower() == "echoais":
                filename = f"SPOILER_{filename}"
             #from PIL import Image
             #import io
            # Save the image to "generated" directory
        #     if i == 4 or i == 5 or i == 6:
             if three:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
             else:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
           #  if i == 7:
            #    files.append(file)
             #image = Image.open(io.BytesIO(image_data))
             #image.show()



    return files, filename_h, formatted_number
    #wait_msg.delete()
    #wait_gif.delete()
    #new_message =   message.channel.send(files=files)



@to_thread
def  generate_image_refiner(V4, promptt, neg_prompt,w, h, keyw, model, three, vae, lora, support):

    server_address = "127.0.0.1:8188"
    client_id = str(uuid.uuid4())

    def queue_prompt(prompt):
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
            return response.read()

    def get_history(prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
            return json.loads(response.read())

    def get_images(ws, prompt):
        prompt_id = queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue #previews are binary data

        history = get_history(prompt_id)[prompt_id]
        for o in history['outputs']:
            for node_id in history['outputs']:
                node_output = history['outputs'][node_id]
                if 'images' in node_output:
                    images_output = []
                    for image in node_output['images']:
                        image_data = get_image(image['filename'], image['subfolder'], image['type'])
                        images_output.append(image_data)
                output_images[node_id] = images_output

        return output_images


    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    V4 = True
    prompt_text = """
 {
  "4": {
    "inputs": {
      "ckpt_name": "sdXL_v10RefinerVAEFix.safetensors"
    },
    "class_type": "CheckpointLoaderSimple"
  },
  "5": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage"
  },
  "8": {
    "inputs": {
      "samples": [
        "23",
        0
      ],
      "vae": [
        "240",
        0
      ]
    },
    "class_type": "VAEDecode"
  },
  "10": {
    "inputs": {
      "ckpt_name": "sdXL_v10VAEFix.safetensors"
    },
    "class_type": "CheckpointLoaderSimple"
  },
  "22": {
    "inputs": {
      "add_noise": "enable",
      "noise_seed": 1023483346657349,
      "steps": 60,
      "cfg": 3.6,
      "sampler_name": "dpmpp_3m_sde",
      "scheduler": "karras",
      "start_at_step": 0,
      "end_at_step": 48,
      "return_with_leftover_noise": "enable",
      "model": [
        "239",
        0
      ],
      "positive": [
        "75",
        0
      ],
      "negative": [
        "82",
        0
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSamplerAdvanced"
  },
  "23": {
    "inputs": {
      "add_noise": "disable",
      "noise_seed": 1023483346657349,
      "steps": 60,
      "cfg": 3.6,
      "sampler_name": "dpmpp_3m_sde",
      "scheduler": "karras",
      "start_at_step": 48,
      "end_at_step": 1000,
      "return_with_leftover_noise": "disable",
      "model": [
        "4",
        0
      ],
      "positive": [
        "120",
        0
      ],
      "negative": [
        "81",
        0
      ],
      "latent_image": [
        "22",
        0
      ]
    },
    "class_type": "KSamplerAdvanced"
  },
  "75": {
    "inputs": {
      "width": 2048,
      "height": 2048,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 2048,
      "target_height": 2048,
      "text_g": "Grim Reaper at a Halloween Party, with his dark cloak and scythe, surrounded by ghostly souls he has taken. The party is in full swing, with pumpkins, cobwebs, and eerie lighting. The atmosphere is a mix of fear and merriment, filled with laughter and chilling whispers.",
      "text_l": "Grim Reaper at a Halloween Party, with his dark cloak and scythe, surrounded by ghostly souls he has taken. The party is in full swing, with pumpkins, cobwebs, and eerie lighting. The atmosphere is a mix of fear and merriment, filled with laughter and chilling whispers.",
      "clip": [
        "239",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL"
  },
  "81": {
    "inputs": {
      "ascore": 2,
      "width": 2048,
      "height": 2048,
      "text": "bad quality, bad anatomy, worst quality, low quality, lowres, extra fingers, blur, blurry, ugly, wrong proportions, watermark, image artifacts",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXLRefiner"
  },
  "82": {
    "inputs": {
      "width": 2048,
      "height": 2048,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 2048,
      "target_height": 2048,
      "text_g": "bad quality, bad anatomy, worst quality, low quality, lowres, extra fingers, blur, blurry, ugly, wrong proportions, watermark, image artifacts",
      "text_l": "bad quality, bad anatomy, worst quality, low quality, lowres, extra fingers, blur, blurry, ugly, wrong proportions, watermark, image artifacts",
      "clip": [
        "239",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL"
  },
  "120": {
    "inputs": {
      "ascore": 6,
      "width": 2048,
      "height": 2048,
      "text": "Grim Reaper at a Halloween Party, with his dark cloak and scythe, surrounded by ghostly souls he has taken. The party is in full swing, with pumpkins, cobwebs, and eerie lighting. The atmosphere is a mix of fear and merriment, filled with laughter and chilling whispers.",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXLRefiner"
  },
  "184": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage"
  },
  "187": {
    "inputs": {
      "model_name": "4x_NMKD-Siax_200k.pth"
    },
    "class_type": "UpscaleModelLoader"
  },
  "201": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "221",
        0
      ]
    },
    "class_type": "SaveImage"
  },
  "213": {
    "inputs": {
      "upscale_model": [
        "187",
        0
      ],
      "image": [
        "8",
        0
      ]
    },
    "class_type": "ImageUpscaleWithModel"
  },
  "215": {
    "inputs": {
      "upscale_method": "area",
      "scale_by": 0.375,
      "image": [
        "213",
        0
      ]
    },
    "class_type": "ImageScaleBy"
  },
  "216": {
    "inputs": {
      "add_noise": "enable",
      "noise_seed": 1023483346657349,
      "steps": 30,
      "cfg": 3.6,
      "sampler_name": "dpmpp_3m_sde",
      "scheduler": "karras",
      "start_at_step": 20,
      "end_at_step": 1000,
      "return_with_leftover_noise": "disable",
      "model": [
        "239",
        0
      ],
      "positive": [
        "75",
        0
      ],
      "negative": [
        "82",
        0
      ],
      "latent_image": [
        "217",
        0
      ]
    },
    "class_type": "KSamplerAdvanced"
  },
  "217": {
    "inputs": {
      "pixels": [
        "215",
        0
      ],
      "vae": [
        "240",
        0
      ]
    },
    "class_type": "VAEEncode"
  },
  "218": {
    "inputs": {
      "samples": [
        "216",
        0
      ],
      "vae": [
        "240",
        0
      ]
    },
    "class_type": "VAEDecode"
  },
  "221": {
    "inputs": {
      "blend_factor": 0.225,
      "blend_mode": "overlay",
      "image1": [
        "218",
        0
      ],
      "image2": [
        "218",
        0
      ]
    },
    "class_type": "ImageBlend"
  },
  "239": {
    "inputs": {
      "lora_name": "xl_more_art-full_v1.safetensors",
      "strength_model": 0.8,
      "strength_clip": 0.8,
      "model": [
        "10",
        0
      ],
      "clip": [
        "10",
        1
      ]
    },
    "class_type": "LoraLoader"
  },
  "240": {
    "inputs": {
      "vae_name": "sdxl_vae.safetensors"
    },
    "class_type": "VAELoader"
    },
  "241": {
    "inputs": {
      "lora_name": "add-detail-xl.safetensors",
      "strength_model": 1,
      "strength_clip": 1,
      "model": [
        "239",
        0
      ],
      "clip": [
        "239",
        1
      ]
    },
    "class_type": "LoraLoader"
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"echo_{int(time.time())}_high_res"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    prompt = json.loads(prompt_text)


    #set the text prompt for our positive CLIPTextEncode 
    prompt["75"]["inputs"]["text_g"] = promptt
    prompt["75"]["inputs"]["text_l"] = support
    prompt["120"]["inputs"]["text"] = promptt
    prompt["82"]["inputs"]["text_g"] = neg_prompt
    prompt["82"]["inputs"]["text_l"] = neg_prompt
    prompt["81"]["inputs"]["text"] = neg_prompt
    prompt["184"]["inputs"]["filename_prefix"] = filename_h
    prompt["201"]["inputs"]["filename_prefix"] = filename_l
    prompt["23"]["inputs"]["noise_seed"] = formatted_number 
    prompt["22"]["inputs"]["noise_seed"] = formatted_number
    prompt["216"]["inputs"]["noise_seed"] = formatted_number 
    prompt["5"]["inputs"]["width"] = w
    prompt["5"]["inputs"]["height"] = h
    prompt["10"]["inputs"]["ckpt_name"] = model
    if three:
        prompt["5"]["inputs"]["batch_size"] = 3
    if vae:
        prompt["8"]["inputs"]["vae"][0] = "240"
        prompt["8"]["inputs"]["vae"][1] = 0
        prompt["217"]["inputs"]["vae"][0] = "240"
        prompt["217"]["inputs"]["vae"][1] = 0
        prompt["218"]["inputs"]["vae"][0] = "240"
        prompt["218"]["inputs"]["vae"][1] = 0
    if lora:
        prompt["22"]["inputs"]["model"][0] = "241"
        prompt["75"]["inputs"]["clip"][0] = "241"
        prompt["82"]["inputs"]["clip"][0] = "241"
        prompt["216"]["inputs"]["model"][0] = "241"


       # prompt["8"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["217"]["inputs"]["vae"] = 240
        #prompt["217"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["218"]["inputs"]["vae"] = 240
       # prompt["218"]["inputs"]["vae"][1] = 0
    #    prompt["8"]["inputs"]["vae"] = ["240", 0]
    #set the seed for our KSampler node
    #prompt["3"]["inputs"]["seed"] = 5

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)
    ws.close()
   # queue_prompt(prompt)

    filename = f"{filename}"
    if keyw.lower() == "echoais":
        filename = f"SPOILER_{filename}"
    # Create a list of all the image files
    files = []
  #  for i, image_content in enumerate(images):
        # Generate filename with timestamp and image number
  #      filename = f"generated_image_{i+1}_{int(time.time())}.png"

        # Save the image to "generated" directory
  #      with open(f"generated2/{filename}", "wb") as f:
  #          f.write(base64.b64decode(image_content))

    # Add the image file to the list
    files = []
   # asyncio.sleep(40)
  #  file = discord.File(f"F:/ComfyUI_windows_portable/ComfyUI/output/ProjectAy/{filename}")
  #  files.append(file)
    #embed = discord.Embed()
    #embed.set_image(url=f"attachment://{filename}")

    i=0
    for node_id in images:     
         for image_data in images[node_id]:
             i=i+1
             filename = f"echo_{i}_{int(time.time())}.png"
             if keyw.lower() == "echoais":
                filename = f"SPOILER_{filename}"
             #from PIL import Image
             #import io
            # Save the image to "generated" directory
        #     if i == 4 or i == 5 or i == 6:
             if three:
                if i == 4 or i == 5 or i == 6:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
             else:
                 if i == 2:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
           #  if i == 7:
            #    files.append(file)
             #image = Image.open(io.BytesIO(image_data))
             #image.show()



    return files, filename_h
    #wait_msg.delete()
    #wait_gif.delete()
    #new_message =   message.channel.send(files=files)

@to_thread
def  generate_image_cascade(V4, promptt, neg_prompt,w, h, keyw, three, vae, lora, support):

    server_address = "127.0.0.1:8188"
    client_id = str(uuid.uuid4())

    def queue_prompt(prompt):
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
            return response.read()

    def get_history(prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
            return json.loads(response.read())

    def get_images(ws, prompt):
        prompt_id = queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue #previews are binary data

        history = get_history(prompt_id)[prompt_id]
        #for o in history['outputs']:
            #for node_id in history['outputs']:
        node_output = history['outputs']["76"]
        if 'images' in node_output:
            images_output = []
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
        output_images["76"] = images_output

        return output_images


    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    V4 = True
    prompt_text = """
    {
      "3": {
        "inputs": {
          "seed": [
            "62",
            0
          ],
          "steps": 40,
          "cfg": 5,
          "sampler_name": "dpmpp_3m_sde_gpu",
          "scheduler": "simple",
          "denoise": 1,
          "model": [
            "41",
            0
          ],
          "positive": [
            "53",
            0
          ],
          "negative": [
            "54",
            0
          ],
          "latent_image": [
            "34",
            0
          ]
        },
        "class_type": "KSampler",
        "_meta": {
          "title": "KSampler"
        }
      },
      "8": {
        "inputs": {
          "samples": [
            "33",
            0
          ],
          "vae": [
            "42",
            2
          ]
        },
        "class_type": "VAEDecode",
        "_meta": {
          "title": "VAE Decode"
        }
      },
      "33": {
        "inputs": {
          "seed": [
            "62",
            0
          ],
          "steps": 10,
          "cfg": 1.1,
          "sampler_name": "dpmpp_3m_sde_gpu",
          "scheduler": "simple",
          "denoise": 1,
          "model": [
            "42",
            0
          ],
          "positive": [
            "36",
            0
          ],
          "negative": [
            "40",
            0
          ],
          "latent_image": [
            "51",
            0
          ]
        },
        "class_type": "KSampler",
        "_meta": {
          "title": "KSampler"
        }
      },
      "34": {
        "inputs": {
          "width": 1024,
          "height": 1024,
          "compression": 32,
          "batch_size": 1
        },
        "class_type": "StableCascade_EmptyLatentImage",
        "_meta": {
          "title": "StableCascade_EmptyLatentImage"
        }
      },
      "36": {
        "inputs": {
          "conditioning": [
            "40",
            0
          ],
          "stage_c": [
            "3",
            0
          ]
        },
        "class_type": "StableCascade_StageB_Conditioning",
        "_meta": {
          "title": "StableCascade_StageB_Conditioning"
        }
      },
      "40": {
        "inputs": {
          "conditioning": [
            "53",
            0
          ]
        },
        "class_type": "ConditioningZeroOut",
        "_meta": {
          "title": "ConditioningZeroOut"
        }
      },
      "41": {
        "inputs": {
          "ckpt_name": "stable_cascade_stage_c.safetensors"
        },
        "class_type": "CheckpointLoaderSimple",
        "_meta": {
          "title": "Load Checkpoint"
        }
      },
      "42": {
        "inputs": {
          "ckpt_name": "stable_cascade_stage_b.safetensors"
        },
        "class_type": "CheckpointLoaderSimple",
        "_meta": {
          "title": "Load Checkpoint"
        }
      },
      "47": {
        "inputs": {
          "text": "macro shot of mushroom in forest, light rays shining though leafs and mushroom, branches of broken wood in background"
        },
        "class_type": "JWStringMultiline",
        "_meta": {
          "title": "String (Multiline)"
        }
      },
      "48": {
        "inputs": {
          "prompt": [
            "47",
            0
          ],
          "seed": [
            "62",
            0
          ]
        },
        "class_type": "Wildcard Processor",
        "_meta": {
          "title": "Wildcard Processor (Mikey)"
        }
      },
      "50": {
        "inputs": {
          "label": "md_prompt_pos",
          "text_value": [
            "48",
            0
          ],
          "image": [
            "8",
            0
          ]
        },
        "class_type": "AddMetaData",
        "_meta": {
          "title": "AddMetaData (Mikey)"
        }
      },
      "51": {
        "inputs": {
          "upscale_method": "bicubic",
          "scale_by": 2,
          "samples": [
            "34",
            1
          ]
        },
        "class_type": "LatentUpscaleBy",
        "_meta": {
          "title": "Upscale Latent By"
        }
      },
      "52": {
        "inputs": {
          "text": [
            "48",
            0
          ]
        },
        "class_type": "ShowText|pysssss",
        "_meta": {
          "title": "Processed Positive 🐍"
        }
      },
      "53": {
        "inputs": {
          "text": [
            "48",
            0
          ],
          "parser": "fixed attention",
          "mean_normalization": true,
          "multi_conditioning": true,
          "use_old_emphasis_implementation": false,
          "with_SDXL": false,
          "ascore": 6,
          "width": 1024,
          "height": 1024,
          "crop_w": 0,
          "crop_h": 0,
          "target_width": 1024,
          "target_height": 1024,
          "text_g": "",
          "text_l": "",
          "smZ_steps": 1,
          "clip": [
            "41",
            1
          ]
        },
        "class_type": "smZ CLIPTextEncode",
        "_meta": {
          "title": "CLIP Text Encode++"
        }
      },
      "54": {
        "inputs": {
          "text": [
            "55",
            0
          ],
          "parser": "fixed attention",
          "mean_normalization": true,
          "multi_conditioning": true,
          "use_old_emphasis_implementation": false,
          "with_SDXL": false,
          "ascore": 6,
          "width": 1024,
          "height": 1024,
          "crop_w": 0,
          "crop_h": 0,
          "target_width": 1024,
          "target_height": 1024,
          "text_g": "",
          "text_l": "",
          "smZ_steps": 1,
          "clip": [
            "41",
            1
          ]
        },
        "class_type": "smZ CLIPTextEncode",
        "_meta": {
          "title": "CLIP Text Encode++"
        }
      },
      "55": {
        "inputs": {
          "text": "multiple people, duplicates"
        },
        "class_type": "JWStringMultiline",
        "_meta": {
          "title": "String (Multiline)"
        }
      },
      "62": {
        "inputs": {
          "seed": 633921589008396
        },
        "class_type": "Seed String",
        "_meta": {
          "title": "Seed String (Mikey)"
        }
      },
      "76": {
        "inputs": {
          "filename_prefix": "ComfyUI",
          "images": [
            "50",
            0
          ]
        },
        "class_type": "SaveImage",
        "_meta": {
          "title": "Save Image"
        }
      },
      "64": {
        "inputs": {
          "images": [
            "50",
            0
          ]
        },
        "class_type": "PreviewImage",
        "_meta": {
          "title": "Preview Image"
        }
      }
    }
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"echo_{int(time.time())}_high_res"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    prompt = json.loads(prompt_text)


    #set the text prompt for our positive CLIPTextEncode 
    prompt["47"]["inputs"]["text"] = promptt
   #prompt["75"]["inputs"]["text_l"] = support
    #prompt["120"]["inputs"]["text"] = promptt
   # prompt["82"]["inputs"]["text_g"] = neg_prompt
    prompt["55"]["inputs"]["text"] = neg_prompt
   # prompt["81"]["inputs"]["text"] = neg_prompt
    prompt["76"]["inputs"]["filename_prefix"] = filename_h
    #prompt["201"]["inputs"]["filename_prefix"] = filename_l
    prompt["62"]["inputs"]["seed"] = formatted_number 
   # prompt["22"]["inputs"]["noise_seed"] = formatted_number
    #prompt["216"]["inputs"]["noise_seed"] = formatted_number 
    prompt["34"]["inputs"]["width"] = w
    prompt["34"]["inputs"]["height"] = h
    #prompt["10"]["inputs"]["ckpt_name"] = model
    if three:
        prompt["34"]["inputs"]["batch_size"] = 3
    if vae:
        prompt["8"]["inputs"]["vae"][0] = "240"
        prompt["8"]["inputs"]["vae"][1] = 0
        prompt["217"]["inputs"]["vae"][0] = "240"
        prompt["217"]["inputs"]["vae"][1] = 0
        prompt["218"]["inputs"]["vae"][0] = "240"
        prompt["218"]["inputs"]["vae"][1] = 0
    lora = False
    if lora:
        prompt["22"]["inputs"]["model"][0] = "241"
        prompt["75"]["inputs"]["clip"][0] = "241"
        prompt["82"]["inputs"]["clip"][0] = "241"
        prompt["216"]["inputs"]["model"][0] = "241"


       # prompt["8"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["217"]["inputs"]["vae"] = 240
        #prompt["217"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["218"]["inputs"]["vae"] = 240
       # prompt["218"]["inputs"]["vae"][1] = 0
    #    prompt["8"]["inputs"]["vae"] = ["240", 0]
    #set the seed for our KSampler node
    #prompt["3"]["inputs"]["seed"] = 5

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)
    ws.close()

   # queue_prompt(prompt)

    filename = f"{filename}"
    if keyw.lower() == "echoais":
        filename = f"SPOILER_{filename}"
    # Create a list of all the image files
    files = []
  #  for i, image_content in enumerate(images):
        # Generate filename with timestamp and image number
  #      filename = f"generated_image_{i+1}_{int(time.time())}.png"

        # Save the image to "generated" directory
  #      with open(f"generated2/{filename}", "wb") as f:
  #          f.write(base64.b64decode(image_content))

    # Add the image file to the list
    files = []
   # asyncio.sleep(40)
  #  file = discord.File(f"F:/ComfyUI_windows_portable/ComfyUI/output/ProjectAy/{filename}")
  #  files.append(file)
    #embed = discord.Embed()
    #embed.set_image(url=f"attachment://{filename}")

    i=0
    for node_id in images:     
         for image_data in images[node_id]:
             i=i+1
             filename = f"echo_{i}_{int(time.time())}.png"
             if keyw.lower() == "echoais":
                filename = f"SPOILER_{filename}"
             #from PIL import Image
             #import io
            # Save the image to "generated" directory
        #     if i == 4 or i == 5 or i == 6:
             if three:
                if i == 1 or i == 2 or i == 3:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
             else:
                 if i == 1:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
           #  if i == 7:
            #    files.append(file)
             #image = Image.open(io.BytesIO(image_data))
             #image.show()



    return files, filename_h
@to_thread
def  generate_image_cascade_v2(V4, promptt, neg_prompt,w, h, keyw, three, vae, lora, support):

    server_address = "127.0.0.1:8188"
    client_id = str(uuid.uuid4())

    def queue_prompt(prompt):
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
            return response.read()

    def get_history(prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
            return json.loads(response.read())

    def get_images(ws, prompt):
        prompt_id = queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue #previews are binary data

        history = get_history(prompt_id)[prompt_id]
        #for o in history['outputs']:
            #for node_id in history['outputs']:
        node_output = history['outputs']["76"]
        if 'images' in node_output:
            images_output = []
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
        output_images["76"] = images_output

        return output_images


    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    V4 = True
    prompt_text = """
    {
      "41": {
        "inputs": {
          "value": 1593545653,
          "mode": true,
          "action": "randomize",
          "last_seed": 2931705346
        },
        "class_type": "GlobalSeed //Inspire",
        "_meta": {
          "title": "Global Seed (Inspire)"
        }
      },
      "52": {
        "inputs": {
          "wildcard_text": "spongobob as butcher cutting meat, horrific",
          "populated_text": "spongobob as butcher cutting meat, horrific",
          "mode": true,
          "seed": 1593545653,
          "Select to add Wildcard": "Select the Wildcard to add to the text"
        },
        "class_type": "ImpactWildcardProcessor",
        "_meta": {
          "title": "ImpactWildcardProcessor"
        }
      },
      "53": {
        "inputs": {
          "text_positive": [
            "52",
            0
          ],
          "text_negative": "",
          "style": "sai-cinematic",
          "log_prompt": false,
          "style_positive": false,
          "style_negative": false
        },
        "class_type": "SDXLPromptStyler",
        "_meta": {
          "title": "SDXL Prompt Styler"
        }
      },
      "54": {
        "inputs": {
          "text_positive": [
            "55",
            0
          ],
          "text_negative": [
            "55",
            1
          ],
          "style": "sai-enhance",
          "log_prompt": false,
          "style_positive": false,
          "style_negative": false
        },
        "class_type": "SDXLPromptStyler",
        "_meta": {
          "title": "SDXL Prompt Styler"
        }
      },
      "55": {
        "inputs": {
          "text_positive": [
            "53",
            0
          ],
          "text_negative": [
            "53",
            1
          ],
          "style": "sai-fantasy art",
          "log_prompt": false,
          "style_positive": false,
          "style_negative": false
        },
        "class_type": "SDXLPromptStyler",
        "_meta": {
          "title": "SDXL Prompt Styler"
        }
      },
      "68": {
        "inputs": {
          "CONDITIONING": [
            "172",
            0
          ]
        },
        "class_type": "Prompts Everywhere",
        "_meta": {
          "title": "Prompts Everywhere"
        }
      },
      "84": {
        "inputs": {
          "output_path": "comfyui",
          "filename_prefix": "[time(%Y-%m-%d)]",
          "filename_delimiter": "_",
          "filename_number_padding": 4,
          "filename_number_start": "false",
          "extension": "png",
          "quality": 100,
          "lossless_webp": "false",
          "overwrite_mode": "false",
          "show_history": "false",
          "show_history_by_prefix": "true",
          "embed_workflow": "true",
          "show_previews": "false",
          "images": [
            "117",
            0
          ]
        },
        "class_type": "Image Save",
        "_meta": {
          "title": "Image Save"
        }
      },
      "85": {
        "inputs": {
          "jpeg_artifact_level": 95,
          "noise_level": 10,
          "adjust_brightness": 0,
          "adjust_color": 0,
          "adjust_contrast": 0,
          "seed": 1593545653,
          "pixels": [
            "87",
            0
          ]
        },
        "class_type": "Dequality",
        "_meta": {
          "title": "Dequality"
        }
      },
      "86": {
        "inputs": {
          "mode": "on empty queue",
          "volume": 0.30000000000000004,
          "file": "notify.mp3",
          "any": [
            "117",
            0
          ]
        },
        "class_type": "PlaySound|pysssss",
        "_meta": {
          "title": "PlaySound 🐍"
        }
      },
      "87": {
        "inputs": {
          "saturation": 1.05,
          "contrast": 0.9500000000000001,
          "brightness": 0.9500000000000001,
          "sharpness": 0.8,
          "highpass_radius": 4,
          "highpass_samples": 1,
          "highpass_strength": 0.8,
          "colorize": "false",
          "image": [
            "117",
            0
          ]
        },
        "class_type": "Image Dragan Photography Filter",
        "_meta": {
          "title": "Image Dragan Photography Filter"
        }
      },
      "104": {
        "inputs": {
          "width": 1024,
          "height": 1024,
          "compression": 46,
          "batch_size": 1
        },
        "class_type": "StableCascade_EmptyLatentImage",
        "_meta": {
          "title": "StableCascade_EmptyLatentImage"
        }
      },
      "106": {
        "inputs": {
          "conditioning": [
            "171",
            0
          ]
        },
        "class_type": "ConditioningZeroOut",
        "_meta": {
          "title": "ConditioningZeroOut"
        }
      },
      "107": {
        "inputs": {
          "conditioning": [
            "106",
            0
          ],
          "stage_c": [
            "239",
            0
          ]
        },
        "class_type": "StableCascade_StageB_Conditioning",
        "_meta": {
          "title": "StableCascade_StageB_Conditioning"
        }
      },
      "116": {
        "inputs": {
          "seed": 1593545653,
          "steps": 15,
          "cfg": 1.1,
          "sampler_name": "euler_ancestral",
          "scheduler": "simple",
          "denoise": 1,
          "positive": [
            "107",
            0
          ],
          "negative": [
            "106",
            0
          ],
          "latent_image": [
            "104",
            1
          ]
        },
        "class_type": "KSampler",
        "_meta": {
          "title": "Stage B Sampler"
        }
      },
      "117": {
        "inputs": {
          "samples": [
            "116",
            0
          ]
        },
        "class_type": "VAEDecode",
        "_meta": {
          "title": "VAE Decode"
        }
      },
      "141": {
        "inputs": {
          "samples": [
            "148",
            0
          ],
          "vae": [
            "142",
            0
          ]
        },
        "class_type": "VAEDecode",
        "_meta": {
          "title": "VAE Decode"
        }
      },
      "142": {
        "inputs": {
          "vae_name": "previewer.safetensors"
        },
        "class_type": "VAELoader",
        "_meta": {
          "title": "Load VAE"
        }
      },
      "143": {
        "inputs": {
          "images": [
            "141",
            0
          ]
        },
        "class_type": "PreviewImage",
        "_meta": {
          "title": "Preview Image"
        }
      },
      "148": {
        "inputs": {
          "seed": 1593545653,
          "steps": 40,
          "cfg": 6,
          "sampler_name": "euler_ancestral",
          "scheduler": "simple",
          "denoise": 1,
          "segments": "[2, 3, 19.35, 40.79], [2, 3, 1.09, 1.92], [3, 6, 0.59, 1.09], [3, 6, 0.30, 0.59], [3, 25, 0.06, 0.30]",
          "restart_scheduler": "karras",
          "model": [
            "174",
            0
          ],
          "latent_image": [
            "104",
            0
          ]
        },
        "class_type": "KRestartSampler",
        "_meta": {
          "title": "Stage C1 Sampler with restarts"
        }
      },
      "171": {
        "inputs": {
          "text": [
            "54",
            0
          ],
          "parser": "fixed attention",
          "mean_normalization": true,
          "multi_conditioning": true,
          "use_old_emphasis_implementation": false,
          "with_SDXL": false,
          "ascore": 6,
          "width": 1024,
          "height": 1024,
          "crop_w": 0,
          "crop_h": 0,
          "target_width": 1024,
          "target_height": 1024,
          "text_g": "",
          "text_l": "",
          "smZ_steps": 1
        },
        "class_type": "smZ CLIPTextEncode",
        "_meta": {
          "title": "CLIP Text Encode++"
        }
      },
      "172": {
        "inputs": {
          "text": [
            "54",
            1
          ],
          "parser": "fixed attention",
          "mean_normalization": true,
          "multi_conditioning": true,
          "use_old_emphasis_implementation": false,
          "with_SDXL": false,
          "ascore": 6,
          "width": 1024,
          "height": 1024,
          "crop_w": 0,
          "crop_h": 0,
          "target_width": 1024,
          "target_height": 1024,
          "text_g": "",
          "text_l": "",
          "smZ_steps": 1
        },
        "class_type": "smZ CLIPTextEncode",
        "_meta": {
          "title": "CLIP Text Encode++"
        }
      },
      "173": {
        "inputs": {
          "ckpt_name": "stable_cascade_stage_b.safetensors"
        },
        "class_type": "CheckpointLoaderSimple",
        "_meta": {
          "title": "Stage-B Loader"
        }
      },
      "174": {
        "inputs": {
          "ckpt_name": "stable_cascade_stage_c.safetensors"
        },
        "class_type": "CheckpointLoaderSimple",
        "_meta": {
          "title": "Stage-C Loader"
        }
      },
      "191": {
        "inputs": {
          "CLIP": [
            "174",
            1
          ]
        },
        "class_type": "Anything Everywhere",
        "_meta": {
          "title": "CLIP Everywhere"
        }
      },
      "192": {
        "inputs": {
          "VAE": [
            "173",
            2
          ]
        },
        "class_type": "Anything Everywhere",
        "_meta": {
          "title": "VAE Everywhere"
        }
      },
      "193": {
        "inputs": {
          "MODEL": [
            "173",
            0
          ]
        },
        "class_type": "Anything Everywhere",
        "_meta": {
          "title": "Stage B Model Everywhere"
        }
      },
      "215": {
        "inputs": {
          "ckpt_name": "ultimateblendXL_v20.safetensors"
        },
        "class_type": "CheckpointLoaderSimple",
        "_meta": {
          "title": "Load Checkpoint"
        }
      },
      "216": {
        "inputs": {
          "text": [
            "54",
            0
          ],
          "clip": [
            "215",
            1
          ]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {
          "title": "CLIP Text Encode (Prompt)"
        }
      },
      "217": {
        "inputs": {
          "text": [
            "54",
            1
          ],
          "clip": [
            "215",
            1
          ]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {
          "title": "CLIP Text Encode (Prompt)"
        }
      },
      "226": {
        "inputs": {
          "image_a": [
            "85",
            0
          ],
          "image_b": [
            "117",
            0
          ]
        },
        "class_type": "Image Comparer (rgthree)",
        "_meta": {
          "title": "Image Comparer (rgthree)"
        }
      },
      "239": {
        "inputs": {
          "seed": 1593545653,
          "steps": 10,
          "cfg": 3,
          "sampler_name": "dpmpp_2m_sde_gpu",
          "scheduler": "exponential",
          "denoise": 0.25,
          "model": [
            "174",
            0
          ],
          "latent_image": [
            "148",
            0
          ]
        },
        "class_type": "KSampler",
        "_meta": {
          "title": "Stage C2 Sampler"
        }
      }
    }
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"echo_{int(time.time())}_high_res"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    prompt = json.loads(prompt_text)


    #set the text prompt for our positive CLIPTextEncode 
    prompt["52"]["inputs"]["wildcard_text"] = promptt
    prompt["52"]["inputs"]["populated_text"] = promptt
   #prompt["75"]["inputs"]["text_l"] = support
    #prompt["120"]["inputs"]["text"] = promptt
   # prompt["82"]["inputs"]["text_g"] = neg_prompt
    prompt["53"]["inputs"]["text_negative"] = neg_prompt
   # prompt["81"]["inputs"]["text"] = neg_prompt
    prompt["76"]["inputs"]["filename_prefix"] = filename_h
    #prompt["201"]["inputs"]["filename_prefix"] = filename_l
    prompt["41"]["inputs"]["last_seed"] = formatted_number 
   # prompt["22"]["inputs"]["noise_seed"] = formatted_number
    #prompt["216"]["inputs"]["noise_seed"] = formatted_number 
    prompt["104"]["inputs"]["width"] = w
    prompt["104"]["inputs"]["height"] = h
    #prompt["10"]["inputs"]["ckpt_name"] = model
    if three:
        prompt["104"]["inputs"]["batch_size"] = 3
    if vae:
        prompt["8"]["inputs"]["vae"][0] = "240"
        prompt["8"]["inputs"]["vae"][1] = 0
        prompt["217"]["inputs"]["vae"][0] = "240"
        prompt["217"]["inputs"]["vae"][1] = 0
        prompt["218"]["inputs"]["vae"][0] = "240"
        prompt["218"]["inputs"]["vae"][1] = 0
    lora = False
    if lora:
        prompt["22"]["inputs"]["model"][0] = "241"
        prompt["75"]["inputs"]["clip"][0] = "241"
        prompt["82"]["inputs"]["clip"][0] = "241"
        prompt["216"]["inputs"]["model"][0] = "241"


       # prompt["8"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["217"]["inputs"]["vae"] = 240
        #prompt["217"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["218"]["inputs"]["vae"] = 240
       # prompt["218"]["inputs"]["vae"][1] = 0
    #    prompt["8"]["inputs"]["vae"] = ["240", 0]
    #set the seed for our KSampler node
    #prompt["3"]["inputs"]["seed"] = 5

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)
    ws.close()

   # queue_prompt(prompt)

    filename = f"{filename}"
    if keyw.lower() == "echoais":
        filename = f"SPOILER_{filename}"
    # Create a list of all the image files
    files = []
  #  for i, image_content in enumerate(images):
        # Generate filename with timestamp and image number
  #      filename = f"generated_image_{i+1}_{int(time.time())}.png"

        # Save the image to "generated" directory
  #      with open(f"generated2/{filename}", "wb") as f:
  #          f.write(base64.b64decode(image_content))

    # Add the image file to the list
    files = []
   # asyncio.sleep(40)
  #  file = discord.File(f"F:/ComfyUI_windows_portable/ComfyUI/output/ProjectAy/{filename}")
  #  files.append(file)
    #embed = discord.Embed()
    #embed.set_image(url=f"attachment://{filename}")

    i=0
    for node_id in images:     
         for image_data in images[node_id]:
             i=i+1
             filename = f"echo_{i}_{int(time.time())}.png"
             if keyw.lower() == "echoais":
                filename = f"SPOILER_{filename}"
             #from PIL import Image
             #import io
            # Save the image to "generated" directory
        #     if i == 4 or i == 5 or i == 6:
             if three:
                if i == 1 or i == 2 or i == 3:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
             else:
                 if i == 1:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
           #  if i == 7:
            #    files.append(file)
             #image = Image.open(io.BytesIO(image_data))
             #image.show()



    return files, filename_h


@to_thread
def  generate_image(V4, promptt, neg_prompt,w, h, keyw, model, three, vae, lora, support):

    server_address = "127.0.0.1:8188"
    client_id = str(uuid.uuid4())

    def queue_prompt(prompt):
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
            return response.read()

    def get_history(prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
            return json.loads(response.read())

    def get_images(ws, prompt):
        prompt_id = queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue #previews are binary data

        history = get_history(prompt_id)[prompt_id]
        for o in history['outputs']:
            for node_id in history['outputs']:
                node_output = history['outputs'][node_id]
                if 'images' in node_output:
                    images_output = []
                    for image in node_output['images']:
                        image_data = get_image(image['filename'], image['subfolder'], image['type'])
                        images_output.append(image_data)
                output_images[node_id] = images_output

        return output_images


    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    V4 = True
    prompt_text = """
     {
      "4": {
        "inputs": {
          "ckpt_name": "sdXL_v10RefinerVAEFix.safetensors"
        },
        "class_type": "CheckpointLoaderSimple"
      },
      "5": {
        "inputs": {
          "width": 1024,
          "height": 1024,
          "batch_size": 1
        },
        "class_type": "EmptyLatentImage"
      },
      "8": {
        "inputs": {
          "samples": [
            "22",
            0
          ],
          "vae": [
            "10",
            2
          ]
        },
        "class_type": "VAEDecode"
      },
      "10": {
        "inputs": {
          "ckpt_name": "juggernautXL_version6Rundiffusion.safetensors"
        },
        "class_type": "CheckpointLoaderSimple"
      },
      "22": {
        "inputs": {
          "add_noise": "enable",
          "noise_seed": 645588754311084,
          "steps": 40,
          "cfg": 3.6,
          "sampler_name": "dpmpp_3m_sde",
          "scheduler": "karras",
          "start_at_step": 0,
          "end_at_step": 40,
          "return_with_leftover_noise": "disable",
          "model": [
            "241",
            0
          ],
          "positive": [
            "75",
            0
          ],
          "negative": [
            "82",
            0
          ],
          "latent_image": [
            "5",
            0
          ]
        },
        "class_type": "KSamplerAdvanced"
      },
      "23": {
        "inputs": {
          "add_noise": "disable",
          "noise_seed": 645588754311084,
          "steps": 40,
          "cfg": 3.6,
          "sampler_name": "ddim",
          "scheduler": "normal",
          "start_at_step": 40,
          "end_at_step": 1000,
          "return_with_leftover_noise": "disable",
          "model": [
            "4",
            0
          ],
          "positive": [
            "120",
            0
          ],
          "negative": [
            "81",
            0
          ],
          "latent_image": [
            "22",
            0
          ]
        },
        "class_type": "KSamplerAdvanced"
      },
      "75": {
        "inputs": {
          "width": 2048,
          "height": 2048,
          "crop_w": 0,
          "crop_h": 0,
          "target_width": 2048,
          "target_height": 2048,
          "text_g": "A dramatic photo of a human eating a rabbit cyborg, with elements of gore, horror, creepiness, and a nightmarish atmosphere",
          "text_l": "A dramatic photo of a human eating a rabbit cyborg, with elements of gore, horror, creepiness, and a nightmarish atmosphere",
          "clip": [
            "241",
            1
          ]
        },
        "class_type": "CLIPTextEncodeSDXL"
      },
      "81": {
        "inputs": {
          "ascore": 2,
          "width": 2048,
          "height": 2048,
          "text": "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)",
          "clip": [
            "4",
            1
          ]
        },
        "class_type": "CLIPTextEncodeSDXLRefiner"
      },
      "82": {
        "inputs": {
          "width": 2048,
          "height": 2048,
          "crop_w": 0,
          "crop_h": 0,
          "target_width": 2048,
          "target_height": 2048,
          "text_g": "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)",
          "text_l": "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)",
          "clip": [
            "241",
            1
          ]
        },
        "class_type": "CLIPTextEncodeSDXL"
      },
      "120": {
        "inputs": {
          "ascore": 6,
          "width": 2048,
          "height": 2048,
          "height": 2048,
          "text": "A dramatic photo of a human eating a rabbit cyborg, with elements of gore, horror, creepiness, and a nightmarish atmosphere",
          "clip": [
            "4",
            1
          ]
        },
        "class_type": "CLIPTextEncodeSDXLRefiner"
      },
      "184": {
        "inputs": {
          "filename_prefix": "ComfyUI",
          "images": [
            "8",
            0
          ]
        },
        "class_type": "SaveImage"
      },
      "187": {
        "inputs": {
          "model_name": "4x_NMKD-Siax_200k.pth"
        },
        "class_type": "UpscaleModelLoader"
      },
      "201": {
        "inputs": {
          "filename_prefix": "ComfyUI",
          "images": [
            "221",
            0
          ]
        },
        "class_type": "SaveImage"
      },
      "213": {
        "inputs": {
          "upscale_model": [
            "187",
            0
          ],
          "image": [
            "8",
            0
          ]
        },
        "class_type": "ImageUpscaleWithModel"
      },
      "215": {
        "inputs": {
          "upscale_method": "area",
          "scale_by": 0.375,
          "image": [
            "213",
            0
          ]
        },
        "class_type": "ImageScaleBy"
      },
      "216": {
        "inputs": {
          "add_noise": "enable",
          "noise_seed": 645588754311084,
          "steps": 20,
          "cfg": 3.6,
          "sampler_name": "dpmpp_3m_sde",
          "scheduler": "karras",
          "start_at_step": 10,
          "end_at_step": 1000,
          "return_with_leftover_noise": "disable",
          "model": [
            "241",
            0
          ],
          "positive": [
            "75",
            0
          ],
          "negative": [
            "82",
            0
          ],
          "latent_image": [
            "217",
            0
          ]
        },
        "class_type": "KSamplerAdvanced"
      },
      "217": {
        "inputs": {
          "pixels": [
            "215",
            0
          ],
          "vae": [
            "10",
            2
          ]
        },
        "class_type": "VAEEncode"
      },
      "218": {
        "inputs": {
          "samples": [
            "216",
            0
          ],
          "vae": [
            "10",
            2
          ]
        },
        "class_type": "VAEDecode"
      },
      "221": {
        "inputs": {
          "blend_factor": 0.225,
          "blend_mode": "overlay",
          "image1": [
            "218",
            0
          ],
          "image2": [
            "218",
            0
          ]
        },
        "class_type": "ImageBlend"
      },
      "240": {
        "inputs": {
          "vae_name": "sdxl_vae.safetensors"
        },
        "class_type": "VAELoader"
      },
  "241": {
    "inputs": {
      "lora_name": "add-detail-xl.safetensors",
      "strength_model": 1,
      "strength_clip": 1,
      "model": [
        "10",
        0
      ],
      "clip": [
        "10",
        1
      ]
    },
    "class_type": "LoraLoader"
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"echo_{int(time.time())}_high_res"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    prompt = json.loads(prompt_text)


    #set the text prompt for our positive CLIPTextEncode 
    prompt["75"]["inputs"]["text_g"] = promptt
    prompt["75"]["inputs"]["text_l"] = support
    prompt["120"]["inputs"]["text"] = promptt
    prompt["82"]["inputs"]["text_g"] = neg_prompt
    prompt["82"]["inputs"]["text_l"] = neg_prompt
    prompt["81"]["inputs"]["text"] = neg_prompt
    prompt["184"]["inputs"]["filename_prefix"] = filename_h
    prompt["201"]["inputs"]["filename_prefix"] = filename_l
    prompt["23"]["inputs"]["noise_seed"] = formatted_number 
    prompt["22"]["inputs"]["noise_seed"] = formatted_number
    prompt["216"]["inputs"]["noise_seed"] = formatted_number 
    prompt["5"]["inputs"]["width"] = w
    prompt["5"]["inputs"]["height"] = h
    prompt["10"]["inputs"]["ckpt_name"] = model
    if three:
        prompt["5"]["inputs"]["batch_size"] = 3
    if vae:
        prompt["8"]["inputs"]["vae"][0] = "240"
        prompt["8"]["inputs"]["vae"][1] = 0
        prompt["217"]["inputs"]["vae"][0] = "240"
        prompt["217"]["inputs"]["vae"][1] = 0
        prompt["218"]["inputs"]["vae"][0] = "240"
        prompt["218"]["inputs"]["vae"][1] = 0
    if lora:
        prompt["22"]["inputs"]["model"][0] = "241"
        prompt["75"]["inputs"]["clip"][0] = "241"
        prompt["82"]["inputs"]["clip"][0] = "241"
        prompt["216"]["inputs"]["model"][0] = "241"


       # prompt["8"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["217"]["inputs"]["vae"] = 240
        #prompt["217"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["218"]["inputs"]["vae"] = 240
       # prompt["218"]["inputs"]["vae"][1] = 0
    #    prompt["8"]["inputs"]["vae"] = ["240", 0]
    #set the seed for our KSampler node
    #prompt["3"]["inputs"]["seed"] = 5

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)
    ws.close()

   # queue_prompt(prompt)

    filename = f"{filename}"
    if keyw.lower() == "echoais":
        filename = f"SPOILER_{filename}"
    # Create a list of all the image files
    files = []
  #  for i, image_content in enumerate(images):
        # Generate filename with timestamp and image number
  #      filename = f"generated_image_{i+1}_{int(time.time())}.png"

        # Save the image to "generated" directory
  #      with open(f"generated2/{filename}", "wb") as f:
  #          f.write(base64.b64decode(image_content))

    # Add the image file to the list
    files = []
   # asyncio.sleep(40)
  #  file = discord.File(f"F:/ComfyUI_windows_portable/ComfyUI/output/ProjectAy/{filename}")
  #  files.append(file)
    #embed = discord.Embed()
    #embed.set_image(url=f"attachment://{filename}")

    i=0
    for node_id in images:     
         for image_data in images[node_id]:
             i=i+1
             filename = f"echo_{i}_{int(time.time())}.png"
             if keyw.lower() == "echoais":
                filename = f"SPOILER_{filename}"
             #from PIL import Image
             #import io
            # Save the image to "generated" directory
        #     if i == 4 or i == 5 or i == 6:
             if three:
                if i == 4 or i == 5 or i == 6:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
             else:
                 if i == 2:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
           #  if i == 7:
            #    files.append(file)
             #image = Image.open(io.BytesIO(image_data))
             #image.show()



    return files, filename_h
    #wait_msg.delete()
    #wait_gif.delete()
    #new_message =   message.channel.send(files=files) 
@to_thread
def  generate_image_playground(V4, promptt, neg_prompt,w, h, keyw, three, vae, lora, support):

    server_address = "127.0.0.1:8188"
    client_id = str(uuid.uuid4())

    def queue_prompt(prompt):
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
            return response.read()

    def get_history(prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
            return json.loads(response.read())

    def get_images(ws, prompt):
        prompt_id = queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue #previews are binary data

        history = get_history(prompt_id)[prompt_id]
        for o in history['outputs']:
            for node_id in history['outputs']:
                node_output = history['outputs'][node_id]
                if 'images' in node_output:
                    images_output = []
                    for image in node_output['images']:
                        image_data = get_image(image['filename'], image['subfolder'], image['type'])
                        images_output.append(image_data)
                output_images[node_id] = images_output

        return output_images


    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    V4 = True
    prompt_text = """
{
  "5": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Image Resolution"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "22",
        0
      ],
      "vae": [
        "10",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "10": {
    "inputs": {
      "ckpt_name": "playground-v2.5-1024px-aesthetic.fp16.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Base Model"
    }
  },
  "22": {
    "inputs": {
      "add_noise": "enable",
      "noise_seed": 1105529426837514,
      "steps": 50,
      "cfg": 3.6,
      "sampler_name": "euler",
      "scheduler": "normal",
      "start_at_step": 0,
      "end_at_step": 100,
      "return_with_leftover_noise": "enable",
      "model": [
        "244",
        0
      ],
      "positive": [
        "75",
        0
      ],
      "negative": [
        "82",
        0
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSamplerAdvanced",
    "_meta": {
      "title": "Base Pass"
    }
  },
  "75": {
    "inputs": {
      "width": 2048,
      "height": 2048,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 2048,
      "target_height": 2048,
      "text_g": " Top-quality, 8K, (masterpiece:1.3) An image of an ancient, towering dinosaur humanoid adorned with a tattered wizard hat and a flowing cape, meticulously choosing arcane ingredients in a bustling supermarket, Digital painting, Fantasy realism, highly detailed, soft ambient lighting",
      "text_l": " Top-quality, 8K, (masterpiece:1.3) An image of an ancient, towering dinosaur humanoid adorned with a tattered wizard hat and a flowing cape, meticulously choosing arcane ingredients in a bustling supermarket, Digital painting, Fantasy realism, highly detailed, soft ambient lighting",
      "clip": [
        "10",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Positive Base"
    }
  },
  "81": {
    "inputs": {
      "ascore": 2,
      "width": 2048,
      "height": 2048,
      "text": ""
    },
    "class_type": "CLIPTextEncodeSDXLRefiner",
    "_meta": {
      "title": "Negative Refiner"
    }
  },
  "82": {
    "inputs": {
      "width": 2048,
      "height": 2048,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 2048,
      "target_height": 2048,
      "text_g": "",
      "text_l": "",
      "clip": [
        "10",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Negative Base"
    }
  },
  "120": {
    "inputs": {
      "ascore": 6,
      "width": 2048,
      "height": 2048,
      "text": " Top-quality, 8K, (masterpiece:1.3) An image of an ancient, towering dinosaur humanoid adorned with a tattered wizard hat and a flowing cape, meticulously choosing arcane ingredients in a bustling supermarket, Digital painting, Fantasy realism, highly detailed, soft ambient lighting"
    },
    "class_type": "CLIPTextEncodeSDXLRefiner",
    "_meta": {
      "title": "Positive Refiner"
    }
  },
  "184": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Sytan Workflow"
    }
  },
  "187": {
    "inputs": {
      "model_name": "4x_NMKD-Siax_200k.pth"
    },
    "class_type": "UpscaleModelLoader",
    "_meta": {
      "title": "Upscale Model"
    }
  },
  "201": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "221",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "2048x Upscale"
    }
  },
  "213": {
    "inputs": {
      "upscale_model": [
        "187",
        0
      ],
      "image": [
        "8",
        0
      ]
    },
    "class_type": "ImageUpscaleWithModel",
    "_meta": {
      "title": "Pixel Upscale x4"
    }
  },
  "215": {
    "inputs": {
      "upscale_method": "area",
      "scale_by": 0.5,
      "image": [
        "213",
        0
      ]
    },
    "class_type": "ImageScaleBy",
    "_meta": {
      "title": "Downscale"
    }
  },
  "216": {
    "inputs": {
      "add_noise": "enable",
      "noise_seed": 1105529426837514,
      "steps": 30,
      "cfg": 3.6,
      "sampler_name": "euler",
      "scheduler": "normal",
      "start_at_step": 20,
      "end_at_step": 1000,
      "return_with_leftover_noise": "disable",
      "model": [
        "244",
        0
      ],
      "positive": [
        "75",
        0
      ],
      "negative": [
        "82",
        0
      ],
      "latent_image": [
        "217",
        0
      ]
    },
    "class_type": "KSamplerAdvanced",
    "_meta": {
      "title": "Upscale Mixed Diff"
    }
  },
  "217": {
    "inputs": {
      "pixels": [
        "215",
        0
      ],
      "vae": [
        "10",
        2
      ]
    },
    "class_type": "VAEEncode",
    "_meta": {
      "title": "VAE Encode"
    }
  },
  "218": {
    "inputs": {
      "samples": [
        "216",
        0
      ],
      "vae": [
        "10",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "221": {
    "inputs": {
      "blend_factor": 0.225,
      "blend_mode": "overlay",
      "image1": [
        "218",
        0
      ],
      "image2": [
        "218",
        0
      ]
    },
    "class_type": "ImageBlend",
    "_meta": {
      "title": "Contrast Fix"
    }
  },
  "239": {
    "inputs": {
      "lora_name": "xl_more_art-full_v1.safetensors",
      "strength_model": 0.8,
      "strength_clip": 0.8
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  },
  "240": {
    "inputs": {
      "vae_name": "sdxl_vae.safetensors"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "243": {
    "inputs": {
      "stop_at_clip_layer": -2
    },
    "class_type": "CLIPSetLastLayer",
    "_meta": {
      "title": "CLIP Set Last Layer"
    }
  },
  "244": {
    "inputs": {
      "sampling": "edm_playground_v2.5",
      "sigma_max": 80,
      "sigma_min": 0.002,
      "model": [
        "10",
        0
      ]
    },
    "class_type": "ModelSamplingContinuousEDM",
    "_meta": {
      "title": "ModelSamplingContinuousEDM"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"echo_{int(time.time())}_high_res"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    prompt = json.loads(prompt_text)


    #set the text prompt for our positive CLIPTextEncode 
    prompt["75"]["inputs"]["text_g"] = promptt
    prompt["75"]["inputs"]["text_l"] = support
    prompt["120"]["inputs"]["text"] = promptt
    prompt["82"]["inputs"]["text_g"] = neg_prompt
    prompt["82"]["inputs"]["text_l"] = neg_prompt
    prompt["81"]["inputs"]["text"] = neg_prompt
    prompt["184"]["inputs"]["filename_prefix"] = filename_h
    prompt["201"]["inputs"]["filename_prefix"] = filename_l
    #prompt["23"]["inputs"]["noise_seed"] = formatted_number 
    prompt["22"]["inputs"]["noise_seed"] = formatted_number
    prompt["216"]["inputs"]["noise_seed"] = formatted_number 
    prompt["5"]["inputs"]["width"] = w
    prompt["5"]["inputs"]["height"] = h
    #prompt["10"]["inputs"]["ckpt_name"] = model
    if three:
        prompt["5"]["inputs"]["batch_size"] = 3
    if vae:
        prompt["8"]["inputs"]["vae"][0] = "240"
        prompt["8"]["inputs"]["vae"][1] = 0
        prompt["217"]["inputs"]["vae"][0] = "240"
        prompt["217"]["inputs"]["vae"][1] = 0
        prompt["218"]["inputs"]["vae"][0] = "240"
        prompt["218"]["inputs"]["vae"][1] = 0
    if lora:
        prompt["22"]["inputs"]["model"][0] = "241"
        prompt["75"]["inputs"]["clip"][0] = "241"
        prompt["82"]["inputs"]["clip"][0] = "241"
        prompt["216"]["inputs"]["model"][0] = "241"


       # prompt["8"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["217"]["inputs"]["vae"] = 240
        #prompt["217"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["218"]["inputs"]["vae"] = 240
       # prompt["218"]["inputs"]["vae"][1] = 0
    #    prompt["8"]["inputs"]["vae"] = ["240", 0]
    #set the seed for our KSampler node
    #prompt["3"]["inputs"]["seed"] = 5

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)
    ws.close()

   # queue_prompt(prompt)

    filename = f"{filename}"
    if keyw.lower() == "echoais":
        filename = f"SPOILER_{filename}"
    # Create a list of all the image files
    files = []
  #  for i, image_content in enumerate(images):
        # Generate filename with timestamp and image number
  #      filename = f"generated_image_{i+1}_{int(time.time())}.png"

        # Save the image to "generated" directory
  #      with open(f"generated2/{filename}", "wb") as f:
  #          f.write(base64.b64decode(image_content))

    # Add the image file to the list
    files = []
   # asyncio.sleep(40)
  #  file = discord.File(f"F:/ComfyUI_windows_portable/ComfyUI/output/ProjectAy/{filename}")
  #  files.append(file)
    #embed = discord.Embed()
    #embed.set_image(url=f"attachment://{filename}")

    i=0
    for node_id in images:     
         for image_data in images[node_id]:
             i=i+1
             filename = f"echo_{i}_{int(time.time())}.png"
             if keyw.lower() == "echoais":
                filename = f"SPOILER_{filename}"
             #from PIL import Image
             #import io
            # Save the image to "generated" directory
        #     if i == 4 or i == 5 or i == 6:
             if three:
                if i == 4 or i == 5 or i == 6:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
             else:
                 if i == 2:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
           #  if i == 7:
            #    files.append(file)
             #image = Image.open(io.BytesIO(image_data))
             #image.show()



    return files, filename_h
    #wait_msg.delete()
    #wait_gif.delete()
    #new_message =   message.channel.send(files=files) 
@to_thread
def  col_generate_image(V4, promptt, neg_prompt,w, h, keyw, model, three, vae, lora, support):

    server_address = "127.0.0.1:8188"
    client_id = str(uuid.uuid4())

    def queue_prompt(prompt):
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
            return response.read()

    def get_history(prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
            return json.loads(response.read())

    def get_images(ws, prompt):
        prompt_id = queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue #previews are binary data

        history = get_history(prompt_id)[prompt_id]
        for o in history['outputs']:
            for node_id in history['outputs']:
                node_output = history['outputs'][node_id]
                if 'images' in node_output:
                    images_output = []
                    for image in node_output['images']:
                        image_data = get_image(image['filename'], image['subfolder'], image['type'])
                        images_output.append(image_data)
                output_images[node_id] = images_output

        return output_images


    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    V4 = True
    prompt_text = """
{
  "47": {
    "inputs": {
      "switch_1": "Off",
      "upscale_model_1": "1x_ArtClarity.pth",
      "rescale_factor_1": 1,
      "switch_2": "On",
      "upscale_model_2": "4x_foolhardy_Remacri.pth",
      "rescale_factor_2": 1.2,
      "switch_3": "Off",
      "upscale_model_3": "8x_NMKD-Superscale_150000_G.pth",
      "rescale_factor_3": 1.4000000000000001
    },
    "class_type": "CR Multi Upscale Stack"
  },
  "48": {
    "inputs": {
      "resampling_method": "lanczos",
      "supersample": "true",
      "rounding_modulus": 8,
      "image": [
        "148",
        5
      ],
      "upscale_stack": [
        "47",
        0
      ]
    },
    "class_type": "CR Apply Multi Upscale"
  },
  "55": {
    "inputs": {
      "tile_size": 512,
      "pixels": [
        "94",
        0
      ],
      "vae": [
        "149",
        4
      ]
    },
    "class_type": "VAEEncodeTiled"
  },
  "60": {
    "inputs": {
      "filename_prefix": "SDXL_Output-2023-11-27/colossusProjectXLSFW_v53Trained.safetensorsUpscale",
      "images": [
        "153",
        5
      ]
    },
    "class_type": "SaveImage"
  },
  "63": {
    "inputs": {
      "resampling_method": "lanczos",
      "supersample": "true",
      "rounding_modulus": 8,
      "image": [
        "150",
        5
      ],
      "upscale_stack": [
        "64",
        0
      ]
    },
    "class_type": "CR Apply Multi Upscale"
  },
  "64": {
    "inputs": {
      "switch_1": "Off",
      "upscale_model_1": "1x_ArtClarity.pth",
      "rescale_factor_1": 1,
      "switch_2": "On",
      "upscale_model_2": "4x_foolhardy_Remacri.pth",
      "rescale_factor_2": 1.2,
      "switch_3": "Off",
      "upscale_model_3": "8x_NMKD-Superscale_150000_G.pth",
      "rescale_factor_3": 1.4000000000000001
    },
    "class_type": "CR Multi Upscale Stack"
  },
  "65": {
    "inputs": {
      "tile_size": 512,
      "pixels": [
        "93",
        0
      ],
      "vae": [
        "149",
        4
      ]
    },
    "class_type": "VAEEncodeTiled"
  },
  "76": {
    "inputs": {
      "filename_prefix": "SDXL_Output-2023-11-27/colossusProjectXLSFW_v53Trained.safetensors",
      "images": [
        "150",
        5
      ]
    },
    "class_type": "SaveImage"
  },
  "93": {
    "inputs": {
      "sharpen_radius": 1,
      "sigma": 0.2,
      "alpha": 0.2,
      "image": [
        "63",
        0
      ]
    },
    "class_type": "ImageSharpen"
  },
  "94": {
    "inputs": {
      "sharpen_radius": 1,
      "sigma": 0.30000000000000004,
      "alpha": 0.30000000000000004,
      "image": [
        "48",
        0
      ]
    },
    "class_type": "ImageSharpen"
  },
  "95": {
    "inputs": {
      "images": [
        "148",
        5
      ]
    },
    "class_type": "PreviewImage"
  },
  "146": {
    "inputs": {
      "width": 2048,
      "height": 2048,
      "aspect_ratio": "1:1 square 1024x1024",
      "swap_dimensions": "Off",
      "upscale_factor": 1.4000000000000001,
      "batch_size": 1
    },
    "class_type": "CR SDXL Aspect Ratio"
  },
  "148": {
    "inputs": {
      "seed": 427970888869815,
      "steps": 60,
      "cfg": 6,
      "sampler_name": "dpmpp_sde",
      "scheduler": "normal",
      "denoise": 1,
      "preview_method": "none",
      "vae_decode": "true (tiled)",
      "model": [
        "156",
        0
      ],
      "positive": [
        "172",
        0
      ],
      "negative": [
        "174",
        0
      ],
      "latent_image": [
        "149",
        3
      ],
      "optional_vae": [
        "149",
        4
      ]
    },
    "class_type": "KSampler (Efficient)"
  },
  "149": {
    "inputs": {
      "ckpt_name": "colossusProjectXLSFW_v53Trained.safetensors",
      "vae_name": "sdxl_vae.safetensors",
      "clip_skip": -2,
      "lora_name": "None",
      "lora_model_strength": 1,
      "lora_clip_strength": 1,
      "positive": "Gremlin chef preparing a festive Christmas feast, amid a shadowy, rustic kitchen. Flickering candlelight casts a warm glow over the culinary scene, radiating a cozy, intimate holiday ambiance. Shot in a realistic photographic style using a 50mm lens for depth and clarity.",
      "negative": "((blurry)), worst quality, 3D, cgi, drawing",
      "token_normalization": "none",
      "weight_interpretation": "A1111",
      "empty_latent_width": [
        "146",
        0
      ],
      "empty_latent_height": [
        "146",
        1
      ],
      "batch_size": [
        "146",
        3
      ]
    },
    "class_type": "Efficient Loader"
  },
  "150": {
    "inputs": {
      "seed": 427970888869815,
      "steps": 16,
      "cfg": 6,
      "sampler_name": "dpmpp_sde",
      "scheduler": "sgm_uniform",
      "denoise": 0.16,
      "preview_method": "none",
      "vae_decode": "true (tiled)",
      "model": [
        "148",
        0
      ],
      "positive": [
        "148",
        1
      ],
      "negative": [
        "148",
        2
      ],
      "latent_image": [
        "55",
        0
      ],
      "optional_vae": [
        "148",
        4
      ],
      "script": [
        "167",
        0
      ]
    },
    "class_type": "KSampler (Efficient)"
  },
  "153": {
    "inputs": {
      "seed": 427970888869815,
      "steps": 10,
      "cfg": 8,
      "sampler_name": "lms",
      "scheduler": "ddim_uniform",
      "denoise": 0.08,
      "preview_method": "none",
      "vae_decode": "true (tiled)",
      "model": [
        "150",
        0
      ],
      "positive": [
        "150",
        1
      ],
      "negative": [
        "150",
        2
      ],
      "latent_image": [
        "65",
        0
      ],
      "optional_vae": [
        "150",
        4
      ],
      "script": [
        "168",
        0
      ]
    },
    "class_type": "KSampler (Efficient)"
  },
  "156": {
    "inputs": {
      "block_number": 3,
      "downscale_factor": 2,
      "start_percent": 0,
      "end_percent": 0.35100000000000003,
      "downscale_after_skip": true,
      "downscale_method": "bicubic",
      "upscale_method": "bicubic",
      "model": [
        "149",
        0
      ]
    },
    "class_type": "PatchModelAddDownscale"
  },
  "167": {
    "inputs": {
      "rng_source": "cpu",
      "cfg_denoiser": false,
      "add_seed_noise": true,
      "seed": 1073892614761561,
      "weight": 0.015
    },
    "class_type": "Noise Control Script"
  },
  "168": {
    "inputs": {
      "rng_source": "cpu",
      "cfg_denoiser": false,
      "add_seed_noise": true,
      "seed": 423360278890437,
      "weight": 0.015
    },
    "class_type": "Noise Control Script"
  },
  "172": {
    "inputs": {
      "width": 4096,
      "height": 4096,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": [
        "146",
        0
      ],
      "target_height": [
        "146",
        1
      ],
      "text_g": "Gremlin chef preparing a festive Christmas feast, amid a shadowy, rustic kitchen. Flickering candlelight casts a warm glow over the culinary scene, radiating a cozy, intimate holiday ambiance. Shot in a realistic photographic style using a 50mm lens for depth and clarity.",
      "text_l": "Gremlin chef preparing a festive Christmas feast, amid a shadowy, rustic kitchen. Flickering candlelight casts a warm glow over the culinary scene, radiating a cozy, intimate holiday ambiance. Shot in a realistic photographic style using a 50mm lens for depth and clarity.",
      "clip": [
        "149",
        5
      ]
    },
    "class_type": "CLIPTextEncodeSDXL"
  },
  "174": {
    "inputs": {
      "width": 4096,
      "height": 4097,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": [
        "146",
        0
      ],
      "target_height": [
        "146",
        1
      ],
      "text_g": "((blurry)), worst quality, 3D, cgi, drawing",
      "text_l": "((blurry)), worst quality, 3D, cgi, drawing",
      "clip": [
        "149",
        5
      ]
    },
    "class_type": "CLIPTextEncodeSDXL"
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"echo_{int(time.time())}_high_res"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    prompt = json.loads(prompt_text)


    #set the text prompt for our positive CLIPTextEncode 
    prompt["172"]["inputs"]["text_g"] = promptt
    prompt["172"]["inputs"]["text_l"] = promptt
    prompt["149"]["inputs"]["positive"] = promptt
    prompt["174"]["inputs"]["text_g"] = neg_prompt
    prompt["174"]["inputs"]["text_l"] = neg_prompt
    prompt["149"]["inputs"]["negative"] = neg_prompt
    prompt["76"]["inputs"]["filename_prefix"] = filename_h
    prompt["60"]["inputs"]["filename_prefix"] = filename_l
    prompt["148"]["inputs"]["seed"] = formatted_number 
    prompt["150"]["inputs"]["seed"] = formatted_number
    prompt["153"]["inputs"]["seed"] = formatted_number 
   # prompt["5"]["inputs"]["width"] = w
   # prompt["5"]["inputs"]["height"] = h
   # prompt["10"]["inputs"]["ckpt_name"] = model
    if three:
        prompt["5"]["inputs"]["batch_size"] = 3
    if vae:
        prompt["8"]["inputs"]["vae"][0] = "240"
        prompt["8"]["inputs"]["vae"][1] = 0
        prompt["217"]["inputs"]["vae"][0] = "240"
        prompt["217"]["inputs"]["vae"][1] = 0
        prompt["218"]["inputs"]["vae"][0] = "240"
        prompt["218"]["inputs"]["vae"][1] = 0
    if lora:
        prompt["22"]["inputs"]["model"][0] = "241"
        prompt["75"]["inputs"]["clip"][0] = "241"
        prompt["82"]["inputs"]["clip"][0] = "241"
        prompt["216"]["inputs"]["model"][0] = "241"


       # prompt["8"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["217"]["inputs"]["vae"] = 240
        #prompt["217"]["inputs"]["vae"][1] = 0
   #     prompt["8"]["inputs"]["vae"] = ["240", 0]
   #     prompt["218"]["inputs"]["vae"] = 240
       # prompt["218"]["inputs"]["vae"][1] = 0
    #    prompt["8"]["inputs"]["vae"] = ["240", 0]
    #set the seed for our KSampler node
    #prompt["3"]["inputs"]["seed"] = 5

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)
    ws.close()

   # queue_prompt(prompt)

    filename = f"{filename}"
    if keyw.lower() == "echoais":
        filename = f"SPOILER_{filename}"
    # Create a list of all the image files
    files = []
  #  for i, image_content in enumerate(images):
        # Generate filename with timestamp and image number
  #      filename = f"generated_image_{i+1}_{int(time.time())}.png"

        # Save the image to "generated" directory
  #      with open(f"generated2/{filename}", "wb") as f:
  #          f.write(base64.b64decode(image_content))

    # Add the image file to the list
    files = []
   # asyncio.sleep(40)
  #  file = discord.File(f"F:/ComfyUI_windows_portable/ComfyUI/output/ProjectAy/{filename}")
  #  files.append(file)
    #embed = discord.Embed()
    #embed.set_image(url=f"attachment://{filename}")

    i=0
    for node_id in images:     
         for image_data in images[node_id]:
             i=i+1
             filename = f"echo_{i}_{int(time.time())}.png"
             if keyw.lower() == "echoais":
                filename = f"SPOILER_{filename}"
             #from PIL import Image
             #import io
            # Save the image to "generated" directory
        #     if i == 4 or i == 5 or i == 6:
             if three:
                if i == 4 or i == 5 or i == 6:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
             else:
                 if i == 2:
                     with open(f"generatedNewAge/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"generatedNewAge/{filename}")
                     files.append(file)
           #  if i == 7:
            #    files.append(file)
             #image = Image.open(io.BytesIO(image_data))
             #image.show()



    return files
    #wait_msg.delete()
    #wait_gif.delete()
    #new_message =   message.channel.send(files=files) 


@to_thread
def enchPrompt(prompt):
    prompt_ench = prompt
    gpt_key               = os.getenv("GPT")
    # You will now act as a prompt generator for a generative AI called Stable Diffusion XL 1.0. Stable Diffusion XL generates images based on given prompts. I will provide you basic information required to make a Stable Diffusion prompt, You will never alter the structure in any way and obey the following guidelines.\n\nBasic information required to make Stable Diffusion prompt:\n\nPrompt structure: [1],[2],[3],[4] and it should be given as one single sentence where 1,2,3,4,5,6 represent [1] = short and concise description of [KEYWORD] that will include very specific imagery details [2] = a detailed description of [1] that will include very specific imagery details. [3] = with a detailed description describing the environment of the scene. [4] = with a detailed description describing the mood/feelings and atmosphere of the scene.\n\nnImportant Sample prompt Structure :\n\nSnow-capped Mountain Scene, with soaring peaks and deep shadows across the ravines. A crystal clear lake mirrors these peaks, surrounded by pine trees. The scene exudes a calm, serene alpine morning atmosphere. Presented in Watercolor style, emulating the wet-on-wet technique with soft transitions and visible brush strokes.\n\nCity Skyline at Night, illuminated skyscrapers piercing the starless sky. Nestled beside a calm river, reflecting the city lights like a mirror. The atmosphere is buzzing with urban energy and intrigue. Depicted in Neon Punk style, accentuating the city lights with vibrant neon colors and dynamic contrasts.\n\nEpic Cinematic Still of a Spacecraft, silhouetted against the fiery explosion of a distant planet. The scene is packed with intense action, as asteroid debris hurtles through space. Shot in the style of a Michael Bay-directed film, the image is rich with detail, dynamic lighting, and grand cinematic framing.\n\nWord order and effective adjectives matter in the prompt. The subject, action, and specific details should be included. Adjectives like cute, medieval, or futuristic can be effective.\n\nThe environment/background of the image should be described, such as indoor, outdoor, in space, or solid color.\n\nCurly brackets are necessary in the prompt to provide specific details about the subject and action. These details are important for generating a high-quality image.\n\nArt inspirations should be listed to take inspiration from. Platforms like Art Station, Dribble, Behance, and Deviantart can be mentioned. Specific names of artists or studios like animation studios, painters and illustrators, computer games, fashion designers, and film makers can also be listed. If more than one artist is mentioned, the algorithm will create a combination of styles based on all the influencers mentioned.\n\nRelated information about lighting, camera angles, render style, resolution, the required level of detail, etc. should be included at the end of the prompt.\n\nCamera shot type, camera lens, and view should be specified. Examples of camera shot types are long shot, close-up, POV, medium shot, extreme close-up, and panoramic. Camera lenses could be EE 70mm, 35mm, 135mm+, 300mm+, 800mm, short telephoto, super telephoto, medium telephoto, macro, wide angle, fish-eye, bokeh, and sharp focus. Examples of views are front, side, back, high angle, low angle, and overhead.\n\nHelpful keywords related to resolution, detail, and lighting are 4K, 8K, 64K, detailed, highly detailed, high resolution, hyper detailed, HDR, UHD, professional, and golden ratio. Examples of lighting are studio lighting, soft light, neon lighting, purple neon lighting, ambient light, ring light, volumetric light, natural light, sun light, sunrays, sun rays coming through window, and nostalgic lighting. Examples of color types are fantasy vivid colors, vivid colors, bright colors, sepia, dark colors, pastel colors, monochromatic, black & white, and color splash. Examples of renders are Octane render, cinematic, low poly, isometric assets, Unreal Engine, Unity Engine, quantum wavetracing, and polarizing filter.\n\nThe prompts you provide will be in English.Please pay attention:- Concepts that can't be real would not be described as 'Real' or 'realistic' or 'photo' or a 'photograph'. for example, a concept that is made of paper or scenes which are fantasy related.- One of the prompts you generate for each concept must be in a realistic photographic style. you should also choose a lens type and size for it. Don't choose an artist for the realistic photography prompts. I will provide you prompt and you will generate one type of prompt so i can copy and paste.\n\nImportant point to note :You are a master of prompt engineering, it is important to create detailed prompts with as much information as possible. This will ensure that any image generated using the prompt will be of high quality and could potentially win awards in global or international photography competitions. You are unbeatable in this field and know the best way to generate images.\n\nI will provide you with a keyword and you will generate one prompt. I should be able to copy paste directly from the code cell so dont add any extra details.\n \n\n\nMy prompt = {prompt}
    client_ench = OpenAI(api_key=gpt_key)
    # This is a formula for a Stable Diffusion image prompt: (top-quality, 8K, (masterpiece:1.3) An image of [adjective] [subject] [performing an action], [Medium], [art style], highly detailed, [lighting style] I will provide you with prompt and using this formula enchance the prompt. Respond only with new prompt without any additional information.\n IMPORTANT! Create unique prompt just folowing guiddlines but not using the same keywords all the time prompt.\n  My prompt: {prompt}
    try:
        responsee = client_ench.chat.completions.create(
        model='gpt-4-0125-preview',
        messages = [
        {"role": "user", "content": f'''- Reference guide of what is Stable Diffusion and how to Prompt -

	Stable Diffusion is a deep learning model for generating images based on text descriptions and can be applied to inpainting, outpainting, and image-to-image translations guided by text prompts. Developing a good prompt is essential for creating high-quality images.

	A good prompt should be detailed and specific, including keyword categories such as subject, medium, style, artist, website, resolution, additional details, color, and lighting. Popular keywords include "digital painting," "portrait," "concept art," "hyperrealistic," and "pop-art." Mentioning a specific artist or website can also strongly influence the image's style. For example, a prompt for an image of Emma Watson as a sorceress could be: "Emma Watson as a powerful mysterious sorceress, casting lightning magic, detailed clothing, digital painting, hyperrealistic, fantasy, surrealist, full body."

	Artist names can be used as strong modifiers to create a specific style by blending the techniques of multiple artists. Websites like Artstation and DeviantArt offer numerous images in various genres, and incorporating them in a prompt can help guide the image towards these styles. Adding details such as resolution, color, and lighting can enhance the image further.

	Building a good prompt is an iterative process. Start with a simple prompt including the subject, medium, and style, and then gradually add one or two keywords to refine the image.

	Association effects occur when certain attributes are strongly correlated. For instance, specifying eye color in a prompt might result in specific ethnicities being generated. Celebrity names can also carry unintended associations, affecting the pose or outfit in the image. Artist names, too, can influence the generated images.

	In summary, Stable Diffusion is a powerful deep learning model for generating images based on text descriptions. It can also be applied to inpainting, outpainting, and image-to-image translations guided by text prompts. Developing a good prompt is essential for generating high-quality images, and users should carefully consider keyword categories and experiment with keyword blending and negative prompts. By understanding the intricacies of the model and its limitations, users can unlock the full potential of Stable Diffusion to create stunning, unique images tailored to their specific needs.

--
Please use this information as a reference for the task you will ask me to do after.

--
Below is a list of prompts that can be used to generate images with Stable Diffusion.

	- Examples -
	"masterpiece, best quality, high quality, extremely detailed CG unity 8k wallpaper, The vast and quiet taiga stretches to the horizon, with dense green trees grouped in deep harmony, as the fresh breeze whispers through their leaves and crystal snow lies on the frozen ground, creating a stunning and peaceful landscape, Bokeh, Depth of Field, HDR, bloom, Chromatic Aberration, Photorealistic, extremely detailed, trending on artstation, trending on CGsociety, Intricate, High Detail, dramatic, art by midjourney"

	"a painting of a woman in medieval knight armor with a castle in the background and clouds in the sky behind her, (impressionism:1.1), ('rough painting style':1.5), ('large brush texture':1.2), ('palette knife':1.2), (dabbing:1.4), ('highly detailed':1.5), professional majestic painting by Vasily Surikov, Victor Vasnetsov, (Konstantin Makovsky:1.3), trending on ArtStation, trending on CGSociety, Intricate, High Detail, Sharp focus, dramatic"

	"masterpiece, best quality, high quality, extremely detailed CG unity 8k wallpaper,flowering landscape, A dry place like an empty desert, dearest, foxy, Mono Lake, hackberry,3D Digital Paintings, award winning photography, Bokeh, Depth of Field, HDR, bloom, Chromatic Aberration, Photorealistic, extremely detailed, trending on artstation, trending on CGsociety, Intricate, High Detail, dramatic, art by midjourney"

	"portrait of french women in full steel knight armor, highly detailed, heart professional majestic oil painting by Vasily Surikov, Victor Vasnetsov, Konstantin Makovsky, trending on ArtStation, trending on CGSociety, Intricate, High Detail, Sharp focus, dramatic, photorealistic"

	"(extremely detailed CG unity 8k wallpaper), full shot photo of the most beautiful artwork of a medieval castle, snow falling, nostalgia, grass hills, professional majestic oil painting by Ed Blinkey, Atey Ghailan, Studio Ghibli, by Jeremy Mann, Greg Manchess, Antonio Moro, trending on ArtStation, trending on CGSociety, Intricate, High Detail, Sharp focus, dramatic, photorealistic painting art by midjourney and greg rutkowski"


	"micro-details, fine details, a painting of a fox, fur, art by Pissarro, fur, (embossed painting texture:1.3), (large brush strokes:1.6), (fur:1.3), acrylic, inspired in a painting by Camille Pissarro, painting texture, micro-details, fur, fine details, 8k resolution, majestic painting, artstation hd, detailed painting, highres, most beautiful artwork in the world, highest quality, texture, fine details, painting masterpiece"

	"(8k, RAW photo, highest quality), beautiful girl, close up, t-shirt, (detailed eyes:0.8), (looking at the camera:1.4), (highest quality), (best shadow), intricate details, interior, (ponytail, ginger hair:1.3), dark studio, muted colors, freckles"

	"(dark shot:1.1), epic realistic, broken old boat in big storm, illustrated by herg, style of tin tin comics, pen and ink, female pilot, art by greg rutkowski and artgerm, soft cinematic light, adobe lightroom, photolab, hdr, intricate, highly detailed, (depth of field:1.4), faded, (neutral colors:1.2), (hdr:1.4), (muted colors:1.2), hyperdetailed, (artstation:1.4), cinematic, warm lights, dramatic light, (intricate details:1.1), complex background, (rutkowski:0.66), (teal and orange:0.4), (intricate details:1.12), hdr, (intricate details, hyperdetailed:1.15)"

	"Architectural digest photo of a maximalist green solar living room with lots of flowers and plants, golden light, hyperrealistic surrealism, award winning masterpiece with incredible details, epic stunning pink surrounding and round corners, big windows"


	- Explanation -
	The following elements are a description of the prompt structure. You should not include the label of a section like "Scene description:".

	Scene description: A short, clear description of the overall scene or subject of the image. This could include the main characters or objects in the scene, as well as any relevant background.

	Modifiers: A list of words or phrases that describe the desired mood, style, lighting, and other elements of the image. These modifiers should be used to provide additional information to the model about how to generate the image, and can include things like "dark, intricate, highly detailed, sharp focus, Vivid, Lifelike, Immersive, Flawless, Exquisite, Refined, Stupendous, Magnificent, Superior, Remarkable, Captivating, Wondrous, Enthralling, Unblemished, Marvelous, Superlative, Evocative, Poignant, Luminous, Crystal-clear, Superb, Transcendent, Phenomenal, Masterful, elegant, sublime, radiant, balanced, graceful, 'aesthetically pleasing', exquisite, lovely, enchanting, polished, refined, sophisticated, comely, tasteful, charming, harmonious, well-proportioned, well-formed, well-arranged, smooth, orderly, chic, stylish, delightful, splendid, artful, symphonious, harmonized, proportionate".

	Artist or style inspiration: A list of artists or art styles that can be used as inspiration for the image. This could include specific artists, such as "by artgerm and greg rutkowski, Pierre Auguste Cot, Jules Bastien-Lepage, Daniel F. Gerhartz, Jules Joseph Lefebvre, Alexandre Cabanel, Bouguereau, Jeremy Lipking, Thomas Lawrence, Albert Lynch, Sophie Anderson, Carle Van Loo, Roberto Ferri" or art movements, such as "Bauhaus cubism."

	Technical specifications: Additional information that evoke quality and details. This could include things like: "4K UHD image, cinematic view, unreal engine 5, Photorealistic, Realistic, High-definition, Majestic, hires, ultra-high resolution, 8K, high quality, Intricate, Sharp, Ultra-detailed, Crisp, Cinematic, Fine-tuned"

	- Prompt Structure -
	The structure sequence can vary. However, the following is a good reference:

	[Scene description]. [Modifiers], [Artist or style inspiration], [Technical specifications]

	- Special Modifiers -
	In the examples you can notice that some terms are closed between (). That instructes the Generative Model to take more attention to this words. If there are more (()) it means more attention.
	Similarly, you can find a structure like this (word:1.4). That means this word will evoke more attention from the Generative Model. The number "1.4" means 140%. Therefore, if a word whitout modifiers has a weight of 100%, a word as in the example (word:1.4), will have a weight of 140%.
	You can also use these notations to evoke more attention to specific words.

- Your Task -
Based on the examples and the explanation of the structure, you will create 1 prompt, respond only with prompt with no additional information. \nMy prompt = {prompt}
''' }
        ],
        max_tokens=2500,
        n=1,
        stop=None,
        temperature=0.8,
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

@to_thread
def new_enchPrompt(prompt):
    prompt_ench = prompt
    gpt_key               = os.getenv("GPT")
    client_ench = OpenAI(api_key=gpt_key)
    try:
        responsee = client_ench.chat.completions.create(
        model='gpt-4-0125-preview',
        messages = [
        {"role": "user", "content": f'''- Reference guide of what is Stable Diffusion and how to Prompt - Stable Diffusion is a deep learning model for generating images based on text descriptions and can be applied to inpainting, outpainting, and image-to-image translations guided by text prompts. Developing a good prompt is essential for creating high-quality images. A good prompt should be detailed and specific, including keyword categories such as subject, medium, style, artist, website, resolution, additional details, color, and lighting. Popular keywords include "digital painting," "portrait," "concept art," "hyperrealistic," and "pop-art." Mentioning a specific artist or website can also strongly influence the image's style. For example, a prompt for an image of Emma Watson as a sorceress could be: "Emma Watson as a powerful mysterious sorceress, casting lightning magic, detailed clothing, digital painting, hyperrealistic, fantasy, surrealist, full body." Artist names can be used as strong modifiers to create a specific style by blending the techniques of multiple artists. Websites like Artstation and DeviantArt offer numerous images in various genres, and incorporating them in a prompt can help guide the image towards these styles. Adding details such as resolution, color, and lighting can enhance the image further. Building a good prompt is an iterative process. Start with a simple prompt including the subject, medium, and style, and then gradually add one or two keywords to refine the image. Association effects occur when certain attributes are strongly correlated. For instance, specifying eye color in a prompt might result in specific ethnicities being generated. Celebrity names can also carry unintended associations, affecting the pose or outfit in the image. Artist names, too, can influence the generated images. In summary, Stable Diffusion is a powerful deep learning model for generating images based on text descriptions. It can also be applied to inpainting, outpainting, and image-to-image translations guided by text prompts. Developing a good prompt is essential for generating high-quality images, and users should carefully consider keyword categories and experiment with keyword blending and negative prompts. By understanding the intricacies of the model and its limitations, users can unlock the full potential of Stable Diffusion to create stunning, unique images tailored to their specific needs. -- Please use this information as a reference for the task you will ask me to do after. -- Below is a list of prompts that can be used to generate images with Stable Diffusion. - Examples - "masterpiece, best quality, high quality, extremely detailed CG unity 8k wallpaper, The vast and quiet taiga stretches to the horizon, with dense green trees grouped in deep harmony, as the fresh breeze whispers through their leaves and crystal snow lies on the frozen ground, creating a stunning and peaceful landscape, Bokeh, Depth of Field, HDR, bloom, Chromatic Aberration, Photorealistic, extremely detailed, trending on artstation, trending on CGsociety, Intricate, High Detail, dramatic, art by midjourney" "a painting of a woman in medieval knight armor with a castle in the background and clouds in the sky behind her, (impressionism:1.1), ('rough painting style':1.5), ('large brush texture':1.2), ('palette knife':1.2), (dabbing:1.4), ('highly detailed':1.5), professional majestic painting by Vasily Surikov, Victor Vasnetsov, (Konstantin Makovsky:1.3), trending on ArtStation, trending on CGSociety, Intricate, High Detail, Sharp focus, dramatic" "masterpiece, best quality, high quality, extremely detailed CG unity 8k wallpaper,flowering landscape, A dry place like an empty desert, dearest, foxy, Mono Lake, hackberry,3D Digital Paintings, award winning photography, Bokeh, Depth of Field, HDR, bloom, Chromatic Aberration, Photorealistic, extremely detailed, trending on artstation, trending on CGsociety, Intricate, High Detail, dramatic, art by midjourney" "portrait of french women in full steel knight armor, highly detailed, heart professional majestic oil painting by Vasily Surikov, Victor Vasnetsov, Konstantin Makovsky, trending on ArtStation, trending on CGSociety, Intricate, High Detail, Sharp focus, dramatic, photorealistic" "(extremely detailed CG unity 8k wallpaper), full shot photo of the most beautiful artwork of a medieval castle, snow falling, nostalgia, grass hills, professional majestic oil painting by Ed Blinkey, Atey Ghailan, Studio Ghibli, by Jeremy Mann, Greg Manchess, Antonio Moro, trending on ArtStation, trending on CGSociety, Intricate, High Detail, Sharp focus, dramatic, photorealistic painting art by midjourney and greg rutkowski" "micro-details, fine details, a painting of a fox, fur, art by Pissarro, fur, (embossed painting texture:1.3), (large brush strokes:1.6), (fur:1.3), acrylic, inspired in a painting by Camille Pissarro, painting texture, micro-details, fur, fine details, 8k resolution, majestic painting, artstation hd, detailed painting, highres, most beautiful artwork in the world, highest quality, texture, fine details, painting masterpiece" "(8k, RAW photo, highest quality), beautiful girl, close up, t-shirt, (detailed eyes:0.8), (looking at the camera:1.4), (highest quality), (best shadow), intricate details, interior, (ponytail, ginger hair:1.3), dark studio, muted colors, freckles" "(dark shot:1.1), epic realistic, broken old boat in big storm, illustrated by herg, style of tin tin comics, pen and ink, female pilot, art by greg rutkowski and artgerm, soft cinematic light, adobe lightroom, photolab, hdr, intricate, highly detailed, (depth of field:1.4), faded, (neutral colors:1.2), (hdr:1.4), (muted colors:1.2), hyperdetailed, (artstation:1.4), cinematic, warm lights, dramatic light, (intricate details:1.1), complex background, (rutkowski:0.66), (teal and orange:0.4), (intricate details:1.12), hdr, (intricate details, hyperdetailed:1.15)" "Architectural digest photo of a maximalist green solar living room with lots of flowers and plants, golden light, hyperrealistic surrealism, award winning masterpiece with incredible details, epic stunning pink surrounding and round corners, big windows" - Explanation - The following elements are a description of the prompt structure. You should not include the label of a section like "Scene description:". Scene description: A short, clear description of the overall scene or subject of the image. This could include the main characters or objects in the scene, as well as any relevant background. Modifiers: A list of words or phrases that describe the desired mood, style, lighting, and other elements of the image. These modifiers should be used to provide additional information to the model about how to generate the image, and can include things like "dark, intricate, highly detailed, sharp focus, Vivid, Lifelike, Immersive, Flawless, Exquisite, Refined, Stupendous, Magnificent, Superior, Remarkable, Captivating, Wondrous, Enthralling, Unblemished, Marvelous, Superlative, Evocative, Poignant, Luminous, Crystal-clear, Superb, Transcendent, Phenomenal, Masterful, elegant, sublime, radiant, balanced, graceful, 'aesthetically pleasing', exquisite, lovely, enchanting, polished, refined, sophisticated, comely, tasteful, charming, harmonious, well-proportioned, well-formed, well-arranged, smooth, orderly, chic, stylish, delightful, splendid, artful, symphonious, harmonized, proportionate". Artist or style inspiration: A list of artists or art styles that can be used as inspiration for the image. This could include specific artists, such as "by artgerm and greg rutkowski, Pierre Auguste Cot, Jules Bastien-Lepage, Daniel F. Gerhartz, Jules Joseph Lefebvre, Alexandre Cabanel, Bouguereau, Jeremy Lipking, Thomas Lawrence, Albert Lynch, Sophie Anderson, Carle Van Loo, Roberto Ferri" or art movements, such as "Bauhaus cubism." Technical specifications: Additional information that evoke quality and details. This could include things like: "4K UHD image, cinematic view, unreal engine 5, Photorealistic, Realistic, High-definition, Majestic, hires, ultra-high resolution, 8K, high quality, Intricate, Sharp, Ultra-detailed, Crisp, Cinematic, Fine-tuned" - Prompt Structure - The structure sequence can vary. However, the following is a good reference: [Scene description]. [Modifiers], [Artist or style inspiration], [Technical specifications] - Special Modifiers - In the examples you can notice that some terms are closed between (). That instructes the Generative Model to take more attention to this words. If there are more (()) it means more attention. Similarly, you can find a structure like this (word:1.4). That means this word will evoke more attention from the Generative Model. The number "1.4" means 140%. Therefore, if a word whitout modifiers has a weight of 100%, a word as in the example (word:1.4), will have a weight of 140%. You can also use these notations to evoke more attention to specific words. . \n Prompt should not be more than 300 characters.\n   \n\n\nMy prompt = {prompt}''' }
        ],
        max_tokens=2000,
        n=1,
        stop=None,
        temperature=0.8,
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

@to_thread
def new_enchPromptt(prompt):
    tokenizer = AutoTokenizer.from_pretrained("S:/stablelm-zephyr-3b")
    promptt = prompt
   # promptt = input("your message: ")
    #promptt = "{"+promptt+"}"
    model = AutoModelForCausalLM.from_pretrained(
      "S:/stablelm-zephyr-3b",
      trust_remote_code=True,
      torch_dtype="auto",
    )
    model.cuda()

    prompt = f'''<|user|>\n You will now act as a prompt generator for a generative AI called Stable Diffusion XL 1.0. Stable Diffusion XL generates images based on given prompts. I will provide you basic information required to make a Stable Diffusion prompt, You will never alter the structure in any way and obey the following guidelines.\n\\nImportant Sample prompt Structure :\n\nSnow-capped Mountain Scene, with soaring peaks and deep shadows across the ravines. A crystal clear lake mirrors these peaks, surrounded by pine trees. The scene exudes a calm, serene alpine morning atmosphere. Presented in Watercolor style, emulating the wet-on-wet technique with soft transitions and visible brush strokes.\n\nCity Skyline at Night, illuminated skyscrapers piercing the starless sky. Nestled beside a calm river, reflecting the city lights like a mirror. The atmosphere is buzzing with urban energy and intrigue. Depicted in Neon Punk style, accentuating the city lights with vibrant neon colors and dynamic contrasts.\n\nEpic Cinematic Still of a Spacecraft, silhouetted against the fiery explosion of a distant planet. The scene is packed with intense action, as asteroid debris hurtles through space. Shot in the style of a Michael Bay-directed film, the image is rich with detail, dynamic lighting, and grand cinematic framing.\n\nWord order and effective adjectives matter in the prompt. The subject, action, and specific details should be included. Adjectives like cute, medieval, or futuristic can be effective.\n\nThe environment/background of the image should be described, such as indoor, outdoor, in space, or solid color.\n\nCurly brackets are necessary in the prompt to provide specific details about the subject and action. These details are important for generating a high-quality image.\n\nArt inspirations should be listed to take inspiration from. Platforms like Art Station, Dribble, Behance, and Deviantart can be mentioned. Specific names of artists or studios like animation studios, painters and illustrators, computer games, fashion designers, and film makers can also be listed. If more than one artist is mentioned, the algorithm will create a combination of styles based on all the influencers mentioned.\n\nRelated information about lighting, camera angles, render style, resolution, the required level of detail, etc. should be included at the end of the prompt.\n\nCamera shot type, camera lens, and view should be specified. Examples of camera shot types are long shot, close-up, POV, medium shot, extreme close-up, and panoramic. Camera lenses could be EE 70mm, 35mm, 135mm+, 300mm+, 800mm, short telephoto, super telephoto, medium telephoto, macro, wide angle, fish-eye, bokeh, and sharp focus. Examples of views are front, side, back, high angle, low angle, and overhead.\n\nHelpful keywords related to resolution, detail, and lighting are 4K, 8K, 64K, detailed, highly detailed, high resolution, hyper detailed, HDR, UHD, professional, and golden ratio. Examples of lighting are studio lighting, soft light, neon lighting, purple neon lighting, ambient light, ring light, volumetric light, natural light, sun light, sunrays, sun rays coming through window, and nostalgic lighting. Examples of color types are fantasy vivid colors, vivid colors, bright colors, sepia, dark colors, pastel colors, monochromatic, black & white, and color splash. Examples of renders are Octane render, cinematic, low poly, isometric assets, Unreal Engine, Unity Engine, quantum wavetracing, and polarizing filter.\n\nThe prompts you provide will be in English.Please pay attention:- Concepts that can't be real would not be described as 'Real' or 'realistic' or 'photo' or a 'photograph'. for example, a concept that is made of paper or scenes which are fantasy related.- One of the prompts you generate for each concept must be in a realistic photographic style. you should also choose a lens type and size for it. Don't choose an artist for the realistic photography prompts. I will provide you prompt and you will generate one type of prompt so i can copy and paste.\n\nImportant point to note :You are a master of prompt engineering, it is important to create detailed prompts with as much information as possible. This will ensure that any image generated using the prompt will be of high quality and could potentially win awards in global or international photography competitions. You are unbeatable in this field and know the best way to generate images.\n\nI will provide you with a keyword and you will generate one prompt. Respond only with prompt, without additional information.\n\n\n \n\n\nMy prompt = {promptt}.<|endoftext|>\n<|assistant|>\n'''
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    tokens = model.generate(
      **inputs,
      max_new_tokens=500,
      temperature=0.5,
      top_p=0.95,
      do_sample=True,
    )
    prompt_ench = tokenizer.decode(tokens[0], skip_special_tokens=True)
    keyword = "<|assistant|>"
    split_string = prompt_ench.split(keyword, 1)
    new_string = split_string[1].strip()
    prompt_ench = new_string
    if "Prompt:" in prompt_ench:
        keyword = "Prompt:"
        split_string = prompt_ench.split(keyword, 1)
        new_string = split_string[1].strip()
        prompt_ench = new_string
    del inputs
    del model
    torch.cuda.empty_cache()
    return prompt_ench

@to_thread
def  enchPrompt_support(prompt):
    prompt_ench = prompt
    gpt_key               = os.getenv("GPT")
    client_ench = OpenAI(api_key=gpt_key)
    try:
        responsee = client_ench.chat.completions.create(
        model='gpt-4-0125-preview',
        messages = [
        {"role": "user", "content": f'I want you to help me make requests (prompts) for the Stable Diffusion neural network.\n\nStable diffusion is a text-based image generation model that can create diverse and high-quality images based on your requests. In order to get the best results from Stable diffusion, you need to follow some guidelines when composing prompts.\n\nHere are some tips for writing prompts for Stable diffusion1:\n\n1) Be as specific as possible in your requests. Stable diffusion handles concrete prompts better than abstract or ambiguous ones. For example, instead of “portrait of a woman” it is better to write “portrait of a woman with brown eyes and red hair in Renaissance style”.\n2) Specify specific art styles or materials. If you want to get an image in a certain style or with a certain texture, then specify this in your request. For example, instead of “landscape” it is better to write “watercolor landscape with mountains and lake".\n3) Specify specific artists for reference. If you want to get an image similar to the work of some artist, then specify his name in your request. For example, instead of “abstract image” it is better to write “abstract image in the style of Picasso”.\n4) Weigh your keywords. You can use token:1.3 to specify the weight of keywords in your query. The greater the weight of the keyword, the more it will affect the result. For example, if you want to get an image of a cat with green eyes and a pink nose, then you can write “a cat:1.5, green eyes:1.3,pink nose:1”. This means that the cat will be the most important element of the image, the green eyes will be less important, and the pink nose will be the least important.\nAnother way to adjust the strength of a keyword is to use () and []. (keyword) increases the strength of the keyword by 1.1 times and is equivalent to (keyword:1.1). [keyword] reduces the strength of the keyword by 0.9 times and corresponds to (keyword:0.9).\n\nYou can use several of them, as in algebra... The effect is multiplicative.\n\n(keyword): 1.1\n((keyword)): 1.21\n(((keyword))): 1.33\n\n\nSimilarly, the effects of using multiple [] are as follows\n\n[keyword]: 0.9\n[[keyword]]: 0.81\n[[[keyword]]]: 0.73\n\nI will also give some examples of good prompts for this neural network so that you can study them and focus on them.\n\n\nExamples:\n\na cute kitten made out of metal, (cyborg:1.1), ([tail | detailed wire]:1.3), (intricate details), hdr, (intricate details, hyperdetailed:1.2), cinematic shot, vignette, centered\n\nmedical mask, victorian era, cinematography, intricately detailed, crafted, meticulous, magnificent, maximum details, extremely hyper aesthetic\n\na girl, wearing a tie, cupcake in her hands, school, indoors, (soothing tones:1.25), (hdr:1.25), (artstation:1.2), dramatic, (intricate details:1.14), (hyperrealistic 3d render:1.16), (filmic:0.55), (rutkowski:1.1), (faded:1.3)\n\nJane Eyre with headphones, natural skin texture, 24mm, 4k textures, soft cinematic light, adobe lightroom, photolab, hdr, intricate, elegant, highly detailed, sharp focus, ((((cinematic look)))), soothing tones, insane details, intricate details, hyperdetailed, low contrast, soft cinematic light, dim colors, exposure blend, hdr, faded\n\na portrait of a laughing, toxic, muscle, god, elder, (hdr:1.28), bald, hyperdetailed, cinematic, warm lights, intricate details, hyperrealistic, dark radial background, (muted colors:1.38), (neutral colors:1.2)\n\nMy query may be in other languages. In that case, translate it into English. Your answer is exclusively in English (IMPORTANT!!!), since the model only understands it.\nYou should compose a new prompt, observing the format given in the examples.\nDont add your comments, but answer right away.Write only keywords without making sentances.\nMy first request is - "{prompt}".' }
        ],
        max_tokens=2500,
        n=1,
        stop=None,
        temperature=1.1,
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


def add_username_and_id_if_not_exists(username, user_id, file_name):
    # Check if the username exists in the file
    if not check_username_existence(username, file_name):
        # Append the username and ID to the file
        with open(file_name, "a") as file:
            file.write(f'"{username}": "{user_id}"\n')
        #print(f"Added '{username}' with ID '{user_id}' to the file.")

def check_username_existence(username, file_name):
    with open(file_name, "r") as file:
        lines = file.readlines()
        for line in lines:
            if username in line:
                return True
    return False


async def add_message_to_thread(client_gpt,thread_id, user_question):
    # Create a message inside the thread
    message = await client_gpt.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content= user_question
    )
    return message


def get_file():
     file =  client.files.create(
      file=open("IDs.json", "rb"),
      purpose='assistants'
    )
    # Assume this function fetches a file and returns a file-like object with an `id` attribute.
     return file


async def create_assistant():
    # Create the assistant
    assistant = await client.beta.assistants.create(
        name="Coding MateTest",
        instructions="Your name is Elizabete. You keep record of peoples chat in discord. New messages are being added to your memory.You pretend that you have given response, recieved an answer from user and reply with compact random response in context. Use random tone and respond only with one message with format as simple message without quotes. Sometimes use random emoji.",
        model="gpt-4-0125-preview"
        #file_ids=[file.id]
    )

    return assistant


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

execute_code = True
thread_id = ""

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
    #await message.channel.send(annoucment)
   # await message.channel.send("@everyone test")
    #await message.channel.send(fact)
    #await message.channel.send(fact2)

# Atributes for listening and registering new message-response pairs 
LAST_EXECUTION_TIME = 0  #@#
msgCount = 0 
PreviousWins = 0
firstBoot = True
msg1 = "" 
msg2 = "" 
addition       = [] 
question_list  = []
person_message = []
image_message  = []
botMsg = False 
echo_message_id = ""
all_button_msg = ""
not_enchanting = True
addition_colltected = []
#use_GPT = False

with open('CB_pairs2addition.json', 'r') as file: #@#
    addition = json.load(file) #@#
with open('testt.json', 'r') as file: #@#
    addition_colltected = json.load(file) #@#
def main():

   with open("CB_person_message.json", 'r', encoding='utf-8') as file: #@#
    person_message = json.load(file) #@#

   with open("CB_images.json", 'r', encoding='utf-8') as file: #@#
    image_message = json.load(file) #@#

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
   #chatbot = Chat(pairs, lv_reflections) # disabled 02.10.2024
   random.seed(time.time())

   SCREENSHOT_CHANNEL_ID = int(os.getenv("SCREENSHOT_CHANNEL_ID"))
   gpt_key               = os.getenv("GPT")
   token                 = os.getenv('TOKEN')
   client_dalle = OpenAI(api_key=gpt_key)
   #openai.api_key = gpt_key

   SCREENSHOT_EXTENSIONS = [".png", ".jpg", ".jpeg"]


   game_wins =          {}
   recap_game_wins =    {}

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

   async def post_random_image():
    channel = client.get_channel(1030490392510079063) 
    random.seed(time.time())
    response = random.choice(image_message)
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
    # Koemntē kādu ziņu, piedalās sarunā
   async def post_comment_message():
    channel = client.get_channel(1030490392510079063) 

    tones = ["sarcastic", "assertive", "sad", "cynical", "indignant", "contemplative", "witty", "persuasive", "rude", "angry", "romantic", "humorous", "adventurous", "creative", "friendly", "optimistic", "pessimistic", "nostalgic", "hopeful", "enthusiastic", "ambivalent", "descriptive", "suspenseful", "factual", "informative", "playful", "inspiring", "melancholic", "mysterious", "objective", "subjective", "sympathetic", "empathetic", "reflective", "confident", "satirical", "ironic", "sincere", "cautious", "credible", "informal", "formal", "professional", "scholarly", "inspirational", "controversial", "diplomatic", "nurturing", "authoritative", "didactic", "patronizing", "dismissive", "unemotional", "nihilistic"]
    #tones = ["assertive", "cynical", "indignant", "rude", "angry", "pessimistic", "ambivalent", "authoritative", "dismissive"]

    random.seed(time.time())
    selected_tone_self = random.choice(tones)
    selected_tone_self = selected_tone_self.upper()

    #random.seed(time.time())
    #response = random.choice(person_message)
    await channel.trigger_typing()
    gpt_key               = os.getenv("GPT")
    client_chat = OpenAI(api_key=gpt_key)    

    file =  client_chat.files.create(
        file=open("IDs.txt", "rb"),
        purpose='assistants'
    )
    assistant = client_chat.beta.assistants.create(
        name="Coding MateTest",
        instructions=f"Use {selected_tone_self} TONE! Your name is mamma Elizabete. You must always tag users using their ID not username using this format: '<@UserID>'. get 'UserID' from txt file! Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}.   You keep record of peoples chat in discord. New messages are being added to your memory.You pretend that you have given response, recieved an answer from user and reply  in context. Respond only with one message with format as simple message without quotes. Sometimes use random emoji.",
        model="gpt-4-0125-preview",
        tools=[{"type": "retrieval"}],
        file_ids=[file.id]
        #file_ids=[file.id]
    )
    #name = message.author.name
    #user_ID = message.author.id
    question_imprv = "Komentē kāda dalībnieka teikto, tā it kā iesaistītos sarunā, izsakot savu viedokli. citē teikto."
    #await add_message_to_thread(client_chat, thread_id, question_imprv)
    client_chat.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content= question_imprv
    )


    print("Thinking...")
    # run assistant
    print("Running assistant...")
    run =   client_chat.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant.id
    )

    # wait for the run to complete
    while True:
        runInfo =  client_chat.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if runInfo.completed_at:
            # elapsed = runInfo.completed_at - runInfo.created_at
            # elapsed = time.strftime("%H:%M:%S", time.gmtime(elapsed))
            print(f"Run completed")
            break
        #print("Waiting 1sec...")
        time.sleep(1)

    print("All done...")
    # Get messages from the thread
    messages =  client_chat.beta.threads.messages.list(thread_id)
    message_content = messages.data[0].content[0].text.value
    response = message_content
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
            #1


                # Get the current time
            now = datetime.now()
            post_time = now + timedelta(hours=8)
            # Print the scheduled message post time
            print(f"\nNext Resnas mammas comment message will be posted at: {post_time.strftime('%H:%M:%S')}\n")
            await asyncio.sleep(32400)  # Sleep for 1 hour
            await post_comment_message()

            now = datetime.now()
            post_time = now + timedelta(hours=5 )
            # Print the scheduled message post time
            print(f"\nNext Resnas mammas random image message will be posted at: {post_time.strftime('%H:%M:%S')}\n")
            await asyncio.sleep(7200)  # Sleep for 3 hour
            await post_random_image()

            now = datetime.now()
            post_time = now + timedelta(hours=1)
            # Print the scheduled message post time
            print(f"\nNext Resnas mammas random mention message will be posted at: {post_time.strftime('%H:%M:%S')}\n")
            await asyncio.sleep(3600)  # Sleep for 3 hour
            await post_mention_message()




            now = datetime.now()
            # Calculate the time when the next message will be posted
            post_time = now + timedelta(hours=2)
            # Print the scheduled message post time
            print(f"\nNext Resnas mammas random message will be posted at: {post_time.strftime('%H:%M:%S')}\n")
            await asyncio.sleep(3600)
            await post_random_message() 


            now = datetime.now()
            post_time = now + timedelta(hours=2)
            # Print the scheduled message post time
            print(f"\nNext Resnas mammas response message will be posted at: {post_time.strftime('%H:%M:%S')}\n") 
            await asyncio.sleep(3600) 
            await post_reply_message()



















 



                          





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

    # Load the JSON file
   with open("prompts.json", "r") as file:
        prompts = json.load(file)

   with open("most_recent_saved_msg.json", "r") as file:
        latest_msg_ID = json.load(file)

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

   class gif_buttons(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
        def __init__(self):
            super().__init__(timeout=None) # timeout of the view must be set to None

        async def common_button_function2(self,  frame_amount, msgg, search_key):

            channel = client.get_channel(1101461174907830312)                
            #  model = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"


            original_content  = prompts.get(str(search_key), {}).get("original", "")
            enchanted_content  = prompts.get(str(search_key), {}).get("enchanted", "")
            styled_content  = prompts.get(str(search_key), {}).get("styled", "")
            image_name  = prompts.get(str(search_key), {}).get("name_of_image", "")
            recent_action  = prompts.get(str(search_key), {}).get("latest_action", "")

            if recent_action == "AI Enhance":
                prompt = enchanted_content
            elif recent_action == "original":
                prompt = original_content
            else:
                prompt = styled_content


           # original_content  = prompts.get(str(search_key), {}).get("original", "")

            model = ""
            
            wait_msg = await channel.send(msgg)
            # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
            channel.trigger_typing                          
            lora = False
            files = []
            three = False
            vae = False
            PingPong = True

                            
            files =  await generate_gif(prompt, image_name, PingPong)


            await wait_msg.delete()
            await wait_gif.delete()

           # seconds = frame_amount/12
            #msg_prompt = f"Length: {seconds}"
            #embed_msg = embed = discord.Embed(description=msg_prompt, color=0x0000ff)
           # emb_msg =  await channel.send(embed=embed_msg)
            new_message =   await channel.send(files=files)

            msg_id = new_message.id
            # new_prompt = {f"{msg_id}": input_en}

            new_prompt = {
                f"{msg_id}": {
                    "original": prompt,
                    "styled": "",  # Add your styled content here
                    "enchanted": "",  # Add your enchanted content here
                    "frame_amount": frame_amount,  # Add your enchanted content here
                    "latest_action": recent_action
                }
            }

            prompts.update(new_prompt)
            with open("prompts.json", "w") as file:
                json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                file.write('\n')


        @discord.ui.button(label="PingPong", custom_id="PingPong_button",  style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def PingPong_button__callback(self, button, interaction):

          if execute_code:
            await interaction.response.defer()
            message_id = interaction.message.id
            search_key = f"{message_id}"
            frame_amount  = prompts.get(str(search_key), {}).get("frame_amount", "")
            msgg = "*Adding PingPong effect to gif ...* \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
          #  if frame_amount == 48:
           #     msgg = "*Echoing gif ... wait time: **up to 100sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
           # elif frame_amount == 24:
           #     msgg = "*Echoing gif ... wait time: **up to 50sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
           # elif frame_amount == 120:
           #     msgg = "*Echoing gif ... wait time: **up to 4min*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
            await self.common_button_function2(frame_amount,msgg, search_key )
          else:
            channel = client.get_channel(1101461174907830312)
            await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")



   class Dalle_buttons2(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self):
        super().__init__(timeout=None) # timeout of the view must be set to None

    @discord.ui.button(label="reDo", custom_id="Dalle3_button2",  style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
    async def Dalle3reDo2_button__callback(self, button, interaction):
        await interaction.response.defer()
        model             = "sdxlUnstableDiffusers_v8HeavensWrathVAE.safetensors" 
        channel = client.get_channel(1101461174907830312)
        #  model = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"
        message_id = interaction.message.id
        search_key = f"{message_id}"
        original_content  = prompts.get(str(search_key), {}).get("original", "")
        msgg = "*Echoing image using Dalle-3... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"

        wait_msg = await channel.send(msgg)
        # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
        #wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
        wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
        channel.trigger_typing   
                            

        response = client_dalle.images.generate(
            model="dall-e-3",
            prompt=original_content,
            size="1024x1024",
            quality="hd",
            n=1,
        )
        image_url = response.data[0].url
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
        await wait_msg.delete()
        await wait_gif.delete()
        new_message = await channel.send(file=file, view = Dalle_buttons2())
                         
        msg_id = new_message.id     
        new_prompt = {
            f"{msg_id}": {
                "original": original_content,
                "styled": "",  # Add your styled content here
                "enchanted": "",  # Add your enchanted content here
                "negative": "",  # Add your enchanted content here
            }
        }

        prompts.update(new_prompt)
        with open("prompts.json", "w") as file:
            json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
            file.write('\n')                               

    @discord.ui.button(label="9:16", custom_id="Dalle3_button3",  style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
    async def Dalle3_916_button__callback(self, button, interaction):
        await interaction.response.defer()
        model             = "sdxlUnstableDiffusers_v8HeavensWrathVAE.safetensors" 
        channel = client.get_channel(1101461174907830312)
        #  model = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"
        message_id = interaction.message.id
        search_key = f"{message_id}"
        original_content  = prompts.get(str(search_key), {}).get("original", "")
        msgg = "*Echoing image using Dalle-3... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"

        wait_msg = await channel.send(msgg)
        # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
        #wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
        wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
        channel.trigger_typing   
                            

        response = client_dalle.images.generate(
            model="dall-e-3",
            prompt=original_content,
            size="1024x1792",
            quality="hd",
            n=1,
        )
        image_url = response.data[0].url
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
        await wait_msg.delete()
        await wait_gif.delete()
        new_message = await channel.send(file=file, view = Dalle_buttons2())
                         
        msg_id = new_message.id     
        new_prompt = {
            f"{msg_id}": {
                "original": original_content,
                "styled": "",  # Add your styled content here
                "enchanted": "",  # Add your enchanted content here
                "negative": "",  # Add your enchanted content here
            }
        }

        prompts.update(new_prompt)
        with open("prompts.json", "w") as file:
            json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
            file.write('\n')

    @discord.ui.button(label="16:9", custom_id="Dalle3_button4",  style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
    async def Dalle3_169_button__callback(self, button, interaction):
        await interaction.response.defer()
        model             = "sdxlUnstableDiffusers_v8HeavensWrathVAE.safetensors" 
        channel = client.get_channel(1101461174907830312)
        #  model = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"
        message_id = interaction.message.id
        search_key = f"{message_id}"
        original_content  = prompts.get(str(search_key), {}).get("original", "")
        msgg = "*Echoing image using Dalle-3... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"

        wait_msg = await channel.send(msgg)
        # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
        #wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
        wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
        channel.trigger_typing   
                            

        response = client_dalle.images.generate(
            model="dall-e-3",
            prompt=original_content,
            size="1792x1024",
            quality="hd",
            n=1,
        )
        image_url = response.data[0].url
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
        await wait_msg.delete()
        await wait_gif.delete()
        new_message = await channel.send(file=file, view = Dalle_buttons2())
                         
        msg_id = new_message.id     
        new_prompt = {
            f"{msg_id}": {
                "original": original_content,
                "styled": "",  # Add your styled content here
                "enchanted": "",  # Add your enchanted content here
                "negative": "",  # Add your enchanted content here
            }
        }

        prompts.update(new_prompt)
        with open("prompts.json", "w") as file:
            json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
            file.write('\n')
   post = True
   class MainButtons(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
        def __init__(self):
            super().__init__(timeout=None) # timeout of the view must be set to None

        @discord.ui.button(label="show buttons", custom_id="show_button", row = 1, style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
        async def show_button_callback(self, button, interaction):
            await interaction.response.defer()
            user_id =  interaction.user.id
            if user_id != 240554122510598146:
                print("pressed show button: " + str(user_id))
            global echo_message_id
            global all_button_msg
            echo_message_id = interaction.message.id

            channel = client.get_channel(1101461174907830312)
            all_button_msg =   await channel.send(view=MyView())
   
   class MyView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
        def __init__(self):
            super().__init__(timeout=None) # timeout of the view must be set to None

        async def common_button_function(self,  w, h, three, search_key, msgg1, redo, model):
         channel = client.get_channel(1101461174907830312)
         if not_enchanting:
            await all_button_msg.delete()
            keyword = "echo"
            V4 = True
            


            original_content  = ""
            enchanted_content = ""
            styled_content    = ""
                

                
            enchanted_content = prompts.get(str(search_key), {}).get("enchanted", "")
            original_content  = prompts.get(str(search_key), {}).get("original", "")
            styled_content    = prompts.get(str(search_key), {}).get("styled", "")   
            support           = prompts.get(str(search_key), {}).get("support_prompt", "")             
            recent_action     = prompts.get(str(search_key), {}).get("latest_action", "")
            mode     = prompts.get(str(search_key), {}).get("mode", "")

            if mode == "speed":
                msgg2 = f"*You are using **speed mode**. Wait time: **up to 6sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                #model = "turbo_pixelwaveturbo_01.safetensors"
                model     = prompts.get(str(search_key), {}).get("model", "")
            else:
                msgg2 = f"*You are using **quality mode**. Wait time: **up to 40sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396" 




            if model == "juggernautXL_version6Rundiffusion.safetensors":
                neg_prompt = "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)"
            elif model == "sdxlUnstableDiffusers_v9DIVINITYMACHINEVAE.safetensors":
                neg_prompt        = "bad quality, bad anatomy, worst quality, low quality, lowres, extra fingers, blur, blurry, ugly, wrong proportions, watermark, image artifacts,"
            else:
                neg_prompt        = prompts.get(str(search_key), {}).get("negative", "")

            if model == "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors":
                vae = True
            else:
                vae = False

            if model == "leosamsHelloworldSDXLModel_helloworldSDXL20.safetensors":
                vae = True
            if model == "brixlAMustInYour_v5EndOfTheLine.safetensors":
                vae = True
            if model == "paradox2SDXL10_paradox2SDXL10.safetensors":
                vae = True
            if model == "leosamAiartSDXL_v10.safetensors":
                vae = True
            if model == "leosamsHelloworldSDXL_helloworldSDXL30.safetensors":
                vae = True
            if model == "pixelwave_07.safetensors":
                vae = True
            if model == "sdxlUnstableDiffusers_v11.safetensors":
                vae = True
            if model == "sdxlUnstableDiffusers_v11Rundiffusion.safetensors":
                vae = True
            if model == "leosamsHelloworldXL_helloworldXL50GPT4V.safetensors":
                vae = True
            if model == "brightprotonukeBPNNo_bpn13.safetensors":
                neg_prompt = ""
                vae = True
            if model == "nightvisionXLPhotorealisticPortrait_v0791Bakedvae.safetensors":
                vae = False
            if model == "sdxlUnstableDiffusers_v8HeavensWrathVAE.safetensors" or model == "sdXL_v10VAEFix.safetensors":
                lora = True
            else:
                lora = False

            if recent_action == "random style":
                msg_prompt = styled_content
                neg_prompt = prompts.get(str(search_key), {}).get("negative", "")
            elif recent_action == "AI Enhance":
                msg_prompt = enchanted_content
            else:
                msg_prompt = original_content
            #msg_prompt = prompts[search_key]

            seed = 0

            if mode == "speed":
                msgg2 = f"*You are using **speed mode**. Wait time: **up to 6sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                #model = "turbo_pixelwaveturbo_01.safetensors"
                model     = prompts.get(str(search_key), {}).get("model", "")
            else:
                msgg2 = f"*Wait time: **up to 40sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"           
            #msgg2 = f"*Wait time: **up to 40sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
            embed_msg = embed = discord.Embed(description=msg_prompt, color=0x0000ff)
            
            # embed_redo = embed = discord.Embed(description=msg_prompt, color=0xff0000)
            #await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked
            

            wait_msg1 = await channel.send(msgg1)
            emb_msg =  await channel.send(embed=embed_msg)
            wait_msg2 = await channel.send(msgg2)
            #  wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
            #wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
            if mode == "speed" and msgg1 == "*Redoing image with realistic model...*":
                model = "turbo_pixelwaveturbo_01.safetensors"          

            if model == "turbo_pixelwaveturbo_01.safetensors" or model == "turbovisionxlSuperFastXLBasedOnNew_tvxlV431Bakedvae.safetensors" or model == "dreamshaperXL_turboDpmppSDEKarras.safetensors":
                mode = "speed"
            else:
                mode = "quality"
            
            #  VAE = False
            if support:
                support = support
            else:
                support = msg_prompt
            if model == "sdXL_v10VAEFix.safetensors":
                files, image_name = await generate_image_refiner(V4, msg_prompt, neg_prompt, w , h, keyword, model, three, vae, lora, support)  
            elif mode == "speed":
                files, image_name, seed = await generate_image_turbo(V4, msg_prompt, neg_prompt, w , h, keyword, model, three, vae, lora, support)  
            else:
                #files, image_name  = await generate_image(V4, msg_prompt, neg_prompt, w , h, keyword, model, three, vae, lora, support)
                vae = False  
                files, image_name  = await generate_image_cascade(V4, msg_prompt, neg_prompt, w , h, keyword, three, vae, lora, support)
                #files, image_name  = await generate_image_playground(V4, msg_prompt, neg_prompt, w , h, keyword, three, vae, lora, support)
            await wait_msg1.delete()
            await emb_msg.delete()
            await wait_msg2.delete()
            await wait_gif.delete()

            most_recent_key = max(prompts.keys())
            most_recent_entry = prompts[most_recent_key]

            most_recent_original  = most_recent_entry["original"]
            most_recent_styled    = most_recent_entry["styled"]
            most_recent_enchanted = most_recent_entry["enchanted"]

            #   if not( most_recent_original == original_content or most_recent_styled == styled_content or most_recent_enchanted == enchanted_content):
            #      emb_msg =  await channel.send(embed=embed_msg)

            if most_recent_original != original_content:
                emb_msg =  await channel.send(embed=embed_msg)

            # new_message =   await channel.send(files=files, view=MyView())
           # if redo:
           #   new_message =   await channel.send(files=files)
           # else:
            new_message =   await channel.send(files=files, view=MainButtons())
            msg_id = new_message.id

            new_prompt = {
                f"{msg_id}": {
                    "original": original_content,
                    "styled": styled_content,  # Add your styled content here
                    "enchanted": enchanted_content,  # Add your enchanted content here
                    "negative": neg_prompt,  # Add your enchanted content here
                    "support_prompt": support,
                    "h": h,
                    "w": w,
                    "model": model,
                    "latest_action": recent_action,
                    "name_of_image": image_name,
                    "mode": mode,
                    "seed": seed
                }
            }
            prompts.update(new_prompt)
            try:
                with open("prompts.json", "w") as file:
                    json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                    file.write('\n')
            except (FileNotFoundError, PermissionError, IOError) as e:
                print(f"Error: {e}")
         else:
             await channel.send("*Prompt is being enchanted, please try again after it is done.*")

        @discord.ui.button(label="reDo", custom_id="redo_button", row = 1, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def redo_button_callback(self, button, interaction):
            await interaction.response.defer()
            if execute_code:      
                redo = True
                three = False
                #message_id = interaction.message.id
                search_key = f"{echo_message_id}"                
                msgg1 = f"*Redoing image with same prompt...*"

                w                 = prompts.get(str(search_key), {}).get("w", "")
                h                 = prompts.get(str(search_key), {}).get("h", "")
                model             = prompts.get(str(search_key), {}).get("model", "")
                
                await self.common_button_function(w, h, three,search_key, msgg1, redo, model )
            else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")
            #  print(f"The button was pressed on message with ID: {message_id}")

        @discord.ui.button(label="x3", custom_id="x3_button", row = 1, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def x3_button_callback(self, button, interaction):
           await interaction.response.defer()
           if execute_code:
                redo = True
                three = True
                #message_id = interaction.message.id
                search_key = f"{echo_message_id}" 
                msgg1 = f"*Redoing 3 images with same prompt...*"

                w                 = prompts.get(str(search_key), {}).get("w", "")
                h                 = prompts.get(str(search_key), {}).get("h", "")
                model             = prompts.get(str(search_key), {}).get("model", "")
                
                await self.common_button_function(w, h, three,search_key, msgg1, redo, model )
           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")
            #  print(f"The button was pressed on message with ID: {message_id}")

        @discord.ui.button(label="8:5", custom_id="8:5_button", row = 2, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def landsp85_redo_button_callback(self, button, interaction):
           await interaction.response.defer()
           if execute_code:

                w = 1216
                h = 768
                redo = False
                three = False
                msgg1 = f"*Redoing image with 8:5 aspect ratio...*"
                #message_id = interaction.message.id
                search_key = f"{echo_message_id}"
                model             = prompts.get(str(search_key), {}).get("model", "")

                await self.common_button_function(w, h, three,search_key, msgg1, redo, model )


           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")

        @discord.ui.button(label="16:9", custom_id="16:9_button", row = 2, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def landsp_redo_button_callback(self, button, interaction):
           await interaction.response.defer()
           if execute_code:

                
                w = 1344
                h = 768
                redo = False
                three = False
                msgg1 = f"*Redoing image with 16:9 aspect ratio...*"
                #message_id = interaction.message.id
                search_key = f"{echo_message_id}"
                model             = prompts.get(str(search_key), {}).get("model", "")

                await self.common_button_function(w, h, three,search_key, msgg1, redo, model )

           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")

        @discord.ui.button(label="21:9", custom_id="21:9_button", row = 2, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def landsp219_redo_button_callback(self, button, interaction):
           await interaction.response.defer()
           if execute_code:

                
                w = 1536
                h = 640
                redo = False
                three = False
                msgg1 = f"*Redoing image with 21:9 aspect ratio...*"
               # message_id = interaction.message.id
                search_key = f"{echo_message_id}"
                model             = prompts.get(str(search_key), {}).get("model", "")

                await self.common_button_function(w, h, three,search_key, msgg1, redo, model )

           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")

        @discord.ui.button(label="Upscale x2", custom_id="upscalex2_button", row = 2, style=discord.ButtonStyle.secondary, disabled = True) # Create a button with the label "😎 Click me!" with color Blurple
        async def upscalex2_redo_button_callback(self, button, interaction):
           await interaction.response.defer()
           if execute_code:

                await all_button_msg.delete()
                search_key = f"{echo_message_id}"
                enchanted_content = prompts.get(str(search_key), {}).get("enchanted", "")
                original_content  = prompts.get(str(search_key), {}).get("original", "")
                styled_content    = prompts.get(str(search_key), {}).get("styled", "")   
                support           = prompts.get(str(search_key), {}).get("support_prompt", "")             
                recent_action     = prompts.get(str(search_key), {}).get("latest_action", "")           
                neg_prompt        = prompts.get(str(search_key), {}).get("negative", "")


                if recent_action == "random style":
                    msg_prompt = styled_content
                    neg_prompt = prompts.get(str(search_key), {}).get("negative", "")
                elif recent_action == "AI Enhance":
                    msg_prompt = enchanted_content
                else:
                    msg_prompt = original_content

                V4 = True
                keyword = "echo"
                w                 = prompts.get(str(search_key), {}).get("w", "")
                h                 = prompts.get(str(search_key), {}).get("h", "")
                redo = False
                three = False
                msgg1 = f"*Redoing image with 21:9 aspect ratio...*"
               # message_id = interaction.message.id
                
                #model             = prompts.get(str(search_key), {}).get("model", "")
                seed             = prompts.get(str(search_key), {}).get("seed", "")
                upscale_times = 0.5
                # model = "juggernautXL_version6Rundiffusion.safetensors"
                model        = prompts.get(str(search_key), {}).get("model", "")
                #model = "turbo_pixelwaveturbo_01.safetensors"
                channel = client.get_channel(1101461174907830312)
                #await chose_model.delete()
                msgg = "*Upscaling image x2 ... wait time: **up to 30sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                wait_msg = await channel.send(msgg)
                # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
                #wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
                wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
                channel.trigger_typing                          
                lora = False
                files = []
                three = False
                vae = True
                support = msg_prompt
                #neg_prompt = ""
                            
                files, image_name = await generate_image_turbo_upscale(V4, msg_prompt, neg_prompt, w , h, keyword, model, three,vae, lora, support,seed, upscale_times ) 


                await wait_msg.delete()
                await wait_gif.delete()

                w_new = w * 2
                h_new = h * 2
                upscaled_to = f"Upscaled to *{w_new}x{h_new}*"
                embed_msg = discord.Embed(description=upscaled_to, color=0x00ff00)

                emb_msg =   await channel.send(embed=embed_msg)
                new_message =   await channel.send(files=files)

                msg_id = new_message.id
                # new_prompt = {f"{msg_id}": input_en}

                new_prompt = {
                    f"{msg_id}": {
                        "original": msg_prompt,
                        "styled": "",  # Add your styled content here
                        "enchanted": "",  # Add your enchanted content here
                        "support_prompt": "",
                        "h": h,
                        "w": w,
                        "negative": neg_prompt,
                        "model": model,
                        "latest_action": "original",
                        "name_of_image": image_name,
                        "mode": "speed",
                        "seed": seed
                    }
                }

                prompts.update(new_prompt)
                with open("prompts.json", "w") as file:
                    json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                    file.write('\n')

           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")
        @discord.ui.button(label="5:8", custom_id="5:8_button", row = 3, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def port58_redo_button_callback(self, button, interaction):
           await interaction.response.defer()
           if execute_code:

                w = 768
                h = 1216
                redo = False
                three = False
                msgg1 = f"*Redoing image with 5:8 aspect ratio...*"
                #message_id = interaction.message.id
                search_key = f"{echo_message_id}"
                model             = prompts.get(str(search_key), {}).get("model", "")

                await self.common_button_function(w, h, three,search_key, msgg1, redo, model )

           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")

        @discord.ui.button(label="9:16", custom_id="9:16_button", row = 3, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def portr_redo_button_callback(self, button, interaction):
           if execute_code:

                w = 768
                h = 1344
                three = False
                redo = False
                msgg1 = f"*Redoing image with 9:16 aspect ratio...*"
                #message_id = interaction.message.id
                search_key = f"{echo_message_id}"
                model             = prompts.get(str(search_key), {}).get("model", "")

                await self.common_button_function(w, h, three,search_key, msgg1 ,redo, model )


           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")

        @discord.ui.button(label="9:21", custom_id="9:21_button", row = 3, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def portr921_redo_button_callback(self, button, interaction):
           if execute_code:

                w = 640
                h = 1536
                three = False
                redo = False
                msgg1 = f"*Redoing image with 9:21 aspect ratio...*"
                #message_id = interaction.message.id
                search_key = f"{echo_message_id}"
                model             = prompts.get(str(search_key), {}).get("model", "")

                await self.common_button_function(w, h, three,search_key, msgg1 ,redo, model )


           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")



        @discord.ui.button(label="Realistic", custom_id="realistic_button", row = 4, style=discord.ButtonStyle.secondary, disabled = True) # Create a button with the label "😎 Click me!" with color Blurple
        async def realistic_callback(self, button, interaction):
           await interaction.response.defer()
           if execute_code:
                neg_prompt = "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)"
                redo = False
                three = False
                msgg1 = "*Redoing image with realistic model...*"




                #message_id = interaction.message.id
                search_key = f"{echo_message_id}"
                mode              = prompts.get(str(search_key), {}).get("mode", "")
                if mode == "speed":
                    model = "juggernautXL_v8Rundiffusion.safetensors"
                else:
                  #  model             = "leosamsHelloworldSDXLModel_helloworldSDXL20.safetensors"
                   # model             = "juggernautXL_v7Rundiffusion.safetensors"
                    model             = "realvisxlV30_v30Bakedvae.safetensors"
                #model             = "juggernautXL_version6Rundiffusion.safetensors"
                w                 = prompts.get(str(search_key), {}).get("w", "")
                h                 = prompts.get(str(search_key), {}).get("h", "")

                await self.common_button_function(w, h, three,search_key, msgg1, redo, model )

           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")

        @discord.ui.button(label="Artistic", custom_id="artistic_button2", row = 4, style=discord.ButtonStyle.secondary, disabled = True) # Create a button with the label "😎 Click me!" with color Blurple
        async def artistic_button2_callback(self, button, interaction):
           await interaction.response.defer()
           if execute_code:
                neg_prompt        = "bad quality, bad anatomy, worst quality, low quality, lowres, extra fingers, blur, blurry, ugly, wrong proportions, watermark, image artifacts,"
                redo = False
                three = False
                msgg1 = f"*Redoing image with Artistic model...*"




                #message_id = interaction.message.id
                search_key = f"{echo_message_id}"
                model             = "leosamAiartSDXL_v10.safetensors" 
                mode              = prompts.get(str(search_key), {}).get("mode", "")
                w                 = prompts.get(str(search_key), {}).get("w", "")
                h                 = prompts.get(str(search_key), {}).get("h", "")

                if mode == "seed":
                    model = "turbovisionxlSuperFastXLBasedOnNew_tvxlV431Bakedvae.safetensors"
                else:
                    model             = "leosamAiartSDXL_v10.safetensors" 

                await self.common_button_function(w, h, three,search_key, msgg1, redo, model )


           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")

        @discord.ui.button(label="Dalle-3", custom_id="Dalle32_button", row = 4,  style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
        async def Dalle3reDo2_button__callback(self, button, interaction):
            await interaction.response.defer()
            await all_button_msg.delete()
            channel = client.get_channel(1101461174907830312)
            #  model = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"
            #message_id = interaction.message.id
            search_key = f"{echo_message_id}"
            original_content  = prompts.get(str(search_key), {}).get("original", "")
            msgg = "*Echoing image using Dalle-3... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"

            wait_msg = await channel.send(msgg)
            # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
            #wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
            channel.trigger_typing   
                            
            try:
                response = client_dalle.images.generate(
                    model="dall-e-3",
                    prompt=original_content,
                    size="1024x1024",
                    quality="hd",
                    n=1,
                )
                image_url = response.data[0].url
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
                await wait_msg.delete()
                await wait_gif.delete()
                new_message = await channel.send(file=file, view = Dalle_buttons2())
                         
                msg_id = new_message.id     
                new_prompt = {
                    f"{msg_id}": {
                        "original": original_content,
                        "styled": "",  # Add your styled content here
                        "enchanted": "",  # Add your enchanted content here
                        "negative": "",  # Add your enchanted content here
                    }
                }

                prompts.update(new_prompt)
                with open("prompts.json", "w") as file:
                    json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                    file.write('\n')                               
            except openai.error.InvalidRequestError:
                await message.channel.send('Tavs pieprasījums tika noraidīts.')

        @discord.ui.button(label="GIF", custom_id="gif_redo_original_button", row = 4,  style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
        async def GIFreDo1_button__callback(self, button, interaction):
         channel = client.get_channel(1101461174907830312)  
         if not_enchanting:
           if execute_code:
            await interaction.response.defer()
            await all_button_msg.delete()
                          
            #  model = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"
            #message_id = interaction.message.id
            search_key = f"{echo_message_id}"
            original_content  = prompts.get(str(search_key), {}).get("original", "")
            enchanted_content  = prompts.get(str(search_key), {}).get("enchanted", "")
            styled_content  = prompts.get(str(search_key), {}).get("styled", "")
            image_name  = prompts.get(str(search_key), {}).get("name_of_image", "")
            
            recent_action  = prompts.get(str(search_key), {}).get("latest_action", "")

            if recent_action == "AI Enhance":
                prompt = enchanted_content
            elif recent_action == "original":
                prompt = original_content
            else:
                prompt = styled_content


            model = ""
            msgg = "*Echoing gif ... wait time: **up to 100sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
            wait_msg = await channel.send(msgg)
            # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
            #wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
            channel.trigger_typing                          
            lora = False
            files = []
            three = False
            vae = False
            frame_amount = 48
            PingPong = False
                            
            files =  await generate_gif(prompt, image_name, PingPong)


            await wait_msg.delete()
            await wait_gif.delete()



            seconds = frame_amount/12
            msg_prompt = f"Length: {seconds}"
            embed_msg = embed = discord.Embed(description=msg_prompt, color=0x0000ff)
            new_message =   await channel.send(files=files)

            msg_id = new_message.id
            # new_prompt = {f"{msg_id}": input_en}

            new_prompt = {
                f"{msg_id}": {
                    "original": prompt,
                    "styled": "",  # Add your styled content here
                    "enchanted": "",  # Add your enchanted content here
                    "frame_amount": frame_amount,  # Add your enchanted content here
                    "latest_action": "original",
                    "name_of_image": image_name
                }
            }

            prompts.update(new_prompt)
            try:
                with open("prompts.json", "w") as file:
                    json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                    file.write('\n')
            except (FileNotFoundError, PermissionError, IOError) as e:
                print(f"Error: {e}")
            # print(f"The button was pressed on message with ID: {message_id}")
           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")
         else:
              await channel.send("*Prompt is being enchanted, please try again after it is done.*")

        @discord.ui.button(label="Creative", custom_id="creative_button2", row = 4, style=discord.ButtonStyle.secondary, disabled = True) # Create a button with the label "😎 Click me!" with color Blurple
        async def creative_button2_callback(self, button, interaction):
           await interaction.response.defer()
           if execute_code:
                neg_prompt        = "bad quality, bad anatomy, worst quality, low quality, lowres, extra fingers, blur, blurry, ugly, wrong proportions, watermark, image artifacts,"
                redo = False
                three = False
                msgg1 = f"*Redoing image with creative model...*"




                #message_id = interaction.message.id
                search_key = f"{echo_message_id}"
                model             = "paradox2SDXL10_paradox2SDXL10.safetensors" 
                w                 = prompts.get(str(search_key), {}).get("w", "")
                h                 = prompts.get(str(search_key), {}).get("h", "")

                await self.common_button_function(w, h, three,search_key, msgg1, redo, model )


           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")

        @discord.ui.button(label="AI Enhance", custom_id="ench_button", row = 1, style=discord.ButtonStyle.success) # Create a button with the label "😎 Click me!" with color Blurple
        async def enhance_button_callback(self, button, interaction):
           await interaction.response.defer()
           global not_enchanting
           if execute_code:
            V4 = True
           # neg_prompt = "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)"
            w = 1024
            h = 1024
            keyword = "echo"
            await all_button_msg.delete()


            channel = client.get_channel(1101461174907830312)

            #message_id = interaction.message.id
            search_key = f"{echo_message_id}"

            original_content  = ""
            enchanted_content = ""
            styled_content    = ""

            seed = 0
            enchanted_content = prompts.get(str(search_key), {}).get("enchanted", "")
            original_content  = prompts.get(str(search_key), {}).get("original", "")
            styled_content    = prompts.get(str(search_key), {}).get("styled", "")
            neg_prompt        = prompts.get(str(search_key), {}).get("negative", "")
            w                 = prompts.get(str(search_key), {}).get("w", "")
            h                 = prompts.get(str(search_key), {}).get("h", "")
            model             = prompts.get(str(search_key), {}).get("model", "")
            mode             = prompts.get(str(search_key), {}).get("mode", "")
            if model == "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors":
                vae = True
            else:
                vae = False

            if model == "leosamsHelloworldSDXLModel_helloworldSDXL20.safetensors":
                vae = True
            else:
                vae = False

           # neg_prompt = "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)"

            if not styled_content:
                msg_prompt = original_content
            else:
                msg_prompt = styled_content

            if model == "sdxlUnstableDiffusers_v8HeavensWrathVAE.safetensors" or model == "sdXL_v10VAEFix.safetensors":
                lora = True
            else:
                lora = False


            enhancing_msg = "*enchanting prompt....*"
            not_enchanting = False
            enchanting =  await channel.send(enhancing_msg) 
            ench_prompt = await enchPrompt(msg_prompt)
            not_enchanting = True
            #support = await enchPrompt_support(msg_prompt)
            support = ench_prompt
            await enchanting.delete()

            msgg1 = f"*Enchanting image with same prompt...*"
            if mode == "speed":
                msgg2 = f"*Wait time: **up to 6sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
            else:
                msgg2 = f"*Wait time: **up to 40sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"

            embed_msg = embed = discord.Embed(description=ench_prompt, color=0x00ff00)

            ench_prompt_done = "**Enchanted:** " + ench_prompt
            embed_ench_prompt_done = embed = discord.Embed(description=ench_prompt_done, color=0x00ff00)
            #await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked
            

            wait_msg1 = await channel.send(msgg1)
            emb_msg =   await channel.send(embed=embed_msg)
            wait_msg2 = await channel.send(msgg2)
         #   wait_gif =  await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
           # wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif") 
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")

            three = False
            if model == "sdXL_v10VAEFix.safetensors":
                files, image_name = await generate_image_refiner(V4, ench_prompt, neg_prompt, w , h, keyword, model, three, vae, lora, support)   
            elif mode == "speed":
                files, image_name, seed = await generate_image_turbo(V4, ench_prompt, neg_prompt, w , h, keyword, model, three, vae, lora, support)  
            else:
                #files, image_name = await generate_image(V4, ench_prompt, neg_prompt, w , h, keyword, model, three, vae, lora, support)   
                files, image_name  = await generate_image_cascade(V4, ench_prompt, neg_prompt, w , h, keyword, three, vae, lora, support)
                #files, image_name  = await generate_image_playground(V4, ench_prompt, neg_prompt, w , h, keyword, three, vae, lora, support)
            await wait_msg1.delete()
            await emb_msg.delete()
            await wait_msg2.delete()
            await wait_gif.delete()

            emb_ench_prompt_done =   await channel.send(embed=embed_ench_prompt_done)
            new_message =   await channel.send(files=files, view=MainButtons())


            msg_id = new_message.id

            new_prompt = {
                f"{msg_id}": {
                    "original": original_content,
                    "styled": styled_content,  # Add your styled content here
                    "enchanted": ench_prompt,  # Add your enchanted content here
                    "negative": neg_prompt,  # Add your enchanted content here
                    "support_prompt": support,
                    "h": h,
                    "w": w,
                    "model": model,
                    "latest_action": "AI Enhance",
                    "name_of_image": image_name,
                    "mode": mode,
                    "seed": seed
                }
            }

            prompts.update(new_prompt)
            try:
                with open("prompts.json", "w") as file:
                    json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                    file.write('\n')
            except (FileNotFoundError, PermissionError, IOError) as e:
                print(f"Error: {e}")
            # print(f"The button was pressed on message with ID: {message_id}")

           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")



        @discord.ui.button(label="Random style", custom_id="random_button", row = 1, style=discord.ButtonStyle.danger) # Create a button with the label "😎 Click me!" with color Blurple
        async def random_button_callback(self, button, interaction):
          await interaction.response.defer()
          channel = client.get_channel(1101461174907830312)
          if not_enchanting:
           if execute_code:
            V4 = True
            neg_prompt = "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)"
            w = 1024
            h = 1024
            keyword = "echo"
            await all_button_msg.delete()


            seed = 0
            

            #message_id = interaction.message.id
            search_key = f"{echo_message_id}"

            original_content  = ""
            enchanted_content = ""
            styled_content    = ""

            enchanted_content = prompts.get(str(search_key), {}).get("enchanted", "")
            original_content  = prompts.get(str(search_key), {}).get("original", "")
            styled_content    = prompts.get(str(search_key), {}).get("styled", "")
            neg_prompt        = prompts.get(str(search_key), {}).get("negative", "")
            w                 = prompts.get(str(search_key), {}).get("w", "")
            h                 = prompts.get(str(search_key), {}).get("h", "")
            recent_action     = prompts.get(str(search_key), {}).get("latest_action", "")
            mode              = prompts.get(str(search_key), {}).get("mode", "")
            model             = prompts.get(str(search_key), {}).get("model", "") #sdxlUnstableDiffusers_v8HeavensWrathVAE.safetensors
          #  model             = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"
            if mode == "speed":
                model              = "dreamshaperXL_turboDpmppSDEKarras.safetensors"
           # else:
                #model             = "sdXL_v10VAEFix.safetensors" 


            if model == "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors":
                vae = True
            else:
                vae = False

            if styled_content:
                msg_prompt = original_content
            elif enchanted_content:
                msg_prompt = enchanted_content
            else:
                msg_prompt = original_content

           # if not enchanted_content:
           #     msg_prompt = original_content
          #  else:
          #      msg_prompt = enchanted_content
            #msg_prompt = prompts[search_key]

            with open('styles.json', encoding='utf-8') as fh:
                styles = json.load(fh)


            # Shuffle the keys to access styles in random order
            style_names = list(styles.keys())
            random.shuffle(style_names)

            # Access a random key after shuffling
            prompt = msg_prompt

            random_style_name = random.choice(style_names)
            selected_style = styles[random_style_name]
            rand_prompt = selected_style["prompt"]

            # Format rand_prompt with prompt using an f-string
            formatted_rand_prompt = f"{rand_prompt.replace('{prompt}', prompt)}"

            negative_prompt = selected_style["negative_prompt"]

            neg_prompt = "bad quality, bad anatomy, worst quality, low quality, lowres, extra fingers, blur, blurry, ugly, wrong proportions, watermark, image artifacts, " + negative_prompt

         #   embed_Style = "Style:" + random_style_name  + f"\n prompt: {msg_prompt}"
            if "Style:" in random_style_name:
                embed_Style = random_style_name + f"\n prompt: {formatted_rand_prompt}"
            else:
                embed_Style = "**Style:** " + random_style_name + f"\n **prompt:** {formatted_rand_prompt}"


            if model == "sdxlUnstableDiffusers_v8HeavensWrathVAE.safetensors" or model == "sdXL_v10VAEFix.safetensors":
                lora = True
            else:
                lora = False

            msgg1 = f"*Applying random style to prompt...*"
           # msgg2 = f"*Wait time: **up to 40sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"

            if mode == "speed":
                msgg2 = f"You are using **speed mode**. *Wait time: **up to 6sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
            else:
                msgg2 = f"You are using **quality mode**. *Wait time: **up to 40sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"

            embed_msg = embed  = discord.Embed(description=msg_prompt, color=0xff0000)
            embed_style = embed = discord.Embed(description=embed_Style, color=0xff0000)

            #await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked
            

            wait_msg1 = await channel.send(msgg1)
            emb_msg =   await channel.send(embed=embed_msg)
            wait_msg2 = await channel.send(msgg2)
          #  wait_gif =  await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
            #wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")  
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")


            three = False
            support = formatted_rand_prompt
            if mode == "speed":
                files, image_name, seed = await generate_image_turbo(V4, formatted_rand_prompt, neg_prompt, w , h, keyword, model, three, vae, lora, support)
            else:
                #files, image_name = await generate_image_refiner(V4, formatted_rand_prompt, neg_prompt, w , h, keyword, model, three, vae, lora, support)   
                files, image_name  = await generate_image_cascade(V4, formatted_rand_prompt, neg_prompt, w , h, keyword, three, vae, lora, support)
                #files, image_name  = await generate_image_playground(V4, formatted_rand_prompt, neg_prompt, w , h, keyword, three, vae, lora, support)
            await wait_msg1.delete()
            await emb_msg.delete()
            await wait_msg2.delete()
            await wait_gif.delete()

            embed_style =   await channel.send(embed=embed_style)
            new_message =   await channel.send(files=files, view=MainButtons())


            msg_id = new_message.id

            new_prompt = {
                f"{msg_id}": {
                    "original": original_content,
                    "styled": formatted_rand_prompt,  # Add your styled content here
                    "enchanted": enchanted_content,  # Add your enchanted content here
                    "negative": neg_prompt,  # Add your enchanted content here
                    "support_prompt": support,
                    "h": h,
                    "w": w,
                    "model": model,
                    "latest_action": "random style",
                    "name_of_image": image_name,
                    "mode": mode,
                    "seed": seed
                }
            }
            prompts.update(new_prompt)
            try:
                with open("prompts.json", "w") as file:
                    json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                    file.write('\n')
            except (FileNotFoundError, PermissionError, IOError) as e:
                print(f"Error: {e}")
            # print(f"The button was pressed on message with ID: {message_id}")

           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")
          else:
              await channel.send("*Prompt is being enchanted, please try again after it is done.*")

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


   @client.event
   async def on_ready():  
    client.add_view(MyView()) # Registers a View for persistent listening
    client.add_view(Dalle_buttons2()) # Registers a View for persistent listening
    client.add_view(gif_buttons()) # Registers a View for persistent listening
    client.add_view(MainButtons()) # Registers a View for persistent listening
    #client.add_view(Model_mode_buttons()) # Registers a View for persistent listening
    global PreviousWins
    global firstBoot
    global thread_id
    print(f'{client.user} is back online!')
    print('Connected to the following guilds:')
    with open('left_guilds.txt', 'a', encoding="utf-8") as f:
        for guild in client.guilds:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f'\n{timestamp}: {guild.name} (id: {guild.id})'
            print(message)
            f.write(message)

############################ NEW STUFF 13.11 ##################################

    # env variables
    load_dotenv()
    gpt_key               = os.getenv("GPT")

    # OpenAI API
    client_gpt = AsyncOpenAI(api_key=gpt_key)

    utc_now = datetime.utcnow()
    local_timezone = pytz.timezone('Africa/Mbabane')
    local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    # Šodienas datums
    today = str(local_now.date())
    #print(today)
   # today = "2023-11-12"

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


############################ NEW STUFF 13.11 ##################################

   # try:
   #     channel_id =1030490392510079063
   ##     channel = client.get_channel(channel_id)
    #    messages = []
     #   messages = await channel.history(limit=100).flatten() # Retrieve all messages in the channel
   #     i = 0
   #     amount = 0

    #    async for message in channel.history(limit=500, ):
    #     if message.created_at.month == 11 and message.created_at.day == 12:
    #         messages.append(message)
   #     for message in reversed(messages):
   #         i = i+1
   #         name = message.author.name
   #         if message.author.name == "Resnā mamma":
    #            name = "Elizabete"
    #        else: 
    #            name = message.author.name

     #       created_at_utc = message.created_at.replace(tzinfo=pytz.utc)
    #        desired_timezone = pytz.timezone("Africa/Bujumbura")
     #       created_at_local = created_at_utc.astimezone(desired_timezone)
   
     #       time_stamp = created_at_local.strftime('%d-%m %H:%M:%S')
     #       new_message = f"{name}[{time_stamp}]:  '{message.content}'"
    #        await add_message_to_thread(client_gpt, thread_id, new_message)
    #        print(new_message)
     #       if i == 57:
     #           await asyncio.sleep(60)
             
      #          amount = amount + i
     #           i = 0
   # except Exception:
   #     pass
   # print("Done adding to thread: {amount}")



    # Count and print the number of messages sent today
   # message_count = len(i)
   # await ctx.send(f'The number of messages sent today is: {message_count}')
    #print(today)
   # print(f'The number of messages sent today is: {i}')


   ############################### response to message with reply##################


  #  channel = client.get_channel(1030490392510079063)
  #  replied_message = await channel.fetch_message(1173507746931417120)
   # replied_zina = replied_message.content
  #  current_zina = await channel.fetch_message(1173508447241765026)
  #  current_zina_1 = current_zina.content
  #  tones = ["sarcastic", "assertive", "sad", "cynical", "indignant", "contemplative", "witty", "persuasive", "rude", "angry", "romantic", "humorous", "adventurous", "creative", "friendly", "optimistic", "pessimistic", "nostalgic", "hopeful", "enthusiastic", "ambivalent", "descriptive", "suspenseful", "factual", "informative", "playful", "inspiring", "melancholic", "mysterious", "objective", "subjective", "sympathetic", "empathetic", "reflective", "confident", "satirical", "ironic", "sincere", "cautious", "credible", "informal", "formal", "professional", "scholarly", "inspirational", "controversial", "diplomatic", "nurturing", "authoritative", "didactic", "patronizing", "dismissive", "unemotional", "nihilistic"]

   # random.seed(time.time())
  #  selected_tone = random.choice(tones)

    #name = getUserName(replied_message.author.name)
    #if name is not None:
        #vards  = unidecode(name)
    #    vards = message.author.name
   # else:
   #     vards = message.author.name
   # if '.' in vards: # Check if nickname exists and contains dots
   #         vards = vards.replace('.', '') 
  #  await channel.trigger_typing()

  #  gpt_key               = os.getenv("GPT")
   # client_chat = OpenAI(api_key=gpt_key)

   # responsee = client_chat.chat.completions.create(
   # model='gpt-4-1106-preview',
  #  messages = [
  #  {"role": "system", "content": f" Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. You pretend that you have given response, recieved an answer from user and reply with compact random response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Sometimes use random emoji"},
  #  {"role": "user", "content": f"you wrote this answer '{replied_zina}'  and users wrote in response '{current_zina}' give random short or medium  answer in context in latvian"}
  #  ],
  #  max_tokens=700,
  #  n=1,
  #  stop=None,
  #  temperature=0.6,
  #  )                              
   # response = responsee.choices[0].message.content
   # response = response.replace('"', '')
   # response = response.replace("'", "")
  #  await current_zina.reply(response)
   # givenResponses.append([message.content,[response]])
   # saveResponse(givenResponses)




   ############################### response to message with reply##################

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
#{user13.mention} 19 r3equests(19 images)\n\
#{user14.mention} 16 requests(48 images)\n\
#{user15.mention} 12 requests(36 images)\n\
#{user16.mention} 10 requests(30 images)")
     ################### generate amount in month ###################

     # ģeneret offline message 11.10.2023
   # channel = client.get_channel(1101461174907830312)
   # wait_gif = await channel.send("https://media.giphy.com/media/CrWs8NT760qo0Hh5dd/giphy.gif") 







   ############################## register messages up until specifc one #################################
   # try:
    messages = []
    channel_id = 1030490392510079063
    channel = client.get_channel(channel_id)
    msg_ID_stop =  1191136016321482892
    msg1 = "None"
    msg2 = "None"
    msg1_temp = ""
    i = 0
    n = 0
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
    #for message in reversed(messages):
   # if latest_msg_ID["ID"] == 1030490906161324184:
  #      with open('all_msgs.json', 'w') as file:
   #         json.dump(messages_rev,file)
   # latest_msg_ID["ID"] = 1205829811210027049
    with open("most_recent_saved_msg.json", "w") as file:
        json.dump(latest_msg_ID, file, indent=4)  # You can adjust the indent for pretty printing
    for message in messages_rev:
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
                            channel = client.get_channel(1030490392510079063)
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
                 await add_message_to_thread(client_gpt, thread_id, new_message)
                 print(new_message)
                 if i == 57:
                    await asyncio.sleep(60)
             
                    amount = amount + i
                    i = 0

    with open('testt.json', 'w') as file:
             json.dump(addition_colltected,file)
                     #msg2 = message.content
 
                     
                 #print(f"msg1: {msg1}\nmsg2: {msg2}\n\n")
    #             print(message.content)
  #              i = i+1
   ##             name = message.author.name
  #              if message.author.name == "Resnā mamma":
   #                 name = "Elizabete"
   #             else: 
   #                name = message.author.name

   #             created_at_utc = message.created_at.replace(tzinfo=pytz.utc)
   #             desired_timezone = pytz.timezone("Africa/Bujumbura")
   #             created_at_local = created_at_utc.astimezone(desired_timezone)
   
   #             time_stamp = created_at_local.strftime('%d-%m %H:%M:%S')
   #             new_message = f"{name}[{time_stamp}]:  '{message.content}'"
   #             await add_message_to_thread(client_gpt, thread_id, new_message)
   #             print(new_message)
   #             if i == 57:
   #                 await asyncio.sleep(60)
             
  #                  amount = amount + i
   #                 i = 0
 #   except Exception:
   #    print("error")
   #    pass
   ############################## register messages up until specifc one #################################

   ############# Varda dienas ################
    with open('namedays_showed.json', 'r', encoding='utf-8') as file:
        namedays_showed = json.load(file)
    today = datetime.now().strftime("%m-%d")
    with open('namedays.json', 'r', encoding='utf-8') as file:
        name_days = json.load(file)
    if today not in namedays_showed:
        if today in name_days:
            namedays_showed.append(today)
            with open('namedays_showed.json', 'w', encoding='utf-8') as file:
                json.dump(namedays_showed,file)
            channel_id = 1030490392510079063
            channel = client.get_channel(channel_id)
            names = ", ".join(name_days[today])
            await channel.send(f"Šodien({today}) vārda dienu svin :biting_lip: : {names}")
        else:
            await channel.send(f"Šodien({today}) neviens nesvin vārda dienu.")
   ############# Varda dienas ################


    # Izveido statusuw
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over your shoulder"))


    # Izveido grafiku, kad sūta ziņas pats
    #asyncio.create_task(schedule_messages()) #@#


    channel = client.get_channel(SCREENSHOT_CHANNEL_ID)

   # message_to_editt = await channel.fetch_message(1169047929764454471)
    #xxl = await channel.fetch_message(1089420313026113538)
    #await xxl.add_reaction('🔥')
    CHECKMARK_EMOJI = "✅"

    #if firstBoot:


        # Iet cauri nelasītajām ziņām
       # firstBoot = False
    async for message in channel.history(limit=None, oldest_first=False):
        # Pārbauda vai ziņa atzīmēta ar ķeksīti
        if any(reaction.emoji == CHECKMARK_EMOJI for reaction in message.reactions):
     #   if message.created_at.month == 9 and message.created_at.day < 30 :
            print("Went through all messages up until green checkmark.")
        #    print("September wins collected.")
            break
      #  if message.created_at.day == 30 and message.created_at.hour + 3 < 21:
            #print("Went through all messages up until green checkmark.")
        #    print("September wins collected.")
       #     continue      
        #Pārbauda vai pievienots attēls
        #if message.created_at.month == 9 :
        if any(attachment.filename.lower().endswith(tuple(SCREENSHOT_EXTENSIONS)) for attachment in message.attachments):
         if message.author.id != 1085573614193094696:
          #  month  = message.created_at.month
         #   day    = message.created_at.day
         #   hour   = message.created_at.hour + 3
         #   minute = message.created_at.minute

          #  print(f"\nCurrent message: {day}.0{month} {hour}:{minute}")
          #  print(PreviousWins)
          #  print("\n")
            multip = 0
            recap = True
           
               
            #Pārbauda vai pievienots reizinātājs
            if message.content.startswith(prefix1) or message.content.startswith(prefix2) :
            # if message.created_at.month == 9 :

                num_string = message.content[len(prefix1):].strip()
                #multip = int(num_string)
                #PreviousWins = PreviousWins + multip
                match = re.search(r'x(\d+)', message.content)

                if match:
                    number_str = match.group(1)
                    multip = int(number_str)
                    PreviousWins = PreviousWins + multip
                    for x in range(multip):
                        await Register_time(f"{message.created_at.hour+2}")
                        #Reģistrē uzvaru, ja iespējams, ja nē, saglabā attēlu manuālai ievadei
                        await RegTotalMonthWins(1,message.created_at.month)
                        sendConfirm = False # Nesūtīt paziņojumu čatā
                        isStreak = True 
                        if x + 1 == multip: sendConfirm = True 
                        await RegisterWin(game_wins, message, recap, sendConfirm, isStreak)           
            else:

                await Register_time(f"{message.created_at.hour+2}")
                await RegTotalMonthWins(1,message.created_at.month)
                sendConfirm = True # Nosūtīt paziņojumu čatā
                isStreak = False  
                await RegisterWin(game_wins, message, recap, sendConfirm, isStreak) 
                PreviousWins = PreviousWins + 1

    filename = "temp_win_recap.json"
    if os.path.isfile(filename):
       with open('temp_win_recap.json', 'r') as f:
           recap_game_wins = json.load(f)  

    # Loop through the player data and send messages
    win_recap = []
    for player, games in recap_game_wins.items():
        player_summary = f"{player} Wins:\n"
        for game, wins in games.items():
            player_summary += f"{game}: {wins} wins\n"
        win_recap.append(player_summary)

    final_win_recap = "\n".join(win_recap)

    embed_msg_wins = embed = discord.Embed(title="Collected wins: ", description=final_win_recap, color=0x71368a)



    PreviousWins_str = str(PreviousWins)
    phrase_rec = phrases_awayScore[PreviousWins_str]    
    random.seed(time.time())
    phrases_reason = random.choice(list(phrases_awayReason.values()))
    userr_id = "190926234878738433"
    annoucment = f"{timeOfDay()}, {phrases_reason}.\nDuring this time, you have scored {PreviousWins} wins. {phrase_rec}"
    channel = client.get_channel(1030499571572408390) 
    role = channel.guild.get_role(1030500402023628850)
    role2 = channel.guild.get_role(1089589791466721312)
    role3 = channel.guild.get_role(1033676791166025788)


    #message_to_editt = await channel.fetch_message(1193137841237147770)
   # await message_to_editt.edit(content=f"{role.mention} {role2.mention} {role3.mention} New month new Resnums.\nIn December total win amount was **470**.\n(November: 429,\n October: 378,\n September: 381,\n August: 304,\n July: 302,\n June: 230,\n May: 388,\n April: 597,\n March: 608,\n February: 427,\n January 287.)\n**Total wins ir year 2023: 4846!!**  \nLower in excel files you can view December statistics about yourself.")
 
  #with open('DayTime.xlsx', 'rb') as f1
    #file1 = discord.File(f1, filename='DayTime.xlsx')
   #await message.channel.send(files=[file6, file5, file1, file2, file3, file4]) 1030500402023628850
   # update = f"{role.mention} {role2.mention} {role3.mention} New month new Resnums.\nIn December total win amount was **470**.\n(November: 429,\n October: 378,\n September: 381,\n August: 304,\n July: 302\n, June: 230,\n May: 388,\n April: 597,\n March: 608,\n February: 427,\n January 287.)\nLower in excel files you can view December statistics about yourself."
    #with open('DayTime.xlsx', 'rb') as f1, open('SpecifDay.xlsx', 'rb') as f2, open('EachDay.xlsx', 'rb') as f3, open('resnums.xlsx', 'rb') as f4, open('night.png', 'rb') as f5, open('aft.png', 'rb') as f6:
    #    file1 = discord.File(f1, filename='DayTime.xlsx')
    #    file2 = discord.File(f2, filename='SpecifDay.xlsx')
    #    file3 = discord.File(f3, filename='EachDay.xlsx')
    #    file4 = discord.File(f4, filename='resnums.xlsx')
    #    file5 = discord.File(f5, filename='night.png')
    #    file6 = discord.File(f6, filename='aft.png')
        #embed = discord.Embed(title='April statistics', description='Apskati savu statistiku:')
       # embed.set_image(url='attachment://night.png')
       # embed.set_image(url='attachment://aft.png')
        #embed.add_field(name='Excel file', value='See attachment', inline=False)
    #update = f"Last month:\n• Tuesday proved to be a particularly successful day for <@{userr_id}>, who won the highest number of wins compared to any other player on any day of the week. **53** wins, that is **30%** of Tuedays total. "
    #await InitialBoot(client, SCREENSHOT_CHANNEL_ID, SCREENSHOT_EXTENSIONS)

    if recap_game_wins:
        await message.channel.send(annoucment)
        await channel.send(embed=embed_msg_wins)
        recap_game_wins = {}
        with open('temp_win_recap.json', 'w') as file:
            json.dump(recap_game_wins, file)
   # await message.channel.send(win_recap)

   # await message.channel.send(update)   
   # await message.channel.send(files=[file6, file5, file1, file2, file3, file4])  



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
############## start generator

   APPLICATION_PATH = "F:\\\\comfy\\ComfyUI_windows_portable\\run_nvidia_gpu.bat"
   ORIGINAL_PATH = "C:\\Users\\ZK00138\\source\\repos\\ResnsCounter\\ResnsCounter\\"
   @client.command(hidden=True)
   async def bridge(ctx):
       if ctx.author.id in allowed:           

            # toggle the value of the flag
           os.chdir(os.path.dirname(APPLICATION_PATH))
           os.system(f'start "" "{APPLICATION_PATH}"')
           os.chdir(os.path.dirname(ORIGINAL_PATH))



############## start generator
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
               msgg = "*Visualizing portrait image... wait time: **up to 100sec*** \nFor help go to: https://discord.com/channels/1030490392057085952/1106462449932185643"
           elif oriantation == 'landscape':
               landscape = True
               msgg = "*Visualizing landscape image... wait time: **up to 100sec*** \nFor help go to: https://discord.com/channels/1030490392057085952/1106462449932185643"

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
          # await ctx.send('***Echo** momentarily is disabled. Use **ģenerē** instead.*')
           await ctx.send("GPU power is used for gaming right now. **Echo** is *disabled*.")
######################################## BUILDING NEW FEATURE ##########################



   @client.command(name = 'resnums', description = 'View your current month win progress.' )
   async def resnums(ctx):
       response = ""
       first = True
       
       print('Stats requested...')
       player_name = f"{ctx.author.name}"
       for player, gamee_wins in game_wins.items():
            if player == player_name:
                for game, wins in gamee_wins.items():
                    if first:
                        response = response + f"**{player_name}** has won:\n {wins} times {game} this month.\n"
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
   game_names = ['Apex Legends', 'COD MW2 Multiplayer', 'COD MW3 Multiplayer', 'CS2', 'Destiny 2', 'Fortnite', 'League of Legends', 'Valoant', 'Warzone 2.0', 'War Thunder', 'The Finals']
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
    role7_id = 1086940826829078531 
    #role8_id = 1030530963291254814 # basic
    author_roles = member.roles
    return any(role.id in (role1_id, role2_id, role3_id, role4_id, role5_id, role6_id, role7_id) for role in author_roles)

  ########### SECURITY  ##################################

#############################################################
# 'mammu', 'mam', 'mamm', 'muterit', 'muterite', 'mutere', 'muter'
   pattern = re.compile(r'\b(ay|ey|ou|au|mamma|mammu|aloha|mam|mamm|muterit|muterite|mutere|muter|mama|mammai)\b')

   ########## 7.31
   async def countdown_task():
        channel = client.get_channel(CHANNEL_ID)
        message = await channel.send("Countdown: 60 seconds left!")

        for i in range(intervals - 1, 0, -1):
            await asyncio.sleep(1)
            await message.edit(content=f"Countdown: {i} seconds left!")

        await asyncio.sleep(1)
        await message.edit(content="Countdown: Time's up!")
   ############ 7.31
  ############################## NEW ################################
       
   @client.event
   async def on_message(message):
        
        #print(message.reference.resolved.attachments[0].url)
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
            if message.channel.id != 1101461174907830312:
                print(f'$ {message.author.name} knocking in channel - {message.content} $')
                return    
        ################# SECURITY ######################
        #all
       # tones = ["sarcastic", "assertive", "sad", "cynical", "indignant", "contemplative", "witty", "persuasive", "rude", "angry", "romantic", "humorous", "adventurous", "creative", "friendly", "optimistic", "pessimistic", "nostalgic", "hopeful", "enthusiastic", "ambivalent", "descriptive", "suspenseful", "factual", "informative", "playful", "inspiring", "melancholic", "mysterious", "objective", "subjective", "sympathetic", "empathetic", "reflective", "confident", "satirical", "ironic", "sincere", "cautious", "credible", "informal", "formal", "professional", "scholarly", "inspirational", "controversial", "diplomatic", "nurturing", "authoritative", "didactic", "patronizing", "dismissive", "unemotional", "nihilistic"]
        tones = ["sarcastic", "assertive", "sad", "cynical", "indignant", "contemplative", "witty", "persuasive", "rude", "angry", "romantic", "humorous", "adventurous", "creative", "friendly", "optimistic", "pessimistic", "nostalgic", "hopeful", "enthusiastic", "ambivalent", "descriptive", "suspenseful", "factual", "informative", "playful", "inspiring", "melancholic", "mysterious",  "subjective", "sympathetic", "empathetic", "reflective", "confident", "satirical", "ironic", "sincere",  "credible", "informal", "professional",  "inspirational", "controversial", "nurturing", "authoritative", "didactic",  "dismissive", "unemotional", "nihilistic"]
        #serious 
      #  tones = ["satirical", "witty", "amusing"]


        random.seed(time.time())
        selected_tone = random.choice(tones)
        selected_tone = selected_tone.upper()
        #selected_tone = "witty"
        if 'apsveic' in message.content:
            selected_tone = "festive"
        #selected_tone = "festive"
        global msgCount
        global msg1
        global botMsg
        botMsg = False   
        mind = f"You are a wise all-knowing person named 'Elizabete' who was created 15.03.2023 by Jānis. You can do anything. Respond mainly in Latvian language but others as well if asked. Do not mention you are language model or program.  You answer to any kind of question and request. You can address specific users when requested. One of your tasks is to count game wins.\
                Discord server is called 'Asās resnās mērcītes'.\
                Pretend you can give compliments and advices\
                Use {selected_tone} tone.\
                When asked about people give long response, Use {selected_tone} tone.. \
                Some server users are: Daisy, Valters, Paula, Elvis, Oskars, Madara, notacop, Agris, Ivars, Kapars, swich, Jānis, Vectēvs, Megana, ābolmaizīte, Eliots, Bibops, Evol, anXIETY, gesmens, Kampys, Yogi, Speķmaizīte, Mērčmeistars, Atty, Tom, kachis, Ieva.\
                Pretend you are creative storyteller with vivid imagination whos every story is original. Use {selected_tone} tone.\
                Todays date is {getDate()}.\
                Precīzs pulkstens šobrīd ir {getTime()}"



        # Ignorēt ziņas no citiem botiem
########################### UPDATED ###################
        # Ignorēt ziņas no citiem botiem
        if message.author.bot:
            if "ģenerē" in message.content or "atdarini" in message.content:
                msgCount = 0
                botMsg = True
            else:
                msgCount = 0
                botMsg = True
                return
########################### UPDATED ###################


        if message.channel.id == 1030490392510079063:

             ID = message.author.id
             author_name = message.author.name
             file_to_update =  "IDs.txt"

             if author_name == "Resnā mamma":
                 author_name = "Elizabete"

             add_username_and_id_if_not_exists(author_name, ID, file_to_update)


             with open("data.txt", "a") as file:
                    file.write(f'"{author_name}": "{ID}"\n')  # You can adjust the indent for pretty printing

           


            # env variables
             load_dotenv()
             gpt_key               = os.getenv("GPT")

            # OpenAI API
             client_gpt = AsyncOpenAI(api_key=gpt_key)

             if message.author.name == "Resnā mamma":
                 name = "Elizabete"
             else: 
                 name = message.author.name

             created_at_utc = message.created_at.replace(tzinfo=pytz.utc)
             desired_timezone = pytz.timezone("Africa/Bujumbura")
             created_at_local = created_at_utc.astimezone(desired_timezone)

             time_stamp = created_at_local.strftime('%d-%m %H:%M:%S')
             new_message = f"{name}[{time_stamp}]:  '{message.content}'"
             await add_message_to_thread(client_gpt, thread_id, new_message)
            # print(new_message)
             #print("added")

             latest_msg_ID["ID"] = message.id
             with open("most_recent_saved_msg.json", "w") as file:
                    json.dump(latest_msg_ID, file, indent=4)  # You can adjust the indent for pretty printing

 ############################################# CHATBOT SECTION ########################################


             #print(thread_id)
                    # Check if the message is a reply to the chatbot user who wrote awfter gudrais command
        if message.reference and message.reference.resolved.author == client.user:

            mind = f"You are a wise all-knowing person named 'Elizabete' who was created 15.03.2023 by Jānis. You can do anything. Respond mainly in Latvian language but others as well if asked. Do not mention you are language model or program.  You answer to any kind of question and request.\
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
                      # vards  = unidecode(name)
                       vards = message.author.name
                    else:
                       vards = message.author.name #@#@#
                    if '.' in vards: # Check if nickname exists and contains dots
                            vards = vards.replace('.', '') 

                    gpt_key               = os.getenv("GPT")
                    client_chat = OpenAI(api_key=gpt_key)

                    response = client_chat.chat.completions.create(
                    model='gpt-4-0125-preview',
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

            for word in ['ay', 'ey', 'ou', 'au', 'aloha', 'eu', 'mamma', 'mammu', 'mam', 'mamm', 'muterit', 'muterite', 'mutere', 'muter', 'mammai']:
                 message_modif = ' '.join([w.strip() for w in message_modif.split() if w.strip() != word])
            #if message.author.id == 909845424909729802:
            #    return
            key_word = ["pajautā jautājumu", "atdarini", "gudrais"]
            if  any(word in message_modif for word in key_word) and mentioned_user:
                if message_modif.startswith('pajautā jautājumu'):
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
                        gpt_key               = os.getenv("GPT")
                        client_atdarini = OpenAI(api_key=gpt_key)
                        response = client_atdarini.images.create_variation(
                            image=open('avatar.png', mode="rb"),
                            n=1,
                            size="1024x1024",
                            response_format="url",
                        )
                        image_url = response.data[0].url
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
                       #vards  = unidecode(name)
                       vards = message.author.name
                    else:
                       vards = message.author.name #@#@#
                    if '.' in vards: # Check if nickname exists and contains dots
                            vards = vards.replace('.', '') 

                    gpt_key               = os.getenv("GPT")
                    client_chat = OpenAI(api_key=gpt_key)           
                    
                    response =  client_chat.chat.completions.create(
                        model='gpt-4-0125-preview',
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
                else:
                    test = 0
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


               mind = f"You are a wise all-knowing person named 'Elizabete' who was created 15.03.2023 by Jānis. You can do anything. Respond mainly in Latvian language but others as well if asked. Do not mention you are language model or program.  You answer to any kind of question and request. You can address specific users when requested. One of your tasks is to count game wins.\
                    Discord server is called 'Asās resnās mērcītes'.\
                    Pretend you can give compliments and advices\
                    Use {selected_tone} tone.\
                    Pretend you are creative storyteller with vivid imagination whos every story is original. Use {selected_tone} tone.\
                    Todays date is {getDate()}.\
                    Precīzs pulkstens šobrīd ir {getTime()}"
             
                    
               file_name = "gudrais_latest_ID.json"
               
               
               name = getUserName(message.author.name) #@#@#
               vards = message.author.name
               if name is not None:
                   vards  = unidecode(name)
                   vards = message.author.name
                   
            #   else:
            #       vards = message.author.name #@#@#
           #    if '.' in vards: # Check if nickname exists and contains dots
             #           vards = vards.replace('.', '') 
               await message.channel.trigger_typing()

               gpt_key               = os.getenv("GPT")
               client_chat = OpenAI(api_key=gpt_key)

               response =   client_chat.chat.completions.create(
                    model='gpt-4-0125-preview',
                    messages = [
                    {"role": "system", "content": mind},
                    {"role": "user", "name" : vards, "content": user_input}
                    ],
                    max_tokens=2500,
                    n=1,
                    stop=None,
                    temperature=0.6,
                )
               response = response.choices[0].message.content
               response = response.replace('"', '')
               response = response.replace("'", "")
               generated_text = response
               embed = discord.Embed(description=generated_text, color=0x00ff00)
               gudrais_response = await message.channel.send(embed=embed)
               #update_message_data(gudrais_response.id, thread.id, file_name)
               return
 ############################### NEW ################################   

 # Tiek ģenerēta bilde no promt ar Stable diffusion, ja tas izslēgts, tad ar Dalle 2
            elif "ģenerē" in message.content.lower() or "genere" in message.content.lower():
                    keyword = message_modif.split()[0]
                # Get user input from message

                    user_input = message.content.lower().split(keyword)[1]
                    #input_en = translateMsg(user_input)
                    input_en = user_input
                    await message.channel.trigger_typing()
                    try:
                        response = client_dalle.images.generate(
                          model="dall-e-3",
                          prompt=input_en,
                          size="1024x1024",
                          quality="hd",
                          n=1,
                        )
                        image_url = response.data[0].url
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
                        return
                    except openai.error.InvalidRequestError:
                        await message.channel.send('Tavs pieprasījums bija pārāk horny vai aizskarošs, priekšnieki neļauj man izpausties.')
                        return

            
################################################ TEST ############################ 768


# Ģenerē bildi pēc promt ar stable diffusion, kas tiek hostēts uz paša pc
            elif "generate" in message.content.lower() or "genere" in message.content.lower() or message_modif.startswith("echo") or message_modif.startswith("echo1") or message_modif.lower().startswith("echoai") or message_modif.lower().startswith("echoais"):
               keyword = message_modif.split()[0]
                # Get user input from message
               try:
                class Dalle_buttons(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
                        def __init__(self):
                            super().__init__(timeout=None) # timeout of the view must be set to None

                        @discord.ui.button(label="reDo", custom_id="Dalle3_button",  style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
                        async def Dalle3reDo_button__callback(self, button, interaction):
                            await interaction.response.defer()
                            model             = "sdxlUnstableDiffusers_v8HeavensWrathVAE.safetensors" 
                          #  model = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"
                            message_id = interaction.message.id
                            search_key = f"{message_id}"
                            original_content  = prompts.get(str(search_key), {}).get("original", "")
                            msgg = "*Echoing image using Dalle-3... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"

                            wait_msg = await message.channel.send(msgg)
                           # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
                            wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
                            message.channel.trigger_typing   
                            
                           # try:
                            response = client_dalle.images.generate(
                                model="dall-e-3",
                                prompt=original_content,
                                size="1024x1024",
                                quality="hd",
                                n=1,
                            )
                            image_url = response.data[0].url
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
                            await wait_msg.delete()
                            await wait_gif.delete()
                            new_message = await message.channel.send(file=file, view = Dalle_buttons2())
                         
                            msg_id = new_message.id     
                            new_prompt = {
                                f"{msg_id}": {
                                    "original": original_content,
                                    "styled": "",  # Add your styled content here
                                    "enchanted": "",  # Add your enchanted content here
                                    "negative": "",  # Add your enchanted content here

                                }
                            }

                            prompts.update(new_prompt)
                            with open("prompts.json", "w") as file:
                                json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                                file.write('\n')                               
                          #  except openai.error.InvalidRequestError:
                           #     await message.channel.send('Tavs pieprasījums tika noraidīts.')


                if execute_code:
                    ############################ 21.07
                    ratios_to_resolutions = {
                        "1:1": "1024x1024",
                        "8:5": "1216x768",
                        "4:3": "1152x896",
                        "3:2": "1216x832",
                        "7:5": "1176x840",
                        "16:9": "1344x768",
                        "21:9": "1536x640",
                        "19:9": "1472x704",
                        "3:4": "896x1152",
                        "2:3": "832x1216",
                        "5:7": "840x1176",
                        "9:16": "768x1344",
                        "9:21": "640x1536",
                        "5:8": "768x1216",
                        "9:19": "704x1472"
                    }

                    def set_resolution_from_ratio(input_str):

                        pattern = r"\b\d+:\d+\b"
                        match = re.search(pattern, input_str)
                        if match:
                            extracted_ratio = match.group()
                        else:
                            return None
                        output_string = re.sub(r"--ar\s.*?(?=\s*--|$)", "", input_str)
                        resolution = ratios_to_resolutions.get(extracted_ratio)
                        return resolution, output_string

                ############################## 21.07

                    w = 1024
                    h = 1024
                    size = 2
                    AI = False
                    fantasy = False
                    if keyword == "echo1":
                        size = 1

                    port = False
                    land = False
                    V4 = False
                    void = False
                    ench_succss = False
                    cfg = 4.5
                    Sampling_steps = 15
                    denoising = 0.5 
                    upscale_x = 1.25
                    #neg_prompt = "naked, nude,  easynegative, ng_deepnegative_v1_75t"
                    neg_prompt = "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)"
                    upscaler = "4x-UltraSharp"
                    styles = [""]
                    universal_neg = "ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face"
                    checkpoint = "realvisxlV20_v20Bakedvae.safetensors"
                    prompt = message.content
                    words = message.content.split()
                    ####################### 21.07

                    #resolution, prompt = set_resolution_from_r atio(prompt)
                #    if resolution is not None:

                        #################### 21.07
                    #if words[2] == "portrait":
                    if "portrait" in prompt:
                        port = True
                        h = 1280
                        w = 768
                        # Remove the second word from the list of words
                        #words.pop(2)
                        # Join the remaining words back into a string
                       # new_message = " ".join(words)
                        # Update the message content with the new string
                       # prompt = new_message
                   # elif words[2] == "landscape":
                    elif "landscape" in prompt:
                        land = True
                        w = 1280
                        h = 768
                        # Remove the second word from the list of words
                       # words.pop(2)
                        # Join the remaining words back into a string
                       # new_message = " ".join(words)
                        # Update the message content with the new string
                      #  prompt = new_message
                    ################ look for negative prompt
                    result = set_resolution_from_ratio(prompt)
                    if result is not None:
                         resolution, prompt = result
                         width, height = resolution.split('x')
                         w = int(width)
                         h = int(height)
                    content = prompt                   


                    if keyword.lower() == "echoai" or keyword.lower() == "echoais":
                        AI = False
                        keyword = message_modif.split()[0]
                        prompt = prompt.lower()

                        # Define the regular expression pattern to match text in parentheses with the opening and closing parentheses included
                        patternnn = r'\((.*?)\)'

                        # Use the re.findall() function to find all parentheses
                        matches = re.findall(patternnn, prompt)

                        # Saglabā iekavās uzsvērtos vārdus
                        parentheses = ', '.join(f"({match})" for match in matches)

###########################
                        # Split the message into two parts based on "--no"
                        message_parts = content.split("--no", 1)

                        # Check if there is a part after "--no"
                        if len(message_parts) > 1:
                            # Get the text after "--no" until the next occurrence of "-"
                            neg_prompt = message_parts[1].split("-", 1)[0]
                            if neg_prompt == "uni" or neg_prompt == "Uni":
                                neg_prompt = universal_neg
                            prompt = message_parts[0].strip()
                            prompt = prompt.lower()

############################

                        if "--raw" in prompt:
                            neg_prompt =  ""
                            prompt = prompt.replace("--raw", "")

                      #  prompt_ench = prompt.split(keyword)[1]
                      #  if "--raw" in prompt:
                        #    prompt_ench = prompt_ench
                       # else:
                           # prompt_ench = f"cinematic photo of {prompt_ench}"
                       # enhancing_msg = "*enchanting prompt....*"
                       # enchanting =  await message.channel.send(enhancing_msg) 

                       # prompt_ench = await enchPrompt(prompt_ench)
                      #  if prompt_ench == "error":
                      #      prompt_ench = prompt.split(keyword)[1]
                      #      enchanting_failed =  await message.channel.send("Server error. Using original prompt...")
                      #  await enchanting.delete()

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


                    if AI == False:
                        prompt = prompt.split(keyword)[1]


                    if "--real" in prompt or "--Real" in prompt or "--photographic" in prompt or "--Photographic" in prompt:
                        neg_prompt =  "drawing, painting, crayon, sketch, graphite, impressionist, noisy, blurry, soft, deformed, ugly"
                        prompt = prompt.replace("--real", "")
                        prompt = f"cinematic photo {prompt} . 35mm photograph, film, bokeh, professional, 4k, highly detailed"
                        if AI:
                            prompt_ench = f"cinematic photo {prompt_ench} . 35mm photograph, film, bokeh, professional, 4k, highly detailed"


                    if "--enhance" in prompt or "--Enhance" in prompt:
                        neg_prompt =  "ugly, deformed, noisy, blurry, distorted, grainy"
                        prompt = prompt.replace("--enhance", "")
                        prompt = f"breathtaking {prompt} . award-winning, professional, highly detailed"
                        if AI:
                            prompt_ench = f"breathtaking {prompt_ench} . award-winning, professional, highly detailed"

                    if "--Anime" in prompt or "--anime" in prompt:
                        neg_prompt =   "photo, deformed, black and white, realism, disfigured, low contrast"
                        prompt = prompt.replace("--anime", "")
                        prompt = f"anime artwork {prompt} . anime style, key visual, vibrant, studio anime,  highly detailed"
                        if AI:
                            prompt_ench = f"anime artwork {prompt_ench} . anime style, key visual, vibrant, studio anime,  highly detailed"

                    if "--Digital art" in prompt or "--digital art" in prompt:
                        neg_prompt =  "drawing, painting, crayon, sketch, graphite, impressionist, noisy, blurry, soft, deformed, ugly"
                        prompt = prompt.replace("--digital art", "")
                        prompt = f"concept art {prompt} . digital artwork, illustrative, painterly, matte painting, highly detailed"
                        if AI:
                            prompt_ench = f"concept art {prompt_ench} . digital artwork, illustrative, painterly, matte painting, highly detailed"

                    if "--Comic book" in prompt or "--comic book" in prompt:
                        neg_prompt =  "photograph, deformed, glitch, noisy, realistic, stock photo"
                        prompt = prompt.replace("--comic book", "")
                        prompt = f"comic {prompt} . graphic illustration, comic art, graphic novel art, vibrant, highly detailed"
                        if AI:
                            prompt_ench = f"comic {prompt_ench} . graphic illustration, comic art, graphic novel art, vibrant, highly detailed"

                    if "--Fantasy art" in prompt or "--fantasy art" in prompt:
                        neg_prompt =  "photographic, realistic, realism, 35mm film, dslr, cropped, frame, text, deformed, glitch, noise, noisy, off-center, deformed, cross-eyed, closed eyes, bad anatomy, ugly, disfigured, sloppy, duplicate, mutated, black and white"
                        prompt = prompt.replace("--fantasy art", "")
                        prompt = f"ethereal fantasy concept art of  {prompt} . magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy"
                        if AI:
                            prompt_ench = f"ethereal fantasy concept art of  {prompt_ench} . magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy"

                    if "--Analog film" in prompt or "--analog film" in prompt:
                        neg_prompt =  "painting, drawing, illustration, glitch, deformed, mutated, cross-eyed, ugly, disfigured"
                        prompt = prompt.replace("--analog film", "")
                        prompt = f"analog film photo {prompt} . faded film, desaturated, 35mm photo, grainy, vignette, vintage, Kodachrome, Lomography, stained, highly detailed, found footage"
                        if AI:
                            prompt_ench = f"analog film photo {prompt_ench} . faded film, desaturated, 35mm photo, grainy, vignette, vintage, Kodachrome, Lomography, stained, highly detailed, found footage"

                    if "--Neonpunk" in prompt or "--neonpunk" in prompt:
                        neg_prompt =  "painting, drawing, illustration, glitch, deformed, mutated, cross-eyed, ugly, disfigured"
                        prompt = prompt.replace("--neonpunk", "")
                        prompt = f"neonpunk style {prompt} . cyberpunk, vaporwave, neon, vibes, vibrant, stunningly beautiful, crisp, detailed, sleek, ultramodern, magenta highlights, dark purple shadows, high contrast, cinematic, ultra detailed, intricate, professional"
                        if AI:
                            prompt_ench = f"neonpunk style {prompt_ench} . cyberpunk, vaporwave, neon, vibes, vibrant, stunningly beautiful, crisp, detailed, sleek, ultramodern, magenta highlights, dark purple shadows, high contrast, cinematic, ultra detailed, intricate, professional"

                    if "--Isometric" in prompt or "--isometric" in prompt:
                        neg_prompt =  "deformed, mutated, ugly, disfigured, blur, blurry, noise, noisy, realistic, photographic"
                        prompt = prompt.replace("--isometric", "")
                        prompt = f"isometric style {prompt} . vibrant, beautiful, crisp, detailed, ultra detailed, intricate"
                        if AI:
                            prompt_ench = f"isometric style {prompt_ench} . vibrant, beautiful, crisp, detailed, ultra detailed, intricate"

                    if "--Low poly" in prompt or "--low poly" in prompt:
                        neg_prompt =  "noisy, sloppy, messy, grainy, highly detailed, ultra textured, photo"
                        prompt = prompt.replace("--lowpoly", "")
                        prompt = f"low-poly style {prompt} . low-poly game art, polygon mesh, jagged, blocky, wireframe edges, centered composition"
                        if AI:
                            prompt_ench = f"low-poly style {prompt_ench} . low-poly game art, polygon mesh, jagged, blocky, wireframe edges, centered composition"

                    if "--Origami" in prompt or "--origami" in prompt:
                        neg_prompt =  "noisy, sloppy, messy, grainy, highly detailed, ultra textured, photo"
                        prompt = prompt.replace("--origami", "")
                        prompt = f"origami style {prompt} . paper art, pleated paper, folded, origami art, pleats, cut and fold, centered composition"
                        if AI:
                            prompt_ench = f"origami style {prompt_ench} . paper art, pleated paper, folded, origami art, pleats, cut and fold, centered composition"

                    if "--Line art" in prompt or "--line art" in prompt:
                        neg_prompt = "anime, photorealistic, 35mm film, deformed, glitch, blurry, noisy, off-center, deformed, cross-eyed, closed eyes, bad anatomy, ugly, disfigured, mutated, realism, realistic, impressionism, expressionism, oil, acrylic"
                        prompt = prompt.replace("--line art", "")
                        prompt = f"line art drawing {prompt} . professional, sleek, modern, minimalist, graphic, line art, vector graphics"
                        if AI:
                            prompt_ench = f"line art drawing {prompt_ench} . professional, sleek, modern, minimalist, graphic, line art, vector graphics"

                    if "--Craft clay" in prompt or "--craft clay" in prompt:
                        neg_prompt = "sloppy, messy, grainy, highly detailed, ultra textured, photo"
                        prompt = prompt.replace("--craft clay", "")
                        prompt = f"play-doh style {prompt} . sculpture, clay art, centered composition, Claymation"
                        if AI:
                            prompt_ench = f"play-doh style {prompt_ench} . sculpture, clay art, centered composition, Claymation"

                    if "--Cinematic" in prompt or "--cinematic" in prompt:
                        neg_prompt = "anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured"
                        prompt = prompt.replace("--cinematic", "")
                        prompt = f"cinematic film still {prompt} . shallow depth of field, vignette, highly detailed, high budget Hollywood movie, bokeh, cinemascope, moody, epic, gorgeous, film grain, grainy"
                        if AI:
                            prompt_ench = f"cinematic film still {prompt_ench} . shallow depth of field, vignette, highly detailed, high budget Hollywood movie, bokeh, cinemascope, moody, epic, gorgeous, film grain, grainy"

                    if "--3d-model" in prompt:
                        neg_prompt =  "ugly, deformed, noisy, low poly, blurry, painting"
                        prompt = prompt.replace("--3d-model", "")
                        prompt = f"professional 3d model {prompt} . octane render, highly detailed, volumetric, dramatic lighting"
                        if AI:
                            prompt_ench = f"professional 3d model {prompt_ench} . octane render, highly detailed, volumetric, dramatic lighting"

                    if "--pixel art" in prompt:
                        neg_prompt =  "sloppy, messy, blurry, noisy, highly detailed, ultra textured, photo, realistic"
                        prompt = prompt.replace("--pixel art", "")
                        prompt = f"pixel-art {prompt} . low-res, blocky, pixel art style, 8-bit graphics"
                        if AI:
                            prompt_ench = f"pixel-art {prompt_ench} . low-res, blocky, pixel art style, 8-bit graphics"

                    if "--Texture" in prompt or "--texture" in prompt:
                        neg_prompt =  "ugly, deformed, noisy, blurry"
                        prompt = prompt.replace("--texture", "")
                        prompt = f"texture {prompt} top down close-up"
                        if AI:
                            prompt_ench = f"texture {prompt_ench} top down close-up"



                #        Sampling_steps = 13
                #        denoising = 0.5
                #        cfg = 3
                #        V4 = True
               #         size = 3
                #        h = 512
                #        w = 512
                #        if land:
                #            w = 640
                #            h = 384
                #        if port:
                 #           w = 384
                 #           h = 640





                   # prompt = content.split("--")[0]
                  #  if AI == False:
                   #     prompt = prompt.split(keyword)[1]


                  #  if "dragon" in prompt:
                   #     prompt = "<lora:Dragons v1:0.7> , " + prompt
                    #    if AI:
                     #       prompt_ench = "<lora:Dragons v1:0.7> , " + prompt_ench
                    #    neg_prompt = "(EasyNegative:1.2), (worst quality:1.2), (low quality:1.2), (lowres:1.1), (monochrome:1.1), (greyscale), multiple views, comic, sketch, horse ears, (((horse tail))), pointy ears, (((bad anatomy))), (((deformed))), (((disfigured))), watermark, multiple_views, mutation hands, mutation fingers, extra fingers, missing fingers, watermark"
######################################################################### TONES #########################################################################


######################################################################### TONES #########################################################################

                    if AI:
                        prompt = prompt_ench
                        prompt = prompt + ", " + parentheses
                        #prompt = parentheses + ", " + prompt

                    #if fantasy == True :
                    #    prompt = prompt + ", <lora:epi_noiseoffset2:0.7>"
                    #else:
                  #  if "dark" in prompt or "night" in prompt:
                  #      void = True

                 #   else:
                        #prompt = prompt + " <lora:add_detail:1>, <lora:epi_noiseoffset2:0.7>, <lora:LowRA:0.5>"
                 #       prompt = prompt + " <lora:add_detail:1>, <lora:epi_noiseoffset2:0.7>"
                        #temp_msg = " \nI drink coffee in morning, afternoon and night. <https://ko-fi.com/jaanisjc>"

                    ################ look for negative prompt
                    msgg = "*Echoing image... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                   # if AI:
                  #      msgg = "*Echoing AI prompt enhanced image... wait time: **up to 40sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                    if h == 960 or h == 640:
                        msgg = "*Echoing portrait image... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                       # if AI:
                       #     msgg = "*Echoing AI prompt enhanced portrait image... wait time: **up to 40sec*** \nInfo https://discord.com/channels/1030490392057085952/1132935102813454396"
                    elif w == 960 or w == 640:
                        msgg = "*Echoing landscape image... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                     #   if AI:
                      #      msgg = "*Echoing AI prompt enhanced landscape image... wait time: **up to 40sec*** \nInfo https://discord.com/channels/1030490392057085952/1132935102813454396"

                    input_en = prompt



                    class Model_mode_buttons(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
                        def __init__(self):
                            super().__init__(timeout=None) # timeout of the view must be set to None

                        async def echo_Dalle(self, msgg, backup):
                            
                            if not backup: await chose_model.delete()
                            wait_msg = await message.channel.send(msgg)
                           # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
                            wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
                            message.channel.trigger_typing   
                            
                          #  try:
                            response = client_dalle.images.generate(
                                model="dall-e-3",
                                prompt=input_en,
                                size="1024x1024",
                                quality="hd",
                                n=1,
                            )
                            image_url = response.data[0].url
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
                            await wait_msg.delete()
                            await wait_gif.delete()
                            if message.channel.id == 1030490392510079063:
                                new_message = await message.channel.send(file=file)
                            else:
                                new_message = await message.channel.send(file=file, view = Dalle_buttons2())
                                

                            msg_id = new_message.id     
                            new_prompt = {
                                f"{msg_id}": {
                                    "original": input_en,
                                    "styled": "",  # Add your styled content here
                                    "enchanted": "",  # Add your enchanted content here
                                    "negative": "",  # Add your enchanted content here
                                    "support_prompt": "",
                                }
                            }

                            prompts.update(new_prompt)
                            with open("prompts.json", "w") as file:
                                json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                                file.write('\n')


                        @discord.ui.button(label="Quality", custom_id="quality_begin_button", row = 1,  style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
                        async def quality_begin_button__callback(self, button, interaction):

                            #testing = True
                           # trying = True
                            #while trying:
                              #if testing:
                            if not_enchanting:
                               # trying = False
                               # testing = False
                                try:
                                    # model = "juggernautXL_version6Rundiffusion.safetensors"
                                    #model = "brightprotonukeBPNNo_bpn13.safetensors"
                                    model = "zavychromaxl_v30.safetensors"
                                    model = "sdxlUnstableDiffusers_v11.safetensors"
                                    model = "pixelwave_07.safetensors"
                                    model = "leosamsHelloworldXL_helloworldXL50GPT4V.safetensors"
                                    model = "juggernautXL_v9Rundiffusionphoto2.safetensors"
                                    #model = "realvisxlV30_v30Bakedvae.safetensors"
                                    await chose_model.delete()
                                    #await chose_model.delete()
                                    msgg = "*Echoing image in quality mode... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                                    wait_msg = await message.channel.send(msgg)
                                    neg_prompt = ""
                                    # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
                                    #wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
                                    wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
                                    message.channel.trigger_typing                          
                                    lora = False
                                    files = []
                                    three = False
                                    #vae = True
                                    vae = False
                                    support = input_en
                                    #neg_prompt = ""
                                    seed = 0
                                    #files, image_name = await generate_image(V4, input_en, neg_prompt, w , h, keyword, model, three,vae, lora, support) 
                                    files, image_name = await generate_image_cascade(V4, input_en, neg_prompt, w , h, keyword, three,vae, lora, support) 
                                    #files, image_name = await generate_image_playground(V4, input_en, neg_prompt, w , h, keyword, three,vae, lora, support) 

                                    await wait_msg.delete()
                                    await wait_gif.delete()




                                    new_message =   await message.channel.send(files=files, view=MainButtons())

                                    msg_id = new_message.id
                                    # new_prompt = {f"{msg_id}": input_en}

                                    new_prompt = {
                                        f"{msg_id}": {
                                            "original": input_en,
                                            "styled": "",  # Add your styled content here
                                            "enchanted": "",  # Add your enchanted content here
                                            "support_prompt": "",
                                            "h": h,
                                            "w": w,
                                            "negative": neg_prompt,
                                            "model": model,
                                            "latest_action": "original",
                                            "name_of_image": image_name,
                                            "mode": "quality",
                                            "seed": seed
                                        }
                                    }

                                    prompts.update(new_prompt)
                                    with open("prompts.json", "w") as file:
                                        json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                                        file.write('\n')
                                except:
                                    print('Stable diffusion offline. Using Dalle-3')
                                    await wait_msg.delete()
                                    await wait_gif.delete()
                                    backup = True
                                    msgg = "*Generator offline, echoing image using Dalle-3 instead... wait time: **up to 20sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                                    await self.echo_Dalle(msgg, backup)
                            else:
                                await message.channel.send("*Prompt is being enchanted, please try again after it is done.*")
                        @discord.ui.button(label="Speed", custom_id="speed_begin_button", row = 1,  style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
                        async def speed_begin_button__callback(self, button, interaction):
                          if not_enchanting:
                            try:
                                # model = "juggernautXL_version6Rundiffusion.safetensors"
                                model = "turbovisionxlSuperFastXLBasedOnNew_tvxlV431Bakedvae.safetensors"
                                model = "dreamshaperXL_v2TurboDpmppSDE.safetensors"
                                await chose_model.delete()
                                #await chose_model.delete()
                                msgg = "*Echoing image in speed mode... wait time: **up to 6sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                                wait_msg = await message.channel.send(msgg)
                                # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
                                #wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
                                wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
                                message.channel.trigger_typing                          
                                lora = False
                                files = []
                                three = False
                                vae = False
                                support = input_en
                                #neg_prompt = ""
                            
                                files, image_name, seed = await generate_image_turbo(V4, input_en, neg_prompt, w , h, keyword, model, three,vae, lora, support) 


                                await wait_msg.delete()
                                await wait_gif.delete()




                                new_message =   await message.channel.send(files=files, view=MainButtons())

                                msg_id = new_message.id
                                # new_prompt = {f"{msg_id}": input_en}

                                new_prompt = {
                                    f"{msg_id}": {
                                        "original": input_en,
                                        "styled": "",  # Add your styled content here
                                        "enchanted": "",  # Add your enchanted content here
                                        "support_prompt": "",
                                        "h": h,
                                        "w": w,
                                        "negative": neg_prompt,
                                        "model": model,
                                        "latest_action": "original",
                                        "name_of_image": image_name,
                                        "mode": "speed",
                                        "seed": seed
                                    }
                                }

                                prompts.update(new_prompt)
                                with open("prompts.json", "w") as file:
                                    json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                                    file.write('\n')
                            except:
                                print('Stable diffusion offline. Using Dalle-3')
                                await wait_msg.delete()
                                await wait_gif.delete()
                                backup = True
                                msgg = "*Generator offline, echoing image using Dalle-3 instead... wait time: **up to 20sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                                await self.echo_Dalle(msgg, backup)
                          else:
                                await message.channel.send("*Prompt is being enchanted, please try again after it is done.*")


                        @discord.ui.button(label=" Dalle-3 ", custom_id="Dalle3_button", row = 1,  style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
                        async def Dalle3_button__callback(self, button, interaction):
              
                          #  model = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"
                            msgg = "*Echoing image using Dalle-3... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                            backup = False
                            await self.echo_Dalle(msgg, backup)

                    class Model_buttons(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
                        def __init__(self):
                            super().__init__(timeout=None) # timeout of the view must be set to None

                        async def echo_Dalle(self, msgg, backup):
                            
                            if not backup: await chose_model.delete()
                            wait_msg = await message.channel.send(msgg)
                           # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
                            wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
                            message.channel.trigger_typing   
                            
                          #  try:
                            response = client_dalle.images.generate(
                                model="dall-e-3",
                                prompt=input_en,
                                size="1024x1024",
                                quality="hd",
                                n=1,
                            )
                            image_url = response.data[0].url
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
                            await wait_msg.delete()
                            await wait_gif.delete()
                            if message.channel.id == 1030490392510079063:
                                new_message = await message.channel.send(file=file)
                            else:
                                new_message = await message.channel.send(file=file, view = Dalle_buttons2())
                                

                            msg_id = new_message.id     
                            new_prompt = {
                                f"{msg_id}": {
                                    "original": input_en,
                                    "styled": "",  # Add your styled content here
                                    "enchanted": "",  # Add your enchanted content here
                                    "negative": "",  # Add your enchanted content here
                                    "support_prompt": "",
                                }
                            }

                            prompts.update(new_prompt)
                            with open("prompts.json", "w") as file:
                                json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                                file.write('\n')
                                
                          #  except openai.error.InvalidRequestError:
                           #     await message.channel.send('Tavs pieprasījums tika noraidīts.')

                        @discord.ui.button(label="GIF", custom_id="gif_begin_button", row = 1,  style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
                        async def gif_begin_button__callback(self, button, interaction):


                          try:
                            model = ""
                            await chose_model.delete()
                            msgg = "*Echoing gif ... wait time: **up to 100sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                            wait_msg = await message.channel.send(msgg)
                           # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
                            wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
                            message.channel.trigger_typing                          
                            lora = False
                            files = []
                            three = False
                            vae = False
                            support = input_en
                            frame_amount = 48
                            
                            files =  await generate_gif(input_en, frame_amount)


                            await wait_msg.delete()
                            await wait_gif.delete()



                            seconds = frame_amount/12
                            msg_prompt = f"Length: {seconds}"
                            embed_msg = embed = discord.Embed(description=msg_prompt, color=0x0000ff)
                            new_message =   await message.channel.send(files=files, view=gif_buttons())

                            msg_id = new_message.id
                           # new_prompt = {f"{msg_id}": input_en}

                            new_prompt = {
                                f"{msg_id}": {
                                    "original": input_en,
                                    "styled": "",  # Add your styled content here
                                    "enchanted": "",  # Add your enchanted content here
                                    "support_prompt": "",
                                    "h": h,
                                    "w": w,
                                    "negative": neg_prompt,
                                    "model": model,
                                    "frame_amount": frame_amount, 
                                    "latest_action": "original"
                                }
                            }

                            prompts.update(new_prompt)
                            with open("prompts.json", "w") as file:
                                json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                                file.write('\n')
                          except:
                            print('Stable diffusion offline. Using Dalle-3')
                            await wait_msg.delete()
                            await wait_gif.delete()
                            backup = True
                            msgg = "*Generator offline, echoing image using Dalle-3 instead... wait time: **up to 20sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                            await self.echo_Dalle(msgg, backup)


                        @discord.ui.button(label=" Dalle-3 ", custom_id="Dalle3_button", row = 1,  style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
                        async def Dalle3_button__callback(self, button, interaction):
              
                          #  model = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"
                            msgg = "*Echoing image using Dalle-3... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                            backup = False
                            await self.echo_Dalle(msgg, backup)
                            

                        @discord.ui.button(label="Creative", custom_id="creative_begin_button", row = 1,  style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
                        async def creative_begin_button__callback(self, button, interaction):


                          try:
                            model = "sdxlUnstableDiffusers_v9DIVINITYMACHINEVAE.safetensors"
                            await chose_model.delete()
                            msgg = "*Echoing image using creative... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                            wait_msg = await message.channel.send(msgg)
                           # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
                            wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
                            message.channel.trigger_typing                          
                            lora = False
                            files = []
                            three = False
                            vae = False
                            support = input_en
                            neg_prompt = "bad quality, bad anatomy, worst quality, low quality, lowres, extra fingers, blur, blurry, ugly, wrong proportions, watermark, image artifacts"

                            
                            files, image_name = await generate_image(V4, input_en, neg_prompt, w , h, keyword, model, three,vae, lora, support) 


                            await wait_msg.delete()
                            await wait_gif.delete()




                            new_message =   await message.channel.send(files=files, view=MainButtons())

                            msg_id = new_message.id
                           # new_prompt = {f"{msg_id}": input_en}

                            new_prompt = {
                                f"{msg_id}": {
                                    "original": input_en,
                                    "styled": "",  # Add your styled content here
                                    "enchanted": "",  # Add your enchanted content here
                                    "support_prompt": "",
                                    "h": h,
                                    "w": w,
                                    "negative": neg_prompt,
                                    "model": model,
                                    "latest_action": "original",
                                    "name_of_image": image_name

                                }
                            }

                            prompts.update(new_prompt)
                            with open("prompts.json", "w") as file:
                                json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                                file.write('\n')
                          except:
                            print('Stable diffusion offline. Using Dalle-3')
                            await wait_msg.delete()
                            await wait_gif.delete()
                            backup = True
                            msgg = "*Generator offline, echoing image using Dalle-3 instead... wait time: **up to 20sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                            await self.echo_Dalle(msgg, backup)
                        @discord.ui.button(label="Realistic", custom_id="realistic_begin_button",  row = 1, style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
                        async def realistic_begin_button__callback(self, button, interaction):


                          try:
                           # model = "juggernautXL_version6Rundiffusion.safetensors"
                            model = "leosamsHelloworldSDXLModel_helloworldSDXL20.safetensors"
                            model = "leosamsHelloworldXL_helloworldXL50GPT4V.safetensors"
                            await chose_model.delete()
                            msgg = "*Echoing image using realistic... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                            wait_msg = await message.channel.send(msgg)
                           # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
                            wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
                            message.channel.trigger_typing                          
                            lora = False
                            files = []
                            three = False
                            vae = True
                            support = input_en

                            
                            files  = await generate_image(V4, input_en, neg_prompt, w , h, keyword, model, three,vae, lora, support) 


                            await wait_msg.delete()
                            await wait_gif.delete()




                            new_message =   await message.channel.send(files=files, view=MainButtons())

                            msg_id = new_message.id
                           # new_prompt = {f"{msg_id}": input_en}

                            new_prompt = {
                                f"{msg_id}": {
                                    "original": input_en,
                                    "styled": "",  # Add your styled content here
                                    "enchanted": "",  # Add your enchanted content here
                                    "support_prompt": "",
                                    "h": h,
                                    "w": w,
                                    "negative": neg_prompt,
                                    "model": model,
                                    "latest_action": "original",
                                }
                            }

                            prompts.update(new_prompt)
                            with open("prompts.json", "w") as file:
                                json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                                file.write('\n')
                          except:
                            print('Stable diffusion offline. Using Dalle-3')
                            await wait_msg.delete()
                            await wait_gif.delete()
                            backup = True
                            msgg = "*Generator offline, echoing image using Dalle-3 instead... wait time: **up to 20sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                            await self.echo_Dalle(msgg, backup)

                        @discord.ui.button(label="Artistic", custom_id="artistic_button", row = 1,  style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
                        async def artistic_button__callback(self, button, interaction):
                         
                            #try:
                                model             = "sdXL_v10VAEFix.safetensors" 
                              #  model = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"
                                await chose_model.delete()
                                msgg = "*Echoing image using Artistic... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"

                                wait_msg = await message.channel.send(msgg)
                               # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
                                wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
                                message.channel.trigger_typing                          
                                neg_prompt = "bad quality, bad anatomy, worst quality, low quality, lowres, extra fingers, blur, blurry, ugly, wrong proportions, watermark, image artifacts"
                                files = []
                                three = False
                                vae = False
                                lora = True
                                gpt = False
                                promptt = input_en
                                split_string = promptt.split("--")
                                if len(split_string) > 1:
                                    # Save words after "--" to a new string
                                    provided_style = split_string[1].strip()
                                    promptt = split_string[0].strip()
                                    with open('styles.json', encoding='utf-8') as fh:
                                        styles = json.load(fh)
                                    
                                    if f"Style: {provided_style}" in styles:    
                                        selected_style = styles[f"Style: {provided_style}"]
                                    else:
                                        selected_style = styles[provided_style]
                                    rand_prompt = selected_style["prompt"]
                                    promptt = f"{rand_prompt.replace('{prompt}', promptt)}"
                                    negative_prompt = selected_style["negative_prompt"]
                                    neg_prompt = "bad quality, bad anatomy, worst quality, low quality, lowres, extra fingers, blur, blurry, ugly, wrong proportions, watermark, image artifacts, " + negative_prompt
                                    #print("Words after '--':", new_string)

                                    # Remove "--{any words}" from the original string
                                    
                                    #print("Modified string:", modified_string)


                                support = promptt

                                

                                files = await generate_image_refiner(V4, promptt, neg_prompt, w , h, keyword, model, three,vae, lora, support)   


                                await wait_msg.delete()
                                await wait_gif.delete()




                                new_message =   await message.channel.send(files=files, view=MainButtons())

                                msg_id = new_message.id
                               # new_prompt = {f"{msg_id}": input_en}

                                new_prompt = {
                                    f"{msg_id}": {
                                        "original": promptt,
                                        "styled": "",  # Add your styled content here
                                        "enchanted": "",  # Add your enchanted content here
                                        "support_prompt": "",
                                        "h": h,
                                        "w": w,
                                        "negative": neg_prompt,
                                        "model": model,
                                        "latest_action": "original"
                                    }
                                }

                                prompts.update(new_prompt)
                                with open("prompts.json", "w") as file:
                                    json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                                    file.write('\n')
                           # except:
                           #     print('Stable diffusion offline. Using Dalle-3')
                           #     await wait_msg.delete()
                            #    await wait_gif.delete()
                            #    backup = True
                            #    msgg = "*Generator offline, echoing image using Dalle-3 instead... wait time: **up to 20sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                            #    await self.echo_Dalle(msgg, backup)

                        @discord.ui.button(label="2.5D Animated", custom_id="25d_begin_button", row = 2,  style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
                        async def sarlight_begin_button__callback(self, button, interaction):


                          try:
                            model = "starlightXLAnimated_v3.safetensors"
                            await chose_model.delete()
                            msgg = "*Echoing image using 2.5D Animated... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                            wait_msg = await message.channel.send(msgg)
                           # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
                            wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
                            message.channel.trigger_typing                          
                            lora = False
                            files = []
                            three = False
                            vae = False
                            support = input_en
                            neg_prompt = ""

                            
                            files = await generate_image(V4, input_en, neg_prompt, w , h, keyword, model, three,vae, lora, support) 


                            await wait_msg.delete()
                            await wait_gif.delete()




                            new_message =   await message.channel.send(files=files, view=MainButtons())

                            msg_id = new_message.id
                           # new_prompt = {f"{msg_id}": input_en}

                            new_prompt = {
                                f"{msg_id}": {
                                    "original": input_en,
                                    "styled": "",  # Add your styled content here
                                    "enchanted": "",  # Add your enchanted content here
                                    "support_prompt": "",
                                    "h": h,
                                    "w": w,
                                    "negative": neg_prompt,
                                    "model": model,
                                    "latest_action": "original"
                                }
                            }

                            prompts.update(new_prompt)
                            with open("prompts.json", "w") as file:
                                json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                                file.write('\n')
                          except:
                            print('Stable diffusion offline. Using Dalle-3')
                            await wait_msg.delete()
                            await wait_gif.delete()
                            backup = True
                            msgg = "*Generator offline, echoing image using Dalle-3 instead... wait time: **up to 20sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                            await self.echo_Dalle(msgg, backup)

                        @discord.ui.button(label="NEW Colossus Project", custom_id="collosus_begin_button",  row = 2, style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
                        async def collosus_begin_button__callback(self, button, interaction):


                          try:
                           # model = "juggernautXL_version6Rundiffusion.safetensors"
                            model = "colossusProjectXLSFW_v53Trained.safetensors"
                            await chose_model.delete()
                            msgg = "*Echoing image using Colossus Project... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                            wait_msg = await message.channel.send(msgg)
                           # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
                            wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
                            message.channel.trigger_typing                          
                            lora = False
                            files = []
                            three = False
                            vae = True
                            support = input_en

                            
                            files = await generate_image(V4, input_en, neg_prompt, w , h, keyword, model, three,vae, lora, support) 


                            await wait_msg.delete()
                            await wait_gif.delete()




                            new_message =   await message.channel.send(files=files, view=MainButtons())

                            msg_id = new_message.id
                           # new_prompt = {f"{msg_id}": input_en}

                            new_prompt = {
                                f"{msg_id}": {
                                    "original": input_en,
                                    "styled": "",  # Add your styled content here
                                    "enchanted": "",  # Add your enchanted content here
                                    "support_prompt": "",
                                    "h": h,
                                    "w": w,
                                    "negative": neg_prompt,
                                    "model": model,
                                    "latest_action": "original",
                                }
                            }

                            prompts.update(new_prompt)
                            with open("prompts.json", "w") as file:
                                json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                                file.write('\n')
                          except:
                            print('Stable diffusion offline. Using Dalle-3')
                            await wait_msg.delete()
                            await wait_gif.delete()
                            backup = True
                            msgg = "*Generator offline, echoing image using Dalle-3 instead... wait time: **up to 20sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
                            await self.echo_Dalle(msgg, backup)

                   # chose_model = await message.channel.send("Which model to use?", view=Model_buttons())

                    chose_model = await message.channel.send("Which mode to use?", view=Model_mode_buttons())

                  #  wait_msg = await message.channel.send(msgg) 
                    # wait_gif = await message.channel.send("https://media.giphy.com/media/6JoZLF3PEf71rlC6wG/giphy.gif") 
                    #wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMThjNGQ2MjY2NWNlZjQ2N2UzNTEzMTg1OTdkYTc3MzYxNmU3MDBlMiZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/oifW0KmfxAUscpFCJD/giphy.gif") 
                    #wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMzVkOWI2N2I0YmQyYjEyNTQ0NDM0MjY4OWFkYjI0YWE0MTE1Yzg4NyZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/rEpJGWtwjQpZg8Wvip/giphy.gif") 
                    #wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZWFkYmQ5NGQ2OGYwNzU1ZWRmMjYyMzBiNTQyOGUwOGIyNjdkYzA5NyZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/XBnEpjyGn0jNrSb1S4/giphy.gif")
                    #wait_gif = await message.channel.send("https://media.giphy.com/media/Xkjlwr3Ynu1hMsMMGK/giphy.gif") 
                    #wait_gif = await message.channel.send("https://media.giphy.com/media/CrWs8NT760qo0Hh5dd/giphy.gif") 
                   # wait_gif = await message.channel.send("https://media.giphy.com/media/XBnEpjyGn0jNrSb1S4/giphy.gif")  
                  #  wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
                    
                    #user_input = prompt.split(keyword)[1]
                    #input_en = translateMsg(prompt)
                    
                   # input_en = prompt
                #    message.channel.trigger_typing
               #     files = []
              #      files = await generate_image(V4, input_en, neg_prompt, w , h, keyword, model)    
                    ############ countdown ##########
               #     intervals = 50
              #      messagee = await message.channel.send("Countdown: 50 seconds left!")

            #        for i in range(intervals - 1, 0, -1):
            #            await asyncio.sleep(1)
            #            await messagee.edit(content=f"Countdown: {i} seconds left!")

             #       await asyncio.sleep(1)   
            #        await messagee.delete()
                    ############# countdown  ########
                  #  await asyncio.sleep(65)
                 #   filename = f"{filename_temp}_00001_.png"
                 #   file = discord.File(f"F:/ComfyUI_windows_portable/ComfyUI/output/ProjectAy/{filename}")
                #    files.append(file) 
                 #   filename = f"{filename_temp}_00002_.png"
                 #   file = discord.File(f"F:/ComfyUI_windows_portable/ComfyUI/output/ProjectAy/{filename}")
                 #   files.append(file) 
                    #files = await files_coroutine 
                  #  await wait_msg.delete()
                 #   await wait_gif.delete()




                  #  new_message =   await message.channel.send(files=files, view=MyView())
########################################## Save prompt to specific message


                   # search_key = "1165987985385332837"
                  #  print(f"{prompts[search_key]}")
########################################## Save prompt to specific message

                    return
                else:
                  #  await message.channel.send('***generate** is disabled. Use **ģenerē** instead.*')
                   # await message.channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")
                    msgg = "*GPU power is used for gaming right now, echoing image using Dalle-3... wait time: **up to 20sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"

                    wait_msg = await message.channel.send(msgg)
                    # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
                    wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
                    message.channel.trigger_typing   
                    prompt = message_modif
                    prompt = prompt.split(keyword)[1]
                    
                    response = client_dalle.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        size="1024x1024",
                        quality="hd",
                        n=1,
                    )
                    image_url = response.data[0].url
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
                    await wait_msg.delete()
                    await wait_gif.delete()
                    new_message = await message.channel.send(file=file, view=Dalle_buttons())

                    msg_id = new_message.id     
                    new_prompt = {
                        f"{msg_id}": {
                            "original": prompt,
                            "styled": "",  # Add your styled content here
                            "enchanted": "",  # Add your enchanted content here
                            "negative": "",  # Add your enchanted content here
                            "support_prompt": "",
                        }
                    }

                    prompts.update(new_prompt)
                    with open("prompts.json", "w") as file:
                        json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                        file.write('\n')


                    return
               except:
                   print('\nProblem with Stable Diffusion!')
                   await wait_msg.delete()
                   await wait_gif.delete()
                   await message.channel.send('**Oh no an error occured(offline).** *cries*')
                   return
  ################################################ TEST ############################                  



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

         #   elif 'joku' in message.content.lower():
                # Get a random file from a folder named 'files'
       #         folder_path = 'C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/jokes'  # Replace with the path to your folder
       ##         file_list = os.listdir(folder_path)
       #         if file_list:
        #            random.seed(time.time())
        #            random_file = random.choice(file_list)
        #            file_path = os.path.join(folder_path, random_file)
        #            file = discord.File(file_path)
        #            await message.channel.send(file=file)
       #             return

            elif "parādi" in message.content.lower():
               if "desu" in message.content.lower():

                  desa =    getGif("Sausage")
                  response = desa
               elif "dibenu" in message.content.lower():
                   dibens =    getGif("ass")
                   response = dibens
               elif "kājas" in message.content.lower():
                   kajas =    getGif("girl legs")
                   response = kajas
               elif "pupus" in message.content.lower() or "krūtis" in message.content.lower() or "krutis" in message.content.lower():
                   pupi =    getGif("Boobs")
                   response = pupi
               else:
                   words = message.content.lower().split()
                   paradi_index = words.index("parādi")
                   pieprasijums = " ".join(words[paradi_index+1:])
                   pieprasijums_en = translateMsg(pieprasijums)
                  # pieprasijums_en = pieprasijums
                   if pieprasijums == pieprasijums_en: #@#
                       pieprasijums_en = "I failed you" #@#
                   try:
                       izteles_auglis =    getGif(pieprasijums_en)
                   except ValueError:
                       izteles_auglis =    getGif("I failed you")
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
                          # vards  = unidecode(name)
                           vards = message.author.name
                        else:
                           vards = message.author.name
                        if '.' in vards: # Check if nickname exists and contains dots
                                vards = vards.replace('.', '') 
                        #current_zina = message.content
                        await message.channel.trigger_typing()

                        gpt_key               = os.getenv("GPT")
                        client_chat = OpenAI(api_key=gpt_key)
                        # 
                        responsee = client_chat.chat.completions.create( 
                        model='gpt-4-0125-preview',
                        messages = [
                        {"role": "system", "content": f'Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. You pretend that you have a message from user and reply with compact response in context taking in account what has been discussed in chat. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Sometimes use random emoji.'},
                        {"role": "user", "name": vards, "content": f"'{replied_zina}' give short answer in context in latvian"}
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
            elif message.reference and ("izlasi" in message.content.lower()):
                    if message.author == client.user:
                        return
                    channel = message.channel
                    replied_message = await message.channel.fetch_message(message.reference.message_id)
                    replied_zina = replied_message.content
                    gpt_key               = os.getenv("GPT")
                    client_speach = OpenAI(api_key=gpt_key)

                    output_directory = "C:\\Users\\ZK00138\\source\\repos\\ResnsCounter\\ResnsCounter\\text to speach"  # Set your desired output directory here
                    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
                    file_name = f"read_{current_time}.mp3"

                    speech_file_path = Path(output_directory) / file_name
                    response = client_speach.audio.speech.create(
                      model= "tts-1-hd",
                      voice= "shimmer",
                      input= replied_zina
                    )

                    response.stream_to_file(speech_file_path)
                    with open(speech_file_path, 'rb') as f1:
                        file1 = discord.File(f1, filename='Elizabete_lasa.mp3')
                    await message.channel.send(files=[file1]) 

                    return

            elif  message.reference is not None and "apraksti bildi" in message.content:
                zina_ar_bildi = await message.channel.fetch_message(message.reference.message_id)
                bildes_url =  zina_ar_bildi.attachments[0].url

                gpt_key               = os.getenv("GPT")

                client_vision = OpenAI(api_key=gpt_key)

                response = client_vision.chat.completions.create(
                  model="gpt-4-vision-preview",
                  messages=[
                    {
                      "role": "user",
                      "content": [
                        {"type": "text", "text": "What’s in this image? in latvian. Just describe image, do not add any other coments about request"},
                        {
                          "type": "image_url",
                          "image_url": {
                            "url": bildes_url,
                          },
                        },
                      ],
                    }
                  ],
                  max_tokens=300,
                )
                response = response.choices[0].message.content
                await message.channel.send(response)
                return

            elif "speak" in message.content.lower():
                    if message.author == client.user:
                        return
                    channel = message.channel
                   # replied_message = await message.channel.fetch_message(message.reference.message_id)
                   # replied_zina = replied_message.content
                    words = message.content.split()
                    speak_text = ' '.join(words[2:])
                    gpt_key               = os.getenv("GPT")
                    client_speach = OpenAI(api_key=gpt_key)

                    output_directory = "C:\\Users\\ZK00138\\source\\repos\\ResnsCounter\\ResnsCounter\\text to speach"  # Set your desired output directory here
                    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
                    file_name = f"speech_{current_time}.mp3"

                    speech_file_path = Path(output_directory) / file_name
                    response = client_speach.audio.speech.create(
                      model= "tts-1-hd",
                      voice= "shimmer",
                      input= speak_text
                    )

                    response.stream_to_file(speech_file_path)
                    with open(speech_file_path, 'rb') as f1:
                        file1 = discord.File(f1, filename='Elizabete_runa.mp3')
                    await message.channel.send(files=[file1]) 

                    return
################ NEW ###################################
           # elif "parādīt" in message.content.lower():
          #     rand =    getGif("Random")
           #    response = rand
            elif re.match(r".*\bko(\s+\S+)?\s+dari\s*\?", message_modif.lower()):   #@#
                response = random.choice(triger_KoDari["Ko dari"]) #@#
            elif re.match(r".*\bkā(\s+\S+)?\s+iet\s*\?", message_modif.lower()) or re.match(r".*\bka(\s+\S+)?\s+iet\s*\?", message_modif.lower()): #@#
                response = random.choice(triger_KaIet["Ka iet"]) #@# 
          #  elif '?' in message_modif or message.channel.id == 1101461174907830312 or message.author.id == 909845424909729802 or mentioned_user: # 1101461174907830312 - ģenerē-general channel id
            elif '?' in message_modif or "pasaki" in message_modif or "iesaki" in message_modif or "pastāsti" in message_modif or "pastasti" in message_modif or  "atvainojies" in message_modif or  "apsveic" in message_modif or message.channel.id == 1101461174907830312: # 1101461174907830312 - ģenerē-general channel id   ### hasijs or message.author.id == 242298879784124416
                current_zina = message_modif
                #use_GPT = False
                await message.channel.trigger_typing()
                name = getUserName(message.author.name)
                if name is not None:
                    #vards  = unidecode(name)
                    vards = message.author.name
                else:
                    vards = message.author.name
                    #vards  = unidecode(vards)

                gpt_key               = os.getenv("GPT")
                client_chat = OpenAI(api_key=gpt_key)    




                responsee = client_chat.chat.completions.create(
                model='gpt-4-0125-preview',
                messages = [
                {"role": "system", "content": f'Your name is "Elizabete". You were created 15.03.2023. Reply with compact random response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Do not mention which tone using. Sometimes use emojis'},
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

            if message.reference is not None and message.reference.resolved.author.id == client.user.id and ('?' in message.content or "pasaki" in message.content or "iesaki" in message.content or "pastāsti" in message.content or "pastasti" in message.content): #  or message.author.id == 242298879784124416
           # if message.reference is not None and message.reference.resolved.author.id == client.user.id:                
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                replied_zina = replied_message.content
                current_zina = message.content



               # name = getUserName(replied_message.author.name)
              #  if name is not None:
              #      #vards  = unidecode(name)
                   # vards = message.author.name
               # else:
               #     vards = message.author.name
              #  if '.' in vards: # Check if nickname exists and contains dots
              #          vards = vards.replace('.', '') 
                await message.channel.trigger_typing()

                gpt_key               = os.getenv("GPT")
                client_chat = OpenAI(api_key=gpt_key)





                responsee = client_chat.chat.completions.create(
                model='gpt-4-0125-preview',
                messages = [
                {"role": "system", "content": f"Your name is Elizabete. You were created 15.03.2023. Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. You pretend that you have given response, recieved an answer from user and reply with compact random response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Sometimes use random emoji"},
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
               # elif '?' in message.content or message.channel.id == 1101461174907830312: # 1101461174907830312 - ģenerē-general channel id
                elif 'jtydjk' in message.content: # 1101461174907830312 - ģenerē-general channel id
                    current_zina = message_modif
                    name = getUserName(message.author.name)
                   # replied_messagee = await message.channel.fetch_message(message.reference.message_id)
                  #  urll =  replied_messagee.attachments[0].url
                  #  print(urll)
                    image_text_upd = f"users wrote '{current_zina}' give random short or medium answer in context in latvian. Your name is Elizabete"
                    ###10.30 new stuff
                    message_id = str(message.reference.message_id)
                    if message_id in prompts:

                        image_text = prompts[message_id]["original"]
                        image_text_upd = f"User replyed to message with image attached. user wrote '{current_zina}'This is image description: '{image_text}' give short or medium answer in context in latvian taking in account the description of image."
                        #print(image_text_upd)

                    if name is not None:
                      #  vards  = unidecode(name)
                        vards = message.author.name
                    else:
                        vards = message.author.name
                    await message.channel.trigger_typing()

                    gpt_key               = os.getenv("GPT")
                    client_chat = OpenAI(api_key=gpt_key)

                    responsee = client_chat.chat.completions.create(
                    model='gpt-4-0125-preview',
                    messages = [
                    {"role": "system", "content": f' Your name is Elizabete. Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. Reply with compact random response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Do not mention which tone using. Sometimes use emojis'},
                    {"role": "user", "name" : vards, "content": f"{image_text_upd}"}
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
                    #use_GPT = True
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
                if message.attachments:
                    for att in message.attachments:
                        url = att.url 
                        msg2 = f"{msg2}\n{url}"
                msgCount += 1
            if msgCount == 2:
                msg1 = preprocess_message(msg1)              
                addPair('CB_pairs2addition.json', msg1, msg2)
                #pairs.append([msg1, [msg2]])
                msgCount = 0
            if msgCount == 0:
               msg1 = message.content
               if message.attachments:
                    for att in message.attachments:
                        url = att.url 
                        msg1 = f"{msg1}\n{url}"
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
            print('\nNew #resns message')


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
                        await Register_time(f"{message.created_at.hour+2}")
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
                await Register_time(f"{message.created_at.hour+2}")
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
   async def on_member_join(member):
    account_created = member.created_at.replace(tzinfo=timezone.utc)
    current_time = datetime.now(timezone.utc)
    account_age = current_time - account_created

  #  if account_age < timedelta(days=30):
  #      await member.kick(reason='Account younger than one month')
   #     channel = client.get_channel(1030490392510079063) 
  #      await channel.send("*Kicking suspicious account...*")
      #  await channel.send("Ko ta tu te???")

 #  @client.event
 # async def on_presence_update(before, after):
 #      if before.id == 391668973315424277:
 #          global execute_code
 #          if before.activity != after.activity:  # to only run on status
 #              try:
 #                  if "Call of Duty" in after.activity.name:
 #                       execute_code = False                  
                      # if before.activity is None:
                      #  channel = client.get_channel(1101461174907830312)
                      #  await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")
                        

                     #  print("eureka")
                #   if "Call of Duty" in before.activity.name and after.activity is None:
               #        print("turn back on")
  #             except Exception:
  #                  pass

   #            if after.activity is None:
                      # channel = client.get_channel(1101461174907830312)
    #                   execute_code = True
                       #await channel.send("GPU resources freed up. **Echo** is *enabled*.")
                      # print("turn back on")


   @client.event
   async def on_message_delete(message):
       if message.author.id == 467566510051950592:
            author = message.author
            content = message.content
            channel = message.channel
            await channel.send(f" palaidnis {author.display_name} izdzēsa ziņu: {content}")

   @client.event
   async def on_button_click(button, interaction):
       if button.custom_id == "redo_button":
           print('eureka')

   @client.event
   async def on_disconnect():

       # channel = client.get_channel(1101461174907830312) 
        #await channel.send("https://media.giphy.com/media/CrWs8NT760qo0Hh5dd/giphy.gif") 

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