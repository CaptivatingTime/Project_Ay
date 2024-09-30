import discord
from api_google import translateMsg
from echo import (
                  generate_face_id_together,
                  generate_face_id_together_creative,
                  generate_face_id_together_unstable,
                  generate_face_id, generate_face_id_creative,
                  generate_face_id_unstable,
                  generate_face_id_unstable,
                  generate_face_id__together_two,
                  generate_face_id__together_creative_two,
                  generate_face_id_unstable_two,
                  generate_face_id_two_people,
                  generate_face_id_creative_two,
                  generate_face_id_unstable_two,
                  generate_face_id_creative_four,
                  generate_face_id_three_people,
                  generate_face_id_creative_three,
                  new_enchPrompt,
                  enchPrompt,
  
                 )
import requests
from PIL import Image
from io import BytesIO
import json
import time
async def atdarini_person(message, atdarini_description, prompts):
    if len(message.mentions) == 1:
                

                
        human = " man "
        if message.mentions[0].id == 122797491044220928 or  message.mentions[0].id == 762091976366620703 or message.mentions[0].id == 391668973315424277 or message.mentions[0].id == 317030319624814592 or message.mentions[0].id == 880446227047665714 :
            human = " girl "
        await message.channel.typing()         
        description_en = translateMsg(atdarini_description)
        #is_one = await one_subject_in_prompt(human + description_en)
        #print(is_one)
        description_enchanted_creative = ''
        if 'together' in message.content:
            description_enchanted = await enchPrompt(human + description_en)
            #description_enchanted_creative = await enchPrompt(human + " creative image " + description_en)
        else:

            description_enchanted = await enchPrompt(human + " photo " + description_en)
            description_enchanted_creative = await enchPrompt(human + " creative image " + description_en)
            description_enchanted_adalberto = await new_enchPrompt(human +  description_en)
            #print(description_enchanted_adalberto + '/n')
        #print(description_enchanted)
        avatar_url = message.mentions[0].display_avatar.url
        avatar_response = requests.get(avatar_url)
        user_id = message.mentions[0].id
        # Check if the avatar image is a GIF
        await message.channel.typing()
        #if user_id == 122797491044220928:
            #   avatar_name = "IPAdapter_00473_.png"


        avatar_name = f"avatar_{user_id}.png"
        with Image.open(BytesIO(avatar_response.content)) as img:
            if img.format == 'GIF':
                # Convert the GIF image to PNG format
                img = img.convert('RGBA')
                bg = Image.new('RGBA', img.size, (255, 255, 255))
                bg.paste(img, img)
                img = bg.convert('RGB')
                img.save(f"avatars/{avatar_name}", 'png')
            else:
                # Save the image as PNG directly
                img.save(f"avatars/{avatar_name}", 'png')
        #  try:
        model = "realisticVisionV60B1_v51VAE.safetensors"
        

        if message.mentions[0].id == 240554122510598146:
                avatar_name = "avatar_1711489951.png"
            # elif message.mentions[0].id == 197621133007126528:
            #    avatar_name = "avatar_1711967172_0.png"  

        if 'together' in message.content:
            files  = await generate_face_id_together(avatar_name, description_enchanted)  
            new_message =   await message.reply(files=files)

            await message.channel.typing()
            files  = await generate_face_id_together_creative(avatar_name,description_enchanted) 
            new_message =   await message.reply(files=files)

            await message.channel.typing()
            # files  = await generate_face_id_together_unstable(avatar_name,description_enchanted) 
            #  new_message =   await message.reply(files=files)
            await message.channel.typing()
            files  = await generate_face_id_together_unstable(avatar_name,description_en) 
            new_message =   await message.reply(files=files)                            

        else:
            files  = await generate_face_id(avatar_name,description_enchanted, model)  
            new_message =   await message.reply(files=files)

            await message.channel.typing()
            files  = await generate_face_id_creative(avatar_name,description_enchanted_creative) 
            new_message =   await message.reply(files=files)

            await message.channel.typing()
            files  = await generate_face_id_unstable(avatar_name,description_enchanted_adalberto) 
            new_message =   await message.reply(files=files)
            await message.channel.typing()
            files  = await generate_face_id_unstable(avatar_name, human + description_en) 
            new_message =   await message.reply(files=files)                           

            #files_enchanted_creative_task = generate_face_id_unstable(avatar_name, description_enchanted_creative)
            #files_enchanted_task = generate_face_id_unstable(avatar_name, description_enchanted)

            #files_enchanted_creative, files_enchanted = await asyncio.gather(files_enchanted_creative_task, files_enchanted_task)

            #combined_files = files_enchanted_creative + files_enchanted
            #new_message = await message.reply(files=combined_files)

            #await message.channel.typing()
            #files  = await generate_face_id_unstable(avatar_name,description_enchanted) 
            #new_message =   await message.reply(files=files)
        msg_id = new_message.id
        new_prompt = {
                f"{msg_id}": {
                    "original": description_en,
                    "original_real": description_enchanted,
                    "adalberto": description_enchanted_adalberto,
                    "original_creative": description_enchanted_creative,
                    "model": "faceid",
                    "name_of_avatar": avatar_name,
                }
        }

        prompts.update(new_prompt)
        with open("prompts.json", "w") as file:
                json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                file.write('\n')
        return
        #  except:
        #      new_message =   await message.channel.send("Hmm kaut kas nogaja greizi.")
        #     return
    elif len(message.mentions) == 2:
        humans = "two men "
        if message.mentions[0].id == 391668973315424277 and message.mentions[1].id == 317030319624814592:  
                humans = "two girls "
        elif message.mentions[1].id == 391668973315424277 and message.mentions[0].id == 317030319624814592:
            humans = "two girls "

        elif message.mentions[0].id == 122797491044220928 and message.mentions[1].id == 317030319624814592:
            humans = "two girls "
        elif message.mentions[1].id == 122797491044220928 and message.mentions[0].id == 317030319624814592:
            humans = "two girls "

        elif message.mentions[0].id == 122797491044220928 and message.mentions[1].id == 391668973315424277:
            humans = "two girls "
        elif message.mentions[1].id == 122797491044220928 and message.mentions[0].id == 391668973315424277:
            humans = "two girls "

        elif message.mentions[0].id == 880446227047665714 and message.mentions[1].id == 391668973315424277:
            humans = "two girls "
        elif message.mentions[1].id == 880446227047665714 and message.mentions[0].id == 391668973315424277:
            humans = "two girls "      
        elif message.mentions[0].id == 880446227047665714 and message.mentions[1].id == 317030319624814592:
            humans = "two girls "
        elif message.mentions[1].id == 880446227047665714 and message.mentions[0].id == 317030319624814592:
            humans = "two girls "

        elif message.mentions[0].id == 880446227047665714 and message.mentions[1].id == 122797491044220928:
            humans = "two girls "
        elif message.mentions[1].id == 880446227047665714 and message.mentions[0].id == 122797491044220928:
            humans = "two girls "
                                        
        elif message.mentions[0].id == 122797491044220928 or message.mentions[0].id == 762091976366620703 or message.mentions[0].id == 391668973315424277 or message.mentions[0].id == 317030319624814592 or message.mentions[0].id == 880446227047665714:
            humans = "girl and man "
        elif message.mentions[1].id == 122797491044220928 or message.mentions[1].id == 762091976366620703 or  message.mentions[1].id == 391668973315424277 or message.mentions[1].id == 317030319624814592 or message.mentions[1].id == 880446227047665714:
            humans = "man and girl "
        await message.channel.typing()
        description_en = translateMsg(atdarini_description)
        description_enchanted_creative = ''
        if 'together' in message.content:
            description_enchanted = await enchPrompt(humans +  description_en)
            #description_enchanted_creative = await enchPrompt(humans + " creative image " + description_en)
        else:
            description_enchanted = await enchPrompt(humans + " photo " + description_en)
            description_enchanted_creative = await enchPrompt(humans  + description_en + " ,creative image ")
            description_enchanted_adalberto = await new_enchPrompt(humans +  description_en)
            #print(description_enchanted_adalberto +'/n')
        #print(description_enchanted)
        avatar_list = []
        i = 0
        for mention in message.mentions:
            user_id = mention.id

            avatar_url = mention.display_avatar.url
            avatar_response = requests.get(avatar_url)
            # Check if the avatar image is a GIF
            await message.channel.typing()
            avatar_name = f"avatar_{user_id}_{i}.png"
            i = i + 1
            if mention.id == 240554122510598146:
                avatar_name = "avatar_1711489951.png"
            # elif mention.id == 197621133007126528:
            #     avatar_name = "avatar_1711967172_0.png"                            
            else:
                with Image.open(BytesIO(avatar_response.content)) as img:
                    if img.format == 'GIF':
                        # Convert the GIF image to PNG format
                        img = img.convert('RGBA')
                        bg = Image.new('RGBA', img.size, (255, 255, 255))
                        bg.paste(img, img)
                        img = bg.convert('RGB')
                        img.save(f"avatars/{avatar_name}", 'png')
                    else:
                        # Save the image as PNG directly
                        img.save(f"avatars/{avatar_name}", 'png')
            avatar_list.append(avatar_name)
        #try:


        if 'together' in message.content:
            files  = await generate_face_id__together_two(avatar_list[0], avatar_list[1], "(3 characters) " + description_enchanted)  
            new_message =   await message.reply(files=files)
            await message.channel.typing()
            files  = await generate_face_id__together_creative_two(avatar_list[0], avatar_list[1],"(3 characters) " + description_enchanted)  
            new_message =   await message.reply(files=files)
            files  = await generate_face_id_unstable_two(avatar_list[0], avatar_list[1],description_enchanted_creative)  
            new_message =   await message.reply(files=files)
        else:

            files  = await generate_face_id_two_people(avatar_list[0], avatar_list[1],description_enchanted)  
            new_message =   await message.reply(files=files)
            await message.channel.typing()
            files  = await generate_face_id_creative_two(avatar_list[0], avatar_list[1],description_enchanted_creative)  
            new_message =   await message.reply(files=files)
            files  = await generate_face_id_unstable_two(avatar_list[0], avatar_list[1],description_enchanted_adalberto)  
            new_message =   await message.reply(files=files)
            files  = await generate_face_id_unstable_two(avatar_list[0], avatar_list[1],humans + description_en)  
            new_message =   await message.reply(files=files)                            
        msg_id = new_message.id
        new_prompt = {
            f"{msg_id}": {
                "original": description_en,
                "original_real": description_enchanted,
                "adalberto": description_enchanted_adalberto,
                "original_creative": description_enchanted_creative,
                "model": "faceid_two",
                "name_of_avatar": avatar_name,
            }
        }

        prompts.update(new_prompt)
        with open("prompts.json", "w") as file:
            json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
            file.write('\n')
            return
        #  except:
            #   new_message =   await message.channel.send("Hmm kaut kas nogāja greizi.")
            #   return
    elif len(message.mentions) == 4:
        girls = [122797491044220928,391668973315424277,317030319624814592, 880446227047665714, 762091976366620703, 1085573614193094696]
        girl_count = 0
        for mention in message.mentions:
            if mention.id in girls:
                girl_count = girl_count + 1
        if girl_count == 4:
            humans = "four girls "
        elif girl_count == 3:
            humans = "three girls and man "
        elif girl_count == 2:
            humans = "two girls and two man "
        elif girl_count == 1:
            humans = "three men and girl "
        else:
            humans = "four men "

        #humans = "three  "
        await message.channel.typing()
        description_en = translateMsg(atdarini_description)
        #description_enchanted = await enchPrompt(humans + " photo " + description_en)
        description_enchanted_creative = await enchPrompt(humans + " photo " + description_en)
        #print(description_enchanted)
        avatar_list = []
        filess = []
        i = 0
        for mention in message.mentions:
            user_id = mention.id

            avatar_url = mention.display_avatar.url
            avatar_response = requests.get(avatar_url)
            # Check if the avatar image is a GIF
            await message.channel.typing()
            avatar_name = f"avatar_{int(time.time())}_{i}.png"
            i = i + 1
            if mention.id == 240554122510598146:
                avatar_name = "avatar_1711489951.png"
            # elif mention.id == 197621133007126528:
            #     avatar_name = "avatar_1711967172_0.png"                            
            else:
                with Image.open(BytesIO(avatar_response.content)) as img:
                    if img.format == 'GIF':
                        # Convert the GIF image to PNG format
                        img = img.convert('RGBA')
                        bg = Image.new('RGBA', img.size, (255, 255, 255))
                        bg.paste(img, img)
                        img = bg.convert('RGB')
                        img.save(f"avatars/{avatar_name}", 'png')
                    else:
                        # Save the image as PNG directly
                        img.save(f"avatars/{avatar_name}", 'png')
            avatar_list.append(avatar_name)
        try:

            #files  = await generate_face_id_two_people(avatar_list[0], avatar_list[1],description_enchanted)  
            #new_message =   await message.reply(files=files)
            #generate_face_id_three_people
            #print(description_enchanted_creative)
            await message.channel.typing()
            # try:
            #     files  = await generate_face_id_reals_four(avatar_list[3],avatar_list[2], avatar_list[0], avatar_list[1], "(4 characters)" + description_enchanted_creative)  
            #      new_message =   await message.reply(files=files)
            #  except:
            #      print("Four failed, trying again")
            #     files  = await generate_face_id_reals_four(avatar_list[3],avatar_list[2], avatar_list[0], avatar_list[1], "(4 characters)" + description_enchanted_creative)  
            #     new_message =   await message.reply(files=files)
            await message.channel.typing()
            try:
                files  = await generate_face_id_creative_four(avatar_list[3],avatar_list[2], avatar_list[0], avatar_list[1], "(4 characters)" + description_enchanted_creative) 
                if len(files) == 2:
                    new_message =   await message.reply(files=[files[0]])
                else:
                    new_message =   await message.reply(files=files)                            	    
            except:
                print("Four failed, trying again")
                files  = await generate_face_id_creative_four(avatar_list[3],avatar_list[2], avatar_list[0], avatar_list[1], "(4 characters)" + description_enchanted_creative) 
                if len(files) == 2:
                    new_message =   await message.reply(files=[files[0]])
                else:
                    new_message =   await message.reply(files=files)

            #model = "realisticVisionV60B1_v51VAE.safetensors"
            #files  = await generate_face_id_three_people(avatar_list[1],avatar_list[0], avatar_list[2], description_enchanted_creative) 
            #new_message =   await message.reply(files=files)
            msg_id = new_message.id
            new_prompt = {
                f"{msg_id}": {
                    "original": description_en,
                    "original_creative": description_enchanted_creative,
                    "model": "faceid_three",
                    "name_of_avatar": avatar_name,
                }
            }

            prompts.update(new_prompt)
            with open("prompts.json", "w") as file:
                json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                file.write('\n')
                return
        except:
            new_message =   await message.channel.send("Hmm kaut kas nogāja greizi.")
            return
    elif len(message.mentions) == 3:
        girls = [122797491044220928,391668973315424277,317030319624814592, 880446227047665714, 762091976366620703]
        girl_count = 0
        for mention in message.mentions:
            if mention.id in girls:
                girl_count = girl_count + 1
        if girl_count == 3:
            humans = "three girls "
        elif girl_count == 2:
            humans = "two girls and man "
        elif girl_count == 1:
            humans = "two men and girl "
        else:
            humans = "three men "

        #humans = "three  "
        await message.channel.typing()
        description_en = translateMsg(atdarini_description)
        #description_enchanted = await enchPrompt(humans + " photo " + description_en)
        description_enchanted_creative = await enchPrompt(humans + " professional portrait photo " + description_en)
        #print(description_enchanted)
        avatar_list = []
        filess = []
        i = 0
        for mention in message.mentions:
            user_id = mention.id

            avatar_url = mention.display_avatar.url
            avatar_response = requests.get(avatar_url)
            # Check if the avatar image is a GIF
            await message.channel.typing()
            avatar_name = f"avatar_{int(time.time())}_{i}.png"
            i = i + 1
            if mention.id == 240554122510598146:
                avatar_name = "avatar_1711489951.png"
            # elif mention.id == 197621133007126528:
            #     avatar_name = "avatar_1711967172_0.png"                            
            else:
                with Image.open(BytesIO(avatar_response.content)) as img:
                    if img.format == 'GIF':
                        # Convert the GIF image to PNG format
                        img = img.convert('RGBA')
                        bg = Image.new('RGBA', img.size, (255, 255, 255))
                        bg.paste(img, img)
                        img = bg.convert('RGB')
                        img.save(f"avatars/{avatar_name}", 'png')
                    else:
                        # Save the image as PNG directly
                        img.save(f"avatars/{avatar_name}", 'png')
            avatar_list.append(avatar_name)
        try:

            # files  = await generate_face_id_two_people(avatar_list[0], avatar_list[1],description_enchanted)  
            #new_message =   await message.reply(files=files)
            #generate_face_id_three_people
            #print(description_enchanted_creative)
            model = "realisticVisionV60B1_v51VAE.safetensors"
            await message.channel.typing()
            files  = await generate_face_id_three_people(avatar_list[1],avatar_list[0], avatar_list[2], "(3 characters) " + description_enchanted_creative) 
            new_message =   await message.reply(files=files)                           
            await message.channel.typing()
            files  = await generate_face_id_creative_three(avatar_list[1],avatar_list[0], avatar_list[2],"(3 characters) " + description_enchanted_creative)  
            new_message =   await message.reply(files=files)

            #await message.channel.typing()
            #files  = await generate_face_id_adalberto_three(avatar_list[1],avatar_list[0], avatar_list[2], "(3 characters) " + description_enchanted_creative) 
            # new_message =   await message.reply(files=files)
            msg_id = new_message.id
            new_prompt = {
                f"{msg_id}": {
                    "original": description_en,
                    "original_creative": description_enchanted_creative,
                    "model": "faceid_three",
                    "name_of_avatar": avatar_name,
                }
            }

            prompts.update(new_prompt)
            with open("prompts.json", "w") as file:
                json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                file.write('\n')
                return
        except:
            new_message =   await message.channel.send("Hmm kaut kas nogāja greizi.")
            return
