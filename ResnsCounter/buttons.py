import discord
import json
#from ResnsCounter import generate_image_refiner, generate_gif, generate_image, enchPrompt, enchPrompt_support


with open("prompts.json", "r") as file:
        prompts = json.load(file)
class MyView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
        execute_code = True
        def __init__(self):
            super().__init__(timeout=None) # timeout of the view must be set to None

        async def common_button_function(self,  w, h, three, search_key, msgg1, redo, model):
            
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

            if model == "juggernautXL_version6Rundiffusion.safetensors":
                neg_prompt = "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)"
            elif model == "sdxlUnstableDiffusers_v8HeavensWrathVAE.safetensors":
                neg_prompt        = "bad quality, bad anatomy, worst quality, low quality, lowres, extra fingers, blur, blurry, ugly, wrong proportions, watermark, image artifacts,"
            else:
                neg_prompt        = prompts.get(str(search_key), {}).get("negative", "")

            if model == "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors":
                vae = True
            else:
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



            
            msgg2 = f"*Wait time: **up to 40sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
            embed_msg = embed = discord.Embed(description=msg_prompt, color=0x0000ff)
            
            # embed_redo = embed = discord.Embed(description=msg_prompt, color=0xff0000)
            #await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked
            channel = client.get_channel(1101461174907830312)

            wait_msg1 = await channel.send(msgg1)
            emb_msg =  await channel.send(embed=embed_msg)
            wait_msg2 = await channel.send(msgg2)
            #  wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
                            

            
            #  VAE = False
            if support:
                support = support
            else:
                support = msg_prompt
            if model == "sdXL_v10VAEFix.safetensors":
                files = await generate_image_refiner(V4, msg_prompt, neg_prompt, w , h, keyword, model, three, vae, lora, support)  
            else:
                files = await generate_image(V4, msg_prompt, neg_prompt, w , h, keyword, model, three, vae, lora, support)  

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
            if redo:
              new_message =   await channel.send(files=files)
            else:
                new_message =   await channel.send(files=files, view=MyView())
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
                }
            }
            prompts.update(new_prompt)
            try:
                with open("prompts.json", "w") as file:
                    json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                    file.write('\n')
            except (FileNotFoundError, PermissionError, IOError) as e:
                print(f"Error: {e}")


        @discord.ui.button(label="reDo", custom_id="redo_button", row = 1, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def redo_button_callback(self, button, interaction):
            await interaction.response.defer()
            execute_code = True
            if execute_code:      
                redo = True
                three = False
                message_id = interaction.message.id
                search_key = f"{message_id}"                
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
                message_id = interaction.message.id
                search_key = f"{message_id}" 
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
                message_id = interaction.message.id
                search_key = f"{message_id}"
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
                message_id = interaction.message.id
                search_key = f"{message_id}"
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
                message_id = interaction.message.id
                search_key = f"{message_id}"
                model             = prompts.get(str(search_key), {}).get("model", "")

                await self.common_button_function(w, h, three,search_key, msgg1, redo, model )

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
                message_id = interaction.message.id
                search_key = f"{message_id}"
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
                message_id = interaction.message.id
                search_key = f"{message_id}"
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
                message_id = interaction.message.id
                search_key = f"{message_id}"
                model             = prompts.get(str(search_key), {}).get("model", "")

                await self.common_button_function(w, h, three,search_key, msgg1 ,redo, model )


           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")



        @discord.ui.button(label="Realistic", custom_id="realistic_button", row = 4, style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
        async def realistic_callback(self, button, interaction):
           await interaction.response.defer()
           if execute_code:
                neg_prompt = "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)"
                redo = False
                three = False
                msgg1 = f"*Redoing image with realistic model...*"




                message_id = interaction.message.id
                search_key = f"{message_id}"
                model             = "juggernautXL_version6Rundiffusion.safetensors"
                w                 = prompts.get(str(search_key), {}).get("w", "")
                h                 = prompts.get(str(search_key), {}).get("h", "")

                await self.common_button_function(w, h, three,search_key, msgg1, redo, model )

           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")

        @discord.ui.button(label="Artistic", custom_id="artistic_button2", row = 4, style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
        async def artistic_button2_callback(self, button, interaction):
           await interaction.response.defer()
           if execute_code:
                neg_prompt        = "bad quality, bad anatomy, worst quality, low quality, lowres, extra fingers, blur, blurry, ugly, wrong proportions, watermark, image artifacts,"
                redo = False
                three = False
                msgg1 = f"*Redoing image with realistic model...*"




                message_id = interaction.message.id
                search_key = f"{message_id}"
                model             = "sdxlUnstableDiffusers_v8HeavensWrathVAE.safetensors" 
                w                 = prompts.get(str(search_key), {}).get("w", "")
                h                 = prompts.get(str(search_key), {}).get("h", "")

                await self.common_button_function(w, h, three,search_key, msgg1, redo, model )


           else:
                channel = client.get_channel(1101461174907830312)
                await channel.send("GPU power is used for gaming right now. **Echo** is *disabled*.")

        @discord.ui.button(label="Dalle-3", custom_id="Dalle32_button", row = 4,  style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
        async def Dalle3reDo2_button__callback(self, button, interaction):
            await interaction.response.defer()
            
            channel = client.get_channel(1101461174907830312)
            #  model = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"
            message_id = interaction.message.id
            search_key = f"{message_id}"
            original_content  = prompts.get(str(search_key), {}).get("original", "")
            msgg = "*Echoing image using Dalle-3... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"

            wait_msg = await channel.send(msgg)
            # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
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

        @discord.ui.button(label="GIF", custom_id="gif_redo_button", row = 4,  style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
        async def GIFreDo1_button__callback(self, button, interaction):
            await interaction.response.defer()
            channel = client.get_channel(1101461174907830312)                
            #  model = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"
            message_id = interaction.message.id
            search_key = f"{message_id}"
            original_content  = prompts.get(str(search_key), {}).get("original", "")
            enchanted_content  = prompts.get(str(search_key), {}).get("enchanted", "")
            styled_content  = prompts.get(str(search_key), {}).get("styled", "")

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
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
            channel.trigger_typing                          
            lora = False
            files = []
            three = False
            vae = False
            

                            
            files =  await generate_gif(prompt)


            await wait_msg.delete()
            await wait_gif.delete()




            new_message =   await channel.send(files=files, view=gif_buttons())

            msg_id = new_message.id
            # new_prompt = {f"{msg_id}": input_en}

            new_prompt = {
                f"{msg_id}": {
                    "original": prompt,
                    "styled": "",  # Add your styled content here
                    "enchanted": "",  # Add your enchanted content here
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


        @discord.ui.button(label="AI Enhance", custom_id="ench_button", row = 1, style=discord.ButtonStyle.success) # Create a button with the label "😎 Click me!" with color Blurple
        async def enhance_button_callback(self, button, interaction):
           await interaction.response.defer()
           if execute_code:
            V4 = True
           # neg_prompt = "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)"
            w = 1024
            h = 1024
            keyword = "echo"



            channel = client.get_channel(1101461174907830312)

            message_id = interaction.message.id
            search_key = f"{message_id}"

            original_content  = ""
            enchanted_content = ""
            styled_content    = ""


            enchanted_content = prompts.get(str(search_key), {}).get("enchanted", "")
            original_content  = prompts.get(str(search_key), {}).get("original", "")
            styled_content    = prompts.get(str(search_key), {}).get("styled", "")
            neg_prompt        = prompts.get(str(search_key), {}).get("negative", "")
            w                 = prompts.get(str(search_key), {}).get("w", "")
            h                 = prompts.get(str(search_key), {}).get("h", "")
            model             = prompts.get(str(search_key), {}).get("model", "")

            if model == "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors":
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
            enchanting =  await channel.send(enhancing_msg) 
            ench_prompt = await enchPrompt(msg_prompt)
            support = await enchPrompt_support(msg_prompt)

            await enchanting.delete()

            msgg1 = f"*Enchanting image with same prompt...*"
            msgg2 = f"*Wait time: **up to 40sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"

            embed_msg = embed = discord.Embed(description=ench_prompt, color=0x00ff00)

            ench_prompt_done = "**Enchanted:** " + ench_prompt
            embed_ench_prompt_done = embed = discord.Embed(description=ench_prompt_done, color=0x00ff00)
            #await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked
            

            wait_msg1 = await channel.send(msgg1)
            emb_msg =   await channel.send(embed=embed_msg)
            wait_msg2 = await channel.send(msgg2)
         #   wait_gif =  await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")                

            three = False
            if model == "sdXL_v10VAEFix.safetensors":
                files = await generate_image_refiner(V4, ench_prompt, neg_prompt, w , h, keyword, model, three, vae, lora, support)   
            else:
                files = await generate_image(V4, ench_prompt, neg_prompt, w , h, keyword, model, three, vae, lora, support)   

            await wait_msg1.delete()
            await emb_msg.delete()
            await wait_msg2.delete()
            await wait_gif.delete()

            emb_ench_prompt_done =   await channel.send(embed=embed_ench_prompt_done)
            new_message =   await channel.send(files=files, view=MyView())


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



        @discord.ui.button(label="Random style", custom_id="random_button", row = 4, style=discord.ButtonStyle.danger) # Create a button with the label "😎 Click me!" with color Blurple
        async def random_button_callback(self, button, interaction):
           await interaction.response.defer()
           if execute_code:
            V4 = True
            neg_prompt = "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)"
            w = 1024
            h = 1024
            keyword = "echo"




            channel = client.get_channel(1101461174907830312)

            message_id = interaction.message.id
            search_key = f"{message_id}"

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

          # model             = prompts.get(str(search_key), {}).get("model", "") sdxlUnstableDiffusers_v8HeavensWrathVAE.safetensors
          #  model             = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"
            model             = "sdXL_v10VAEFix.safetensors" 

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
            msgg2 = f"*Wait time: **up to 40sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"

            embed_msg = embed  = discord.Embed(description=msg_prompt, color=0xff0000)
            embed_style = embed = discord.Embed(description=embed_Style, color=0xff0000)

            #await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked
            

            wait_msg1 = await channel.send(msgg1)
            emb_msg =   await channel.send(embed=embed_msg)
            wait_msg2 = await channel.send(msgg2)
          #  wait_gif =  await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")                


            three = False
            support = formatted_rand_prompt
            files = await generate_image_refiner(V4, formatted_rand_prompt, neg_prompt, w , h, keyword, model, three, vae, lora, support)   
            await wait_msg1.delete()
            await emb_msg.delete()
            await wait_msg2.delete()
            await wait_gif.delete()

            embed_style =   await channel.send(embed=embed_style)
            new_message =   await channel.send(files=files, view=MyView())


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
        wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
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
                "original": input_en,
                "styled": "",  # Add your styled content here
                "enchanted": "",  # Add your enchanted content here
                "negative": "",  # Add your enchanted content here
            }
        }

        prompts.update(new_prompt)
        with open("prompts.json", "w") as file:
            json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
            file.write('\n')  
