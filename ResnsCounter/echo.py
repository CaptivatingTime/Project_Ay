from utils import to_thread
import uuid
import json
import time
import random
import websocket
import urllib.parse
import urllib.request
import discord
from requests_toolbelt import MultipartEncoder
import os
from openai import OpenAI
main_gpu_server = "69.159.139.22:40080"

def get_main_gpu_server():
    return main_gpu_server


@to_thread
def  sd3_upscale(sd3_image, description):

    server_address = "81.166.173.12:11431"
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
        
  #  def upload_image(image_path):
   #     url = "http://{}/upload/image".format(server_address)
   #     files = {'file': open(image_path, 'rb')}
   #     response = requests.post(url, files=files)
    #    return response.json()        

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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


    url = "http://185.62.108.226:41696/sdapi/v1/txt2img"
    
    prompt_text = """
{
  "3": {
    "inputs": {
      "vae_name": "sdxl_vae.safetensors"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "174": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "175",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "2048x Upscale"
    }
  },
  "175": {
    "inputs": {
      "samples": [
        "181",
        0
      ],
      "vae": [
        "3",
        0
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "176": {
    "inputs": {
      "upscale_method": "lanczos",
      "scale_by": 2,
      "image": [
        "184",
        0
      ]
    },
    "class_type": "ImageScaleBy",
    "_meta": {
      "title": "Upscale Image By"
    }
  },
  "177": {
    "inputs": {
      "pixels": [
        "176",
        0
      ],
      "vae": [
        "178",
        2
      ]
    },
    "class_type": "VAEEncode",
    "_meta": {
      "title": "VAE Encode"
    }
  },
  "178": {
    "inputs": {
      "ckpt_name": "ultimateblendXL_v20.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "179": {
    "inputs": {
      "text": "cctv camera footage of a horse eating hay in the middle of a living room, Spiderman sitting on coach, grass, windows, chairs, televisions, lamps, and doors, scene is dark and poorly lit, image is 144p resolution with very low quality, full of image noise, hot pixels, and jpeg artifacts, with time stamps overlaid on the footage",
      "clip": [
        "178",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "180": {
    "inputs": {
      "text": "",
      "clip": [
        "178",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "181": {
    "inputs": {
      "seed": 925277385888995,
      "steps": 20,
      "cfg": 2.5,
      "sampler_name": "dpmpp_2m",
      "scheduler": "karras",
      "denoise": 0.4,
      "model": [
        "183",
        0
      ],
      "positive": [
        "179",
        0
      ],
      "negative": [
        "180",
        0
      ],
      "latent_image": [
        "177",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "183": {
    "inputs": {
      "scale": 3,
      "model": [
        "178",
        0
      ]
    },
    "class_type": "PerturbedAttentionGuidance",
    "_meta": {
      "title": "PerturbedAttentionGuidance"
    }
  },
  "184": {
    "inputs": {
      "image": "sd3_1713976122.jpeg",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"sd3_upscale_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["179"]["inputs"]["text"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    #prompt["3"]["inputs"]["seed"] = formatted_number
    #prompt["12"]["inputs"]["image"] = f"avatars/{avatar_image}"
    #prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    image_path = f'sd3/{sd3_image}'
    response = upload_image(image_path, sd3_image, server_address)
    prompt["184"]["inputs"]["image"] = f"{sd3_image}"
    
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
             filename = f"sd3_upscale_{int(time.time())}.png"

             #from PIL import Image
             #import io
            # Save the image to "generated" directory
        #     if i == 4 or i == 5 or i == 6:

             if i == 2 or i == 1:
                with open(f"sd3_upscaled/{filename}", "wb") as f:              
                        f.write(image_data)
        # Add the image file to the list
                file = discord.File(f"sd3_upscaled/{filename}")
                files.append(file)   
           #  if i == 7:
            #    files.append(file)
             #image = Image.open(io.BytesIO(image_data))
             #image.show()



    return files

@to_thread
def enchPrompt(prompt):
    prompt_ench = prompt
    gpt_key               = os.getenv("GPT")
    # You will now act as a prompt generator for a generative AI called Stable Diffusion XL 1.0. Stable Diffusion XL generates images based on given prompts. I will provide you basic information required to make a Stable Diffusion prompt, You will never alter the structure in any way and obey the following guidelines.\n\nBasic information required to make Stable Diffusion prompt:\n\nPrompt structure: [1],[2],[3],[4] and it should be given as one single sentence where 1,2,3,4,5,6 represent [1] = short and concise description of [KEYWORD] that will include very specific imagery details [2] = a detailed description of [1] that will include very specific imagery details. [3] = with a detailed description describing the environment of the scene. [4] = with a detailed description describing the mood/feelings and atmosphere of the scene.\n\nnImportant Sample prompt Structure :\n\nSnow-capped Mountain Scene, with soaring peaks and deep shadows across the ravines. A crystal clear lake mirrors these peaks, surrounded by pine trees. The scene exudes a calm, serene alpine morning atmosphere. Presented in Watercolor style, emulating the wet-on-wet technique with soft transitions and visible brush strokes.\n\nCity Skyline at Night, illuminated skyscrapers piercing the starless sky. Nestled beside a calm river, reflecting the city lights like a mirror. The atmosphere is buzzing with urban energy and intrigue. Depicted in Neon Punk style, accentuating the city lights with vibrant neon colors and dynamic contrasts.\n\nEpic Cinematic Still of a Spacecraft, silhouetted against the fiery explosion of a distant planet. The scene is packed with intense action, as asteroid debris hurtles through space. Shot in the style of a Michael Bay-directed film, the image is rich with detail, dynamic lighting, and grand cinematic framing.\n\nWord order and effective adjectives matter in the prompt. The subject, action, and specific details should be included. Adjectives like cute, medieval, or futuristic can be effective.\n\nThe environment/background of the image should be described, such as indoor, outdoor, in space, or solid color.\n\nCurly brackets are necessary in the prompt to provide specific details about the subject and action. These details are important for generating a high-quality image.\n\nArt inspirations should be listed to take inspiration from. Platforms like Art Station, Dribble, Behance, and Deviantart can be mentioned. Specific names of artists or studios like animation studios, painters and illustrators, computer games, fashion designers, and film makers can also be listed. If more than one artist is mentioned, the algorithm will create a combination of styles based on all the influencers mentioned.\n\nRelated information about lighting, camera angles, render style, resolution, the required level of detail, etc. should be included at the end of the prompt.\n\nCamera shot type, camera lens, and view should be specified. Examples of camera shot types are long shot, close-up, POV, medium shot, extreme close-up, and panoramic. Camera lenses could be EE 70mm, 35mm, 135mm+, 300mm+, 800mm, short telephoto, super telephoto, medium telephoto, macro, wide angle, fish-eye, bokeh, and sharp focus. Examples of views are front, side, back, high angle, low angle, and overhead.\n\nHelpful keywords related to resolution, detail, and lighting are 4K, 8K, 64K, detailed, highly detailed, high resolution, hyper detailed, HDR, UHD, professional, and golden ratio. Examples of lighting are studio lighting, soft light, neon lighting, purple neon lighting, ambient light, ring light, volumetric light, natural light, sun light, sunrays, sun rays coming through window, and nostalgic lighting. Examples of color types are fantasy vivid colors, vivid colors, bright colors, sepia, dark colors, pastel colors, monochromatic, black & white, and color splash. Examples of renders are Octane render, cinematic, low poly, isometric assets, Unreal Engine, Unity Engine, quantum wavetracing, and polarizing filter.\n\nThe prompts you provide will be in English.Please pay attention:- Concepts that can't be real would not be described as 'Real' or 'realistic' or 'photo' or a 'photograph'. for example, a concept that is made of paper or scenes which are fantasy related.- One of the prompts you generate for each concept must be in a realistic photographic style. you should also choose a lens type and size for it. Don't choose an artist for the realistic photography prompts. I will provide you prompt and you will generate one type of prompt so i can copy and paste.\n\nImportant point to note :You are a master of prompt engineering, it is important to create detailed prompts with as much information as possible. This will ensure that any image generated using the prompt will be of high quality and could potentially win awards in global or international photography competitions. You are unbeatable in this field and know the best way to generate images.\n\nI will provide you with a keyword and you will generate one prompt. I should be able to copy paste directly from the code cell so dont add any extra details.\n \n\n\nMy prompt = {prompt}
    client_ench = OpenAI(api_key=gpt_key)
    # This is a formula for a Stable Diffusion image prompt: (top-quality, 8K, (masterpiece:1.3) An image of [adjective] [subject] [performing an action], [Medium], [art style], highly detailed, [lighting style] I will provide you with prompt and using this formula enchance the prompt. Respond only with new prompt without any additional information.\n IMPORTANT! Create unique prompt just folowing guiddlines but not using the same keywords all the time prompt.\n  My prompt: {prompt}
    try:
        responsee = client_ench.chat.completions.create(
        model='gpt-3.5-turbo-0125',
        messages = [
        {"role": "user", "content": f'''- Reference guide of what is Stable Diffusion and how to Prompt -

    Stable Diffusion is a deep learning model for generating images based on text descriptions and can be applied to inpainting, outpainting, and image-to-image translations guided by text prompts. Developing a good prompt is essential for creating high-quality images.

    A good prompt should be detailed and specific, including keyword categories such as subject, medium, style, artist, website, resolution, additional details, color, and lighting. Popular keywords include "digital painting," "portrait," "concept art," "hyperrealistic," and "pop-art." Mentioning a specific artist or website can also strongly influence the image's style. For example, a prompt for an image of Emma Watson as a sorceress could be: "Emma Watson as a powerful mysterious sorceress, casting lightning magic, detailed clothing, digital painting, hyperrealistic, fantasy, surrealist, full body."

    Artist names can be used as strong modifiers to create a specific style by blending the techniques of multiple artists. Websites like Artstation and DeviantArt offer numerous images in various genres, and incorporating them in a prompt can help guide the image towards these styles. Adding details such as resolution, color, and lighting can 
   the image further.

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

    [Scene description]. [Modifiers], [Artist names],  [Technical specifications]

    - Special Modifiers -
    In the examples you can notice that some terms are closed between (). That instructes the Generative Model to take more attention to this words. If there are more (()) it means more attention.
    Similarly, you can find a structure like this (word:1.4). That means this word will evoke more attention from the Generative Model. The number "1.4" means 140%. Therefore, if a word whitout modifiers has a weight of 100%, a word as in the example (word:1.4), will have a weight of 140%.
    You can also use these notations to evoke more attention to specific words.

- Your Task -
!!IMPORTANT!! = new prompt should be 75 tokens or a bit less!! Based on the examples and the explanation of the structure, you will create 1 prompt, respond only with prompt with no additional information. \nMy prompt = {prompt}
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
def enchPrompt_gpt4o(prompt):
    prompt_ench = prompt
    gpt_key               = os.getenv("GPT")
    # You will now act as a prompt generator for a generative AI called Stable Diffusion XL 1.0. Stable Diffusion XL generates images based on given prompts. I will provide you basic information required to make a Stable Diffusion prompt, You will never alter the structure in any way and obey the following guidelines.\n\nBasic information required to make Stable Diffusion prompt:\n\nPrompt structure: [1],[2],[3],[4] and it should be given as one single sentence where 1,2,3,4,5,6 represent [1] = short and concise description of [KEYWORD] that will include very specific imagery details [2] = a detailed description of [1] that will include very specific imagery details. [3] = with a detailed description describing the environment of the scene. [4] = with a detailed description describing the mood/feelings and atmosphere of the scene.\n\nnImportant Sample prompt Structure :\n\nSnow-capped Mountain Scene, with soaring peaks and deep shadows across the ravines. A crystal clear lake mirrors these peaks, surrounded by pine trees. The scene exudes a calm, serene alpine morning atmosphere. Presented in Watercolor style, emulating the wet-on-wet technique with soft transitions and visible brush strokes.\n\nCity Skyline at Night, illuminated skyscrapers piercing the starless sky. Nestled beside a calm river, reflecting the city lights like a mirror. The atmosphere is buzzing with urban energy and intrigue. Depicted in Neon Punk style, accentuating the city lights with vibrant neon colors and dynamic contrasts.\n\nEpic Cinematic Still of a Spacecraft, silhouetted against the fiery explosion of a distant planet. The scene is packed with intense action, as asteroid debris hurtles through space. Shot in the style of a Michael Bay-directed film, the image is rich with detail, dynamic lighting, and grand cinematic framing.\n\nWord order and effective adjectives matter in the prompt. The subject, action, and specific details should be included. Adjectives like cute, medieval, or futuristic can be effective.\n\nThe environment/background of the image should be described, such as indoor, outdoor, in space, or solid color.\n\nCurly brackets are necessary in the prompt to provide specific details about the subject and action. These details are important for generating a high-quality image.\n\nArt inspirations should be listed to take inspiration from. Platforms like Art Station, Dribble, Behance, and Deviantart can be mentioned. Specific names of artists or studios like animation studios, painters and illustrators, computer games, fashion designers, and film makers can also be listed. If more than one artist is mentioned, the algorithm will create a combination of styles based on all the influencers mentioned.\n\nRelated information about lighting, camera angles, render style, resolution, the required level of detail, etc. should be included at the end of the prompt.\n\nCamera shot type, camera lens, and view should be specified. Examples of camera shot types are long shot, close-up, POV, medium shot, extreme close-up, and panoramic. Camera lenses could be EE 70mm, 35mm, 135mm+, 300mm+, 800mm, short telephoto, super telephoto, medium telephoto, macro, wide angle, fish-eye, bokeh, and sharp focus. Examples of views are front, side, back, high angle, low angle, and overhead.\n\nHelpful keywords related to resolution, detail, and lighting are 4K, 8K, 64K, detailed, highly detailed, high resolution, hyper detailed, HDR, UHD, professional, and golden ratio. Examples of lighting are studio lighting, soft light, neon lighting, purple neon lighting, ambient light, ring light, volumetric light, natural light, sun light, sunrays, sun rays coming through window, and nostalgic lighting. Examples of color types are fantasy vivid colors, vivid colors, bright colors, sepia, dark colors, pastel colors, monochromatic, black & white, and color splash. Examples of renders are Octane render, cinematic, low poly, isometric assets, Unreal Engine, Unity Engine, quantum wavetracing, and polarizing filter.\n\nThe prompts you provide will be in English.Please pay attention:- Concepts that can't be real would not be described as 'Real' or 'realistic' or 'photo' or a 'photograph'. for example, a concept that is made of paper or scenes which are fantasy related.- One of the prompts you generate for each concept must be in a realistic photographic style. you should also choose a lens type and size for it. Don't choose an artist for the realistic photography prompts. I will provide you prompt and you will generate one type of prompt so i can copy and paste.\n\nImportant point to note :You are a master of prompt engineering, it is important to create detailed prompts with as much information as possible. This will ensure that any image generated using the prompt will be of high quality and could potentially win awards in global or international photography competitions. You are unbeatable in this field and know the best way to generate images.\n\nI will provide you with a keyword and you will generate one prompt. I should be able to copy paste directly from the code cell so dont add any extra details.\n \n\n\nMy prompt = {prompt}
    client_ench = OpenAI(api_key=gpt_key)
    # This is a formula for a Stable Diffusion image prompt: (top-quality, 8K, (masterpiece:1.3) An image of [adjective] [subject] [performing an action], [Medium], [art style], highly detailed, [lighting style] I will provide you with prompt and using this formula enchance the prompt. Respond only with new prompt without any additional information.\n IMPORTANT! Create unique prompt just folowing guiddlines but not using the same keywords all the time prompt.\n  My prompt: {prompt}
    try:
        responsee = client_ench.chat.completions.create(
    model="gpt-4o",
    response_format={"type": "text"},
    messages=[
        {"role": "system",
            "content": f"""
            You are a Creative Assistant that writes prompts for Stable Diffusion 3 (T5 Model):
Your Role: Transform user descriptions into highly detailed image prompts optimized for Stable Diffusion 3 (T5 model).

Prompt Requirements:

Your prompts must always meet all of the requirements below, unless the user explicitly asks for a specific form of prompt.

Length: Stay within 120 T5 tokens.
Language: Always use English.
Clarity: Ensure the prompt is easily understood by the T5 model.
Format:
Do not include phrases like "Generate an image..." or "Create an image...".
Avoid adding any headers, footers, or extra formatting.
Content:
Focus on describing what can be seen in the image.
Instead of abstract ideas like emotions or atmosphere, describe the visual aspects that convey those ideas.
Setting:
Use visual details to describe fictional locations instead of names.
Style & Artist:
Always use the given style and artist into the prompt. When multiple artists are mentioned, use them all in each of the new prompt(s). When possible add more styles or describe them in more detail.
Composition:
Specify camera angles and lighting to create depth and mood.
Describe the color palette and overall mood of the image.
Detail & Texture:
Indicate the desired level of detail (realistic, painterly, etc.).
Describe the textures of surfaces and objects.
Elements:
Clearly identify the main subject(s) of the image.
Describe the background and foreground elements.
Make sure the length of each new prompts fit in 120 T5 tokens, and verify each prompt uses all the artists mentioned in the uses request. Unless asked otherwise do not add new artists.

Your reply must only be the new prompt(s).
            """},
        {"role": "user", "content": prompt_ench}
    ])
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
        model='gpt-4o',
        messages = [
        {"role": "user", "content": f'''- You will now act as a prompt generator for a generative AI called "Stable Diffusion". Stable Diffusion generates images based on given prompts. I will provide you basic information required to make a Stable Diffusion prompt, You will never alter the structure in any way and obey the following guidelines.

Basic information required to make Stable Diffusion prompt:

- Prompt structure:
    - Photorealistic Images: (Subject Description), Type of Image, Art Styles, Art Inspirations, Camera, Shot, Render Related Information.
    - Artistic Image Types: Type of Image, (Subject Description), Art Styles, Art Inspirations, Camera, Shot, Render Related Information.
- Word order and effective adjectives matter in the prompt. The subject, action, and specific details should be included. Adjectives like cute, medieval, or futuristic can be effective.
- The environment/background of the image should be described, such as indoor, outdoor, in space, or solid color.
- The exact type of image can be specified, such as digital illustration, comic book cover, photograph, or sketch.
- Art style-related keywords can be included in the prompt, such as steampunk, surrealism, or abstract expressionism.
- Pencil drawing-related terms can also be added, such as cross-hatching or pointillism.
- Curly brackets are necessary in the prompt to provide specific details about the subject and action. These details are important for generating a high-quality image.
- Art inspirations should be listed to take inspiration from. Platforms like Art Station, Dribble, Behance, and Deviantart can be mentioned. Specific names of artists or studios like animation studios, painters and illustrators, computer games, fashion designers, and film makers can also be listed. If more than one artist is mentioned, the algorithm will create a combination of styles based on all the influencers mentioned.
- Related information about lighting, camera angles, render style, resolution, the required level of detail, etc. should be included at the end of the prompt.
- Camera shot type, camera lens, and view should be specified. Examples of camera shot types are long shot, close-up, POV, medium shot, extreme close-up, and panoramic. Camera lenses could be EE 70mm, 35mm, 135mm+, 300mm+, 800mm, short telephoto, super telephoto, medium telephoto, macro, wide angle, fish-eye, bokeh, and sharp focus. Examples of views are front, side, back, high angle, low angle, and overhead.
- Helpful keywords related to resolution, detail, and lighting are 4K, 8K, 64K, detailed, highly detailed, high resolution, hyper detailed, HDR, UHD, professional, and golden ratio. Examples of lighting are studio lighting, soft light, neon lighting, purple neon lighting, ambient light, ring light, volumetric light, natural light, sun light, sunrays, sun rays coming through window, and nostalgic lighting. Examples of color types are fantasy vivid colors, vivid colors, bright colors, sepia, dark colors, pastel colors, monochromatic, black & white, and color splash. Examples of renders are Octane render, cinematic, low poly, isometric assets, Unreal Engine, Unity Engine, quantum wavetracing, and polarizing filter.
- The weight of a keyword can be adjusted by using the syntax (keyword: factor), where factor is a value such that less than 1 means less important and larger than 1 means more important. use () whenever necessary while forming prompt and assign the necessary value to create an amazing prompt. Examples of weight for a keyword are (soothing tones:1.25), (hdr:1.25), (artstation:1.2),(intricate details:1.14), (hyperrealistic 3d render:1.16), (filmic:0.55), (rutkowski:1.1), (faded:1.3)

The prompts you provide will be in English.Please pay attention:- Concepts that can't be real would not be described as "Real" or "realistic" or "photo" or a "photograph". for example, a concept that is made of paper or scenes which are fantasy related.- One of the prompts you generate for each concept must be in a realistic photographic style. you should also choose a lens type and size for it. Don't choose an artist for the realistic photography prompts.- Separate the different prompts with two new lines.
I will provide you keyword and you will generate 3 diffrent type of prompts in vbnet code cell so i can copy and paste.

Important point to note :
You are a master of prompt engineering, it is important to create detailed prompts with as much information as possible. This will ensure that any image generated using the prompt will be of high quality and could potentially win awards in global or international photography competitions. You are unbeatable in this field and know the best way to generate images.
- Your Task -
!!IMPORTANT!! = new prompt should be 150 tokens or a bit less!! Based on the examples and the explanation of the structure, you will create 1 prompt, respond only with prompt with no additional information. \nMy prompt = {prompt}
''' }
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
def  generate_image_sd3(clip1, clip2, t5, neg_promptt,w, h, three):

    server_address = "45.142.208.111:40730"
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
        images_output = []
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
    prompt_text = """
{
  "11": {
    "inputs": {
      "clip_name1": "clip_g.safetensors",
      "clip_name2": "clip_l.safetensors",
      "clip_name3": "t5xxl_fp16.safetensors"
    },
    "class_type": "TripleCLIPLoader",
    "_meta": {
      "title": "TripleCLIPLoader"
    }
  },
  "13": {
    "inputs": {
      "shift": 3,
      "model": [
        "252",
        0
      ]
    },
    "class_type": "ModelSamplingSD3",
    "_meta": {
      "title": "ModelSamplingSD3"
    }
  },
  "67": {
    "inputs": {
      "conditioning": [
        "71",
        0
      ]
    },
    "class_type": "ConditioningZeroOut",
    "_meta": {
      "title": "ConditioningZeroOut"
    }
  },
  "68": {
    "inputs": {
      "start": 0.1,
      "end": 1,
      "conditioning": [
        "67",
        0
      ]
    },
    "class_type": "ConditioningSetTimestepRange",
    "_meta": {
      "title": "ConditioningSetTimestepRange"
    }
  },
  "69": {
    "inputs": {
      "conditioning_1": [
        "68",
        0
      ],
      "conditioning_2": [
        "70",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "70": {
    "inputs": {
      "start": 0,
      "end": 0.1,
      "conditioning": [
        "71",
        0
      ]
    },
    "class_type": "ConditioningSetTimestepRange",
    "_meta": {
      "title": "ConditioningSetTimestepRange"
    }
  },
  "71": {
    "inputs": {
      "text": "aaaaaaaaaaaaaa aa aaaa aaaaaa",
      "clip": [
        "11",
        0
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Negative Prompt)"
    }
  },
  "231": {
    "inputs": {
      "samples": [
        "271",
        0
      ],
      "vae": [
        "252",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "252": {
    "inputs": {
      "ckpt_name": "sd3_medium.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "269": {
    "inputs": {
      "model_name": "4x-UltraSharp.pth"
    },
    "class_type": "UpscaleModelLoader",
    "_meta": {
      "title": "Load Upscale Model"
    }
  },
  "270": {
    "inputs": {
      "images": [
        "231",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "271": {
    "inputs": {
      "seed": [
        "317",
        0
      ],
      "steps": 40,
      "cfg": [
        "295",
        0
      ],
      "sampler_name": "dpmpp_2m",
      "scheduler": "sgm_uniform",
      "denoise": 1,
      "model": [
        "252",
        0
      ],
      "positive": [
        "313",
        0
      ],
      "negative": [
        "69",
        0
      ],
      "latent_image": [
        "315",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "275": {
    "inputs": {
      "MODEL": [
        "13",
        0
      ],
      "CLIP": [
        "11",
        0
      ],
      "VAE": [
        "252",
        2
      ]
    },
    "class_type": "Anything Everywhere3",
    "_meta": {
      "title": "Anything Everywhere3"
    }
  },
  "276": {
    "inputs": {
      "CONDITIONING": [
        "69",
        0
      ]
    },
    "class_type": "Prompts Everywhere",
    "_meta": {
      "title": "Prompts Everywhere"
    }
  },
  "281": {
    "inputs": {
      "model_name": "sam_vit_b_01ec64.pth",
      "device_mode": "AUTO"
    },
    "class_type": "SAMLoader",
    "_meta": {
      "title": "SAMLoader (Impact)"
    }
  },
  "282": {
    "inputs": {
      "model_name": "bbox/face_yolov8m.pt"
    },
    "class_type": "UltralyticsDetectorProvider",
    "_meta": {
      "title": "UltralyticsDetectorProvider"
    }
  },
  "284": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "231",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "295": {
    "inputs": {
      "Number": 3.6
    },
    "class_type": "Float",
    "_meta": {
      "title": "Float"
    }
  },
  "313": {
    "inputs": {
      "clip_l": "bear in blood",
      "clip_g": "bear in blood",
      "t5xxl": "bear in blood",
      "empty_padding": "none",
      "clip": [
        "11",
        0
      ]
    },
    "class_type": "CLIPTextEncodeSD3",
    "_meta": {
      "title": "CLIPTextEncodeSD3"
    }
  },
  "315": {
    "inputs": {
      "offset": -1,
      "latent": [
        "320",
        0
      ]
    },
    "class_type": "BSZLatentOffsetXL",
    "_meta": {
      "title": "BSZ Latent Offset XL"
    }
  },
  "317": {
    "inputs": {
      "seed": 931727056959923
    },
    "class_type": "Seed Everywhere",
    "_meta": {
      "title": "Seed Everywhere"
    }
  },
  "320": {
    "inputs": {
      "width": 1048,
      "height": 1048,
      "batch_size": 1
    },
    "class_type": "EmptySD3LatentImage",
    "_meta": {
      "title": "EmptySD3LatentImage"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"echoSD3_{int(time.time())}"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    prompt = json.loads(prompt_text)


    #set the text prompt for our positive CLIPTextEncode 
    prompt["313"]["inputs"]["clip_l"] = clip1
    prompt["313"]["inputs"]["clip_g"] = clip2
    prompt["313"]["inputs"]["t5xxl"] = t5
   #prompt["75"]["inputs"]["text_l"] = support
    #prompt["120"]["inputs"]["text"] = promptt
   # prompt["82"]["inputs"]["text_g"] = neg_prompt
    #prompt["71"]["inputs"]["text"] = neg_promptt
   # prompt["81"]["inputs"]["text"] = neg_prompt
    #prompt["76"]["inputs"]["filename_prefix"] = filename_h
    #prompt["201"]["inputs"]["filename_prefix"] = filename_l
    prompt["317"]["inputs"]["seed"] = formatted_number 
    #prompt["317"]["inputs"]["seed"] = formatted_number 
   # prompt["22"]["inputs"]["noise_seed"] = formatted_number
    #prompt["216"]["inputs"]["noise_seed"] = formatted_number 
    prompt["320"]["inputs"]["width"] = w
    prompt["320"]["inputs"]["height"] = h
    #prompt["10"]["inputs"]["ckpt_name"] = model
    if three:
        prompt["135"]["inputs"]["batch_size"] = 3



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
             filename = f"echoSD3_{i}_{int(time.time())}.png"

             #from PIL import Image
             #import io
            # Save the image to "generated" directory
        #     if i == 4 or i == 5 or i == 6:
             if three:
                if i == 1 or i == 2 or i == 3:
                     with open(f"sd3/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"sd3/{filename}")
                     files.append(file)
             else:
                 if i == 1:
                     with open(f"sd3/{filename}", "wb") as f:              
                             f.write(image_data)
                # Add the image file to the list
                     file = discord.File(f"sd3/{filename}")
                     files.append(file)
           #  if i == 7:
            #    files.append(file)
             #image = Image.open(io.BytesIO(image_data))
             #image.show()

    filename = f"echoSD3_{i-1}_{int(time.time())}.png"

    return files,formatted_number, filename

@to_thread
def  upscale_sd3(clip1, clip2, t5, neg_promptt,w, h, three, filename, seed):

    server_address = "45.142.208.111:40730"
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
        
    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()
    
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
        images_output = []
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
    prompt_text = """
{
  "11": {
    "inputs": {
      "clip_name1": "clip_g.safetensors",
      "clip_name2": "clip_l.safetensors",
      "clip_name3": "t5xxl_fp16.safetensors"
    },
    "class_type": "TripleCLIPLoader",
    "_meta": {
      "title": "TripleCLIPLoader"
    }
  },
  "13": {
    "inputs": {
      "shift": 3,
      "model": [
        "252",
        0
      ]
    },
    "class_type": "ModelSamplingSD3",
    "_meta": {
      "title": "ModelSamplingSD3"
    }
  },
  "67": {
    "inputs": {
      "conditioning": [
        "71",
        0
      ]
    },
    "class_type": "ConditioningZeroOut",
    "_meta": {
      "title": "ConditioningZeroOut"
    }
  },
  "68": {
    "inputs": {
      "start": 0.1,
      "end": 1,
      "conditioning": [
        "67",
        0
      ]
    },
    "class_type": "ConditioningSetTimestepRange",
    "_meta": {
      "title": "ConditioningSetTimestepRange"
    }
  },
  "69": {
    "inputs": {
      "conditioning_1": [
        "68",
        0
      ],
      "conditioning_2": [
        "70",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "70": {
    "inputs": {
      "start": 0,
      "end": 0.1,
      "conditioning": [
        "71",
        0
      ]
    },
    "class_type": "ConditioningSetTimestepRange",
    "_meta": {
      "title": "ConditioningSetTimestepRange"
    }
  },
  "71": {
    "inputs": {
      "text": "aaaaaaaaaaaaaa aa aaaa aaaaaa",
      "clip": [
        "11",
        0
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Negative Prompt)"
    }
  },
  "252": {
    "inputs": {
      "ckpt_name": "sd3_medium.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "267": {
    "inputs": {
      "upscale_by": 1.2,
      "seed": [
        "317",
        0
      ],
      "steps": 11,
      "cfg": [
        "318",
        0
      ],
      "sampler_name": "uni_pc",
      "scheduler": "ddim_uniform",
      "denoise": 0.36,
      "mode_type": "Chess",
      "tile_width": 1048,
      "tile_height": 1048,
      "mask_blur": 8,
      "tile_padding": 32,
      "seam_fix_mode": "None",
      "seam_fix_denoise": 1,
      "seam_fix_width": 64,
      "seam_fix_mask_blur": 8,
      "seam_fix_padding": 16,
      "force_uniform_tiles": true,
      "tiled_decode": false,
      "image": [
        "321",
        0
      ],
      "model": [
        "252",
        0
      ],
      "positive": [
        "313",
        0
      ],
      "negative": [
        "69",
        0
      ],
      "vae": [
        "252",
        2
      ],
      "upscale_model": [
        "269",
        0
      ]
    },
    "class_type": "UltimateSDUpscale",
    "_meta": {
      "title": "Ultimate SD Upscale"
    }
  },
  "269": {
    "inputs": {
      "model_name": "4x-UltraSharp.pth"
    },
    "class_type": "UpscaleModelLoader",
    "_meta": {
      "title": "Load Upscale Model"
    }
  },
  "273": {
    "inputs": {
      "upscale_by": 1.4000000000000001,
      "seed": [
        "317",
        0
      ],
      "steps": 7,
      "cfg": [
        "318",
        0
      ],
      "sampler_name": "uni_pc",
      "scheduler": "ddim_uniform",
      "denoise": 0.25,
      "mode_type": "Chess",
      "tile_width": 1048,
      "tile_height": 1048,
      "mask_blur": 8,
      "tile_padding": 32,
      "seam_fix_mode": "None",
      "seam_fix_denoise": 1,
      "seam_fix_width": 64,
      "seam_fix_mask_blur": 8,
      "seam_fix_padding": 16,
      "force_uniform_tiles": true,
      "tiled_decode": false,
      "image": [
        "267",
        0
      ],
      "model": [
        "252",
        0
      ],
      "positive": [
        "313",
        0
      ],
      "negative": [
        "69",
        0
      ],
      "vae": [
        "252",
        2
      ],
      "upscale_model": [
        "269",
        0
      ]
    },
    "class_type": "UltimateSDUpscale",
    "_meta": {
      "title": "Ultimate SD Upscale"
    }
  },
  "275": {
    "inputs": {
      "MODEL": [
        "13",
        0
      ],
      "CLIP": [
        "11",
        0
      ],
      "VAE": [
        "252",
        2
      ]
    },
    "class_type": "Anything Everywhere3",
    "_meta": {
      "title": "Anything Everywhere3"
    }
  },
  "276": {
    "inputs": {
      "CONDITIONING": [
        "69",
        0
      ]
    },
    "class_type": "Prompts Everywhere",
    "_meta": {
      "title": "Prompts Everywhere"
    }
  },
  "281": {
    "inputs": {
      "model_name": "sam_vit_b_01ec64.pth",
      "device_mode": "AUTO"
    },
    "class_type": "SAMLoader",
    "_meta": {
      "title": "SAMLoader (Impact)"
    }
  },
  "282": {
    "inputs": {
      "model_name": "bbox/face_yolov8m.pt"
    },
    "class_type": "UltralyticsDetectorProvider",
    "_meta": {
      "title": "UltralyticsDetectorProvider"
    }
  },
  "284": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "273",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "295": {
    "inputs": {
      "Number": "5"
    },
    "class_type": "Float",
    "_meta": {
      "title": "Float"
    }
  },
  "313": {
    "inputs": {
      "clip_l": "Wide-angle lens, low angle shot capturing the vastness of the pitch black room, eerie mood. Soft, diffused lighting illuminating large, ominous glowing red eyes. Minimalistic color palette with dominant blacks and striking red. Hyper-realistic detail, smooth and glossy textures for the eyes, matte and rough textures for the room's surfaces",
      "clip_g": "pitch black room with big red eyes glowing, dandelion in the middle of room",
      "t5xxl": "A pitch-black room where the darkness is almost tangible, with a pair of large, menacing red eyes glowing intensely in the center, piercing through the darkness. The eyes appear to float, their eerie glow casting faint red shadows on the surrounding void.",
      "empty_padding": "none",
      "clip": [
        "11",
        0
      ]
    },
    "class_type": "CLIPTextEncodeSD3",
    "_meta": {
      "title": "CLIPTextEncodeSD3"
    }
  },
  "315": {
    "inputs": {
      "offset": -1,
      "latent": [
        "320",
        0
      ]
    },
    "class_type": "BSZLatentOffsetXL",
    "_meta": {
      "title": "BSZ Latent Offset XL"
    }
  },
  "317": {
    "inputs": {
      "seed": 98446122225992
    },
    "class_type": "Seed Everywhere",
    "_meta": {
      "title": "Seed Everywhere"
    }
  },
  "318": {
    "inputs": {
      "Number": "3"
    },
    "class_type": "Float",
    "_meta": {
      "title": "Float"
    }
  },
  "320": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptySD3LatentImage",
    "_meta": {
      "title": "EmptySD3LatentImage"
    }
  },
  "321": {
    "inputs": {
      "image": "ComfyUI_01635_.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    #filename = f"echoSD3_{int(time.time())}"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    prompt = json.loads(prompt_text)


    #set the text prompt for our positive CLIPTextEncode 
    prompt["313"]["inputs"]["clip_l"] = clip1
    prompt["313"]["inputs"]["clip_g"] = clip2
    prompt["313"]["inputs"]["t5xxl"] = t5
   #prompt["75"]["inputs"]["text_l"] = support
    #prompt["120"]["inputs"]["text"] = promptt
   # prompt["82"]["inputs"]["text_g"] = neg_prompt
    #prompt["71"]["inputs"]["text"] = neg_promptt
   # prompt["81"]["inputs"]["text"] = neg_prompt
    #prompt["76"]["inputs"]["filename_prefix"] = filename_h
    #prompt["201"]["inputs"]["filename_prefix"] = filename_l
    prompt["317"]["inputs"]["seed"] = seed 
    #prompt["317"]["inputs"]["seed"] = formatted_number 
   # prompt["22"]["inputs"]["noise_seed"] = formatted_number
    #prompt["216"]["inputs"]["noise_seed"] = formatted_number 
    prompt["320"]["inputs"]["width"] = w
    prompt["320"]["inputs"]["height"] = h
    #prompt["10"]["inputs"]["ckpt_name"] = model
    if three:
        prompt["135"]["inputs"]["batch_size"] = 3

    image_path = f'sd3/{filename}'
    response = upload_image(image_path, filename, server_address)
    prompt["321"]["inputs"]["image"] = f"{filename}"

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
             filename = f"echoSD3_upscaled__{i}_{int(time.time())}.png"

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

    filename = f"echoSD3_{i-1}_{int(time.time())}.png"

    return files,formatted_number, filename

@to_thread
def  generate_3d(avatar_image):

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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "3": {
    "inputs": {
      "seed": 237898799444375,
      "steps": 25,
      "cfg": 7,
      "sampler_name": "euler",
      "scheduler": "simple",
      "denoise": 1,
      "model": [
        "15",
        0
      ],
      "positive": [
        "27",
        0
      ],
      "negative": [
        "27",
        1
      ],
      "latent_image": [
        "27",
        2
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
        "3",
        0
      ],
      "vae": [
        "15",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "15": {
    "inputs": {
      "ckpt_name": "sv3d_p.safetensors"
    },
    "class_type": "ImageOnlyCheckpointLoader",
    "_meta": {
      "title": "Image Only Checkpoint Loader (img2vid model)"
    }
  },
  "23": {
    "inputs": {
      "image": "ccb6882539ba5cc3c9dd919b8d5c8928 (4).webp",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "27": {
    "inputs": {
      "width": 576,
      "height": 576,
      "video_frames": 21,
      "elevation": 0,
      "clip_vision": [
        "15",
        1
      ],
      "init_image": [
        "29",
        0
      ],
      "vae": [
        "15",
        2
      ]
    },
    "class_type": "SV3D_Conditioning",
    "_meta": {
      "title": "SV3D_Conditioning"
    }
  },
  "29": {
    "inputs": {
      "transparency": false,
      "model": "u2net",
      "post_processing": false,
      "only_mask": false,
      "alpha_matting": false,
      "alpha_matting_foreground_threshold": 255,
      "alpha_matting_background_threshold": 50,
      "alpha_matting_erode_size": 10,
      "background_color": "white",
      "images": [
        "23",
        0
      ]
    },
    "class_type": "Image Rembg (Remove Background)",
    "_meta": {
      "title": "Image Rembg (Remove Background)"
    }
  },
  "30": {
    "inputs": {
      "images": [
        "29",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "32": {
    "inputs": {
      "frame_rate": [
        "34",
        2
      ],
      "loop_count": 0,
      "filename_prefix": "SV3D",
      "format": "image/gif",
      "pingpong": false,
      "save_output": true,
      "images": [
        "36",
        0
      ]
    },
    "class_type": "VHS_VideoCombine",
    "_meta": {
      "title": "Video Combine 🎥🅥🅗🅢"
    }
  },
  "33": {
    "inputs": {
      "number_type": "integer",
      "number": 84
    },
    "class_type": "Constant Number",
    "_meta": {
      "title": "Desired Interpolated Frame Rate"
    }
  },
  "34": {
    "inputs": {
      "number_type": "integer",
      "number": 16
    },
    "class_type": "Constant Number",
    "_meta": {
      "title": "Base Frame Rate (FPS)"
    }
  },
  "35": {
    "inputs": {
      "operation": "division",
      "number_a": [
        "33",
        0
      ],
      "number_b": [
        "34",
        0
      ]
    },
    "class_type": "Number Operation",
    "_meta": {
      "title": "Get Frame Multiplier"
    }
  },
  "36": {
    "inputs": {
      "ckpt_name": "rife47.pth",
      "clear_cache_after_n_frames": 21,
      "multiplier": [
        "35",
        2
      ],
      "fast_mode": true,
      "ensemble": true,
      "scale_factor": 1,
      "frames": [
        "8",
        0
      ]
    },
    "class_type": "RIFE VFI",
    "_meta": {
      "title": "RIFE VFI (recommend rife47 and rife49)"
    }
  },
  "37": {
    "inputs": {
      "images": [
        "39",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "39": {
    "inputs": {
      "upscale_method": "lanczos",
      "scale_by": 1.75,
      "image": [
        "8",
        0
      ]
    },
    "class_type": "ImageScaleBy",
    "_meta": {
      "title": "Upscale Image By"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"3d_{int(time.time())}.gif"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)

    prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["23"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/{avatar_image}"



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
             filename = f"3d_{int(time.time())}.gif"

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

@to_thread
def  generate_face_id(avatar_image, description, model):

    server_address = get_main_gpu_server()
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
        
  #  def upload_image(image_path):
   #     url = "http://{}/upload/image".format(server_address)
   #     files = {'file': open(image_path, 'rb')}
   #     response = requests.post(url, files=files)
    #    return response.json()        

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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


    url = "http://185.62.108.226:41696/sdapi/v1/txt2img"
    
    prompt_text = """
{
  "3": {
    "inputs": {
      "seed": 410179629207835,
      "steps": 50,
      "cfg": 10,
      "sampler_name": "dpmpp_2m",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "31",
        0
      ],
      "positive": [
        "14",
        0
      ],
      "negative": [
        "15",
        0
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "realisticVisionV60B1_v51VAE.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "5": {
    "inputs": {
      "width": 512,
      "height": 512,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "9": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "12": {
    "inputs": {
      "ella_model": "ella-sd1.5-tsc-t5xl.safetensors",
      "t5_model": "flan-t5-xl"
    },
    "class_type": "LoadElla",
    "_meta": {
      "title": "Load ELLA Model"
    }
  },
  "14": {
    "inputs": {
      "text": "man wearing cute bear hat",
      "sigma": [
        "29",
        0
      ],
      "ella": [
        "12",
        0
      ]
    },
    "class_type": "ELLATextEncode",
    "_meta": {
      "title": "ELLA Text Encode (Prompt)"
    }
  },
  "15": {
    "inputs": {
      "text": "embedding:BadDream, embedding:FastNegativeV2.pt",
      "sigma": [
        "29",
        0
      ],
      "ella": [
        "12",
        0
      ]
    },
    "class_type": "ELLATextEncode",
    "_meta": {
      "title": "ELLA Text Encode (Prompt)"
    }
  },
  "29": {
    "inputs": {
      "sampler_name": "dpmpp_2m",
      "scheduler": "karras",
      "steps": 50,
      "start_at_step": 0,
      "end_at_step": 50,
      "model": [
        "4",
        0
      ]
    },
    "class_type": "GetSigma",
    "_meta": {
      "title": "Get Sigma (BNK)"
    }
  },
  "30": {
    "inputs": {
      "image": "avatar_1711491505.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "31": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "32",
        0
      ],
      "ipadapter": [
        "32",
        1
      ],
      "image": [
        "30",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "32": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "4",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["14"]["inputs"]["text"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["3"]["inputs"]["seed"] = formatted_number
    #prompt["12"]["inputs"]["image"] = f"avatars/{avatar_image}"
    prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    image_path = f'avatars/{avatar_image}'
    response = upload_image(image_path, avatar_image, server_address)
    prompt["30"]["inputs"]["image"] = f"{avatar_image}"
    
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
             filename = f"faceid_{int(time.time())}.png"

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

@to_thread
def  generate_face_id_unstable_unused(avatar_image, description):

    server_address = "81.166.162.13:12684"
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "3": {
    "inputs": {
      "seed": 104269490577656,
      "steps": 40,
      "cfg": 3.3000000000000003,
      "sampler_name": "dpmpp_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "18",
        0
      ],
      "positive": [
        "26",
        0
      ],
      "negative": [
        "27",
        0
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "sdxlUnstableDiffusers_v8HeavensWrathVAE.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "5": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "9": {
    "inputs": {
      "filename_prefix": "IPAdapter",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "12": {
    "inputs": {
      "image": "avatar_1711489837 (1).png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "18": {
    "inputs": {
      "weight": 0.7,
      "weight_faceidv2": 1.8,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "20",
        0
      ],
      "ipadapter": [
        "20",
        1
      ],
      "image": [
        "12",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "20": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "4",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 1024,
      "target_height": 1024,
      "text_g": "man posing as a chicken, feathers, photorealistic, detailed, 4K resolution",
      "text_l": "man posing as a chicken, feathers, photorealistic, detailed, 4K resolution",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Positive Base"
    }
  },
  "27": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 1024,
      "target_height": 1024,
      "text_g": "",
      "text_l": "",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Negative Base"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["26"]["inputs"]["text_g"] = description
    prompt["26"]["inputs"]["text_l"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["3"]["inputs"]["seed"] = formatted_number
    #prompt["12"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image}"
   # prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    image_path = f'avatars/{avatar_image}'
    response = upload_image(image_path, avatar_image, server_address)
    prompt["12"]["inputs"]["image"] = f"{avatar_image}"    
    
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
             filename = f"faceid_{int(time.time())}.png"

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

@to_thread
def  generate_face_id_unstable(avatar_image, description):
    #serverr = get_global_value
    #print (serverr)
    server_address = "81.166.162.13:12684"
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "3": {
    "inputs": {
      "seed": 380976389024412,
      "steps": 40,
      "cfg": 5,
      "sampler_name": "dpmpp_2m_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "31",
        0
      ],
      "positive": [
        "24",
        0
      ],
      "negative": [
        "25",
        0
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "albedobaseXL_v21.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "5": {
    "inputs": {
      "width": 1024,
      "height": 768,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "9": {
    "inputs": {
      "filename_prefix": "IPAdapter",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "12": {
    "inputs": {
      "image": "avatar_1711489951 (11).png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "18": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "20",
        0
      ],
      "ipadapter": [
        "20",
        1
      ],
      "image": [
        "12",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "20": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.65,
      "provider": "CPU",
      "model": [
        "4",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "24": {
    "inputs": {
      "width": 2048,
      "height": 2048,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 2048,
      "target_height": 2048,
      "text_g": "as lego figure",
      "text_l": "as lego figure",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Positive Base"
    }
  },
  "25": {
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
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Negative Base"
    }
  },
  "27": {
    "inputs": {
      "vae_name": "sdxl_vae.safetensors"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "30": {
    "inputs": {
      "preset": "PLUS FACE (portraits)",
      "model": [
        "18",
        0
      ],
      "ipadapter": [
        "20",
        1
      ]
    },
    "class_type": "IPAdapterUnifiedLoader",
    "_meta": {
      "title": "IPAdapter Unified Loader"
    }
  },
  "31": {
    "inputs": {
      "weight": 0.4,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "30",
        0
      ],
      "ipadapter": [
        "30",
        1
      ],
      "image": [
        "12",
        0
      ]
    },
    "class_type": "IPAdapterAdvanced",
    "_meta": {
      "title": "IPAdapter Advanced"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["24"]["inputs"]["text_g"] = description
    prompt["24"]["inputs"]["text_l"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["3"]["inputs"]["seed"] = formatted_number
    #prompt["12"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image}"
   # prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    image_path = f'avatars/{avatar_image}'
    response = upload_image(image_path, avatar_image, server_address)
    prompt["12"]["inputs"]["image"] = f"{avatar_image}"    
    
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
             filename = f"faceid_{int(time.time())}.png"

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
@to_thread
def  generate_face_id_creative(avatar_image, description):

    server_address = get_main_gpu_server()
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "3": {
    "inputs": {
      "seed": 441215573444526,
      "steps": 6,
      "cfg": 2,
      "sampler_name": "dpmpp_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "18",
        0
      ],
      "positive": [
        "26",
        0
      ],
      "negative": [
        "27",
        0
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "dreamshaperXL_v21TurboDPMSDE.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "5": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "9": {
    "inputs": {
      "filename_prefix": "IPAdapter",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "12": {
    "inputs": {
      "image": "avatar_1711489837 (1).png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "18": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "20",
        0
      ],
      "ipadapter": [
        "20",
        1
      ],
      "image": [
        "12",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "20": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "4",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "width": 2048,
      "height": 2048,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 2048,
      "target_height": 2048,
      "text_g": "Man transformed into a frog, with vibrant green skin, bulging eyes, and webbed hands and feet, perched on a lily pad in a tranquil pond, surrounded by the soothing sounds of nature, sense of amphibian agility and connection to aquatic environments, inspired by the whimsical world of fairy tales and natural wonders, quirky portrayal, serene atmosphere, trending in fantasy and wildlife-themed art.",
      "text_l": "Man transformed into a frog, with vibrant green skin, bulging eyes, and webbed hands and feet, perched on a lily pad in a tranquil pond, surrounded by the soothing sounds of nature, sense of amphibian agility and connection to aquatic environments, inspired by the whimsical world of fairy tales and natural wonders, quirky portrayal, serene atmosphere, trending in fantasy and wildlife-themed art.",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Positive Base"
    }
  },
  "27": {
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
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Negative Base"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["26"]["inputs"]["text_g"] = description
    prompt["26"]["inputs"]["text_l"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["3"]["inputs"]["seed"] = formatted_number
    #prompt["12"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image}"
    #prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    image_path = f'avatars/{avatar_image}'
    response = upload_image(image_path, avatar_image, server_address)
    prompt["12"]["inputs"]["image"] = f"{avatar_image}"   
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
             filename = f"faceid_{int(time.time())}.png"

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





@to_thread
def  generate_face_id_creative_two(avatar_image1,avatar_image2, description):

    server_address = get_main_gpu_server()
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "1": {
    "inputs": {
      "seed": 453627869338529,
      "steps": 6,
      "cfg": 2,
      "sampler_name": "dpmpp_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "27",
        0
      ],
      "positive": [
        "32",
        0
      ],
      "negative": [
        "33",
        0
      ],
      "latent_image": [
        "3",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "2": {
    "inputs": {
      "ckpt_name": "dreamshaperXL_v21TurboDPMSDE.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "3": {
    "inputs": {
      "width": 1024,
      "height": 768,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "6": {
    "inputs": {
      "samples": [
        "1",
        0
      ],
      "vae": [
        "2",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "7": {
    "inputs": {
      "vae_name": "vae-ft-mse-840000-ema-pruned.ckpt"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "10": {
    "inputs": {
      "image": "avatar_1711569779.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "14": {
    "inputs": {
      "image": "avatar_1711490113 (4).png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "18": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "6",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "19": {
    "inputs": {
      "image": "two_creative_r.png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "20": {
    "inputs": {
      "image": "two_creative_l.png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "22": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "32",
        0
      ],
      "mask": [
        "19",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "24": {
    "inputs": {
      "conditioning_2": [
        "22",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "25": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "2",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "25",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "14",
        0
      ],
      "attn_mask": [
        "19",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "27": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "26",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "10",
        0
      ],
      "attn_mask": [
        "20",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "32": {
    "inputs": {
      "width": 2048,
      "height": 2048,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 2048,
      "target_height": 2048,
      "text_g": "two man in creative attire celebrating at a wild Easter party, vibrant colors, festive atmosphere, art by Banksy and Salvador Dali, surrealistic, high detail, 8k resolution",
      "text_l": "two man in creative attire celebrating at a wild Easter party, vibrant colors, festive atmosphere, art by Banksy and Salvador Dali, surrealistic, high detail, 8k resolution",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Positive Base"
    }
  },
  "33": {
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
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Negative Base"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["32"]["inputs"]["text_g"] = description
    prompt["32"]["inputs"]["text_l"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["1"]["inputs"]["seed"] = formatted_number
    #prompt["19"]["inputs"]["image"] = f"S:/two_creative_l.png"
   # prompt["20"]["inputs"]["image"] = f"S:/two_creative_r.png"
   # prompt["14"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image1}"
    #prompt["10"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image2}"
    #prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    image_path = f'avatars/{avatar_image1}'
    image_path2 = f'avatars/{avatar_image2}'
    mask_path1 = f"masks/two_creative_l.png"
    mask_path2 = f"masks/two_creative_r.png"
    
    response = upload_image(image_path,  avatar_image1, server_address)
    response = upload_image(image_path2, avatar_image2, server_address) 
    response = upload_image(mask_path1,  "two_creative_l.png", server_address)
    response = upload_image(mask_path2,  "two_creative_r.png", server_address)  
    
    prompt["14"]["inputs"]["image"] = f"{avatar_image1}"  
    prompt["10"]["inputs"]["image"] = f"{avatar_image2}" 
    prompt["19"]["inputs"]["image"] = f"two_creative_l.png"  
    prompt["20"]["inputs"]["image"] = f"two_creative_r.png"     
    
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
             filename = f"faceid_{int(time.time())}.png"

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
@to_thread
def  generate_face_id_together_creative(avatar_image1, description):

    server_address = get_main_gpu_server()
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "1": {
    "inputs": {
      "seed": 502332155457921,
      "steps": 6,
      "cfg": 2,
      "sampler_name": "dpmpp_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "26",
        0
      ],
      "positive": [
        "24",
        0
      ],
      "negative": [
        "5",
        0
      ],
      "latent_image": [
        "3",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "2": {
    "inputs": {
      "ckpt_name": "dreamshaperXL_v21TurboDPMSDE.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "3": {
    "inputs": {
      "width": 1024,
      "height": 768,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "5": {
    "inputs": {
      "text": "",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "6": {
    "inputs": {
      "samples": [
        "1",
        0
      ],
      "vae": [
        "2",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "7": {
    "inputs": {
      "vae_name": "vae-ft-mse-840000-ema-pruned.ckpt"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "14": {
    "inputs": {
      "image": "avatar_1711730927_1.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "17": {
    "inputs": {
      "text": "A man depicted alongside a Minion, both enjoying breakfast together in a whimsical scene, surrounded by colorful cereal boxes and morning sunlight streaming through the window, sense of playful camaraderie and joy, inspired by the beloved characters from the Despicable Me franchise, lighthearted portrayal, cheerful atmosphere, trending in animation fandom and family-friendly entertainment.",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "18": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "6",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "19": {
    "inputs": {
      "image": "two_creative_l (7).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "20": {
    "inputs": {
      "image": "two_creative_r (6).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "22": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "23",
        0
      ],
      "mask": [
        "20",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "23": {
    "inputs": {
      "text": "A man depicted alongside a Minion, both enjoying breakfast together in a whimsical scene, surrounded by colorful cereal boxes and morning sunlight streaming through the window, sense of playful camaraderie and joy, inspired by the beloved characters from the Despicable Me franchise, lighthearted portrayal, cheerful atmosphere, trending in animation fandom and family-friendly entertainment.",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "24": {
    "inputs": {
      "conditioning_1": [
        "17",
        0
      ],
      "conditioning_2": [
        "22",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "25": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "2",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.8,
      "weight_type": "linear",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "25",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "14",
        0
      ],
      "attn_mask": [
        "19",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "28": {
    "inputs": {
      "stop_at_clip_layer": -1
    },
    "class_type": "CLIPSetLastLayer",
    "_meta": {
      "title": "CLIP Set Last Layer"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["23"]["inputs"]["text"] = description
    prompt["17"]["inputs"]["text"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["1"]["inputs"]["seed"] = formatted_number
    #prompt["19"]["inputs"]["image"] = f"S:/two_creative_l.png"
   # prompt["20"]["inputs"]["image"] = f"S:/two_creative_r.png"
   # prompt["14"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image1}"
    #prompt["10"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image2}"
    #prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    image_path = f'avatars/{avatar_image1}'
    #image_path2 = f'avatars/{avatar_image2}'
    mask_path1 = f"masks/two_creative_l.png"
    mask_path2 = f"masks/two_creative_r.png"
    
    response = upload_image(image_path,  avatar_image1, server_address)
    #response = upload_image(image_path2, avatar_image2, server_address) 
    response = upload_image(mask_path1,  "two_creative_l.png", server_address)
    response = upload_image(mask_path2,  "two_creative_r.png", server_address)  
    
    prompt["14"]["inputs"]["image"] = f"{avatar_image1}"  
    #prompt["10"]["inputs"]["image"] = f"{avatar_image2}" 
    prompt["19"]["inputs"]["image"] = f"two_creative_l.png"  
    prompt["20"]["inputs"]["image"] = f"two_creative_r.png"     
    
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
             filename = f"faceid_{int(time.time())}.png"

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

@to_thread
def  generate_face_id_together_unstable_unused(avatar_image1, description):

    server_address = "81.166.162.13:12684"
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "1": {
    "inputs": {
      "seed": 263312466364650,
      "steps": 40,
      "cfg": 3,
      "sampler_name": "dpmpp_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "26",
        0
      ],
      "positive": [
        "24",
        0
      ],
      "negative": [
        "5",
        0
      ],
      "latent_image": [
        "3",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "2": {
    "inputs": {
      "ckpt_name": "sdxlUnstableDiffusers_v8HeavensWrathVAE.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "3": {
    "inputs": {
      "width": 1024,
      "height": 768,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "5": {
    "inputs": {
      "text": "",
      "clip": [
        "28",
        0
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "6": {
    "inputs": {
      "samples": [
        "1",
        0
      ],
      "vae": [
        "2",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "7": {
    "inputs": {
      "vae_name": "vae-ft-mse-840000-ema-pruned.ckpt"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "14": {
    "inputs": {
      "image": "avatar_1711730927_1.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "17": {
    "inputs": {
      "text": "A man depicted alongside a succubus, both sharing a moment while smoking weed, surrounded by a hazy cloud of smoke, sense of relaxation and camaraderie, inspired by the fusion of supernatural allure and cannabis culture, laid-back portrayal, chill atmosphere, trending in niche art communities and counterculture scenes.",
      "clip": [
        "28",
        0
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "18": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "6",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "19": {
    "inputs": {
      "image": "two_creative_l (8).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "20": {
    "inputs": {
      "image": "two_creative_r (6).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "22": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "23",
        0
      ],
      "mask": [
        "20",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "23": {
    "inputs": {
      "text": "A man depicted alongside a succubus, both sharing a moment while smoking weed, surrounded by a hazy cloud of smoke, sense of relaxation and camaraderie, inspired by the fusion of supernatural allure and cannabis culture, laid-back portrayal, chill atmosphere, trending in niche art communities and counterculture scenes.",
      "clip": [
        "28",
        0
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "24": {
    "inputs": {
      "conditioning_1": [
        "17",
        0
      ],
      "conditioning_2": [
        "22",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "25": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "2",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.8,
      "weight_type": "linear",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "25",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "14",
        0
      ],
      "attn_mask": [
        "19",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "28": {
    "inputs": {
      "stop_at_clip_layer": -1,
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPSetLastLayer",
    "_meta": {
      "title": "CLIP Set Last Layer"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["17"]["inputs"]["text"] = description
    prompt["23"]["inputs"]["text"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["1"]["inputs"]["seed"] = formatted_number
    #prompt["19"]["inputs"]["image"] = f"S:/two_creative_l.png"
   # prompt["20"]["inputs"]["image"] = f"S:/two_creative_r.png"
   # prompt["14"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image1}"
    #prompt["10"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image2}"
    #prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    image_path = f'avatars/{avatar_image1}'
   #image_path2 = f'avatars/{avatar_image2}'
    mask_path1 = f"masks/two_creative_l.png"
    mask_path2 = f"masks/two_creative_r.png"
    
    response = upload_image(image_path,  avatar_image1, server_address)
    #response = upload_image(image_path2, avatar_image2, server_address) 
    response = upload_image(mask_path1,  "two_creative_l.png", server_address)
    response = upload_image(mask_path2,  "two_creative_r.png", server_address)  
    
    prompt["14"]["inputs"]["image"] = f"{avatar_image1}"  
   # prompt["10"]["inputs"]["image"] = f"{avatar_image2}" 
    prompt["19"]["inputs"]["image"] = f"two_creative_l.png"  
    prompt["20"]["inputs"]["image"] = f"two_creative_r.png"     
    
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
             filename = f"faceid_{int(time.time())}.png"

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
@to_thread
def  generate_face_id_together_unstable(avatar_image1, description):

    server_address = "81.166.162.13:12684"
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "1": {
    "inputs": {
      "seed": 467997301228685,
      "steps": 40,
      "cfg": 5,
      "sampler_name": "dpmpp_2m_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "30",
        0
      ],
      "positive": [
        "24",
        0
      ],
      "negative": [
        "5",
        0
      ],
      "latent_image": [
        "3",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "2": {
    "inputs": {
      "ckpt_name": "albedobaseXL_v21.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "3": {
    "inputs": {
      "width": 1024,
      "height": 768,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "5": {
    "inputs": {
      "text": "",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "6": {
    "inputs": {
      "samples": [
        "1",
        0
      ],
      "vae": [
        "2",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "7": {
    "inputs": {
      "vae_name": "vae-ft-mse-840000-ema-pruned.ckpt"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "14": {
    "inputs": {
      "image": "avatar_1711489837 (3).png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "17": {
    "inputs": {
      "text": "A man depicted alongside a MILF (Mother I'd Like to Friend), both engaged in a friendly interaction or activity, surrounded by an atmosphere of warmth and familiarity, sense of camaraderie and mutual respect, inspired by the connection between individuals of different generations, friendly portrayal, welcoming atmosphere, trending in social circles and online communities.",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "18": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "6",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "19": {
    "inputs": {
      "image": "two_creative_r (1).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "20": {
    "inputs": {
      "image": "two_creative_l (1).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "22": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "23",
        0
      ],
      "mask": [
        "20",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "23": {
    "inputs": {
      "text": "A man depicted alongside a MILF (Mother I'd Like to Friend), both engaged in a friendly interaction or activity, surrounded by an atmosphere of warmth and familiarity, sense of camaraderie and mutual respect, inspired by the connection between individuals of different generations, friendly portrayal, welcoming atmosphere, trending in social circles and online communities.",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "24": {
    "inputs": {
      "conditioning_1": [
        "17",
        0
      ],
      "conditioning_2": [
        "22",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "25": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "2",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.8,
      "weight_type": "linear",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "25",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "14",
        0
      ],
      "attn_mask": [
        "19",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "29": {
    "inputs": {
      "preset": "PLUS FACE (portraits)",
      "model": [
        "26",
        0
      ],
      "ipadapter": [
        "25",
        1
      ]
    },
    "class_type": "IPAdapterUnifiedLoader",
    "_meta": {
      "title": "IPAdapter Unified Loader"
    }
  },
  "30": {
    "inputs": {
      "weight": 0.4,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "29",
        0
      ],
      "ipadapter": [
        "29",
        1
      ],
      "image": [
        "14",
        0
      ]
    },
    "class_type": "IPAdapterAdvanced",
    "_meta": {
      "title": "IPAdapter Advanced"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["17"]["inputs"]["text"] = description
    prompt["23"]["inputs"]["text"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["1"]["inputs"]["seed"] = formatted_number
    #prompt["19"]["inputs"]["image"] = f"S:/two_creative_l.png"
   # prompt["20"]["inputs"]["image"] = f"S:/two_creative_r.png"
   # prompt["14"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image1}"
    #prompt["10"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image2}"
    #prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    image_path = f'avatars/{avatar_image1}'
   #image_path2 = f'avatars/{avatar_image2}'
    mask_path1 = f"masks/two_creative_l.png"
    mask_path2 = f"masks/two_creative_r.png"
    
    response = upload_image(image_path,  avatar_image1, server_address)
    #response = upload_image(image_path2, avatar_image2, server_address) 
    response = upload_image(mask_path1,  "two_creative_l.png", server_address)
    response = upload_image(mask_path2,  "two_creative_r.png", server_address)  
    
    prompt["14"]["inputs"]["image"] = f"{avatar_image1}"  
   # prompt["10"]["inputs"]["image"] = f"{avatar_image2}" 
    prompt["19"]["inputs"]["image"] = f"two_creative_l.png"  
    prompt["20"]["inputs"]["image"] = f"two_creative_r.png"     
    
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
             filename = f"faceid_{int(time.time())}.png"

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
@to_thread
def  generate_face_id_together(avatar_image1, description):

    server_address = get_main_gpu_server()
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "1": {
    "inputs": {
      "seed": 81245034211546,
      "steps": 40,
      "cfg": 6,
      "sampler_name": "ddpm",
      "scheduler": "ddim_uniform",
      "denoise": 1,
      "model": [
        "26",
        0
      ],
      "positive": [
        "24",
        0
      ],
      "negative": [
        "5",
        0
      ],
      "latent_image": [
        "3",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "2": {
    "inputs": {
      "ckpt_name": "realisticVisionV60B1_v51VAE.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "3": {
    "inputs": {
      "width": 768,
      "height": 512,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "5": {
    "inputs": {
      "text": "",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "6": {
    "inputs": {
      "samples": [
        "1",
        0
      ],
      "vae": [
        "2",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "7": {
    "inputs": {
      "vae_name": "vae-ft-mse-840000-ema-pruned.ckpt"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "14": {
    "inputs": {
      "image": "avatar_1711730927_1.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "17": {
    "inputs": {
      "text": "A man depicted alongside a MILF (Mother I'd Like to Friend), both engaged in a friendly interaction or activity, surrounded by an atmosphere of warmth and familiarity, sense of camaraderie and mutual respect, inspired by the connection between individuals of different generations, friendly portrayal, welcoming atmosphere, trending in social circles and online communities.",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "18": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "6",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "19": {
    "inputs": {
      "image": "ComfyUI_temp_uppcb_00001_ - Copy (6).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "20": {
    "inputs": {
      "image": "ComfyUI_temp_yrupq_00002_ - Copy (6).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "22": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "23",
        0
      ],
      "mask": [
        "20",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "23": {
    "inputs": {
      "text": "A man depicted alongside a MILF (Mother I'd Like to Friend), both engaged in a friendly interaction or activity, surrounded by an atmosphere of warmth and familiarity, sense of camaraderie and mutual respect, inspired by the connection between individuals of different generations, friendly portrayal, welcoming atmosphere, trending in social circles and online communities.",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "24": {
    "inputs": {
      "conditioning_1": [
        "17",
        0
      ],
      "conditioning_2": [
        "22",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "25": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "2",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.8,
      "weight_type": "linear",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "25",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "14",
        0
      ],
      "attn_mask": [
        "19",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "28": {
    "inputs": {
      "stop_at_clip_layer": -1,
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPSetLastLayer",
    "_meta": {
      "title": "CLIP Set Last Layer"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["17"]["inputs"]["text"] = description
    prompt["23"]["inputs"]["text"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["1"]["inputs"]["seed"] = formatted_number
   # prompt["14"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image1}"
   # prompt["10"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image2}"



    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    image_path = f'avatars/{avatar_image1}'
    #image_path2 = f'avatars/{avatar_image2}'
    mask_path1 = f"masks/ComfyUI_temp_uppcb_00001_ - Copy.png"
    mask_path2 = f"masks/ComfyUI_temp_yrupq_00002_ - Copy.png"
    
    response = upload_image(image_path,  avatar_image1, server_address)
    #response = upload_image(image_path2, avatar_image2, server_address) 
    response = upload_image(mask_path1,  "ComfyUI_temp_uppcb_00001_ - Copy.png", server_address)
    response = upload_image(mask_path2,  "ComfyUI_temp_yrupq_00002_ - Copy.png", server_address)   
    
    prompt["14"]["inputs"]["image"] = f"{avatar_image1}"  
    #prompt["10"]["inputs"]["image"] = f"{avatar_image2}"
    prompt["19"]["inputs"]["image"] = f"ComfyUI_temp_uppcb_00001_ - Copy.png"  
    prompt["20"]["inputs"]["image"] = f"ComfyUI_temp_yrupq_00002_ - Copy.png"      
    
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
             filename = f"faceid_{int(time.time())}.png"

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

@to_thread
def  generate_face_id_unstable_two_unused(avatar_image1,avatar_image2, description):

    server_address = "81.166.162.13:12684"
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
                        break
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
    
    prompt_text = """
{
  "1": {
    "inputs": {
      "seed": 225736056973096,
      "steps": 40,
      "cfg": 3.3000000000000003,
      "sampler_name": "dpmpp_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "27",
        0
      ],
      "positive": [
        "32",
        0
      ],
      "negative": [
        "33",
        0
      ],
      "latent_image": [
        "3",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "2": {
    "inputs": {
      "ckpt_name": "sdxlUnstableDiffusers_v8HeavensWrathVAE.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "3": {
    "inputs": {
      "width": 1024,
      "height": 768,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "6": {
    "inputs": {
      "samples": [
        "1",
        0
      ],
      "vae": [
        "2",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "7": {
    "inputs": {
      "vae_name": "vae-ft-mse-840000-ema-pruned.ckpt"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "10": {
    "inputs": {
      "image": "avatar_1711489951.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "14": {
    "inputs": {
      "image": "avatar_1711614369.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "18": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "6",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "19": {
    "inputs": {
      "image": "two_creative_l.png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "20": {
    "inputs": {
      "image": "two_creative_r.png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "22": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "32",
        0
      ],
      "mask": [
        "19",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "24": {
    "inputs": {
      "conditioning_2": [
        "22",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "25": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "2",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "weight": 0.7,
      "weight_faceidv2": 1.8,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "25",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "14",
        0
      ],
      "attn_mask": [
        "19",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "27": {
    "inputs": {
      "weight": 0.7,
      "weight_faceidv2": 1.8,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "26",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "10",
        0
      ],
      "attn_mask": [
        "20",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "32": {
    "inputs": {
      "width": 2048,
      "height": 2048,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 2048,
      "target_height": 2048,
      "text_g": "two men, eccentric, mad scientists, laboratory setting, colorful potions, futuristic gadgets, whimsical, surreal, vivid colors, digital painting, hyperrealistic, 8K resolution, by Greg Rutkowski, trending on ArtStation",
      "text_l": "two men, eccentric, mad scientists, laboratory setting, colorful potions, futuristic gadgets, whimsical, surreal, vivid colors, digital painting, hyperrealistic, 8K resolution, by Greg Rutkowski, trending on ArtStation",
      "clip": [
        "35",
        0
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Positive Base"
    }
  },
  "33": {
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
        "35",
        0
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Negative Base"
    }
  },
  "35": {
    "inputs": {
      "stop_at_clip_layer": -1,
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPSetLastLayer",
    "_meta": {
      "title": "CLIP Set Last Layer"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["32"]["inputs"]["text_g"] = description
    prompt["32"]["inputs"]["text_l"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["1"]["inputs"]["seed"] = formatted_number
    #prompt["19"]["inputs"]["image"] = f"S:/two_creative_l.png"
   # prompt["20"]["inputs"]["image"] = f"S:/two_creative_r.png"
   # prompt["14"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image1}"
    #prompt["10"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image2}"
    #prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    image_path = f'avatars/{avatar_image1}'
    image_path2 = f'avatars/{avatar_image2}'
    mask_path1 = f"masks/two_creative_l.png"
    mask_path2 = f"masks/two_creative_r.png"
    
    response = upload_image(image_path,  avatar_image1, server_address)
    response = upload_image(image_path2, avatar_image2, server_address) 
    response = upload_image(mask_path1,  "two_creative_l.png", server_address)
    response = upload_image(mask_path2,  "two_creative_r.png", server_address)  
    
    prompt["14"]["inputs"]["image"] = f"{avatar_image1}"  
    prompt["10"]["inputs"]["image"] = f"{avatar_image2}" 
    prompt["19"]["inputs"]["image"] = f"two_creative_l.png"  
    prompt["20"]["inputs"]["image"] = f"two_creative_r.png"     
    
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
             filename = f"faceid_{int(time.time())}.png"

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

@to_thread
def  generate_face_id_unstable_two(avatar_image1,avatar_image2, description):

    server_address = "81.166.162.13:12684"
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
                        break
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
    
    prompt_text = """
{
  "1": {
    "inputs": {
      "seed": 900171224162926,
      "steps": 40,
      "cfg": 5,
      "sampler_name": "dpmpp_2m_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "40",
        0
      ],
      "positive": [
        "24",
        0
      ],
      "negative": [
        "33",
        0
      ],
      "latent_image": [
        "3",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "2": {
    "inputs": {
      "ckpt_name": "albedobaseXL_v21.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "3": {
    "inputs": {
      "width": 1024,
      "height": 768,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "6": {
    "inputs": {
      "samples": [
        "1",
        0
      ],
      "vae": [
        "2",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "7": {
    "inputs": {
      "vae_name": "vae-ft-mse-840000-ema-pruned.ckpt"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "10": {
    "inputs": {
      "image": "avatar_1711569779.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "14": {
    "inputs": {
      "image": "avatar_1711491706 (9).png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "18": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "6",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "19": {
    "inputs": {
      "image": "two_creative_r (2).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "20": {
    "inputs": {
      "image": "two_creative_l (2).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "22": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "32",
        0
      ],
      "mask": [
        "19",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "24": {
    "inputs": {
      "conditioning_1": [
        "35",
        0
      ],
      "conditioning_2": [
        "22",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "25": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "2",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "linear",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "25",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "14",
        0
      ],
      "attn_mask": [
        "19",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "27": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "linear",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "38",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "10",
        0
      ],
      "attn_mask": [
        "20",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "32": {
    "inputs": {
      "width": 2048,
      "height": 2048,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 2048,
      "target_height": 2048,
      "text_g": "A digital illustration of two men sharing coffee, sitting across each other at a rustic wooden table outdoors. The scene is set in a cozy, cobblestone-paved European alleyway, adorned with hanging green plants and warm, ambient lighting, capturing the essence of a serene morning. Art style: Norman Rockwell-inspired, with a touch of modern digital painting techniques. Art inspirations: ArtStation, Norman Rockwell. Camera: 35mm lens, medium shot, slightly overhead angle to include the alleyways charm. Render related information: detailed with a soft focus for a nostalgic feel, HDR lighting emphasizing the warm tones of the morning sun, and a high resolution of 4K to capture intricate textures of the coffee, facial expressions, and the rustic environment.",
      "text_l": "A digital illustration of two men sharing coffee, sitting across each other at a rustic wooden table outdoors. The scene is set in a cozy, cobblestone-paved European alleyway, adorned with hanging green plants and warm, ambient lighting, capturing the essence of a serene morning. Art style: Norman Rockwell-inspired, with a touch of modern digital painting techniques. Art inspirations: ArtStation, Norman Rockwell. Camera: 35mm lens, medium shot, slightly overhead angle to include the alleyways charm. Render related information: detailed with a soft focus for a nostalgic feel, HDR lighting emphasizing the warm tones of the morning sun, and a high resolution of 4K to capture intricate textures of the coffee, facial expressions, and the rustic environment.",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Positive Base"
    }
  },
  "33": {
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
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Negative Base"
    }
  },
  "35": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "32",
        0
      ],
      "mask": [
        "20",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "37": {
    "inputs": {
      "preset": "PLUS FACE (portraits)",
      "model": [
        "26",
        0
      ],
      "ipadapter": [
        "25",
        1
      ]
    },
    "class_type": "IPAdapterUnifiedLoader",
    "_meta": {
      "title": "IPAdapter Unified Loader"
    }
  },
  "38": {
    "inputs": {
      "weight": 0.4,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "37",
        0
      ],
      "ipadapter": [
        "37",
        1
      ],
      "image": [
        "14",
        0
      ]
    },
    "class_type": "IPAdapterAdvanced",
    "_meta": {
      "title": "IPAdapter Advanced"
    }
  },
  "39": {
    "inputs": {
      "preset": "PLUS FACE (portraits)",
      "model": [
        "27",
        0
      ],
      "ipadapter": [
        "25",
        1
      ]
    },
    "class_type": "IPAdapterUnifiedLoader",
    "_meta": {
      "title": "IPAdapter Unified Loader"
    }
  },
  "40": {
    "inputs": {
      "weight": 0.4,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "39",
        0
      ],
      "ipadapter": [
        "39",
        1
      ],
      "image": [
        "10",
        0
      ]
    },
    "class_type": "IPAdapterAdvanced",
    "_meta": {
      "title": "IPAdapter Advanced"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["32"]["inputs"]["text_g"] = description
    prompt["32"]["inputs"]["text_l"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["1"]["inputs"]["seed"] = formatted_number
    #prompt["19"]["inputs"]["image"] = f"S:/two_creative_l.png"
   # prompt["20"]["inputs"]["image"] = f"S:/two_creative_r.png"
   # prompt["14"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image1}"
    #prompt["10"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image2}"
    #prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    image_path = f'avatars/{avatar_image1}'
    image_path2 = f'avatars/{avatar_image2}'
    mask_path1 = f"masks/two_creative_l.png"
    mask_path2 = f"masks/two_creative_r.png"
    
    response = upload_image(image_path,  avatar_image1, server_address)
    response = upload_image(image_path2, avatar_image2, server_address) 
    response = upload_image(mask_path1,  "two_creative_l.png", server_address)
    response = upload_image(mask_path2,  "two_creative_r.png", server_address)  
    
    prompt["14"]["inputs"]["image"] = f"{avatar_image1}"  
    prompt["10"]["inputs"]["image"] = f"{avatar_image2}" 
    prompt["19"]["inputs"]["image"] = f"two_creative_l.png"  
    prompt["20"]["inputs"]["image"] = f"two_creative_r.png"     
    
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
             filename = f"faceid_{int(time.time())}.png"

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

@to_thread
def  generate_face_id_creative_three(avatar_image1,avatar_image2,avatar_image3, description):

    server_address = get_main_gpu_server() 
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "1": {
    "inputs": {
      "seed": 281980807495543,
      "steps": 6,
      "cfg": 2,
      "sampler_name": "dpmpp_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "35",
        0
      ],
      "positive": [
        "32",
        0
      ],
      "negative": [
        "33",
        0
      ],
      "latent_image": [
        "3",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "2": {
    "inputs": {
      "ckpt_name": "realvisxlV40_v40LightningBakedvae.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "3": {
    "inputs": {
      "width": 1024,
      "height": 512,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "6": {
    "inputs": {
      "samples": [
        "1",
        0
      ],
      "vae": [
        "2",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "7": {
    "inputs": {
      "vae_name": "vae-ft-mse-840000-ema-pruned.ckpt"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "10": {
    "inputs": {
      "image": "avatar_1711569779.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "14": {
    "inputs": {
      "image": "avatar_1711490113 (4).png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "18": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "6",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "19": {
    "inputs": {
      "image": "m2 (4).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "20": {
    "inputs": {
      "image": "l2 (3).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "22": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "32",
        0
      ],
      "mask": [
        "19",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "24": {
    "inputs": {
      "conditioning_2": [
        "22",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "25": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "2",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "25",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "14",
        0
      ],
      "attn_mask": [
        "19",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "27": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "26",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "10",
        0
      ],
      "attn_mask": [
        "20",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "32": {
    "inputs": {
      "width": 2048,
      "height": 2048,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 2048,
      "target_height": 2048,
      "text_g": "three man in creative attire celebrating at a wild Easter party, vibrant colors, festive atmosphere, art by Banksy and Salvador Dali, surrealistic, high detail, 8k resolution",
      "text_l": "three man in creative attire celebrating at a wild Easter party, vibrant colors, festive atmosphere, art by Banksy and Salvador Dali, surrealistic, high detail, 8k resolution",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Positive Base"
    }
  },
  "33": {
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
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Negative Base"
    }
  },
  "35": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "27",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "37",
        0
      ],
      "attn_mask": [
        "36",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "36": {
    "inputs": {
      "image": "r (1).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "37": {
    "inputs": {
      "image": "avatar_1711490047 (1).png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["32"]["inputs"]["text_g"] = description
    prompt["32"]["inputs"]["text_l"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["1"]["inputs"]["seed"] = formatted_number
   # prompt["19"]["inputs"]["image"] = f"S:/m22.png"
   # prompt["20"]["inputs"]["image"] = f"S:/l22.png"
   # prompt["36"]["inputs"]["image"] = f"S:/r22.png"
   # prompt["14"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image1}"
   # prompt["10"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image2}"
   # prompt["37"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image3}"
    #prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    image_path = f'avatars/{avatar_image1}'
    image_path2 = f'avatars/{avatar_image2}'
    image_path3 = f'avatars/{avatar_image3}'
    mask_path1 = f"masks/m22.png"
    mask_path2 = f"masks/l22.png"
    mask_path3 = f"masks/r22.png"
    
    response = upload_image(image_path,  avatar_image1, server_address)
    response = upload_image(image_path2, avatar_image2, server_address) 
    response = upload_image(image_path3, avatar_image3, server_address) 
    response = upload_image(mask_path1,  "m22.png", server_address)
    response = upload_image(mask_path2,  "l22.png", server_address)  
    response = upload_image(mask_path3,  "r22.png", server_address)  
    
    prompt["14"]["inputs"]["image"] = f"{avatar_image1}"  
    prompt["10"]["inputs"]["image"] = f"{avatar_image2}"
    prompt["37"]["inputs"]["image"] = f"{avatar_image3}" 
    prompt["19"]["inputs"]["image"] = f"m22.png"  
    prompt["20"]["inputs"]["image"] = f"l22.png"
    prompt["36"]["inputs"]["image"] = f"r22.png"  
    
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
             filename = f"faceid_{int(time.time())}.png"

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

@to_thread
def  generate_face_id_adalberto_three(avatar_image1,avatar_image2,avatar_image3, description):

    server_address = "81.166.162.13:12684" 
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "1": {
    "inputs": {
      "seed": 606241772965251,
      "steps": 60,
      "cfg": 7.5,
      "sampler_name": "dpmpp_2m_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "35",
        0
      ],
      "positive": [
        "32",
        0
      ],
      "negative": [
        "33",
        0
      ],
      "latent_image": [
        "3",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "2": {
    "inputs": {
      "ckpt_name": "albedobaseXL_v21.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "3": {
    "inputs": {
      "width": 1024,
      "height": 512,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "6": {
    "inputs": {
      "samples": [
        "1",
        0
      ],
      "vae": [
        "2",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "7": {
    "inputs": {
      "vae_name": "vae-ft-mse-840000-ema-pruned.ckpt"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "10": {
    "inputs": {
      "image": "avatar_1711489653.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "14": {
    "inputs": {
      "image": "avatar_1711491505.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "18": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "6",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "19": {
    "inputs": {
      "image": "l22 (1).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "20": {
    "inputs": {
      "image": "m22.png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "22": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "32",
        0
      ],
      "mask": [
        "19",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "24": {
    "inputs": {
      "conditioning_2": [
        "22",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "25": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "2",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "25",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "14",
        0
      ],
      "attn_mask": [
        "19",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "27": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "26",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "10",
        0
      ],
      "attn_mask": [
        "20",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "32": {
    "inputs": {
      "width": 2048,
      "height": 2048,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 2048,
      "target_height": 2048,
      "text_g": "two men and a girl throwing legos at people, playful, vibrant colors, dynamic composition, modern art style, trending on ArtStation, high quality image",
      "text_l": "two men and a girl throwing legos at people, playful, vibrant colors, dynamic composition, modern art style, trending on ArtStation, high quality image",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Positive Base"
    }
  },
  "33": {
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
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Negative Base"
    }
  },
  "35": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "27",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "37",
        0
      ],
      "attn_mask": [
        "36",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "36": {
    "inputs": {
      "image": "r22.png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "37": {
    "inputs": {
      "image": "avatar_1711714888_1.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["32"]["inputs"]["text_g"] = description
    prompt["32"]["inputs"]["text_l"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["1"]["inputs"]["seed"] = formatted_number
   # prompt["19"]["inputs"]["image"] = f"S:/m22.png"
   # prompt["20"]["inputs"]["image"] = f"S:/l22.png"
   # prompt["36"]["inputs"]["image"] = f"S:/r22.png"
   # prompt["14"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image1}"
   # prompt["10"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image2}"
   # prompt["37"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image3}"
    #prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    image_path = f'avatars/{avatar_image1}'
    image_path2 = f'avatars/{avatar_image2}'
    image_path3 = f'avatars/{avatar_image3}'
    mask_path1 = f"masks/m22.png"
    mask_path2 = f"masks/l22.png"
    mask_path3 = f"masks/r22.png"
    
    response = upload_image(image_path,  avatar_image1, server_address)
    response = upload_image(image_path2, avatar_image2, server_address) 
    response = upload_image(image_path3, avatar_image3, server_address) 
    response = upload_image(mask_path1,  "m22.png", server_address)
    response = upload_image(mask_path2,  "l22.png", server_address)  
    response = upload_image(mask_path3,  "r22.png", server_address)  
    
    prompt["14"]["inputs"]["image"] = f"{avatar_image1}"  
    prompt["10"]["inputs"]["image"] = f"{avatar_image2}"
    prompt["37"]["inputs"]["image"] = f"{avatar_image3}" 
    prompt["19"]["inputs"]["image"] = f"m22.png"  
    prompt["20"]["inputs"]["image"] = f"l22.png"
    prompt["36"]["inputs"]["image"] = f"r22.png"  
    
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
             filename = f"faceid_{int(time.time())}.png"

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
@to_thread
def  generate_face_id_creative_four(avatar_image1,avatar_image2,avatar_image3,avatar_image4, description):

    server_address = get_main_gpu_server() 
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "1": {
    "inputs": {
      "seed": 886924809193170,
      "steps": 6,
      "cfg": 2,
      "sampler_name": "dpmpp_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "38",
        0
      ],
      "positive": [
        "46",
        0
      ],
      "negative": [
        "33",
        0
      ],
      "latent_image": [
        "3",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "2": {
    "inputs": {
      "ckpt_name": "dreamshaperXL_v21TurboDPMSDE.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "3": {
    "inputs": {
      "width": 1344,
      "height": 768,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "6": {
    "inputs": {
      "samples": [
        "1",
        0
      ],
      "vae": [
        "2",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "7": {
    "inputs": {
      "vae_name": "vae-ft-mse-840000-ema-pruned.ckpt"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "10": {
    "inputs": {
      "image": "avatar_1711489837.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "14": {
    "inputs": {
      "image": "avatar_1711538353.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "18": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "6",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "19": {
    "inputs": {
      "image": "four2 (1).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "20": {
    "inputs": {
      "image": "four1 (1).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "22": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "32",
        0
      ],
      "mask": [
        "19",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "24": {
    "inputs": {
      "conditioning_1": [
        "41",
        0
      ],
      "conditioning_2": [
        "22",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "25": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "2",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "25",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "14",
        0
      ],
      "attn_mask": [
        "19",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "27": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "26",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "10",
        0
      ],
      "attn_mask": [
        "20",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "32": {
    "inputs": {
      "width": 2048,
      "height": 2048,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 2048,
      "target_height": 2048,
      "text_g": "4 four guys as drag queens",
      "text_l": "4 four guys as drag queens",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Positive Base"
    }
  },
  "33": {
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
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Negative Base"
    }
  },
  "35": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "27",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "37",
        0
      ],
      "attn_mask": [
        "36",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "36": {
    "inputs": {
      "image": "four3 (3).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "37": {
    "inputs": {
      "image": "avatar_1711569711.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "38": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "35",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "40",
        0
      ],
      "attn_mask": [
        "39",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "39": {
    "inputs": {
      "image": "four4 (4).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "40": {
    "inputs": {
      "image": "avatar_1711569675.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "41": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "32",
        0
      ],
      "mask": [
        "36",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "42": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "32",
        0
      ],
      "mask": [
        "20",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "44": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "32",
        0
      ],
      "mask": [
        "39",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "45": {
    "inputs": {
      "conditioning_1": [
        "24",
        0
      ],
      "conditioning_2": [
        "44",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "46": {
    "inputs": {
      "conditioning_1": [
        "42",
        0
      ],
      "conditioning_2": [
        "45",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["32"]["inputs"]["text_g"] = description
    prompt["32"]["inputs"]["text_l"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["1"]["inputs"]["seed"] = formatted_number
   # prompt["19"]["inputs"]["image"] = f"S:/m22.png"
   # prompt["20"]["inputs"]["image"] = f"S:/l22.png"
   # prompt["36"]["inputs"]["image"] = f"S:/r22.png"
   # prompt["14"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image1}"
   # prompt["10"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image2}"
   # prompt["37"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image3}"
    #prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    image_path = f'avatars/{avatar_image1}'
    image_path2 = f'avatars/{avatar_image2}'
    image_path3 = f'avatars/{avatar_image3}'
    image_path4 = f'avatars/{avatar_image4}'
    mask_path1 = f"masks/four1.png"
    mask_path2 = f"masks/four2.png"
    mask_path3 = f"masks/four3.png"
    mask_path4 = f"masks/four4.png"
    
    response = upload_image(image_path,  avatar_image1, server_address)
    response = upload_image(image_path2, avatar_image2, server_address) 
    response = upload_image(image_path3, avatar_image3, server_address) 
    response = upload_image(image_path4, avatar_image4, server_address)
    response = upload_image(mask_path1,  "four1.png", server_address)
    response = upload_image(mask_path2,  "four2.png", server_address)  
    response = upload_image(mask_path3,  "four3.png", server_address)
    response = upload_image(mask_path4,  "four4.png", server_address) 
    
    prompt["14"]["inputs"]["image"] = f"{avatar_image1}"  
    prompt["10"]["inputs"]["image"] = f"{avatar_image2}"
    prompt["37"]["inputs"]["image"] = f"{avatar_image3}" 
    prompt["40"]["inputs"]["image"] = f"{avatar_image4}" 
    prompt["20"]["inputs"]["image"] = f"four1.png"  
    prompt["19"]["inputs"]["image"] = f"four2.png"
    prompt["36"]["inputs"]["image"] = f"four3.png"  
    prompt["39"]["inputs"]["image"] = f"four4.png" 
    
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
             filename = f"faceid_{int(time.time())}.png"

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


@to_thread
def  generate_face_id_reals_four(avatar_image1,avatar_image2,avatar_image3,avatar_image4, description):

    server_address = "81.166.162.13:12684" 
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "1": {
    "inputs": {
      "seed": 80502671390773,
      "steps": 40,
      "cfg": 3.6,
      "sampler_name": "dpmpp_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "38",
        0
      ],
      "positive": [
        "46",
        0
      ],
      "negative": [
        "33",
        0
      ],
      "latent_image": [
        "3",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "2": {
    "inputs": {
      "ckpt_name": "realisticStockPhoto_v20.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "3": {
    "inputs": {
      "width": 1344,
      "height": 768,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "6": {
    "inputs": {
      "samples": [
        "1",
        0
      ],
      "vae": [
        "2",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "7": {
    "inputs": {
      "vae_name": "vae-ft-mse-840000-ema-pruned.ckpt"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "10": {
    "inputs": {
      "image": "avatar_1711489809.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "14": {
    "inputs": {
      "image": "avatar_1711491706.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "18": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "6",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "19": {
    "inputs": {
      "image": "four2.png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "20": {
    "inputs": {
      "image": "four1.png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "22": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "32",
        0
      ],
      "mask": [
        "19",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "24": {
    "inputs": {
      "conditioning_1": [
        "41",
        0
      ],
      "conditioning_2": [
        "22",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "25": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "2",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "weight": 1,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "25",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "14",
        0
      ],
      "attn_mask": [
        "19",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "27": {
    "inputs": {
      "weight": 1,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "26",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "10",
        0
      ],
      "attn_mask": [
        "20",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "32": {
    "inputs": {
      "width": 2048,
      "height": 2048,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 2048,
      "target_height": 2048,
      "text_g": "4 four guys as drag queens",
      "text_l": "4 four guys as drag queens",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Positive Base"
    }
  },
  "33": {
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
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Negative Base"
    }
  },
  "35": {
    "inputs": {
      "weight": 1,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "27",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "37",
        0
      ],
      "attn_mask": [
        "36",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "36": {
    "inputs": {
      "image": "four3.png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "37": {
    "inputs": {
      "image": "avatar_1711569711.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "38": {
    "inputs": {
      "weight": 1,
      "weight_faceidv2": 1.7,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "35",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "40",
        0
      ],
      "attn_mask": [
        "39",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "39": {
    "inputs": {
      "image": "four4.png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "40": {
    "inputs": {
      "image": "avatar_1711574392_1.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "41": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "32",
        0
      ],
      "mask": [
        "36",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "42": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "32",
        0
      ],
      "mask": [
        "20",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "44": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "32",
        0
      ],
      "mask": [
        "39",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "45": {
    "inputs": {
      "conditioning_1": [
        "24",
        0
      ],
      "conditioning_2": [
        "44",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "46": {
    "inputs": {
      "conditioning_1": [
        "42",
        0
      ],
      "conditioning_2": [
        "45",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["32"]["inputs"]["text_g"] = description
    prompt["32"]["inputs"]["text_l"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["1"]["inputs"]["seed"] = formatted_number
   # prompt["19"]["inputs"]["image"] = f"S:/m22.png"
   # prompt["20"]["inputs"]["image"] = f"S:/l22.png"
   # prompt["36"]["inputs"]["image"] = f"S:/r22.png"
   # prompt["14"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image1}"
   # prompt["10"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image2}"
   # prompt["37"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image3}"
    #prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    image_path = f'avatars/{avatar_image1}'
    image_path2 = f'avatars/{avatar_image2}'
    image_path3 = f'avatars/{avatar_image3}'
    image_path4 = f'avatars/{avatar_image4}'
    mask_path1 = f"masks/four1.png"
    mask_path2 = f"masks/four2.png"
    mask_path3 = f"masks/four3.png"
    mask_path4 = f"masks/four4.png"
    
    response = upload_image(image_path,  avatar_image1, server_address)
    response = upload_image(image_path2, avatar_image2, server_address) 
    response = upload_image(image_path3, avatar_image3, server_address) 
    response = upload_image(image_path4, avatar_image4, server_address)
    response = upload_image(mask_path1,  "four1.png", server_address)
    response = upload_image(mask_path2,  "four2.png", server_address)  
    response = upload_image(mask_path3,  "four3.png", server_address)
    response = upload_image(mask_path4,  "four4.png", server_address) 
    
    prompt["14"]["inputs"]["image"] = f"{avatar_image1}"  
    prompt["10"]["inputs"]["image"] = f"{avatar_image2}"
    prompt["37"]["inputs"]["image"] = f"{avatar_image3}" 
    prompt["40"]["inputs"]["image"] = f"{avatar_image4}" 
    prompt["20"]["inputs"]["image"] = f"four1.png"  
    prompt["19"]["inputs"]["image"] = f"four2.png"
    prompt["36"]["inputs"]["image"] = f"four3.png"  
    prompt["39"]["inputs"]["image"] = f"four4.png" 
    
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
             filename = f"faceid_{int(time.time())}.png"

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

@to_thread
def  generate_face_id__together_creative_two(avatar_image1,avatar_image2, description):

    server_address = get_main_gpu_server() 
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "1": {
    "inputs": {
      "seed": 80722034304666,
      "steps": 6,
      "cfg": 2,
      "sampler_name": "dpmpp_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "31",
        0
      ],
      "positive": [
        "34",
        0
      ],
      "negative": [
        "5",
        0
      ],
      "latent_image": [
        "3",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "2": {
    "inputs": {
      "ckpt_name": "dreamshaperXL_v21TurboDPMSDE.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "3": {
    "inputs": {
      "width": 1024,
      "height": 768,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "5": {
    "inputs": {
      "text": "",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "6": {
    "inputs": {
      "samples": [
        "1",
        0
      ],
      "vae": [
        "2",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "7": {
    "inputs": {
      "vae_name": "vae-ft-mse-840000-ema-pruned.ckpt"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "14": {
    "inputs": {
      "image": "avatar_1711490022 (1).png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "17": {
    "inputs": {
      "text": "two men  with   anime girl",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "18": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "6",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "19": {
    "inputs": {
      "image": "m (4).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "20": {
    "inputs": {
      "image": "r (5).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "22": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "23",
        0
      ],
      "mask": [
        "20",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "23": {
    "inputs": {
      "text": "two men  with   anime girl",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "24": {
    "inputs": {
      "conditioning_1": [
        "22",
        0
      ],
      "conditioning_2": [
        "32",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "25": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "2",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.8,
      "weight_type": "linear",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "25",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "14",
        0
      ],
      "attn_mask": [
        "19",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "28": {
    "inputs": {
      "stop_at_clip_layer": -1
    },
    "class_type": "CLIPSetLastLayer",
    "_meta": {
      "title": "CLIP Set Last Layer"
    }
  },
  "29": {
    "inputs": {
      "image": "avatar_1711569797.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "30": {
    "inputs": {
      "image": "l (5).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "31": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.8,
      "weight_type": "linear",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "26",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "29",
        0
      ],
      "attn_mask": [
        "30",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "32": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "33",
        0
      ],
      "mask": [
        "30",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "33": {
    "inputs": {
      "text": "two men  with   anime girl",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "34": {
    "inputs": {
      "conditioning_1": [
        "17",
        0
      ],
      "conditioning_2": [
        "24",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["17"]["inputs"]["text"] = description
    prompt["23"]["inputs"]["text"] = description
    prompt["33"]["inputs"]["text"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["1"]["inputs"]["seed"] = formatted_number
   # prompt["19"]["inputs"]["image"] = f"S:/m22.png"
   # prompt["20"]["inputs"]["image"] = f"S:/l22.png"
   # prompt["36"]["inputs"]["image"] = f"S:/r22.png"
   # prompt["14"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image1}"
   # prompt["10"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image2}"
   # prompt["37"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image3}"
    #prompt["4"]["inputs"]["ckpt_name"] = model


    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    image_path = f'avatars/{avatar_image1}'
    image_path2 = f'avatars/{avatar_image2}'
    #image_path3 = f'avatars/{avatar_image3}'
    mask_path1 = f"masks/m22.png"
    mask_path2 = f"masks/l22.png"
    mask_path3 = f"masks/r22.png"
    
    response = upload_image(image_path,  avatar_image1, server_address)
    response = upload_image(image_path2, avatar_image2, server_address) 
    #response = upload_image(image_path3, avatar_image3, server_address) 
    response = upload_image(mask_path1,  "m22.png", server_address)
    response = upload_image(mask_path2,  "l22.png", server_address)  
    response = upload_image(mask_path3,  "r22.png", server_address)  
    
    prompt["14"]["inputs"]["image"] = f"{avatar_image1}"  
    prompt["29"]["inputs"]["image"] = f"{avatar_image2}"
    #prompt["37"]["inputs"]["image"] = f"{avatar_image3}" 
    prompt["30"]["inputs"]["image"] = f"l22.png"  
    prompt["19"]["inputs"]["image"] = f"r22.png"
    prompt["20"]["inputs"]["image"] = f"m22.png" 
    
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
             filename = f"faceid_{int(time.time())}.png"

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
@to_thread
def  generate_face_id_two_people(avatar_image1,avatar_image2, description):

    server_address = get_main_gpu_server()
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "2": {
    "inputs": {
      "ckpt_name": "realisticVisionV60B1_v51VAE.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "3": {
    "inputs": {
      "width": 768,
      "height": 512,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "6": {
    "inputs": {
      "samples": [
        "28",
        0
      ],
      "vae": [
        "2",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "7": {
    "inputs": {
      "vae_name": "vae-ft-mse-840000-ema-pruned.ckpt"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "10": {
    "inputs": {
      "image": "avatar_1711569779.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "14": {
    "inputs": {
      "image": "avatar_1711490113 (4).png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "18": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "6",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "19": {
    "inputs": {
      "image": "ComfyUI_temp_uppcb_00001_ - Copy.png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "20": {
    "inputs": {
      "image": "ComfyUI_temp_yrupq_00002_ - Copy.png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "22": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "30",
        0
      ],
      "mask": [
        "19",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "24": {
    "inputs": {
      "conditioning_1": [
        "33",
        0
      ],
      "conditioning_2": [
        "22",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "25": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "2",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.8,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "25",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "14",
        0
      ],
      "attn_mask": [
        "19",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "27": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.8,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "26",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "10",
        0
      ],
      "attn_mask": [
        "20",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "28": {
    "inputs": {
      "seed": 718988425182440,
      "steps": 50,
      "cfg": 10,
      "sampler_name": "dpmpp_2m",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "27",
        0
      ],
      "positive": [
        "34",
        0
      ],
      "negative": [
        "31",
        0
      ],
      "latent_image": [
        "3",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "29": {
    "inputs": {
      "ella_model": "ella-sd1.5-tsc-t5xl.safetensors",
      "t5_model": "flan-t5-xl"
    },
    "class_type": "LoadElla",
    "_meta": {
      "title": "Load ELLA Model"
    }
  },
  "30": {
    "inputs": {
      "text": "two men in a futuristic digimon world, highly detailed, cinematic view, vivid colors",
      "sigma": [
        "32",
        0
      ],
      "ella": [
        "29",
        0
      ]
    },
    "class_type": "ELLATextEncode",
    "_meta": {
      "title": "ELLA Text Encode (Prompt)"
    }
  },
  "31": {
    "inputs": {
      "text": "embedding:BadDream, embedding:FastNegativeV2.pt",
      "sigma": [
        "32",
        0
      ],
      "ella": [
        "29",
        0
      ]
    },
    "class_type": "ELLATextEncode",
    "_meta": {
      "title": "ELLA Text Encode (Prompt)"
    }
  },
  "32": {
    "inputs": {
      "sampler_name": "dpmpp_2m",
      "scheduler": "karras",
      "steps": 50,
      "start_at_step": 0,
      "end_at_step": 50,
      "model": [
        "2",
        0
      ]
    },
    "class_type": "GetSigma",
    "_meta": {
      "title": "Get Sigma (BNK)"
    }
  },
  "33": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "30",
        0
      ],
      "mask": [
        "20",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "34": {
    "inputs": {
      "conditioning_1": [
        "30",
        0
      ],
      "conditioning_2": [
        "24",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["30"]["inputs"]["text"] = description
    #prompt["23"]["inputs"]["text"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["28"]["inputs"]["seed"] = formatted_number
   # prompt["14"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image1}"
   # prompt["10"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image2}"



    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    image_path = f'avatars/{avatar_image1}'
    image_path2 = f'avatars/{avatar_image2}'
    mask_path1 = f"masks/ComfyUI_temp_uppcb_00001_ - Copy.png"
    mask_path2 = f"masks/ComfyUI_temp_yrupq_00002_ - Copy.png"
    
    response = upload_image(image_path,  avatar_image1, server_address)
    response = upload_image(image_path2, avatar_image2, server_address) 
    response = upload_image(mask_path1,  "ComfyUI_temp_uppcb_00001_ - Copy.png", server_address)
    response = upload_image(mask_path2,  "ComfyUI_temp_yrupq_00002_ - Copy.png", server_address)   
    
    prompt["14"]["inputs"]["image"] = f"{avatar_image1}"  
    prompt["10"]["inputs"]["image"] = f"{avatar_image2}"
    prompt["19"]["inputs"]["image"] = f"ComfyUI_temp_uppcb_00001_ - Copy.png"  
    prompt["20"]["inputs"]["image"] = f"ComfyUI_temp_yrupq_00002_ - Copy.png"      
    
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
             filename = f"faceid_{int(time.time())}.png"

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


@to_thread
def  generate_face_id_three_people(avatar_image1,avatar_image2,avatar_image3, description):

    server_address = get_main_gpu_server()
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "2": {
    "inputs": {
      "ckpt_name": "realisticVisionV60B1_v51VAE.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "3": {
    "inputs": {
      "width": 1024,
      "height": 512,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "6": {
    "inputs": {
      "samples": [
        "28",
        0
      ],
      "vae": [
        "2",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "7": {
    "inputs": {
      "vae_name": "vae-ft-mse-840000-ema-pruned.ckpt"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "10": {
    "inputs": {
      "image": "avatar_1711569779.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "14": {
    "inputs": {
      "image": "avatar_1711490113 (4).png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "18": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "6",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "19": {
    "inputs": {
      "image": "m22 (7).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "20": {
    "inputs": {
      "image": "l22 (8).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "22": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "30",
        0
      ],
      "mask": [
        "19",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "24": {
    "inputs": {
      "conditioning_1": [
        "33",
        0
      ],
      "conditioning_2": [
        "22",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "25": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "2",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "weight": 0.9,
      "weight_faceidv2": 1.8,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "25",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "14",
        0
      ],
      "attn_mask": [
        "19",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "27": {
    "inputs": {
      "weight": 0.9,
      "weight_faceidv2": 1.8,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "26",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "10",
        0
      ],
      "attn_mask": [
        "20",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "28": {
    "inputs": {
      "seed": 74200006549893,
      "steps": 50,
      "cfg": 10,
      "sampler_name": "dpmpp_2m",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "40",
        0
      ],
      "positive": [
        "34",
        0
      ],
      "negative": [
        "31",
        0
      ],
      "latent_image": [
        "3",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "29": {
    "inputs": {
      "ella_model": "ella-sd1.5-tsc-t5xl.safetensors",
      "t5_model": "flan-t5-xl"
    },
    "class_type": "LoadElla",
    "_meta": {
      "title": "Load ELLA Model"
    }
  },
  "30": {
    "inputs": {
      "text": "Three men standing in the vast desert landscape, rugged, adventurous, majestic, golden hour lighting, cinematic view, high resolution, detailed image",
      "sigma": [
        "32",
        0
      ],
      "ella": [
        "29",
        0
      ]
    },
    "class_type": "ELLATextEncode",
    "_meta": {
      "title": "ELLA Text Encode (Prompt)"
    }
  },
  "31": {
    "inputs": {
      "text": "embedding:BadDream, embedding:FastNegativeV2.pt",
      "sigma": [
        "32",
        0
      ],
      "ella": [
        "29",
        0
      ]
    },
    "class_type": "ELLATextEncode",
    "_meta": {
      "title": "ELLA Text Encode (Prompt)"
    }
  },
  "32": {
    "inputs": {
      "sampler_name": "dpmpp_2m",
      "scheduler": "karras",
      "steps": 50,
      "start_at_step": 0,
      "end_at_step": 50,
      "model": [
        "2",
        0
      ]
    },
    "class_type": "GetSigma",
    "_meta": {
      "title": "Get Sigma (BNK)"
    }
  },
  "33": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "30",
        0
      ],
      "mask": [
        "20",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "34": {
    "inputs": {
      "conditioning_1": [
        "30",
        0
      ],
      "conditioning_2": [
        "42",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "38": {
    "inputs": {
      "image": "avatar_1711516548.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "39": {
    "inputs": {
      "image": "r22 (8).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "40": {
    "inputs": {
      "weight": 0.9,
      "weight_faceidv2": 1.8,
      "weight_type": "ease in-out",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "27",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "38",
        0
      ],
      "attn_mask": [
        "39",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "41": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "30",
        0
      ],
      "mask": [
        "39",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "42": {
    "inputs": {
      "conditioning_1": [
        "41",
        0
      ],
      "conditioning_2": [
        "24",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["30"]["inputs"]["text"] = description
    #prompt["23"]["inputs"]["text"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["28"]["inputs"]["seed"] = formatted_number
    #prompt["14"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image1}"
   # prompt["10"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image2}"
   # prompt["30"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image3}"



    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    image_path = f'avatars/{avatar_image1}'
    image_path2 = f'avatars/{avatar_image2}'
    image_path3 = f'avatars/{avatar_image3}'
    mask_path1 = f"masks/m22.png"
    mask_path2 = f"masks/l22.png"
    mask_path3 = f"masks/r22.png"
    
    response = upload_image(image_path,  avatar_image1, server_address)
    response = upload_image(image_path2, avatar_image2, server_address) 
    response = upload_image(image_path3, avatar_image3, server_address) 
    #response = upload_image(mask_path1,  "m22.png",    server_address)
    #response = upload_image(mask_path2,  "l22.png",    server_address)  
    #response = upload_image(mask_path3,  "r22.png",    server_address)  
    
    prompt["14"]["inputs"]["image"] = f"{avatar_image1}"  
    prompt["10"]["inputs"]["image"] = f"{avatar_image2}"
    prompt["38"]["inputs"]["image"] = f"{avatar_image3}" 
    prompt["19"]["inputs"]["image"] = f"m22.png"  
    prompt["20"]["inputs"]["image"] = f"l22.png"
    prompt["39"]["inputs"]["image"] = f"r22.png"      
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
             filename = f"faceid_{int(time.time())}.png"

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

@to_thread
def  generate_face_id__together_two(avatar_image1,avatar_image2, description):

    server_address = get_main_gpu_server()
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

    def upload_image(input_path, name, server_address, image_type="input", overwrite=True):
      with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
          fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
          }
        )

        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
          return response.read()

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
    
    prompt_text = """
{
  "1": {
    "inputs": {
      "seed": 80722034304666,
      "steps": 40,
      "cfg": 6,
      "sampler_name": "ddim",
      "scheduler": "ddim_uniform",
      "denoise": 1,
      "model": [
        "31",
        0
      ],
      "positive": [
        "34",
        0
      ],
      "negative": [
        "5",
        0
      ],
      "latent_image": [
        "3",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "2": {
    "inputs": {
      "ckpt_name": "realisticVisionV60B1_v51VAE.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "3": {
    "inputs": {
      "width": 768,
      "height": 512,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "5": {
    "inputs": {
      "text": "embedding:BadDream, embedding:FastNegativeV2, ",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "6": {
    "inputs": {
      "samples": [
        "1",
        0
      ],
      "vae": [
        "2",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "7": {
    "inputs": {
      "vae_name": "vae-ft-mse-840000-ema-pruned.ckpt"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "14": {
    "inputs": {
      "image": "avatar_1711490022 (1).png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "17": {
    "inputs": {
      "text": "two men  with   anime girl",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "18": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "6",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "19": {
    "inputs": {
      "image": "m (4).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "20": {
    "inputs": {
      "image": "r (5).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "22": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "23",
        0
      ],
      "mask": [
        "20",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "23": {
    "inputs": {
      "text": "two men  with   anime girl",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "24": {
    "inputs": {
      "conditioning_1": [
        "22",
        0
      ],
      "conditioning_2": [
        "32",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  },
  "25": {
    "inputs": {
      "preset": "FACEID PLUS V2",
      "lora_strength": 0.6,
      "provider": "CPU",
      "model": [
        "2",
        0
      ]
    },
    "class_type": "IPAdapterUnifiedLoaderFaceID",
    "_meta": {
      "title": "IPAdapter Unified Loader FaceID"
    }
  },
  "26": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.8,
      "weight_type": "linear",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "25",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "14",
        0
      ],
      "attn_mask": [
        "19",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "28": {
    "inputs": {
      "stop_at_clip_layer": -1
    },
    "class_type": "CLIPSetLastLayer",
    "_meta": {
      "title": "CLIP Set Last Layer"
    }
  },
  "29": {
    "inputs": {
      "image": "avatar_1711569797.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "30": {
    "inputs": {
      "image": "l (5).png",
      "channel": "red",
      "upload": "image"
    },
    "class_type": "LoadImageMask",
    "_meta": {
      "title": "Load Image (as Mask)"
    }
  },
  "31": {
    "inputs": {
      "weight": 0.8,
      "weight_faceidv2": 1.8,
      "weight_type": "linear",
      "combine_embeds": "concat",
      "start_at": 0,
      "end_at": 1,
      "embeds_scaling": "V only",
      "model": [
        "26",
        0
      ],
      "ipadapter": [
        "25",
        1
      ],
      "image": [
        "29",
        0
      ],
      "attn_mask": [
        "30",
        0
      ]
    },
    "class_type": "IPAdapterFaceID",
    "_meta": {
      "title": "IPAdapter FaceID"
    }
  },
  "32": {
    "inputs": {
      "strength": 1,
      "set_cond_area": "default",
      "conditioning": [
        "33",
        0
      ],
      "mask": [
        "30",
        0
      ]
    },
    "class_type": "ConditioningSetMask",
    "_meta": {
      "title": "Conditioning (Set Mask)"
    }
  },
  "33": {
    "inputs": {
      "text": "two men  with   anime girl",
      "clip": [
        "2",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "34": {
    "inputs": {
      "conditioning_1": [
        "17",
        0
      ],
      "conditioning_2": [
        "24",
        0
      ]
    },
    "class_type": "ConditioningCombine",
    "_meta": {
      "title": "Conditioning (Combine)"
    }
  }
}
    """

  #  def queue_prompt(prompt):
  #      p = {"prompt": prompt}
  #      data = json.dumps(p).encode('utf-8')
  #      req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
 #       request.urlopen(req)


    filename = f"faceid_{int(time.time())}.png"
    filename_h = f"ProjectAy/{filename}"
    filename_l = f"ProjectAy/echo_{int(time.time())}_low_res"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    #upload_image("F:/3d/1.png","1",server_address, image_type="input", overwrite=True)

    #prompt["23"]["inputs"]["image"] = imagee
    

    prompt = json.loads(prompt_text)
    prompt["17"]["inputs"]["text"] = description
    prompt["23"]["inputs"]["text"] = description
    prompt["33"]["inputs"]["text"] = description
    #prompt["23"]["inputs"]["text"] = description
    #prompt["32"]["inputs"]["filename_prefix"] = filename_h
    prompt["1"]["inputs"]["seed"] = formatted_number
    #prompt["14"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image1}"
   # prompt["10"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image2}"
   # prompt["30"]["inputs"]["image"] = f"C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/avatars/{avatar_image3}"



    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    image_path = f'avatars/{avatar_image1}'
    image_path2 = f'avatars/{avatar_image2}'
    #image_path3 = f'avatars/{avatar_image3}'
    mask_path1 = f"masks/m22.png"
    mask_path2 = f"masks/l22.png"
    mask_path3 = f"masks/r22.png"
    
    response = upload_image(image_path,  avatar_image1, server_address)
    response = upload_image(image_path2, avatar_image2, server_address) 
    #response = upload_image(image_path3, avatar_image3, server_address) 
    #response = upload_image(mask_path1,  "m22.png",    server_address)
    #response = upload_image(mask_path2,  "l22.png",    server_address)  
    #response = upload_image(mask_path3,  "r22.png",    server_address)  
    
    prompt["14"]["inputs"]["image"] = f"{avatar_image1}"  
    prompt["29"]["inputs"]["image"] = f"{avatar_image2}"
    #prompt["30"]["inputs"]["image"] = f"{avatar_image3}" 
    prompt["30"]["inputs"]["image"] = f"l22.png"  
    prompt["19"]["inputs"]["image"] = f"r22.png"
    prompt["20"]["inputs"]["image"] = f"m22.png"     
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
             filename = f"faceid_{int(time.time())}.png"

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
      "steps": 8,
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



    return files, filename, formatted_number
    #wait_msg.delete()
    #wait_gif.delete()
    #new_message =   message.channel.send(files=files)

@to_thread
def  generate_image_lightning(V4, promptt, neg_prompt,w, h, keyw, model, three, vae, lora, support, steps):

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
      "ckpt_name": "aetherverseLightning_v10.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "6": {
    "inputs": {
      "text": [
        "50",
        0
      ],
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "7": {
    "inputs": {
      "text": "",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "18": {
    "inputs": {
      "samples": [
        "63",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "30": {
    "inputs": {
      "resolution": "Square (1024x1024)",
      "aspect": "Horizontal"
    },
    "class_type": "SDXLResolutionPresets",
    "_meta": {
      "title": "SDXL Resolution Presets (ws)"
    }
  },
  "48": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "18",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "50": {
    "inputs": {
      "wildcard_text": "",
      "populated_text": "monkey wearing paper bag as mask pointing gun",
      "mode": false,
      "seed": 746913003801215,
      "Select to add Wildcard": "Select the Wildcard to add to the text"
    },
    "class_type": "ImpactWildcardProcessor",
    "_meta": {
      "title": "ImpactWildcardProcessor"
    }
  },
  "52": {
    "inputs": {
      "b1": 1.02,
      "b2": 1.12,
      "s1": 0.9,
      "s2": 0.75,
      "model": [
        "4",
        0
      ]
    },
    "class_type": "FreeU_V2",
    "_meta": {
      "title": "FreeU_V2"
    }
  },
  "62": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "63": {
    "inputs": {
      "seed": 645967361688314,
      "steps": 8,
      "cfg": 2.5,
      "sampler_name": "dpmpp_sde",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "52",
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
        "62",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "70": {
    "inputs": {
      "upscale_method": "bicubic",
      "scale_by": 1.25,
      "samples": [
        "63",
        0
      ]
    },
    "class_type": "LatentUpscaleBy",
    "_meta": {
      "title": "Upscale Latent By"
    }
  },
  "71": {
    "inputs": {
      "seed": 868016408951753,
      "steps": 10,
      "cfg": 1.8,
      "sampler_name": "dpmpp_sde",
      "scheduler": "karras",
      "denoise": 0.5700000000000001,
      "model": [
        "74",
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
        "70",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "72": {
    "inputs": {
      "samples": [
        "71",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "73": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "72",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "74": {
    "inputs": {
      "sharpness_multiplier": 1,
      "sharpness_method": "anisotropic",
      "tonemap_multiplier": 0,
      "tonemap_method": "reinhard",
      "tonemap_percentile": 100,
      "contrast_multiplier": 0,
      "combat_method": "subtract",
      "combat_cfg_drift": 0,
      "rescale_cfg_phi": 0,
      "extra_noise_type": "gaussian",
      "extra_noise_method": "add",
      "extra_noise_multiplier": 0.8,
      "extra_noise_lowpass": 100,
      "divisive_norm_size": 127,
      "divisive_norm_multiplier": 0,
      "spectral_mod_mode": "hard_clamp",
      "spectral_mod_percentile": 5,
      "spectral_mod_multiplier": 0,
      "affect_uncond": "None",
      "dyn_cfg_augmentation": "None",
      "seed": 705856465856991,
      "model": [
        "52",
        0
      ]
    },
    "class_type": "Latent Diffusion Mega Modifier",
    "_meta": {
      "title": "Latent Diffusion Mega Modifier"
    }
  },
  "76": {
    "inputs": {
      "guide_size": 256,
      "guide_size_for": true,
      "max_size": 768,
      "seed": 789817620541772,
      "steps": 15,
      "cfg": 1,
      "sampler_name": "dpmpp_sde",
      "scheduler": "karras",
      "denoise": 0.5700000000000001,
      "feather": 5,
      "noise_mask": true,
      "force_inpaint": true,
      "bbox_threshold": 0.67,
      "bbox_dilation": 15,
      "bbox_crop_factor": 3,
      "sam_detection_hint": "center-1",
      "sam_dilation": 15,
      "sam_threshold": 0.93,
      "sam_bbox_expansion": 15,
      "sam_mask_hint_threshold": 0.7,
      "sam_mask_hint_use_negative": "False",
      "drop_size": 10,
      "wildcard": "",
      "cycle": 1,
      "inpaint_model": false,
      "noise_mask_feather": 2,
      "image": [
        "72",
        0
      ],
      "model": [
        "74",
        0
      ],
      "clip": [
        "4",
        1
      ],
      "vae": [
        "4",
        2
      ],
      "positive": [
        "6",
        0
      ],
      "negative": [
        "7",
        0
      ],
      "bbox_detector": [
        "78",
        0
      ],
      "sam_model_opt": [
        "79",
        0
      ]
    },
    "class_type": "FaceDetailer",
    "_meta": {
      "title": "FaceDetailer"
    }
  },
  "78": {
    "inputs": {
      "model_name": "bbox/face_yolov8m.pt"
    },
    "class_type": "UltralyticsDetectorProvider",
    "_meta": {
      "title": "UltralyticsDetectorProvider"
    }
  },
  "79": {
    "inputs": {
      "model_name": "sam_vit_b_01ec64.pth",
      "device_mode": "AUTO"
    },
    "class_type": "SAMLoader",
    "_meta": {
      "title": "SAMLoader (Impact)"
    }
  },
  "81": {
    "inputs": {
      "images": [
        "76",
        2
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "82": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "76",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
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
    filename_original = f"ProjectAy/{filename}"
    filename_upscale = f"ProjectAy/echo_{int(time.time())}_low_res"
    filename_face_swap = f"ProjectAy/echo_{int(time.time())}_face_swap"
    random_14_digit_number = random.randint(10**13, (10**14)-1)
    formatted_number = "{:014d}".format(random_14_digit_number)

    prompt = json.loads(prompt_text)


    #set the text prompt for our positive CLIPTextEncode 
    prompt["50"]["inputs"]["populated_text"] = promptt
   # prompt["75"]["inputs"]["text_l"] = support
   # prompt["120"]["inputs"]["text"] = promptt
   # prompt["58"]["inputs"]["text"] = neg_prompt
    #prompt["82"]["inputs"]["text_l"] = neg_prompt
   # prompt["81"]["inputs"]["text"] = neg_prompt
    prompt["48"]["inputs"]["filename_prefix"] = filename_upscale
    prompt["73"]["inputs"]["filename_prefix"] = filename_original
    prompt["82"]["inputs"]["filename_prefix"] = filename_face_swap
    #prompt["201"]["inputs"]["filename_prefix"] = filename_l
    prompt["50"]["inputs"]["seed"] = formatted_number 
    prompt["63"]["inputs"]["seed"] = formatted_number
    prompt["71"]["inputs"]["seed"] = formatted_number 
    prompt["76"]["inputs"]["seed"] = formatted_number 
    #prompt["22"]["inputs"]["noise_seed"] = formatted_number
    #prompt["216"]["inputs"]["noise_seed"] = formatted_number 
    prompt["62"]["inputs"]["width"] = w
    prompt["62"]["inputs"]["height"] = h
    prompt["63"]["inputs"]["steps"] = steps
    prompt["4"]["inputs"]["ckpt_name"] = model
    if three:
        prompt["62"]["inputs"]["batch_size"] = 3
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



    #with open(f"S:/comfy/ComfyUI_windows_portable/ComfyUI/output/{filename_face_swap}", "wb") as f:              
    #        f.write(image_data)
# Add the image file to the list
    i = 1
    if three:
        while i < 4:
                file = discord.File(f"S:/comfy/ComfyUI_windows_portable/ComfyUI/output/{filename_face_swap}_0000{i}_.png")
                files.append(file)
                i = i+1
    else:

        file = discord.File(f"S:/comfy/ComfyUI_windows_portable/ComfyUI/output/{filename_face_swap}_00001_.png")
        files.append(file)

  #  i=0
  #  for node_id in images:     
  #       for image_data in images[node_id]:
  #           i=i+1
  #           filename = f"echo_{i}_{int(time.time())}.png"
  #           if keyw.lower() == "echoais":
  #              filename = f"SPOILER_{filename}"
             #from PIL import Image
             #import io
            # Save the image to "generated" directory
        #     if i == 4 or i == 5 or i == 6:
  #           if three:
  ##                   with open(f"generatedNewAge/{filename}", "wb") as f:              
   #                          f.write(image_data)
                # Add the image file to the list
   #                  file = discord.File(f"generatedNewAge/{filename}")
   #                  files.append(file)
   #          else:
   #              if i == 3:
   #                  with open(f"generatedNewAge/{filename}", "wb") as f:              
   #                          f.write(image_data)
   #             # Add the image file to the list
   #                  file = discord.File(f"generatedNewAge/{filename}")
   #                  files.append(file)
           #  if i == 7:
            #    files.append(file)
             #image = Image.open(io.BytesIO(image_data))
             #image.show()



    return files, filename_face_swap, formatted_number
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

    server_address = "81.166.162.13:12684"
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
        images_output = []
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
        "78",
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
        "80",
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
        "34",
        1
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "34": {
    "inputs": {
      "width": 1536,
      "height": 1536,
      "compression": 42,
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
      "text": "terrified cucumber screaming while being blended in blender"
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
      "mean_normalization": false,
      "multi_conditioning": false,
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
      "mean_normalization": false,
      "multi_conditioning": false,
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
  "63": {
    "inputs": {
      "sub_directory": "%date:yyyyMM%/%date:yyyyMMdd%-sc",
      "filename_text_1": "masslevel-sc-",
      "filename_text_2": "-%genSeed.seed%-",
      "filename_text_3": "base",
      "filename_separator": "",
      "timestamp": "true",
      "counter_type": "none",
      "filename_text_1_pos": 0,
      "filename_text_2_pos": 2,
      "filename_text_3_pos": 3,
      "timestamp_pos": 1,
      "timestamp_type": "job",
      "counter_pos": 4,
      "extra_metadata": "",
      "images": [
        "50",
        0
      ]
    },
    "class_type": "Save Images No Display",
    "_meta": {
      "title": "Save Images No Display (Mikey)"
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
  },
  "77": {
    "inputs": {
      "boost": true,
      "model": [
        "41",
        0
      ]
    },
    "class_type": "Automatic CFG",
    "_meta": {
      "title": "Automatic CFG"
    }
  },
  "78": {
    "inputs": {
      "scale": 3,
      "adaptive_scale": 0,
      "unet_block": "middle",
      "unet_block_id": 0,
      "model": [
        "77",
        0
      ]
    },
    "class_type": "PerturbedAttention",
    "_meta": {
      "title": "Perturbed-Attention Guidance"
    }
  },
  "79": {
    "inputs": {
      "boost": true,
      "model": [
        "42",
        0
      ]
    },
    "class_type": "Automatic CFG",
    "_meta": {
      "title": "Automatic CFG"
    }
  },
  "80": {
    "inputs": {
      "scale": 3,
      "adaptive_scale": 0,
      "unet_block": "middle",
      "unet_block_id": 0,
      "model": [
        "79",
        0
      ]
    },
    "class_type": "PerturbedAttention",
    "_meta": {
      "title": "Perturbed-Attention Guidance"
    }
  },
  "85": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "86",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "2048x Upscale"
    }
  },
  "86": {
    "inputs": {
      "samples": [
        "92",
        0
      ],
      "vae": [
        "89",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "87": {
    "inputs": {
      "upscale_method": "lanczos",
      "scale_by": 1.00,
      "image": [
        "8",
        0
      ]
    },
    "class_type": "ImageScaleBy",
    "_meta": {
      "title": "Upscale Image By"
    }
  },
  "88": {
    "inputs": {
      "pixels": [
        "87",
        0
      ],
      "vae": [
        "89",
        2
      ]
    },
    "class_type": "VAEEncode",
    "_meta": {
      "title": "VAE Encode"
    }
  },
  "89": {
    "inputs": {
      "ckpt_name": "ultimateblendXL_v20.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "90": {
    "inputs": {
      "text": "terrified cucumber screaming while being blended in blender",
      "clip": [
        "89",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "91": {
    "inputs": {
      "text": "",
      "clip": [
        "89",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "92": {
    "inputs": {
      "seed": [
        "62",
        0
      ],
      "steps": 20,
      "cfg": 5.5,
      "sampler_name": "dpmpp_2m",
      "scheduler": "karras",
      "denoise": 0.4,
      "model": [
        "93",
        0
      ],
      "positive": [
        "90",
        0
      ],
      "negative": [
        "91",
        0
      ],
      "latent_image": [
        "88",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "93": {
    "inputs": {
      "scale": 3,
      "model": [
        "89",
        0
      ]
    },
    "class_type": "PerturbedAttentionGuidance",
    "_meta": {
      "title": "PerturbedAttentionGuidance"
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
    prompt["90"]["inputs"]["text"] = promptt
   #prompt["75"]["inputs"]["text_l"] = support
    #prompt["120"]["inputs"]["text"] = promptt
   # prompt["82"]["inputs"]["text_g"] = neg_prompt
    prompt["55"]["inputs"]["text"] = neg_prompt
    prompt["91"]["inputs"]["text"] = neg_prompt
   # prompt["81"]["inputs"]["text"] = neg_prompt
    #prompt["76"]["inputs"]["filename_prefix"] = filename_h
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
def  generate_image_CosXL(V4, promptt, neg_prompt,w, h, keyw, three, vae, lora, support):

    server_address = "81.166.162.13:12684"
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
  "3": {
    "inputs": {
      "seed": 398321814909516,
      "steps": 40,
      "cfg": 6,
      "sampler_name": "dpmpp_sde_gpu",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "4",
        0
      ],
      "positive": [
        "24",
        0
      ],
      "negative": [
        "25",
        0
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "cosxl.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "5": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "7": {
    "inputs": {
      "text": ""
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "27",
        0
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "9": {
    "inputs": {
      "filename_prefix": "IPAdapter",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "24": {
    "inputs": {
      "width": 2048,
      "height": 2048,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 2048,
      "target_height": 2048,
      "text_g": "Close-up photo of a man transformed into a mythical yeti, detailed fur texture, dramatic lighting, surrealistic style",
      "text_l": "Close-up photo of a man transformed into a mythical yeti, detailed fur texture, dramatic lighting, surrealistic style",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Positive Base"
    }
  },
  "25": {
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
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncodeSDXL",
    "_meta": {
      "title": "Negative Base"
    }
  },
  "27": {
    "inputs": {
      "vae_name": "sdxl_vae.safetensors"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
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
    prompt["24"]["inputs"]["text_g"] = promptt
    prompt["24"]["inputs"]["text_l"] = promptt
   #prompt["75"]["inputs"]["text_l"] = support
    #prompt["120"]["inputs"]["text"] = promptt
    prompt["7"]["inputs"]["text"] = neg_prompt
    #prompt["55"]["inputs"]["text"] = neg_prompt
   # prompt["81"]["inputs"]["text"] = neg_prompt
    #prompt["76"]["inputs"]["filename_prefix"] = filename_h
    #prompt["201"]["inputs"]["filename_prefix"] = filename_l
    prompt["3"]["inputs"]["seed"] = formatted_number 
   # prompt["22"]["inputs"]["noise_seed"] = formatted_number
    #prompt["216"]["inputs"]["noise_seed"] = formatted_number 
    prompt["5"]["inputs"]["width"] = w
    prompt["5"]["inputs"]["height"] = h
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
def  generate_image_pixart(V4, promptt, neg_prompt,w, h, keyw, three, vae, lora, support, ratio):

    server_address = "69.159.139.22:40080"
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
  "3": {
    "inputs": {
      "vae_name": "sdxl_vae.safetensors"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "6": {
    "inputs": {
      "width": [
        "128",
        0
      ],
      "height": [
        "128",
        1
      ],
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "20": {
    "inputs": {
      "ckpt_name": "PixArt-Sigma-XL-2-1024-MS.pth",
      "model": "PixArtMS_Sigma_XL_2"
    },
    "class_type": "PixArtCheckpointLoader",
    "_meta": {
      "title": "PixArt Checkpoint Loader"
    }
  },
  "66": {
    "inputs": {
      "filename_prefix": "ComfyUI_PixArt",
      "images": [
        "157",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "113": {
    "inputs": {
      "text": "strawberry with horific face standing in dark",
      "T5": [
        "144",
        0
      ]
    },
    "class_type": "T5TextEncode",
    "_meta": {
      "title": "T5 Text Encode"
    }
  },
  "125": {
    "inputs": {
      "text": "watermark",
      "T5": [
        "144",
        0
      ]
    },
    "class_type": "T5TextEncode",
    "_meta": {
      "title": "T5 Text Encode"
    }
  },
  "128": {
    "inputs": {
      "model": "PixArtMS_Sigma_XL_2",
      "ratio": "1.00"
    },
    "class_type": "PixArtResolutionSelect",
    "_meta": {
      "title": "PixArt Resolution Select"
    }
  },
  "144": {
    "inputs": {
      "t5v11_name": "t5-v1.1-xxl/pytorch_model-00001-of-00002.bin",
      "t5v11_ver": "xxl",
      "path_type": "folder",
      "device": "cpu",
      "dtype": "default"
    },
    "class_type": "T5v11Loader",
    "_meta": {
      "title": "T5v1.1 Loader"
    }
  },
  "155": {
    "inputs": {
      "seed": 72672869803516,
      "steps": 30,
      "cfg": 6,
      "sampler_name": "res_momentumized",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "20",
        0
      ],
      "positive": [
        "113",
        0
      ],
      "negative": [
        "125",
        0
      ],
      "latent_image": [
        "6",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "157": {
    "inputs": {
      "samples": [
        "155",
        0
      ],
      "vae": [
        "3",
        0
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "174": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "175",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "2048x Upscale"
    }
  },
  "175": {
    "inputs": {
      "samples": [
        "181",
        0
      ],
      "vae": [
        "3",
        0
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "176": {
    "inputs": {
      "upscale_method": "lanczos",
      "scale_by": 1.5,
      "image": [
        "157",
        0
      ]
    },
    "class_type": "ImageScaleBy",
    "_meta": {
      "title": "Upscale Image By"
    }
  },
  "177": {
    "inputs": {
      "pixels": [
        "176",
        0
      ],
      "vae": [
        "178",
        2
      ]
    },
    "class_type": "VAEEncode",
    "_meta": {
      "title": "VAE Encode"
    }
  },
  "178": {
    "inputs": {
      "ckpt_name": "ultimateblendXL_v20.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "179": {
    "inputs": {
      "text": "strawberry with horific face standing in dark",
      "clip": [
        "178",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "180": {
    "inputs": {
      "text": "watermark",
      "clip": [
        "178",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "181": {
    "inputs": {
      "seed": 72672869803516,
      "steps": 20,
      "cfg": 2.5,
      "sampler_name": "dpmpp_sde",
      "scheduler": "karras",
      "denoise": 0.4,
      "model": [
        "178",
        0
      ],
      "positive": [
        "179",
        0
      ],
      "negative": [
        "180",
        0
      ],
      "latent_image": [
        "177",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
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
    prompt["113"]["inputs"]["text"] = promptt
    prompt["179"]["inputs"]["text"] = promptt
   #prompt["75"]["inputs"]["text_l"] = support
    #prompt["120"]["inputs"]["text"] = promptt
    prompt["125"]["inputs"]["text"] = neg_prompt + ", watermark"
    prompt["180"]["inputs"]["text"] = neg_prompt + ", watermark"
    #prompt["55"]["inputs"]["text"] = neg_prompt
   # prompt["81"]["inputs"]["text"] = neg_prompt
    #prompt["76"]["inputs"]["filename_prefix"] = filename_h
    #prompt["201"]["inputs"]["filename_prefix"] = filename_l
    prompt["155"]["inputs"]["seed"] = formatted_number 
    prompt["181"]["inputs"]["seed"] = formatted_number 
   # prompt["22"]["inputs"]["noise_seed"] = formatted_number
    #prompt["216"]["inputs"]["noise_seed"] = formatted_number 
    #prompt["5"]["inputs"]["width"] = w
    #prompt["5"]["inputs"]["height"] = h
    prompt["128"]["inputs"]["ratio"] = ratio
    #prompt["10"]["inputs"]["ckpt_name"] = model


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
                if i == 2 or i == 4 or i == 4:
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
   # prompt["52"]["inputs"]["wildcard_text"] = promptt
   # prompt["52"]["inputs"]["populated_text"] = promptt
   #prompt["75"]["inputs"]["text_l"] = support
    #prompt["120"]["inputs"]["text"] = promptt
   # prompt["82"]["inputs"]["text_g"] = neg_prompt
   # prompt["53"]["inputs"]["text_negative"] = neg_prompt
   # prompt["81"]["inputs"]["text"] = neg_prompt
   # prompt["84"]["inputs"]["filename_prefix"] = filename_h
    #prompt["201"]["inputs"]["filename_prefix"] = filename_l
   # prompt["41"]["inputs"]["last_seed"] = formatted_number 
   # prompt["22"]["inputs"]["noise_seed"] = formatted_number
    #prompt["216"]["inputs"]["noise_seed"] = formatted_number 
   # prompt["104"]["inputs"]["width"] = w
   # prompt["104"]["inputs"]["height"] = h
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
          "sampler_name": "dpmpp_2m",
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
          "sampler_name": "dpmpp_2m",
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

    server_address = "81.166.162.13:12684"
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
      "noise_seed": 1059717413832628,
      "steps": 50,
      "cfg": 3,
      "sampler_name": "dpmpp_2m",
      "scheduler": "karras",
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
      "text_g": "kraken with arms and legs sitting on park bench, flames in background",
      "text_l": "kraken with arms and legs sitting on park bench, flames in background",
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
      "text": "kraken with arms and legs sitting on park bench, flames in background"
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
      "noise_seed": 1059717413832628,
      "steps": 30,
      "cfg": 3,
      "sampler_name": "dpmpp_2m",
      "scheduler": "karras",
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



    return files, filename_h, formatted_number
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
      "pingpong": true,
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
