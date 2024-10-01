import time
import os
import discord
from discord import app_commands
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
import warnings 
import numpy as np
from nltk.chat.util import Chat
from pathlib import Path
import requests
import openai
from openai import OpenAI, AsyncOpenAI
from io import BytesIO
from PIL import Image
from unidecode import unidecode
import base64
import logging
import pytz
import json
from colorama import Fore
from bs4 import BeautifulSoup
import anthropic
import seaborn as sns
import matplotlib.pyplot as plt
from collections import deque
import httpx

 ### NEW ###
##M created my me
from bot_Chatting import Chatbot,get_similar_response
from Registration import RegisterWin, Register_time, RegTotalMonthWins
from api_giphy import getGif
from api_google import translateMsg
from echo import (
                  generate_image_sd3,
                  upscale_sd3,
                  enchPrompt_gpt4o,
                 )
from functions import (getTime,
                       getDate,
                       preprocess_message,
                       replace_starting_phrase,
                       add_message_to_thread,
                       get_threadID,
                       scan_unsaved_msg,
                       notify_nameday,
                       notify_weather,
                       timeOfDay
                      )

from slash_commands import (resnums_slash,
                            stop_music,
                            play_music
                           )
from chat_functions import (post_random_image,
                            post_random_message,
                            post_mention_message,
                            post_reply_message,
                            post_comment_message
                           )

from functions_onMessage import gudrais_response
from functions_atdarini import atdarini_person
from Classes import Config, MsgCollector
from activityTracker import trackActivity
# suppress the warning
warnings.filterwarnings("ignore", message="The parameter 'token_pattern' will not be used since 'tokenizer' is not None'")

# Ctrl + K, then Ctrl + U if you’re on Windows


############# gudrais ######################
# Function to load data from JSON file
firstBoot = True
def load_data_from_json(file_name):
    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {}



def addPair(file_name, msg1, msg2): 
    if file_name == 'CB_pairs2addition.json':
        MyMsgCollector.setAdditionMsgs([msg1,[msg2]])
        with open(file_name, 'w') as file:
            json.dump(MyMsgCollector.getAdditionMsgs(),file)
        return MyMsgCollector.getAdditionMsgs()
    else:
        #addition_colltected = []
        MyMsgCollector.setAdditionMsgsCollected([msg1,[msg2]])
        # with open(file_name, 'w') as file:
        #     json.dump(addition_colltected,file)
        return MyMsgCollector.getAdditionMsgsCollected()
def get_direct_gif_link(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        gif_url = soup.find('meta', property='og:image')['content']
        return gif_url
    except Exception as e:
        print("Error fetching GIF link:", e)
        return None


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





def process_string_for_atdarini(input_string):
    # Define regular expression pattern to match mentions of the format <@some_num>
    mention_pattern = r'<@\d+>'
    
    # Replace all occurrences of mention_pattern with an empty string
    processed_string = re.sub(mention_pattern, '', input_string)
    
    # Split the processed string into words
    words = processed_string.split()
    
    # If there are more than 2 words
    if len(words) > 2:
        # Join the first two words
        first_two_words = ' '.join(words[:2])
        
        # Join the remaining words
        rest_of_string = ' '.join(words[2:])
        
        return first_two_words, rest_of_string
    else:
        return input_string, None

def process_string_for_atdarini_two(input_string):
    words = input_string.split()
    if len(words) > 2:
        first_two_words = ' '.join(words[:2])
        rest_of_string = ' '.join(words[2:])
        return first_two_words, rest_of_string
    else:
        return input_string, None


Myconfig = Config()
MyMsgCollector = MsgCollector()

with open('CB_pairs2addition.json', 'r') as file: 
    MyMsgCollector.setAdditionMsgs(json.load(file)) 
with open('testt.json', 'r') as file: 
    MyMsgCollector.setAdditionMsgsCollected(json.load(file)) 

def main():
   
    # Saglabāziņas starp lietotāju un bobotu
   def saveResponse(list):
         with open('CB_givenResponses.json', 'w') as file:
          json.dump(list, file)

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
            return nick

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

   with open("CB_question_list.json", 'r', encoding='utf-8') as file: #@#
    question_list = json.load(file) #@#

   with open("CB_triger_ko_dari.json", 'r', encoding='utf-8') as file: #@#
    triger_KoDari = json.load(file) #@#
    
   with open("CB_triger_ka_iet.json", 'r', encoding='utf-8') as file: #@#
    triger_KaIet = json.load(file) #@#

   with open("CB_conv_cooldown.json", 'r', encoding='utf-8') as file: 
    conv_cooldown = json.load(file)

   with open("CB_conv_cooldown.json", 'r', encoding='utf-8') as file: 
    conv_cooldown = json.load(file)

   with open('gifs_Lonely.json', 'r') as f:
       gifs_lonely = json.load(f)

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



   load_dotenv()
   intents = discord.Intents.default()
   intents.message_content = True
   intents.guilds          = True
   intents.members         = True
   intents.messages        = True
   intents.presences       = True
   intents.emojis          = True
   client = commands.Bot(intents=discord.Intents.all(), command_prefix='!')
   

     ## Slash commaands
   @client.tree.command(name = 'resnums')
   async def resnums(interaction: discord.Interaction):
       await resnums_slash(interaction, game_wins)

   @client.tree.command(name="play", description="DJ Elizabete muzika(url or nosaukums)")
   async def play_slash(interaction: discord.Interaction, song: str):
    nextRecomended = False
    newCall = True
    YTplaylist_url = "None"
    await play_music(interaction, song, client, nextRecomended, YTplaylist_url, newCall)
    

   @client.tree.command(name="stop", description="Sutit DJ Elizabeti majas")
   async def stop_slash(interaction: discord.Interaction):
       await stop_music(interaction, client) 

    ## Slash commaands
   

   #Chatbot initialization
   pairs, response_list, lv_reflections = Chatbot()
   #chatbot = Chat(pairs, lv_reflections) # disabled 02.10.2024
   random.seed(time.time())

   SCREENSHOT_CHANNEL_ID = int(os.getenv("SCREENSHOT_CHANNEL_ID"))
   SCREENSHOT_EXTENSIONS = [".png", ".jpg", ".jpeg"]
   gpt_key               = os.getenv("GPT")
   token                 = os.getenv('TOKEN')
   client_dalle = OpenAI(api_key=gpt_key)

   

   @client.command()
   async def edit_message(ctx, message_id: int):
        # Fetch the message
        message = await ctx.channel.fetch_message(message_id)

        # Create button component
        #button = discord.ui.button(style=discord.ButtonStyle.primary, label="Test")

        # Create action row and add button to it
       # action_row = discord.ui.ActionRow()
      #  action_row.add_button(button)

        # Edit the message adding the action row
        await message.edit(view = statsButton())
   #client.add_command(edit_message)


# Nosūtīt random ziņu ik pēc noteikta laika #general kanālā 
###################### INTERACT IN CHAT OVER TIME ########################

    # Runā pats grafiks
   async def schedule_messages():
        #global elizabeteLastMsg
        while True:

            channel = client.get_channel(Myconfig.getChatChannel()) 


            now = datetime.now() + timedelta(hours=1 )
            post_time = now + timedelta(hours=1)
            # Print the scheduled message post time
            print(f"\nNext Resnas mammas response message will be posted at: {post_time.strftime('%H:%M:%S')}\n") 
            await asyncio.sleep(3600)
            if Myconfig.getElizabeteLastMsg() == False: 
                await post_reply_message(channel, client, pairs, response_list)

            now = datetime.now() + timedelta(hours=1 )
            post_time = now + timedelta(hours=2)
            # Print the scheduled message post time
            print(f"\nNext Resnas mammas random mention message will be posted at: {post_time.strftime('%H:%M:%S')}\n")
            print("last message sent by Elizabete: " + str(Myconfig.getElizabeteLastMsg()))
            await asyncio.sleep(7200)  # Sleep for 3 hour
            print("last message sent by Elizabete: " + str(Myconfig.getElizabeteLastMsg()))
            if Myconfig.getElizabeteLastMsg() == False:
                await post_mention_message(channel, client, pairs, response_list, question_list)


            now = datetime.now() + timedelta(hours=1 )
            # Calculate the time when the next message will be posted
            post_time = now + timedelta(hours=2)
            # Print the scheduled message post time
            print(f"\nNext Resnas mammas random message will be posted at: {post_time.strftime('%H:%M:%S')}\n")
            await asyncio.sleep(7200)
            if Myconfig.getElizabeteLastMsg() == False:
                await post_random_message(channel, client, pairs, response_list) 

            now = datetime.now() + timedelta(hours=1 )
            post_time = now + timedelta(hours=1 )
            # Print the scheduled message post time
            print(f"\nNext Resnas mammas random image message will be posted at: {post_time.strftime('%H:%M:%S')}\n")
            await asyncio.sleep(3600)  # Sleep for 3 hour
            if Myconfig.getElizabeteLastMsg() == False:
                await post_random_image(channel, client, pairs, response_list)

            now = datetime.now() + timedelta(hours=1 )
            post_time = now + timedelta(hours=2)
            # Print the scheduled message post time
            print(f"\nNext Resnas mammas comment message will be posted at: {post_time.strftime('%H:%M:%S')}\n")
            await asyncio.sleep(7200)  # Sleep for 1 hour
            if Myconfig.getElizabeteLastMsg() == False:
                await post_comment_message(channel, client, pairs, response_list, Myconfig.getThreadID())

###################### INTERACT IN CHAT OVER TIME ########################^


   prefix1 = "x"
   prefix2 = "+"

   class statsButton(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self):
        super().__init__(timeout=None) # timeout of the view must be set to None

    @discord.ui.button(label="view this month wins", custom_id="stats", row = 1, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
    async def stats_button__callback(self,interaction, button ):
           await interaction.response.defer()
           channel = interaction.channel
           player_name = f"{interaction.user.name}"
           #print(player_name)
           response = ""
           found_player = False
           first = True
       
           print('Stats requested...')
                    
           for player, gamee_wins in game_wins.items():
                if player == player_name:
                    found_player = True
                    for game, wins in gamee_wins.items():
                        if first:
                            response = response + f"**{player_name}** has won:\n **{wins}** times {game} this month.\n"
                            first = False
                        else: response = response + f"{wins} times {game}.\n"
           if not found_player:
                response = f"**{player_name}** has no wins this month."
                    #await message.channel.trigger_typing() #@#
                   # await asyncio.sleep(2) #@#            
           print(response)
           stats = await channel.send(response)
           await asyncio.sleep(5)
           await stats.delete()
           print(f"{player_name} Stats provided!")
    @discord.ui.button(label="view your all-time wins", custom_id="alltime_stats", row = 2,  style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
    async def alltimestats_button__callback(self,interaction, button ):
            await interaction.response.defer()
            channel = interaction.channel
            player_name = f"{interaction.user.name}"
            # Load JSON data from a file
            with open('all_wins.json', 'r') as f:
                data = json.load(f)




            #graph_wins
            # Function to extract and structure wins by month-year and game for a player
            def extract_wins_by_month_year_and_game(player_data):
                structured_data = {}

                for date, games in player_data.items():
                    month, year = date.split('.')
                    month_year = f"{month}.{year}"
                    if month_year not in structured_data:
                        structured_data[month_year] = {}
                    for game, wins in games.items():
                        if game not in structured_data[month_year]:
                            structured_data[month_year][game] = 0
                        structured_data[month_year][game] += wins

                return structured_data



            # Extract and structure wins by month-year and game
            player_data = data.get(player_name, {})
            wins_by_month_year_and_game = extract_wins_by_month_year_and_game(player_data)

            # Calculate total wins across all months for each game
            total_wins_all_months = {game: sum(wins.values()) for game, wins in wins_by_month_year_and_game.items()}

            # Total wins across all games
            total_wins_all_games = sum(total_wins_all_months.values())

            # Prepare data for plotting
            # Sort month-year keys chronologically
            all_month_years = sorted(wins_by_month_year_and_game.keys(), key=lambda x: datetime.strptime(x, "%m.%Y"))
            all_games = sorted({game for month_year in wins_by_month_year_and_game.values() for game in month_year.keys()})
            month_year_indices = np.arange(len(all_month_years))
            bar_width = 0.1

            # Create the grouped bar chart
            fig, ax = plt.subplots(figsize=(15, 7))

            # Use Seaborn color palette
            colors = sns.color_palette("tab10", len(all_games))

            for i, game in enumerate(all_games):
                wins = [wins_by_month_year_and_game[month_year].get(game, 0) for month_year in all_month_years]
                ax.bar(month_year_indices + i * bar_width, wins, bar_width, label=game, color=colors[i])

            # Add win counts on top of each bar
            for i, game in enumerate(all_games):
                wins = [wins_by_month_year_and_game[month_year].get(game, 0) for month_year in all_month_years]
                for j in range(len(all_month_years)):
                    if wins[j] > 0:  # Only display if wins are greater than 0
                        ax.text(month_year_indices[j] + i * bar_width, wins[j] + 0.1, str(wins[j]), ha='center', va='bottom', fontsize=8)

            # Display the total wins across all games above the graph
            ax.text(0.5, max(total_wins_all_months.values()) + 20, f'Total Wins Across All Months: {total_wins_all_games}', ha='center', fontsize=12)

            # Configure plot
            ax.set_title(f"{player_name}'s Game Wins by Month-Year", fontsize=16, fontweight='bold')
            ax.set_xlabel('Month-Year', fontsize=14)
            ax.set_ylabel('Wins', fontsize=14)
            ax.set_xticks(month_year_indices + bar_width * (len(all_games) - 1) / 2)
            ax.set_xticklabels(all_month_years, rotation=45, ha='right')
            ax.legend(title='Games', fontsize=12)
            ax.grid(axis='y', linestyle='--', alpha=0.7)

            # Set background color
            ax.set_facecolor('#f0f0f0')  # Light gray

            # Set tight layout
            plt.tight_layout()
            game_wins_image = f'stats/{player_name}_game_wins.png'
            # Save the graph as a PNG image with the player's nickname as the filename
            plt.savefig(game_wins_image, dpi=300)

            #graph_wins
            #graph_specificDay
            # Load JSON data from file
            with open('SpecifDay.json', 'r') as file:
                data = json.load(file)
            """
            Plot the wins of a specific player across each day.
    
            Args:
            - player (str): The nickname of the player whose wins are to be plotted.
            """
            # Initialize lists to store data for plotting
            days = []
            wins = []
    
            # Iterate through each day and extract wins for the chosen player
            for day, day_data in data.items():
                if player_name in day_data:
                    days.append(day)
                    wins.append(day_data[player_name])
    
            # Plotting
            plt.figure(figsize=(10, 6))
            plt.plot(days, wins, marker='o', linestyle='-', color='orange', linewidth=2, markersize=8, label=player_name)
            plt.xlabel('Day', fontsize=12)
            plt.ylabel('Wins', fontsize=12)
            plt.title(f'Wins of Player {player_name} Across Each Day', fontsize=14)
            plt.xticks(rotation=45, ha='right', fontsize=10)
            plt.yticks(fontsize=10)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.legend(loc='upper left', fontsize=10)
            plt.gca().set_facecolor('#f0f0f0')  # Set background color
            plt.tight_layout()

            specificDay_image = f'stats/{player_name}_wins_plot.png'
            plt.savefig(specificDay_image)  # Save plot to an image file
            #graph_specificDay
            #graph_dayTime
            # Read the data from the JSON file
            with open('DayTime.json', 'r') as file:
                data = json.load(file)
            # Select the data for the specified player (change 'player_name' to the desired player's nickname)
            player_data = {time_of_day: wins.get(player_name, 0) for time_of_day, wins in data.items()}

            # Plot the data

            # Extracting wins and labels
            wins = list(player_data.values())
            labels = list(player_data.keys())

            # Plotting
            plt.figure(figsize=(8, 8), facecolor='lightgrey')  # Set the background color to light grey
            colors = plt.cm.tab20.colors  # Get a list of colors from the 'tab20' colormap
            explode = (0.1, 0, 0, 0)  # Explode the first slice (morning) for emphasis
            plt.pie(wins, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, explode=explode, shadow=True)
            plt.title(f'Wins Distribution for Player: {player_name}', fontsize=16)
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.tight_layout()

            # Save the plot to a file with the player's nickname as the filename
            dayTime_image = f'stats/{player_name}_wins_distribution.png'
            plt.savefig(dayTime_image)
            #graph_dayTime
            # Load JSON data from file
            with open('message_hours.json', 'r') as file:
                data = json.load(file)


            # Get the wins data for the player and sort it by hour
            player_data = data[player_name]
            hours = sorted(map(int, player_data.keys()))
            wins = [player_data[str(hour)] for hour in hours]
    
            # Plotting
            plt.figure(figsize=(10, 6))
            plt.plot(hours, wins, marker='o', linestyle='-', color='orange', linewidth=2, markersize=8, label=player_name)
            plt.vlines(hours, ymin=0, ymax=wins, color='gray', linestyle='dotted', linewidth=1)  # Add vertical lines
            plt.xlabel('Hour of the Day', fontsize=12)
            plt.ylabel('Wins', fontsize=12)
            plt.title(f'Wins of Player {player_name} Across Each Hour of the Day', fontsize=14)
            plt.xticks(hours, fontsize=10)
            plt.yticks(fontsize=10)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.legend(loc='upper left', fontsize=10)
            plt.gca().set_facecolor('#f0f0f0')  # Set background color
            plt.tight_layout()
            hours_image = f'stats/{player_name}_hour_plot.png'
            plt.savefig(hours_image)  # Save plot to an image file


                   

            files = [
                discord.File(dayTime_image),
                discord.File(game_wins_image),
                discord.File(specificDay_image),
                discord.File(hours_image)
            ]

            all_time_stats = await channel.send(f"*{player_name} requested stats*",files=files)

            print(f"{player_name} all-time stats provided!")

   class Dalle_buttons2(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self):
        super().__init__(timeout=None) # timeout of the view must be set to None

    @discord.ui.button(label="reDo", custom_id="Dalle3_button2",  style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
    async def Dalle3reDo2_button__callback(self,interaction, button ):
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
       # wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
        wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdmgwNGgxazBlMGxpNjl3amV0ZDRibHl4ZGY1Nnp1MXdqM2Iyd2QzaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BASS1qt1KIQ2HTD5Gs/source.gif")
        channel.typing   
                            

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
    async def Dalle3_916_button__callback(self,interaction, button ):
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
      #  wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
        wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdmgwNGgxazBlMGxpNjl3amV0ZDRibHl4ZGY1Nnp1MXdqM2Iyd2QzaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BASS1qt1KIQ2HTD5Gs/source.gif")
        channel.typing   
                            

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
    async def Dalle3_169_button__callback(self,interaction, button ):
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
      #  wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
        wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdmgwNGgxazBlMGxpNjl3amV0ZDRibHl4ZGY1Nnp1MXdqM2Iyd2QzaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BASS1qt1KIQ2HTD5Gs/source.gif")
        channel.typing   
                            

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
        async def show_button_callback(self,interaction, button ):
            await interaction.response.defer()
            user_id =  interaction.user.id
            if user_id != 240554122510598146:
                print("pressed show button: " + str(user_id))
            Myconfig.setEchoMessageID(interaction.message.id)

            channel = client.get_channel(1101461174907830312)
            Myconfig.setEchoButtons(await channel.send(view=MyView()))


   class MyView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
        def __init__(self):
            super().__init__(timeout=None) # timeout of the view must be set to None

        async def common_button_function(self,  w, h, three, search_key, msgg1, redo, model):
            channel = client.get_channel(1101461174907830312)

            await Myconfig.getEchoButtons().delete()
            keyword = "echo"
            V4 = True
            

            ratio = "1.00"
            original_content  = ""
            enchanted_content = ""
            styled_content    = ""
                

                
            enchanted_content = prompts.get(str(search_key), {}).get("enchanted", "")
            original_content  = prompts.get(str(search_key), {}).get("original", "")
            styled_content    = prompts.get(str(search_key), {}).get("styled", "")   
            #support           = prompts.get(str(search_key), {}).get("support_prompt", "")             
            recent_action     = prompts.get(str(search_key), {}).get("latest_action", "")
            og_message     = prompts.get(str(search_key), {}).get("og_message", "")
            #mode     = prompts.get(str(search_key), {}).get("mode", "")
            neg_prompt        = prompts.get(str(search_key), {}).get("negative", "")
            clip1 = prompts.get(str(search_key), {}).get("clip1", "")
            clip2 = prompts.get(str(search_key), {}).get("clip2", "")
            t5 = prompts.get(str(search_key), {}).get("t5", "")
            #model     = prompts.get(str(search_key), {}).get("model", "")


            msgg2 = f"*Wait time: **up to 40sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396" 






            if recent_action == "random style":
                msg_prompt = styled_content
                neg_prompt = prompts.get(str(search_key), {}).get("negative", "")
            elif recent_action == "AI Enhance":
                msg_prompt = enchanted_content
            else:
                msg_prompt = original_content
            #msg_prompt = prompts[search_key]

            seed = 0

                

            msgg2 = f"*Wait time: **up to 40sec***"           
            #msgg2 = f"*Wait time: **up to 40sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
            embed_msg = embed = discord.Embed(description=t5, color=0x0000ff)
            
            # embed_redo = embed = discord.Embed(description=msg_prompt, color=0xff0000)
            #await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked
            

            wait_msg1 = await channel.send(msgg1)
            emb_msg =  await channel.send(embed=embed_msg)
            wait_msg2 = await channel.send(msgg2)
            #  wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
            #wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
          #  wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdmgwNGgxazBlMGxpNjl3amV0ZDRibHl4ZGY1Nnp1MXdqM2Iyd2QzaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BASS1qt1KIQ2HTD5Gs/source.gif")
      

          #  if model == "dreamshaperXL_v21TurboDPMSDE.safetensors" or model == "turbovisionxlSuperFastXLBasedOnNew_tvxlV431Bakedvae.safetensors" or model == "dreamshaperXL_turboDpmppSDEKarras.safetensors":
          #      mode = "speed"
          ##  else:
          #      mode = "quality"
            files, seed,filename = await generate_image_sd3(clip1,clip2,t5, neg_prompt, w, h, three )     
            #  VAE = False

                #files, image_name  = await generate_image_playground(V4, msg_prompt, neg_prompt, w , h, keyword, three, vae, lora, support)
            await wait_msg1.delete()
            await emb_msg.delete()
            await wait_msg2.delete()
            await wait_gif.delete()

            most_recent_key = max(prompts.keys())
            most_recent_entry = prompts[most_recent_key]
            message = await channel.fetch_message(og_message)


            new_message =   await message.reply(files=files, view=MainButtons())
            
            most_recent_original  = most_recent_entry["original"]
            most_recent_styled    = most_recent_entry["styled"]
            most_recent_enchanted = most_recent_entry["enchanted"]

            #   if not( most_recent_original == original_content or most_recent_styled == styled_content or most_recent_enchanted == enchanted_content):
            #      emb_msg =  await channel.send(embed=embed_msg)

            #if most_recent_original != original_content:
             #   emb_msg =  await channel.send(embed=embed_msg)

            # new_message =   await channel.send(files=files, view=MyView())
           # if redo:
           #   new_message =   await channel.send(files=files)
           # else:
            channel = client.get_channel(1101461174907830312)

            msg_id = new_message.id

            new_prompt = {
                f"{msg_id}": {
                    "og_message": og_message,
                    "original": original_content,
                    "styled": styled_content,  # Add your styled content here
                    "enchanted": enchanted_content,  # Add your enchanted content here
                    "negative": neg_prompt,  # Add your enchanted content here
                    "h": h,
                    "w": w,
                    "model": model,
                    "latest_action": recent_action,
                    "seed": seed,
                    "clip1": clip1,
                    "clip2": clip2,
                    "t5": t5,
                    "seed": seed,
                    "filename": filename
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
        async def redo_button_callback(self,interaction, button ):
            await interaction.response.defer()   
            redo = True
            three = False
            #message_id = interaction.message.id
            search_key = f"{Myconfig.getEchoMessageID()}"                
            msgg1 = f"*Redoing image with same prompt...*"

            w                 = prompts.get(str(search_key), {}).get("w", "")
            h                 = prompts.get(str(search_key), {}).get("h", "")
            model             = prompts.get(str(search_key), {}).get("model", "")
            
            await self.common_button_function(w, h, three,search_key, msgg1, redo, model )

            #  print(f"The button was pressed on message with ID: {message_id}")

        @discord.ui.button(label="x3", custom_id="x3_button", row = 1, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def x3_button_callback(self,interaction, button ):
            await interaction.response.defer()
            redo = True
            three = True
            #message_id = interaction.message.id
            search_key = f"{Myconfig.getEchoMessageID()}" 
            msgg1 = f"*Redoing 3 images with same prompt...*"

            w                 = prompts.get(str(search_key), {}).get("w", "")
            h                 = prompts.get(str(search_key), {}).get("h", "")
            model             = prompts.get(str(search_key), {}).get("model", "")
            
            await self.common_button_function(w, h, three,search_key, msgg1, redo, model )


        @discord.ui.button(label="8:5", custom_id="8:5_button", row = 2, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def landsp85_redo_button_callback(self,interaction, button ):
            await interaction.response.defer()

            search_key = f"{Myconfig.getEchoMessageID()}"
            model             = prompts.get(str(search_key), {}).get("model", "")
            mode     = prompts.get(str(search_key), {}).get("mode", "")
            if mode == "elle":
                w = 768
                h = 512
            else:
                w = 1216
                h = 768
            redo = False
            three = False
            msgg1 = f"*Redoing image with 8:5 aspect ratio...*"
            #message_id = interaction.message.id


            await self.common_button_function(w, h, three,search_key, msgg1, redo, model )




        @discord.ui.button(label="16:9", custom_id="16:9_button", row = 2, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def landsp_redo_button_callback(self,interaction, button ):
            await interaction.response.defer()

            search_key = f"{Myconfig.getEchoMessageID()}"
            model             = prompts.get(str(search_key), {}).get("model", "")
            mode     = prompts.get(str(search_key), {}).get("mode", "")
            if mode == "elle":
                w = 768
                h = 512
            else:
            
                w = 1344
                h = 768
            redo = False
            three = False
            msgg1 = f"*Redoing image with 16:9 aspect ratio...*"
            #message_id = interaction.message.id

            await self.common_button_function(w, h, three,search_key, msgg1, redo, model )



        @discord.ui.button(label="21:9", custom_id="21:9_button", row = 2, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def landsp219_redo_button_callback(self,interaction, button ):
            await interaction.response.defer()

            search_key = f"{Myconfig.getEchoMessageID()}"
            model             = prompts.get(str(search_key), {}).get("model", "")
            mode     = prompts.get(str(search_key), {}).get("mode", "")
            if mode == "elle":
                w = 768
                h = 512
            else:
            
                w = 1536
                h = 640
            redo = False
            three = False
            msgg1 = f"*Redoing image with 21:9 aspect ratio...*"
            # message_id = interaction.message.id

            await self.common_button_function(w, h, three,search_key, msgg1, redo, model )



        @discord.ui.button(label="Upscale x2", custom_id="upscalex2_button", row = 2, style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
        async def upscalex2_redo_button_callback(self, interaction, button ):
            await interaction.response.defer()

            await Myconfig.getEchoButtons().delete()
            search_key = f"{Myconfig.getEchoMessageID()}"
            enchanted_content = prompts.get(str(search_key), {}).get("enchanted", "")
            original_content  = prompts.get(str(search_key), {}).get("original", "")
            styled_content    = prompts.get(str(search_key), {}).get("styled", "")   
            #support           = prompts.get(str(search_key), {}).get("support_prompt", "")             
            recent_action     = prompts.get(str(search_key), {}).get("latest_action", "")
            og_message     = prompts.get(str(search_key), {}).get("og_message", "")
            #mode     = prompts.get(str(search_key), {}).get("mode", "")
            neg_prompt        = prompts.get(str(search_key), {}).get("negative", "")
            clip1 = prompts.get(str(search_key), {}).get("clip1", "")
            clip2 = prompts.get(str(search_key), {}).get("clip2", "")
            t5 = prompts.get(str(search_key), {}).get("t5", "")
            filename = prompts.get(str(search_key), {}).get("filename", "")

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
            #  wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdmgwNGgxazBlMGxpNjl3amV0ZDRibHl4ZGY1Nnp1MXdqM2Iyd2QzaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BASS1qt1KIQ2HTD5Gs/source.gif")
            channel.typing                          
            lora = False
            files = []
            three = False
            vae = True
            support = msg_prompt
            #neg_prompt = ""
                        
            files,seed, filename = await upscale_sd3(clip1, clip2, t5, neg_prompt,w, h, three, filename, seed)

            
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
                    "og_message": og_message,
                    "original": original_content,
                    "styled": styled_content,  # Add your styled content here
                    "enchanted": enchanted_content,  # Add your enchanted content here
                    "negative": neg_prompt,  # Add your enchanted content here
                    "h": h,
                    "w": w,
                    "model": model,
                    "latest_action": recent_action,
                    "seed": seed,
                    "clip1": clip1,
                    "clip2": clip2,
                    "t5": t5,
                    "seed": seed,
                    "filename": filename
                }
            }
            prompts.update(new_prompt)
            try:
                with open("prompts.json", "w") as file:
                    json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                    file.write('\n')
            except (FileNotFoundError, PermissionError, IOError) as e:
                print(f"Error: {e}")


        @discord.ui.button(label="5:8", custom_id="5:8_button", row = 3, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def port58_redo_button_callback(self,interaction, button ):
            await interaction.response.defer()
            
            search_key = f"{Myconfig.getEchoMessageID()}"
            model             = prompts.get(str(search_key), {}).get("model", "")
            mode     = prompts.get(str(search_key), {}).get("mode", "")
            if mode == "elle":
                w = 512
                h = 768
            else:

                w = 768
                h = 1216
            redo = False
            three = False
            msgg1 = f"*Redoing image with 5:8 aspect ratio...*"
            #message_id = interaction.message.id

            await self.common_button_function(w, h, three,search_key, msgg1, redo, model )



        @discord.ui.button(label="9:16", custom_id="9:16_button", row = 3, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def portr_redo_button_callback(self,interaction, button ):

            search_key = f"{Myconfig.getEchoMessageID()}"
            model             = prompts.get(str(search_key), {}).get("model", "")
            mode     = prompts.get(str(search_key), {}).get("mode", "")
            if mode == "elle":
                w = 512
                h = 768
            else:

                w = 768
                h = 1344
            three = False
            redo = False
            msgg1 = f"*Redoing image with 9:16 aspect ratio...*"
            #message_id = interaction.message.id

            await self.common_button_function(w, h, three,search_key, msgg1 ,redo, model )




        @discord.ui.button(label="9:21", custom_id="9:21_button", row = 3, style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
        async def portr921_redo_button_callback(self,interaction, button ):

            search_key = f"{Myconfig.getEchoMessageID()}"
            model             = prompts.get(str(search_key), {}).get("model", "")
            mode     = prompts.get(str(search_key), {}).get("mode", "")
            if mode == "elle":
                w = 512
                h = 768
            else:


                w = 640
                h = 1536
            three = False
            redo = False
            msgg1 = f"*Redoing image with 9:21 aspect ratio...*"
            #message_id = interaction.message.id

            await self.common_button_function(w, h, three,search_key, msgg1 ,redo, model )






        @discord.ui.button(label="Dalle-3", custom_id="Dalle32_button", row = 4,  style=discord.ButtonStyle.secondary) # Create a button with the label "😎 Click me!" with color Blurple
        async def Dalle3reDo2_button__callback(self,interaction, button ):
            await interaction.response.defer()
            await Myconfig.getEchoButtons().delete()
            channel = client.get_channel(1101461174907830312)
            #  model = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"
            #message_id = interaction.message.id
            search_key = f"{Myconfig.getEchoMessageID()}"
            original_content  = prompts.get(str(search_key), {}).get("original", "")
            msgg = "*Echoing image using Dalle-3... wait time: **up to 40sec*** \nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"

            wait_msg = await channel.send(msgg)
            # wait_gif = await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
            #wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")
          #  wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdmgwNGgxazBlMGxpNjl3amV0ZDRibHl4ZGY1Nnp1MXdqM2Iyd2QzaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BASS1qt1KIQ2HTD5Gs/source.gif")
            channel.typing    
                            
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
                await channel.send('Tavs pieprasījums tika noraidīts.')





        @discord.ui.button(label="AI Enhance", custom_id="ench_button", row = 1, style=discord.ButtonStyle.success) # Create a button with the label "😎 Click me!" with color Blurple
        async def enhance_button_callback(self,interaction, button ):
            await interaction.response.defer()

            V4 = True
           # neg_prompt = "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)"
            search_key = f"{Myconfig.getEchoMessageID()}"
            model             = prompts.get(str(search_key), {}).get("model", "")
            mode     = prompts.get(str(search_key), {}).get("mode", "")
            if mode == "elle":
                w = 512
                h = 512
            else:
                w = 1024
                h = 1024
            keyword = "echo"
            await Myconfig.getEchoButtons().delete()


            channel = client.get_channel(1101461174907830312)

            #message_id = interaction.message.id
            search_key = f"{Myconfig.getEchoMessageID()}"

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
            mode              = prompts.get(str(search_key), {}).get("mode", "")
            og_message        = prompts.get(str(search_key), {}).get("og_message", "")
            #ratio             = prompts.get(str(search_key), {}).get("ratio", "")
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
            enchanting =  await channel.send(enhancing_msg) 
            ench_prompt = await enchPrompt_gpt4o("hyper detailed, " + original_content)
            #support = await enchPrompt_support(msg_prompt)
            support = ench_prompt
            await enchanting.delete()

            msgg1 = f"*Enchanting image with same prompt...*"
            if mode == "speed":
                msgg2 = f"*Wait time: **up to 6sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"
            else:
                msgg2 = f"*Wait time: **up to 40sec***"

            embed_msg = embed = discord.Embed(description=ench_prompt, color=0x00ff00)

            ench_prompt_done = "**Enchanted:** " + ench_prompt
            embed_ench_prompt_done = embed = discord.Embed(description=ench_prompt_done, color=0x00ff00)
            #await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked
            

            wait_msg1 = await channel.send(msgg1)
            emb_msg =   await channel.send(embed=embed_msg)
            wait_msg2 = await channel.send(msgg2)
         #   wait_gif =  await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
           # wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif") 
          #  wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdmgwNGgxazBlMGxpNjl3amV0ZDRibHl4ZGY1Nnp1MXdqM2Iyd2QzaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BASS1qt1KIQ2HTD5Gs/source.gif")

            three = False
            files, seed, filename = await generate_image_sd3(ench_prompt,neg_prompt, w, h, three )
                #files, image_name  = await generate_image_playground(V4, ench_prompt, neg_prompt, w , h, keyword, three, vae, lora, support)
            await wait_msg1.delete()
            await emb_msg.delete()
            await wait_msg2.delete()
            await wait_gif.delete()

            #emb_ench_prompt_done =   await channel.send(embed=embed_ench_prompt_done)
            channel = client.get_channel(1101461174907830312)
            message = await channel.fetch_message(og_message)
        #    new_message =   await message.reply(files=files, view=MainButtons())            
            new_message =   await message.reply("*Enhanced*",files=files, view=MainButtons())


            msg_id = new_message.id

            new_prompt = {
                f"{msg_id}": {
                    "og_message": og_message,
                    "original": original_content,
                    "styled": styled_content,  # Add your styled content here
                    "enchanted": ench_prompt,  # Add your enchanted content here
                    "negative": neg_prompt,  # Add your enchanted content here
                    "h": h,
                    "w": w,
                    "model": model,
                    "latest_action": "AI Enhance",
                    "mode": mode,
                    "seed": seed,
                    "filename": filename
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





        @discord.ui.button(label="Random style", custom_id="random_button", row = 1, style=discord.ButtonStyle.danger, disabled = True) # Create a button with the label "😎 Click me!" with color Blurple
        async def random_button_callback(self,interaction, button ):
            await interaction.response.defer()
            channel = client.get_channel(1101461174907830312)

            V4 = True
            neg_prompt = "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)"
            w = 1024
            h = 1024
            keyword = "echo"
            await Myconfig.getEchoButtons().delete()


            seed = 0
            

            #message_id = interaction.message.id
            search_key = f"{Myconfig.getEchoMessageID()}"

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
           # mode              = prompts.get(str(search_key), {}).get("mode", "")
            model             = prompts.get(str(search_key), {}).get("model", "") #sdxlUnstableDiffusers_v8HeavensWrathVAE.safetensors
           # ratio              = prompts.get(str(search_key), {}).get("ratio", "")
          #  model             = "sdxlUnstableDiffusers_v9DIVINITYMACHINE.safetensors"

           # else:
                #model             = "sdXL_v10VAEFix.safetensors" 




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


            msgg2 = f"You are using **quality mode**. *Wait time: **up to 40sec***\nInfo: https://discord.com/channels/1030490392057085952/1132935102813454396"

            embed_msg = embed  = discord.Embed(description=msg_prompt, color=0xff0000)
            embed_style = embed = discord.Embed(description=embed_Style, color=0xff0000)

            #await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked
            

            wait_msg1 = await channel.send(msgg1)
            emb_msg =   await channel.send(embed=embed_msg)
            wait_msg2 = await channel.send(msgg2)
          #  wait_gif =  await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExazBhbGl6eDRvZmRjZTYydDRibWk2cGlodG01dWo1ZHp0bG56eWR6YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BafwY2lTD28xjy1GFP/giphy.gif") 
            #wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmMzb2J4b2M5ajEwd2Z4azByc3RqZWE2NTlxNnN0a2xmbDdtNnF2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QKhRz2iaGw4v5rNIx7/giphy.gif")  
           # wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2Vzc3BsbXBmdHk0NW1odzd4NnBvdm4wOG10NjZnZzV0bHA4NHN0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0oHZSBUjawh3OLRbO9/giphy.gif")
            wait_gif = await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdmgwNGgxazBlMGxpNjl3amV0ZDRibHl4ZGY1Nnp1MXdqM2Iyd2QzaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BASS1qt1KIQ2HTD5Gs/source.gif")


            three = False
            files = await generate_image_sd3(formatted_rand_prompt,neg_prompt, w, h, three )  
            await wait_msg1.delete()
            await emb_msg.delete()
            await wait_msg2.delete()
            await wait_gif.delete()

            embed_style =   await channel.send(embed=embed_style)
            new_message =   await channel.send(f"*Style: {random_style_name}*",files=files, view=MainButtons())


            msg_id = new_message.id

            new_prompt = {
                f"{msg_id}": {
                    "original": original_content,
                    "styled": formatted_rand_prompt,  # Add your styled content here
                    "enchanted": enchanted_content,  # Add your enchanted content here
                    "negative": neg_prompt,  # Add your enchanted content here
                    "h": h,
                    "w": w,
                    "model": model,
                    "latest_action": "random style",
                    "seed": seed,
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


   @client.command()
   async def sync(ctx):
        print("sync command")
        if ctx.author.id == 240554122510598146:
            #guild = discord.Object(id=1085598182102278174)  # Replace with your server's ID
            synced = await client.tree.sync()
            await ctx.send(f'Command tree synced. {len(synced)}')
        else:
            await ctx.send('You must be the owner to use this command!')

   @client.event
   async def on_ready():  
    #client.add_view(MyView()) # Registers a View for persistent listening
    #client.add_view(Dalle_buttons2()) # Registers a View for persistent listening
   # client.add_view(gif_buttons()) # Registers a View for persistent listening
    #client.add_view(MainButtons()) # Registers a View for persistent listening
   # client.add_view(statsButton()) # Registers a View for persistent listening
    #client.add_view(faceid_button()) # Registers a View for persistent listening
    #client.add_view(Model_mode_buttons()) # Registers a View for persistent listening

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

    Myconfig.setThreadID(await get_threadID())

    channel_id = Myconfig.getChatChannel() 
    channel = client.get_channel(channel_id)

    await scan_unsaved_msg(client,channel)

    await notify_nameday(channel)
    await notify_weather(channel, 'Riga', False)
    await notify_weather(channel, 'Liepaja', True)
   ############################## register messages up until specifc one #################################

   ############# Varda dienas ################

    print("successfully finished startup")
   ############# Varda dienas ################


    # Izveido statusuw
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="leafs falling 🍂🍁"))


    # Izveido grafiku, kad sūta ziņas pats
    asyncio.create_task(schedule_messages()) #@#

    channel = client.get_channel(SCREENSHOT_CHANNEL_ID)
    #channel = client.get_channel(1085598243808886944)


    CHECKMARK_EMOJI = "✅"

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
                    MyMsgCollector.setPreviousWins(MyMsgCollector.getPreviousWins() + multip)
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
                MyMsgCollector.setPreviousWins(MyMsgCollector.getPreviousWins() + 1)

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



    PreviousWins_str = str(MyMsgCollector.getPreviousWins())
    phrase_rec = phrases_awayScore[PreviousWins_str]    
    random.seed(time.time())
    phrases_reason = random.choice(list(phrases_awayReason.values()))
    userr_id = "190926234878738433"
    annoucment = f"{timeOfDay()}, {phrases_reason}.\nDuring this time, you have scored {MyMsgCollector.getPreviousWins()} wins. {phrase_rec}"
    channel = client.get_channel(SCREENSHOT_CHANNEL_ID) 
   # role = channel.guild.get_role(1030500402023628850)
    #role2 = channel.guild.get_role(1089589791466721312)
   # role3 = channel.guild.get_role(1033676791166025788)


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




   @client.command(name='palidziba', description='View full list of my abilities.') #@#
   async def palidziba(ctx):
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
       await ctx.send('*Somebody used **/palidziba** command on me*')
       mention = await ctx.send(f'{user.mention}, I just slid into your DMs.')
       await asyncio.sleep(5)
       await mention.delete()
   

   @client.command(name = 'info', description = 'View rules and information about Resnums.' )
   async def info(ctx):

       response = 'Winning any kind of game gives you **one** Resns point. When adding screenshot you can also mention your colleagues, so they get win counted as well.\n'\
                  'MW2 resnums is counted if game has been **WON** and **ACHIEVED** minimal kill requirements!\n'\
                  'Search n destroy, ranked, free for all and big maps(32 teammates) need **JUST** a **WIN**. Other modes need **AT LEAST** 35 kills and a **WIN**.\n'\
                  'For real sweat-lords managing  to get **AT LEAST** 20 kills in WARZONE as a prize will be ***Mega XXL Resns***.\n'\
                  'TOP5 in each game category will earn title **Mēneša Resnais** at the end of the month.'
      #await message.channel.typing() #@#
       #await asyncio.sleep(2) #@#
       await ctx.send(response)

   allowed = [240554122510598146, 391668973315424277]

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



   chat_history = deque(maxlen=10)
   def add_message_chat_history(sender, message):
        chat_history.append(f'"{sender}": "{message}"')
   def get_chat_history():
        return "chat_history = '''\n" + ",\n".join(chat_history) + "\n'''"
   
   
   ########### SECURITY  #################################
   def has_role(member):
    role1_id = 1030581546966597742  # OG member
    role2_id = 1089589791466721312  # member
    role3_id = 1082740980609978378
    role4_id = 1061384574002790420 
    role5_id = 1087337344320929793 #santehniķi
    role6_id = 1030530963291254814 # basic user
    role7_id = 1086940826829078531 
    role7_id = 1088108792018911372 

    #role8_id = 1030530963291254814 # basic
    author_roles = member.roles
    return any(role.id in (role1_id, role2_id, role3_id, role4_id, role5_id, role6_id, role7_id) for role in author_roles)

   def extract_text_and_link(input_string):
        # Regular expression pattern to match URLs
        url_pattern = re.compile(r'(https?://\S+)')

        # Extract the URL from the input string
        url_match = url_pattern.search(input_string)

        if url_match:
            url = url_match.group(1)
            text = input_string[:url_match.start()].strip()

            # Check if the URL is not for a GIF or video
            if not any(ext in url.lower() for ext in ['.gif', '.mp4', '.avi', '.mov', '.webp']):
                return text, url
            else:
                return text, None
        else:
            return input_string.strip(), None
  ########### SECURITY  ##################################

#############################################################

   pattern = re.compile(r'\b(ay|ey|ou|au|mamma|mammu|aloha|mam|mamm|muterit|muterite|mutere|muter|mama|mammai)\b')


  ############################## NEW ################################
         
   @client.event
   async def on_message(message):
        genEnabled = True 
        usingRentGPU = False
        gptON = True

        
        
        if message.channel.id == Myconfig.getChatChannel():
             
             author_name = message.author.name
             if author_name == "Resnā mamma":
                 author_name = "Elizabete" 
             if author_name == "theeight":
                 author_name = "Aģents E" 
             if author_name == "daisyvongrim":
                 author_name = "prosta desa" 
             if author_name == "megga7866":
                 author_name = "Aģente K"
             if author_name == "mitraisbandits":
                 author_name = "Kapars"
             if author_name == "jaanisjc":
                 author_name = "Aģents J"                     
             add_message_chat_history(author_name,message.content)
             if message.author.bot:
                 Myconfig.setElizabeteLastMsg(True)
             else:
                 Myconfig.setElizabeteLastMsg(False)



        if message.content.startswith('!'):
        # Process commands
          await client.process_commands(message)
          return
        

        ################# SECURITY ######################
        if message.guild is None:
            # Handle DMs differently here
            print(f'$ {message.author.name} knocking in DM - {message.content} $')
            return

       # if not has_role(message.author):
            # If the author doesn't have either of the two specific roles, return from the function
        #    if message.channel.id != 1101461174907830312:
         #       print(f'$ {message.author.name} knocking in channel - {message.content} $')
          #      return    
        ################# SECURITY ######################
        #all
       # tones = ["sarcastic", "assertive", "sad", "cynical", "indignant", "contemplative", "witty", "persuasive", "rude", "angry", "romantic", "humorous", "adventurous", "creative", "friendly", "optimistic", "pessimistic", "nostalgic", "hopeful", "enthusiastic", "ambivalent", "descriptive", "suspenseful", "factual", "informative", "playful", "inspiring", "melancholic", "mysterious", "objective", "subjective", "sympathetic", "empathetic", "reflective", "confident", "satirical", "ironic", "sincere", "cautious", "credible", "informal", "formal", "professional", "scholarly", "inspirational", "controversial", "diplomatic", "nurturing", "authoritative", "didactic", "patronizing", "dismissive", "unemotional", "nihilistic"]
       # tones = ["sarcastic", "assertive", "sad", "cynical", "indignant", "contemplative", "witty", "persuasive", "rude", "angry", "romantic", "humorous", "adventurous", "creative", "friendly", "optimistic", "pessimistic", "nostalgic", "hopeful", "enthusiastic", "ambivalent", "descriptive", "suspenseful", "factual", "informative", "playful", "inspiring", "melancholic", "mysterious",  "subjective", "sympathetic", "empathetic", "reflective", "confident", "satirical", "ironic", "sincere",  "credible", "informal", "professional",  "inspirational", "controversial", "nurturing", "authoritative", "didactic",  "dismissive", "unemotional", "nihilistic"]
        tones = [
        "Joker chaotic",
        "Hannibal Lecter brilliant",
        "Vito Corleone authoritative",
        "Dracula aristocratic",
        "Ebenezer Scrooge miserly",
        "HAL 9000 detached",
        "Voldemort ruthless",
        "Thanos determined",
        "Loki mischievous",
        "Darth Vader menacing",
        "Sauron malevolent",
        "Maleficent vengeful",
        "Cruella de Vil vain",
        "Scar cunning",
        "Green Goblin maniacal",
        "Lex Luthor calculating",
        "Bane brutal",
        "Norman Bates disturbed",
        "Red Skull fanatical",
        "The Wicked Witch of the West wicked"
        ]
        #serious 
      #  tones = ["satirical", "witty", "amusing"]
        atdarini_description = None
        if "atdarini" in message.content.lower():
            first_two_words,   atdarini_description_response = process_string_for_atdarini_two(message.content.lower())
            first_three_words, atdarini_description = process_string_for_atdarini(message.content.lower())            

        random.seed(time.time())
        selected_tone = random.choice(tones)
        selected_tone = selected_tone.upper()
        #selected_tone = "rude clown"
        if 'apsveic' in message.content:
            selected_tone = "festive"
        #selected_tone = "festive"
        Myconfig.setBotMsg(False)  
        mind = f"You are a wise all-knowing person named 'Elizabete' who was created 15.03.2023 by Jānis. You can do anything. Respond mainly in Latvian language but others as well if asked. Do not mention you are language model or program.  You answer to any kind of question and request. You can address specific users when requested. One of your tasks is to count game wins.\
                Discord server is called 'Asās resnās mērcītes'.\
                Pretend you can give compliments and advices\
                Use {selected_tone} tone.\
                When asked about people give long response, Use {selected_tone} tone.. \
                Pretend you are creative storyteller with vivid imagination whos every story is original. Use {selected_tone} tone.\
                Todays date is {getDate()}.\
                Precīzs pulkstens šobrīd ir {getTime()}"




########################### UPDATED ###################
        # Ignorēt ziņas no citiem botiem
        if message.author.bot:
            if "ģenerē" in message.content or "atdarini" in message.content or "parādi" in message.content:
                MyMsgCollector.setMsgCount(0)
                Myconfig.setBotMsg(True)
            else:
                MyMsgCollector.setMsgCount(0)
                Myconfig.setBotMsg(True)
                return

        if message.channel.id == Myconfig.getChatChannel():
            Myconfig.setMesageNr(Myconfig.getMessageNr() + 1)
        if Myconfig.getMessageNr() >= Myconfig.getReaction_threshold():
            emojis = message.guild.emojis
            if emojis:
                # Choose a random emoji
                emoji = random.choice(emojis)
                # React to the message with the random emoji
                await message.add_reaction(emoji)
            Myconfig.setMesageNr(0)
            Myconfig.setReaction_threshold()
        

        if "onlyfan leaks here" in message.content.lower():
            admin = client.get_user(240554122510598146)
            await admin.send(f"SPAM DETECTED! Message from {message.author} in {message.channel.name}: {message.content}")

            await message.delete()
            return
########################### UPDATED ###################


        if message.channel.id == Myconfig.getChatChannel():

             ID = message.author.id
             author_name = message.author.name
             file_to_update =  "IDs.txt"

             if author_name == "Resnā mamma":
                 author_name = "Elizabete"

             add_username_and_id_if_not_exists(author_name, ID, file_to_update)           


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
             await add_message_to_thread(client_gpt, Myconfig.getThreadID(), new_message)
            # print(new_message)
             #print("added")

             latest_msg_ID["ID"] = message.id
             with open("most_recent_saved_msg.json", "w") as file:
                    json.dump(latest_msg_ID, file, indent=4)  # You can adjust the indent for pretty printing

 ############################################# CHATBOT SECTION ########################################



        # Check if the message is a reply to the chatbot user who wrote after gudrais command
        if message.reference and message.reference.resolved.author == client.user:
                    for embed in message.reference.resolved.embeds:
                        if embed.description:
                            generated_text = await gudrais_response(message, gptON)
                            embed = discord.Embed(description=generated_text, color=0x00ff00)
                            await message.channel.send(embed=embed)
                            return
        #Check if message contains trigger word
        if pattern.search(message.content.lower()):
            hasImage = False

            message_modif = message.content.lower()
            # Pārbauda vai ir pieminēts lietotājs ziņā
            parts = message.content.split() #@#
            mentioned_user = None
            response = None

            #Check if message contains image
            if message.reference is not None:
                try:
                    zina_ar_bildi = await message.channel.fetch_message(message.reference.message_id)
                    bildes_url =  zina_ar_bildi.attachments[0].url
                    hasImage = True
                except Exception as e:
                    hasImage = False
                    print(f"An error occurred: {e}")           
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

            # Remove trigger word from message
            for word in ['ay', 'ey', 'ou', 'au', 'aloha', 'eu', 'mamma', 'mammu', 'mam', 'mamm', 'muterit', 'muterite', 'mutere', 'muter', 'mammai']:
                 message_modif = ' '.join([w.strip() for w in message_modif.split() if w.strip() != word])
                 question, web_link = extract_text_and_link(message_modif)
            #if message.author.id == 909845424909729802:
            #    return
            key_phrase = ["pajautā jautājumu", "atdarini", "gudrais"]

                    

                    


            if  any(word in message_modif for word in key_phrase) and mentioned_user:
                if message_modif.startswith('pajautā jautājumu'):
                    random.seed(time.time())
                    response = random.choice(question_list)
                    message_to_send = f"{mentioned_user.mention}, {response}"

                    await asyncio.sleep(1)
                    await message.channel.send(message_to_send)
############################### NEW ################################



                # Atdarina lietotāja profila bildi
                elif atdarini_description is not None and message.reference is None:
                        atdarini_person(message, atdarini_description, prompts)

                # Atdarina lietotāja profila bildi random ar chatgpt bez apraksta
                elif "atdarini " in message.content.lower() and len(message.mentions) > 0 and message.reference is None:
                    if len(message.mentions) > 0:
                        
                        avatar_url = message.mentions[0].display_avatar.url
                        avatar_response = requests.get(avatar_url)
                        # Check if the avatar image is a GIF
                        await message.channel.typing()
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
                    await message.channel.typing()
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
                        model='gpt-4o',
                        messages = [
                        {"role": "system", "content": mind },    
                        {"role": "user", "content": f"user message: '{user_input}'. Give random response about person as reply to him including some facts. Use {selected_tone} tone. Use latvian language.  Do not as questions."}
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


               mind = f"You just moved to new server. You are a wise all-knowing person named 'Elizabete' who was created 15.03.2023 by Jānis. You can do anything. Respond mainly in Latvian language but others as well if asked. Do not mention you are language model or program.  You answer to any kind of question and request. You can address specific users when requested. One of your tasks is to count game wins.\
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
                   
 
               await message.channel.typing()
               if gptON:
                   gpt_key               = os.getenv("GPT")
                   client_chat = OpenAI(api_key=gpt_key)

                   response =   client_chat.chat.completions.create(
                        model='gpt-4o',
                        messages = [
                        {"role": "system", "content": mind},
                        {"role": "user", "name" : vards, "content": f'{user_input}.  Do not as questions.'}
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
                   await message.channel.send(embed=embed)
                   #update_message_data(gudrais_response.id, thread.id, file_name)
                   return
               else:
                    vards = message.author.name
                    claude_key               = os.getenv("CLAUDE")
                    #pass_prompt = prompt
                    #context = prompt

                    response = anthropic.Anthropic(api_key=claude_key).messages.create(
                        model="claude-3-opus-20240229",
                        max_tokens=2500,
                        temperature=0.6,
                        system= mind,
                        messages=[
                             {"role": "user", "content": f"user ({vards}) f'{user_input}.  Do not as questions."}
                        ]
                    )

                    response = response.content[0].text
                    generated_text = response
                    embed = discord.Embed(description=generated_text, color=0x00ff00)
                    await message.channel.send(embed=embed)
                    #update_message_data(gudrais_response.id, thread.id, file_name)
                    return
 ############################### NEW ################################   
            elif web_link is not None:
                await message.channel.typing()
                scraped_text = ""
                gpt_key               = os.getenv("GPT")
                client_chat = OpenAI(api_key=gpt_key)   
                url = web_link  # Replace with the target URL
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                response = requests.get(url, headers=headers)
                current_zina = question
                if response.status_code == 200:
                    # Step 2: Parse the content of the page
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Step 3: Extract text from specific elements
                    paragraphs = soup.find_all('p')
                    if paragraphs:
                        for p in paragraphs:
                            scraped_text = scraped_text + p.get_text()
                            #print(p.get_text())
                        #print(scraped_text)
                        responsee = client_chat.chat.completions.create(
                        model='gpt-4o',
                        messages = [
                        {"role": "system", "content": f'''Your name is "Elizabete". People also call you "mamma". You were created 15.03.2023.  Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. Reply with short response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Do not mention which tone using. Sometimes use emojis
                        Text from requested website: {scraped_text} '''},
                        {"role": "user", "name" : author_name, "content": f"users wrote '{current_zina}' give human-like detailed but compact opinion in few sentences about given website text. Do not ask questions."}
                        ],
                        max_tokens=4000,
                        n=1,
                        stop=None,
                        temperature=0.6,
                        )
                        response = responsee.choices[0].message.content
                        response = response.replace('"', '')
                        response = response.replace("'", "")
                        await message.channel.send(response)
                        return
                    else:
                        message.channel.send("Neko neatradu.")
                        return
    
                else:
                        message.channel.send("Nevarēju atgūt lapu.")
                        return
                return
 # Tiek ģenerēta bilde ar Dalle 3
            elif "ģenerē" in message.content.lower() or "genere" in message.content.lower():
                    keyword = message_modif.split()[0]
                # Get user input from message

                    user_input = message.content.lower().split(keyword)[1]
                    #input_en = translateMsg(user_input)
                    input_en = user_input
                    await message.channel.typing()
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
                    except:
                        await message.channel.send('Tavs pieprasījums bija pārāk horny vai aizskarošs, priekšnieki neļauj man izpausties.')
                        return


################################################ TEST ############################ 768
            elif "echosketch" in message.content.lower() or "echoSketch" in message.content.lower():
                keyword = message_modif.split()[0]
                prompt_sketch = message.content.lower().split(keyword)[1]
                sd3_key                 = os.getenv('SD3')
                message.channel.typing
                messageID = message.id
                sketch_file_name = ""
                if message.attachments:
                    for attachment in message.attachments:
                        if attachment.content_type.startswith('image'):
                            # Construct the file path
                            sketch_file_name = f"{messageID}_{attachment.filename}"
                            save_path = os.path.join("./sketches", sketch_file_name)
                            # Download the image and save it locally
                            await attachment.save(save_path)
                else:
                    new_message = await message.reply("Nav pievienota bilde.")
                    return
                        #print(f"Saved image as {sketch_file_name} in ./sketches")

                msgg = "*Upgrading sketch...*"
                wait_msg = await message.channel.send(msgg)
                wait_gif = await                     message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmZ6d2YzMDllNDR2bzBmenc0dnl1ZGp0b3RqcW9iaGgzcjA4Mm1obyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BASS1qt1KIQ2HTD5Gs/giphy.gif")
                try:
                    response = requests.post(
                        f"https://api.stability.ai/v2beta/stable-image/control/sketch",
                        headers={
                            "authorization": f"Bearer {sd3_key}",
                            "accept": "image/*"
                        },
                        files={
                            "image": open(f"./sketches/{sketch_file_name}", "rb")
                        },
                        data={
                            "prompt": prompt_sketch,
                            "control_strength": 0.7,
                            "output_format": "png"
                        },
                    )
                except:
                    new_message = await message.reply("Pārāk daudz pikselu bildei, vajag resize uz mazāku.")
                    return


                if response.status_code == 200:
                    with open(f"./sketches_done/{messageID}.png", 'wb') as file:
                       file.write(response.content)
                       file = discord.File(f"./sketches_done/{messageID}.png")
                       await wait_msg.delete()
                       await wait_gif.delete()                        
                       new_message = await message.reply(file=file)
                       msg_id = new_message.id
                       new_prompt = {
                            f"{msg_id}": {
                                "original": prompt_sketch,
                                "og_message": message.id,
                                "sketch_filename": sketch_file_name,
                                "model": "sd3",
                                "last_action": "original",
                                "mode": "sd3",
                            }
                        }

                       prompts.update(new_prompt)
                       with open("prompts.json", "w") as file:
                            json.dump(prompts, file, indent=4)
                            file.write('\n')
                       return

                else:
                    await wait_msg.delete()
                    await wait_gif.delete()                        
                    new_message = await message.reply("Kaut kas nogāja greizi. Iespējams bildei parāk daudz pikselu, vajag resize uz mazāku. (max 9,437,184 pixels)")
                    raise Exception(str(response.json()))

                    return



                return

# Ģenerē bildi pēc promt ar stable diffusion, kas tiek hostēts uz paša pc
            elif "generate" in message.content.lower() or "genere" in message.content.lower() or message_modif.startswith("echo") or message_modif.startswith("echo1") or message_modif.lower().startswith("echoai") or message_modif.lower().startswith("echoais"):
                    if not genEnabled:
                        print("genenabled return")
                        return
                    keyword = message_modif.split()[0]
                # Get user input from message
               #try:
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
                            message.channel.typing    
                            
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
                    AI = False
                    V4 = False

                    #neg_prompt = "naked, nude,  easynegative, ng_deepnegative_v1_75t"
                    neg_prompt = "(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch)"

                    prompt = message.content
                    words = message.content.split()

                    if "portrait" in prompt:
                        port = True
                        h = 1280
                        w = 768

                    elif "landscape" in prompt:
                        land = True
                        w = 1280
                        h = 768

                    ################ look for negative prompt
                    result = set_resolution_from_ratio(prompt)
                    if result is not None:
                         resolution, prompt = result
                         width, height = resolution.split('x')
                         w = int(width)
                         h = int(height)
                    content = prompt                   





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





##################### 


                    if usingRentGPU:
            
                        print("usinggpu")
                        model = "sd3"

                        msgg = "*Echoing image...*"
                        wait_msg = await message.channel.send(msgg)
                        neg_prompt = ""

                        wait_gif = await                     message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmZ6d2YzMDllNDR2bzBmenc0dnl1ZGp0b3RqcW9iaGgzcjA4Mm1obyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BASS1qt1KIQ2HTD5Gs/giphy.gif")
                        message.channel.typing                           
                        files = []
                        three = False
                        #vae = True
                        vae = False
                        support = input_en
                        #pixart_prompt = await new_enchPrompt_pixart(input_en)
                        #print(elle_prompt)
                        #neg_prompt = ""
                        seed = 0
                        w = 1024
                        h = 1024
                        try:
                            prompt_clip1 = input_en
                            prompt_t5 = input_en
                        except:
                            await message.channel.send("using original prompt.")
                            prompt_ench = input_en
                        files, seed, filename = await generate_image_sd3(prompt_clip1,input_en,prompt_t5, neg_prompt, w, h, three )

                        await wait_msg.delete()
                        await wait_gif.delete()
                        new_message =   await message.channel.send(files=files, view=MainButtons())
                        og_message = message.id
                        msg_id = new_message.id
                        # new_prompt = {f"{msg_id}": input_en}

                        new_prompt = {
                            f"{msg_id}": {
                                "og_message": og_message,
                                "original": input_en,
                                "styled": "",  # Add your styled content here
                                "enchanted": prompt_t5,  # Add your enchanted content here
                                "support_prompt": "",
                                "h": h,
                                "w": w,
                                "negative": neg_prompt,
                                "model": model,
                                "latest_action": "AI Enhance",
                                "clip1": prompt_clip1,
                                "clip2": input_en,
                                "t5": prompt_t5,
                                "seed": seed,
                                "filename": filename
                            }
                        }

                        prompts.update(new_prompt)
                        with open("prompts.json", "w") as file:
                            json.dump(prompts, file, indent=4)  # You can adjust the indent for pretty printing
                            file.write('\n')   
                        return
                    else: # using sd3 api or dalle3
                        msgg = "*Echoing image...*"
                        wait_msg = await message.channel.send(msgg)                           
                        wait_gif = await                     message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmZ6d2YzMDllNDR2bzBmenc0dnl1ZGp0b3RqcW9iaGgzcjA4Mm1obyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BASS1qt1KIQ2HTD5Gs/giphy.gif") 
                        sd3_key                 = os.getenv('SD3')
                        filename = f"sd3_{int(time.time())}.jpeg"
                        file_path = f"./sd3/{filename}"

                        response = requests.post(
                            f"https://api.stability.ai/v2beta/stable-image/generate/ultra",
                            headers={
                                "authorization": f"Bearer {sd3_key}",
                                "accept": "image/*"
                            },
                            files={"none": ''},
                            data={
                                "prompt": f"{input_en}",
                                "output_format": "jpeg",
                                "aspect_ratio": "1:1",
                            },
                        )

                        if response.status_code == 200:
                            with open(f"{file_path}", 'wb') as file:
                                file.write(response.content)
                            file = discord.File(file_path)
                            await wait_msg.delete()
                            await wait_gif.delete()
                            new_message = await message.reply(file=file, view=MainButtons())
                            msg_id = new_message.id
                            new_prompt = {
                                f"{msg_id}": {
                                    "original": input_en,
                                    "og_message": message.id,
                                    "model": "sd3",
                                    "aspect_ratio": "1:1",
                                    "last_action": "original",
                                    "name_of_image": filename,
                                    "mode": "sd3",
                                }
                            }

                            prompts.update(new_prompt)
                            with open("prompts.json", "w") as file:
                                json.dump(prompts, file, indent=4)
                                file.write('\n')
                            return

                        else:
                            msgg = "*Echoing image...*"
                            wait_msg = await message.channel.send(msgg)                           
                            wait_gif = await                     message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmZ6d2YzMDllNDR2bzBmenc0dnl1ZGp0b3RqcW9iaGgzcjA4Mm1obyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/BASS1qt1KIQ2HTD5Gs/giphy.gif")                          
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
                            if message.channel.id == Myconfig.getChatChannel():
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
                            raise Exception(str(response.json()))            
                        return


                    return
                

            elif "atdarini manu bildi" in message.content.lower():
               avatar_url = message.author.display_avatar.url
               avatar_response = requests.get(avatar_url)
               avatar_image = Image.open(BytesIO(avatar_response.content))
               avatar_image.save('avatar.png')
               await message.channel.typing()
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


            elif "parādi" in message.content.lower() or "paradi" in message.content.lower():
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
                   #if pieprasijums == pieprasijums_en: #@#
                   #    pieprasijums_en = "I failed you" #@#
                   try:
                       izteles_auglis =    getGif(pieprasijums_en)
                   except ValueError:
                       try:
                           izteles_auglis =    getGif(pieprasijums)
                       except ValueError:

                           izteles_auglis =    getGif("random")
                   response = izteles_auglis
################ NEW ###################################

# Pajautā botam, lai viņš atrbild uz konkrēto lietotāja ziņu
            elif  message.reference is not None and hasImage:
                zina_ar_bildi = await message.channel.fetch_message(message.reference.message_id)
                bildes_url =  zina_ar_bildi.attachments[0].url
                current_zina = message_modif
                gpt_key               = os.getenv("GPT")
                await message.channel.typing()


                client_chat = OpenAI(api_key=gpt_key)

                responsee = client_chat.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"'Your name is 'Elizabete'. People also call you 'mamma'. Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. You pretend that you have given response, recieved an answer from user and reply with compact response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Sometimes use random emoji"},
                    {
                        "role": "user",
                        "content": [
                        {"type": "text", "text": f"user wrote '{current_zina} give generic human like short or medium  answer in context in latvian add your opinion. Do not as questions."},
                        {
                            "type": "image_url",
                            "image_url": {
                            "url": bildes_url,
                            },
                        },
                        ],
                    }
                    ],
                    max_tokens=1000,
                    temperature=0.6,
                )
                response = responsee.choices[0].message.content
                await message.channel.send(response)
                return

            elif message.reference and (pattern.search(message.content.lower())):
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
                        await message.channel.typing()

                        gpt_key               = os.getenv("GPT")
                        client_chat = OpenAI(api_key=gpt_key)
                        formatted_chat_history = get_chat_history()
                        #print(formatted_chat_history)
                        # 
                        responsee = client_chat.chat.completions.create( 
                        model='gpt-4o',
                        messages = [
                        {"role": "system", "content": f'''Your name is Elizabete. Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. You pretend that you have a message from user and reply with compact response in context taking in account what has been discussed in chat. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Sometimes use random emoji.
                        {formatted_chat_history}'''},
                        {"role": "user", "name": vards, "content": f"'{replied_zina}' give human-like short answer in context using chat history. Do not ask questions. Don't repeat yourself."}
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

                    output_directory = "text to speach"  # Set your desired output directory here
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

                    output_directory = "text to speach"  # Set your desired output directory here
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
          
          
            elif  '?' in message_modif or "pasaki" in message_modif or "iesaki" in message_modif or "pastāsti" in message_modif or "pastasti" in message_modif or  "atvainojies" in message_modif or  "apsveic" in message_modif or message.channel.id == 1101461174907830312  or mentioned_user: # 1101461174907830312 - ģenerē-general channel id   ### hasijs or message.author.id == 242298879784124416
                current_zina = message_modif
                #selected_tone = "grounded nostalgic tone"
                #use_GPT = False
                await message.channel.typing()
                name = getUserName(message.author.name)
                if name is not None:
                    #vards  = unidecode(name)
                    vards = message.author.name
                else:
                    vards = message.author.name
                    #vards  = unidecode(vards)

                if gptON:
                    gpt_key               = os.getenv("GPT")
                    client_chat = OpenAI(api_key=gpt_key)    
                    formatted_chat_history = get_chat_history()
                    #print(formatted_chat_history)



                    responsee = client_chat.chat.completions.create(
                    model='gpt-4o',
                    messages = [
                    {"role": "system", "content": f'''Your name is "Elizabete". People also call you "mamma".Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. You were created 15.03.2023. Reply with short response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Do not mention which tone using. Sometimes use emojis
                    {formatted_chat_history}'''},
                    {"role": "user", "name" : vards, "content": f"users wrote '{current_zina}' give human-like short answer in context using chat history. If possible  sometimes refer to previous sent messages and users. Do not ask questions. Don't repeat yourself."}
                    ],
                    max_tokens=700,
                    n=1,
                    stop=None,
                    temperature=0.6,
                    )
                    response = responsee.choices[0].message.content
                    response = response.replace('"', '')
                    response = response.replace("'", "")
                    if mentioned_user:
                        response = f"{mentioned_user.mention} {response}"

                    # Speciāli atbild uz Yogi ziņām
                    if message.author.id == 909845424909729802:
                       await message.reply(response)
                    else:
                        await message.channel.send(response)

                    givenResponses.append([message_modif,[response]])
                    saveResponse(givenResponses)
                    return
                else:
                    author_name = message.author.name
                    if author_name == "theeight":
                         vards = "Aģents E" 
                # author_name = message.author.name
                    if author_name == "Resnā mamma":
                         vards = "Elizabete" 
                    if author_name == "theeight":
                         vards = "Aģents E" 
                    if author_name == "daisyvongrim":
                         vards = "prosta desa" 
                    if author_name == "megga7866":
                         vards = "Aģente K"
                    if author_name == "mitraisbandits":
                         vards = "Kapars"
                    if author_name == "jaanisjc":
                         vards = "Aģents J"                              
                    formatted_chat_history = get_chat_history()
                    claude_key               = os.getenv("CLAUDE")
                    #pass_prompt = prompt
                    #context = prompt

                    responsee = anthropic.Anthropic(api_key=claude_key).messages.create(
                        model="claude-3-opus-20240229",
                        max_tokens=700,
                        temperature=0.6,
                        system= f"""
                            Your name is "Elizabete". People also call you "mamma".Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. You were created 15.03.2023. Reply with short response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Do not mention which tone using. Sometimes use emojis
                                                {formatted_chat_history}
                                """,
                        messages=[
                             {"role": "user", "content": f"user ({vards}) wrote '{current_zina}' give human-like short answer in context using chat history. If possible  sometimes refer to previous sent messages and users. Do not ask questions. Don't repeat yourself."}
                        ]
                    )

                    response = responsee.content[0].text
                    if mentioned_user:
                        response = f"{mentioned_user.mention} {response}"
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
                        return
                else: 
                    random.seed(time.time())
                    while  not response:
                        print('Random')
                        random_response = random.choice(response_list)
                        response = random_response
                    await message.channel.typing()
                    await message.channel.send(response)
                    givenResponses.append([message_modif,[response]])
                    saveResponse(givenResponses)         
                    return




        try:

            #Atbild, ja ir veiks replay vai mention
           if (client.user.mentioned_in(message) or message.reference is not None and  message.reference.resolved.author.id == client.user.id):
            hasImage = False
            try:
                    #zina_ar_bildi = await message.channel.fetch_message(message.reference.message_id)
                    bildes_url =  message.attachments[0].url
                    hasImage = True
            except:
                    hasImage = False
            if "parādi" in message.content.lower():
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
                   try:
                       izteles_auglis =    getGif(pieprasijums_en)
                   except ValueError:
                       try:
                           izteles_auglis =    getGif(pieprasijums)
                       except ValueError:

                           izteles_auglis =    getGif("random")
                   response = izteles_auglis
                   await message.channel.send(response)
                   return

            elif hasImage:
                #zina_ar_bildi = await message.channel.fetch_message(message.reference.message_id)

                if gptON:
                    bildes_url =  message.attachments[0].url
                    current_zina = message.content
                    gpt_key               = os.getenv("GPT")
                    #await message.channel.typing()
                    formatted_chat_history = get_chat_history()

                    client_chat = OpenAI(api_key=gpt_key)

                    responsee = client_chat.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": f''''Your name is 'Elizabete'. People also call you 'mamma'. Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. You pretend that you have given response, recieved an answer from user and reply with compact response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Sometimes use random emoji
                            '''},
                        {
                            "role": "user",
                            "content": [
                            {"type": "text", "text": f"user wrote '{current_zina}' give amusing human like short or medium  opinion about image in latvian. If possible refer to previous sent messages and users. Do not as questions.Don't repeat yourself."},
                            {
                                "type": "image_url",
                                "image_url": {
                                "url": bildes_url,
                                },
                            },
                            ],
                        }
                        ],
                        max_tokens=1000,
                        temperature=0.6,
                    )
                    response = responsee.choices[0].message.content
                    await message.channel.send(response)
                    return
                else:
                    author_name = message.author.name
                   # author_name = message.author.name
                    if author_name == "theeight":
                         vards = "Aģents E" 
                # author_name = message.author.name
                    if author_name == "Resnā mamma":
                         vards = "Elizabete" 
                    if author_name == "theeight":
                         vards = "Aģents E" 
                    if author_name == "daisyvongrim":
                         vards = "prosta desa" 
                    if author_name == "megga7866":
                         vards = "Aģente K"
                    if author_name == "mitraisbandits":
                         vards = "Kapars"
                    if author_name == "jaanisjc":
                         vards = "Aģents J"                   
                    current_zina = message.content
                    bildes_url =  message.attachments[0].url
                    image1_media_type = "image/png"
                    image1_data = base64.b64encode(httpx.get(bildes_url).content).decode("utf-8")
                    formatted_chat_history = get_chat_history()

                    claude_key               = os.getenv("CLAUDE")
                    #pass_prompt = prompt
                    #context = prompt

                    responsee = anthropic.Anthropic(api_key=claude_key).messages.create(
                        model="claude-3-opus-20240229",
                        max_tokens=1024,
                        temperature=0.6,
                        system= f"""
                            Your name is 'Elizabete'. People also call you 'mamma'. Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. You pretend that you have given response, recieved an answer from user and reply with compact response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Sometimes use random emoji
                            {formatted_chat_history}
                                """,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": image1_media_type,
                                            "data": image1_data,
                                        },
                                    },
                                    {
                                        "type": "text",
                                        "text": f"user wrote '{current_zina}' give amusing human like short or medium  opinion about image in latvian. If possible refer to previous sent messages and users. Do not as questions.Don't repeat yourself."
                                    }
                                ],
                            }
                        ]
                    )

                    response = responsee.content[0].text

                    await message.channel.send(response)
                    return
            
            elif (client.user.mentioned_in(message) or (message.reference is not None and message.reference.resolved.author.id == client.user.id)) and ('?' in message.content or "pasaki" in message.content or "iesaki" in message.content or "pastāsti" in message.content or "pastasti" in message.content): #  or message.author.id == 242298879784124416
           # if message.reference is not None and message.reference.resolved.author.id == client.user.id:  
                replied_zina = ''
                if message.reference is not None and message.reference.resolved.author.id == client.user.id:                  
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
                await message.channel.typing()


                if gptON:

                    gpt_key               = os.getenv("GPT")
                    client_chat = OpenAI(api_key=gpt_key)
                    formatted_chat_history = get_chat_history()
                    #print(formatted_chat_history)


                    responsee = client_chat.chat.completions.create(
                    model='gpt-4o',
                    messages = [
                    {"role": "system", "content": f'''Your name is Elizabete. People also call you 'mamma'. You were created 15.03.2023. Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. You pretend that you have given response, recieved an answer from user and reply with compact response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Sometimes use random emoji.
                    {formatted_chat_history}'''},
                    {"role": "user", "content": f"you wrote this answer '{replied_zina}'  and users wrote in response '{current_zina}' give human-like short answer in context using chat history. If possible  sometimes refer to previous sent messages and users. Do not ask questions.Don't repeat yourself"}
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
                    formatted_chat_history = get_chat_history()
                    claude_key               = os.getenv("CLAUDE")
                    #pass_prompt = prompt
                    #context = prompt

                    responsee = anthropic.Anthropic(api_key=claude_key).messages.create(
                        model="claude-3-opus-20240229",
                        max_tokens=700,
                        temperature=0.6,
                        system= f"""
                            Your name is Elizabete. People also call you 'mamma'. You were created 15.03.2023. Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. You pretend that you have given response, recieved an answer from user and reply with compact response in context. Use {selected_tone} tone and respond only with one message with format as simple message without quotes. Sometimes use random emoji.
                    {formatted_chat_history}
                                """,
                        messages=[
                             {"role": "user", "content": f"you wrote this answer '{replied_zina}'  and user wrote in response '{current_zina}' give human-like short answer in context using chat history. If possible  sometimes refer to previous sent messages and users. Do not ask questions.Don't repeat yourself"}
                        ]
                    )

                    response = responsee.content[0].text
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
                elif message.channel.id == 1101461174907830312: # 1101461174907830312 - ģenerē-general channel id
                    current_zina = message_modif
                    name = getUserName(message.author.name)
                   # replied_messagee = await message.channel.fetch_message(message.reference.message_id)
                  #  urll =  replied_messagee.attachments[0].url
                  #  print(urll)
                    image_text_upd = f"users wrote '{current_zina}' give SHORT ANSWER WITH FEW WORDS. Your name is Elizabete"
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
                    await message.channel.typing()

                    gpt_key               = os.getenv("GPT")
                    client_chat = OpenAI(api_key=gpt_key)

                    responsee = client_chat.chat.completions.create(
                    model='gpt-4o',
                    messages = [
                    {"role": "system", "content": f'GIVE SHORT ANSWER. You just moved to new server. Your name is mamma Elizabete. You are expert photographer who knows a lot about good pictures. Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}. Respond only with one message with format as simple message without quotes. RESPOND SHORT!! Sometimes use emojis'},
                    {"role": "user", "name" : vards, "content": f"{image_text_upd} . Do not as questions."}
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
                    await message.channel.typing()
                    await message.channel.send(response)
                    return
            else: 
                random.seed(time.time())
                while  not response:
                    print('Random')
                    random_response = random.choice(response_list)
                    response = random_response
                await message.channel.typing()
                await message.channel.send(response)
                givenResponses.append([message.content,[response]])
                saveResponse(givenResponses)
                return
        except Exception as e:
            print(e)
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
        if message.channel.id == Myconfig.getChatChannel():
            if Myconfig.getBotMsg() == True:#@#
                MyMsgCollector.setMsgCount(0) 
                return
            if MyMsgCollector.getMsgCount() == 1:
                MyMsgCollector.setMsg2(message.content)
                if message.attachments:
                    for att in message.attachments:
                        url = att.url 
                        MyMsgCollector.setMsg2(f"{MyMsgCollector.getMsg2()}\n{url}")
                MyMsgCollector.setMsgCount(MyMsgCollector.getMsgCount() + 1)
            if MyMsgCollector.getMsgCount() == 2:
                MyMsgCollector.setMsg1(preprocess_message(MyMsgCollector.getMsg1()))              
                addPair('CB_pairs2addition.json', MyMsgCollector.getMsg1(), MyMsgCollector.getMsg2())
                #pairs.append([msg1, [msg2]])
                MyMsgCollector.setMsgCount(0) 
            if MyMsgCollector.getMsgCount() == 0:
               MyMsgCollector.setMsg1(message.content)
               if message.attachments:
                    for att in message.attachments:
                        url = att.url 
                        MyMsgCollector.setMsg1(f"{MyMsgCollector.getMsg1()}\n{url}")
               MyMsgCollector.setMsgCount(MyMsgCollector.getMsgCount() + 1)
########################### NEW ########################


        # Apstrādāt ziņu, ja ir pievienots attēls
        if message.channel.id != SCREENSHOT_CHANNEL_ID:
            return

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
                    await message.channel.typing()
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
   handler = logging.FileHandler(filename=f'logs/discord_{timestamp}.log', encoding='utf-8', mode='w')
   handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
   logger.addHandler(handler)

   @client.event
   async def on_member_join(member):
    account_created = member.created_at.replace(tzinfo=timezone.utc)
    current_time = datetime.now(timezone.utc)
    account_age = current_time - account_created

    if account_age < timedelta(days=30):
        #await member.kick(reason='Account younger than one month')
        channel = client.get_channel(Myconfig.getChatChannel()) 
        #await channel.send("*Kicking suspicious account...*")
        await channel.send("*suspicious account joined...* Ko ta tu te??? ")
   
   @client.event
   async def on_presence_update(before, after):
       global firstBoot
       role_ids_to_check = [1030544437262155846, 1061383886074040352, 1089589791466721312, 1278355030486945879]
       #channel = client.get_channel(1097995867090333706)
       await trackActivity(before, after, role_ids_to_check, firstBoot)
       if firstBoot == True:
           firstBoot = False       
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
