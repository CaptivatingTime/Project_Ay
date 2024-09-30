
import discord
from discord.ext import commands
import yt_dlp
from discord import FFmpegPCMAudio
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import asyncio
import random
import json


#flags for playback
is_playing = False
was_stopped = False
not_playlist = True
playlist_info = 'None'
isRandom = False
continuesPlay = False
music_channel = 0
username = 'None'
YTplaylist_title = 'None'
artist_name = ''
voice_client = ''
elizabeteClient = ''
nextType = 'None'

with open("song_history.json", 'r', encoding='utf-8') as file: #@#
    song_history = json.load(file) #@#

# Store previously recommended video IDs
recommended_ids = set()
played_songs_playlist = set()
# Youtube search client
load_dotenv()
youtube_key = os.getenv("YOUTUBE")
youtube = build('youtube', 'v3', developerKey=youtube_key)

### functions for slash commands ###


async def getNextPlaylistSong():
    global played_songs_playlist, playlist_info

    foundSong = False
    foundSongURL = ''
    nextSongName = 'None'
    currentSongName = 'None'
    audio_url = 'None'

    for video_info in playlist_info:
        if "Deleted video" in video_info['title']:
            continue       
        audio_url = video_info['url']

        if audio_url not in played_songs_playlist:
            if foundSong == False:  # If the current song has not been found yet
                played_songs_playlist.add(audio_url)
                foundSongURL = audio_url
                currentSongName = video_info['title']
                foundSong = True
            elif foundSong == True:  # If current song is found, set next song
                nextSongName = video_info['title']
                return foundSongURL, nextSongName, currentSongName, audio_url

    return foundSongURL, nextSongName, currentSongName, audio_url
            
def randomSong():
    all_songs = []
    with open("song_history.json", 'r', encoding='utf-8') as file:
        song_history = json.load(file)
    for user in song_history:
        for songName in song_history[user]:
            all_songs.append(song_history[user][songName])
                
    url = random.choice(all_songs)
    return url
       

async def saveSong(user, songName, songUrl):
    with open("song_history.json", 'r', encoding='utf-8') as file:
        song_history = json.load(file)
    if user not in song_history:
        song_history[user] = {}
    if songName not in song_history[user]:
        song_history[user][songName] = songUrl
    with open("song_history.json", 'w', encoding='utf-8') as file:  
            json.dump(song_history, file, indent=4)  # You can adjust the indent for pretty printing
            file.write('\n')  
# Search youtube by song title
def search_youtube(query):
    url = ''

    request = youtube.search().list(
        part='snippet',
        q=query,
        type='video',
        videoCategoryId='10',  # Music category
        maxResults=1  # Number of results to return
    )
    response = request.execute()

    for item in response.get('items', []):
        title = item['snippet']['title']
        video_id = item['id']['videoId']
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f'Title: {title}\nLink: https://www.youtube.com/watch?v={video_id}\n')
    return url

# Function to join a voice channel
async def join_voice_channel(interaction, client):
    if interaction.user.voice is None:
        await interaction.response.send_message("Tu neesi voicā.")
        return None
    
    channel = interaction.user.voice.channel
    voice_client = discord.utils.get(client.voice_clients, guild=interaction.guild)

    if voice_client is None:
        voice_client = await channel.connect()
    return voice_client

# erach for recomended song
def get_next_related_video(query):
    global recommended_ids
    #load_dotenv()
    #youtube_key = os.getenv("YOUTUBE")
    #youtube = build('youtube', 'v3', developerKey=youtube_key)

    request = youtube.search().list(
        part='snippet',
        q=query,
        type='video',
        videoCategoryId='10',  # Music category 
        maxResults=10  # Get a few related videos
    )
    response = request.execute()

    # Choose a random related video from the list
    related_videos = response.get('items', [])
        # Filter out previously recommended video IDs
    available_videos = [video for video in related_videos if video['id']['videoId'] not in recommended_ids]
    if available_videos:
        next_video = random.choice(available_videos)
        title = next_video['snippet']['title']
        next_video_id = next_video['id']['videoId']
        next_video_url = f"https://www.youtube.com/watch?v={next_video_id}"
        # Store the ID to avoid future repeats
        recommended_ids.add(next_video_id)        
        print(f'Title: {title}\nLink: https://www.youtube.com/watch?v={next_video_id}\n')
    else:
        print("No new recommendations available.")



        
        
    return next_video_url


async def continuePlaying(err):
    global is_playing, was_stopped, recommended_ids,not_playlist, YTplaylist_title, elizabeteClient, nextType
    if was_stopped:
        was_stopped = False   
        return     
    embed = ''
    if err:
        print(f"Error occurred while playing: {str(err)}")
    else:
        async def play_recommended_song(err):
            global was_stopped
            if was_stopped:  # Check if playback was stopped intentionally
                was_stopped = False  # Reset the flag for future playback
                return  # Exit if playback was stopped     
            if err:
                print(f"Error occurred while playing: {str(err)}")
            else:
                try:
                    print("Scheduling the next recommended song...")
                    nextType = 'recommended'
                    await continuePlaying(nextType)
                except Exception as e:
                    print(f"Error occurred while scheduling the next song: {str(e)}")
        async def play_next_song(err):
                global was_stopped
                if was_stopped:  # Check if playback was stopped intentionally
                    was_stopped = False  # Reset the flag for future playback
                    return  # Exit if playback was stopped     
                if err:
                    print(f"Error occurred while playing: {str(err)}")
                else:
                    not_playlist = False
                    #next_video_url = await getNextPlaylistSong(YTplaylist_url)
                    next_video_url = ""
                    nextType = 'playlist'
                    try:
                        print("Scheduling the next playlist song...")               
                        await continuePlaying(nextType)
                    except Exception as e:
                        print(f"Error occurred while scheduling the next song: {str(e)}") 
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -filter:a "volume=0.25"'
        }
        
        if nextType == "playlist":
            YTvideo_url, nextSongTitle, video_title, video_url = await getNextPlaylistSong()
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True  # Suppresses output from yt-dlp
            }            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # Extract information about the video
                    video_info = ydl.extract_info(video_url, download=False)
                    audio_url = video_info['url']  # Audio stream URL
                except Exception as e:
                    print("3")
                    if 'Video unavailable' in str(e):
                        print(f"Skipping song {video_title} due to error: {str(e)}")
                        YTvideo_url, nextSongTitle, video_title, video_url = await getNextPlaylistSong()
                        video_info = ydl.extract_info(video_url, download=False)
                    else:
                        await print(f"An error occurred: {str(e)}")
                        return                
            embed = discord.Embed(
                title=f"📜*Now playing playlist:* **{YTplaylist_title}**",  # Set the title
                description=f" *📀 Current song:* **{video_title}**\n⏩ *Next song:* **{nextSongTitle}**",  # Set the video title in the description
                color=discord.Color.blue()  # Choose any color you'd like
            )
            await music_channel.send(embed=embed)  
            await saveSong(username, video_title, YTvideo_url)
            source = FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)   
            voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(continuePlaying(e), elizabeteClient.loop))       
                

        elif nextType == 'recommended':
            YTvideo_url = get_next_related_video(artist_name)
            embed = discord.Embed(
                title="📀*Now playing next similar song:*",  # Set the title
                description=f"**{video_title}**",  # Set the video title in the description
                color=discord.Color.blue()  # Choose any color you'd like
            )
            await music_channel.send(embed=embed)
    
    #audio_url = video_info['url']  # Audio stream URL
    #video_title = video_info['title']  # Video title
    #video_id = video_info['id']
    
    #artist_name = video_info.get('artist', video_info.get('uploader', 'Unknown Artist'))



   # if YTplaylist_title != "None":
    #    recommended_ids.add(video_id)




### functions for slash commands ###


### Slash commands ###

     

# view resnums progress
async def resnums_slash (interaction: discord.Interaction, game_wins):
    
       response = ""
       first = True
       
       print('Stats requested...')
       
       player_name = f"{interaction.user.name}"
       for player, gamee_wins in game_wins.items():
            if player == player_name:
                for game, wins in gamee_wins.items():
                    if first:
                        response = response + f"**{player_name}** has won:\n {wins} times {game} this month.\n"
                        first = False
                    else: response = response + f"{wins} times {game}.\n"

                #await message.channel.typing() #@#
               # await asyncio.sleep(2) #@#              
                stats = await interaction.response.send_message(response)
       print(f"{player_name} Stats provided!")    

# Function to play YouTube audio using yt-dlp

# check if it playlist and play t if True
async def play_music(interaction: discord.Interaction, YTvideo_url, client, nextSong, YTplaylist_url, newCall):
    global playlist_info, isRandom, is_playing, was_stopped, recommended_ids, not_playlist, music_channel, YTplaylist_title, username
    nextSongTitle    = 'None'
    YTplaylist_title = 'None'
    isRandom = False

    music_channel = client.get_channel(interaction.channel_id)
    username = interaction.user.name

    if YTplaylist_url != "None":
        YTvideo_url = YTplaylist_url
    else:
        playlist_info = 'None'
    if nextSong == False:
        await interaction.response.defer()
        # If a song is currently playing, stop it
        voice_client = discord.utils.get(client.voice_clients, guild=interaction.guild)
        if is_playing and voice_client is not None:
            voice_client.stop()  # Stop the currently playing song
            was_stopped = True        

    is_playing = True  # Set the state to indicate that a song is playing

    if YTvideo_url == "random":
        YTvideo_url = randomSong()
        isRandom = True
    elif "https" not in YTvideo_url:
        YTvideo_url = search_youtube(YTvideo_url)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True  # Suppresses output from yt-dlp
    }

    # Run yt-dlp in a separate thread to avoid blocking the event loop
    def extract_video_info():
        ydl_opts = {
            'socket_timeout': 10,
            'extract_flat': True,  # This avoids fetching full format information.
            'skip_download': True,  # Skip downloading the video data.
            'quiet': True,  # Reduce log output.
            'simulate': True,  # Only simulate the download (doesn't actually fetch files).
            'force_generic_extractor': False,  # Avoid fallback to the generic extractor if YouTube extractor fails.
        }        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(YTvideo_url, download=False)
    if "playlist" in YTvideo_url:    
            try:
                info = await asyncio.to_thread(extract_video_info)  # Run extract_info asynchronously
            except Exception as e:
                print("2")
                await music_channel.send(f"An error occurred: {str(e)}")
                return
    # Playlist requested
      # It's a playlist
            playlist_info = info['entries']
            YTplaylist_title = info['title']
            YTplaylist_url = YTvideo_url
            playlist = info
            not_playlist = False
            YTvideo_url, nextSongTitle, currentSongName, audio_url = await getNextPlaylistSong()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # Extract information about the video
                    video_info = ydl.extract_info(YTvideo_url, download=False)
                    audio_url = video_info['url']  # Audio stream URL
                    video_title = video_info['title']  # Video title
                except Exception as e:
                    print("3")
                    await interaction.followup.send(f"An error occurred: {str(e)}")
                    return       
            await play_video(interaction, video_info, client, nextSong,YTvideo_url, YTplaylist_url, YTplaylist_title, nextSongTitle)

     # One song requested       
    else:
        # Extract information about the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Extract information about the video
                video_info = ydl.extract_info(YTvideo_url, download=False)
            except Exception as e:
                print("3")
                await interaction.followup.send(f"An error occurred: {str(e)}")
                return    
        #audio_url = video_info['url']  # Audio stream URL
        #video_title = video_info['title']  # Video title

        await play_video(interaction, video_info, client, nextSong,YTvideo_url, YTvideo_url, YTplaylist_title, nextSongTitle)

# play single song
async def play_video(interaction: discord.Interaction, video_info, client, nextRecomended, YTvideo_url, YTplaylist_url, YTplaylist_title, nextSongTitle):
    global is_playing, was_stopped, recommended_ids,not_playlist, artist_name, voice_client, elizabeteClient, nextType

    audio_url = video_info['url']  # Audio stream URL
    video_title = video_info['title']  # Video title
    video_id = video_info['id']
    
    artist_name = video_info.get('artist', video_info.get('uploader', 'Unknown Artist'))
    elizabeteClient = client

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -filter:a "volume=0.25"'
    }

    voice_client = await join_voice_channel(interaction, client)
    
    if YTplaylist_title != "None":
        recommended_ids.add(video_id)
        embed = discord.Embed(
            title=f"📜*Now playing playlist:* **{YTplaylist_title}**",  # Set the title
            description=f" *📀 Current song:* **{video_title}**\n⏩ *Next song:* **{nextSongTitle}**",  # Set the video title in the description
            color=discord.Color.blue()  # Choose any color you'd like
        )     
        await interaction.followup.send(embed=embed)

    elif nextRecomended == False:
        recommended_ids.add(video_id)
        embed = discord.Embed(
            title="📀*Now playing:*",  # Set the title
            description=f"**{video_title}**",  # Set the video title in the description
            color=discord.Color.blue()  # Choose any color you'd like
        )     
        await interaction.followup.send(embed=embed)
    else:
        embed = discord.Embed(
            title="📀*Now playing next similar song:*",  # Set the title
            description=f"**{video_title}**",  # Set the video title in the description
            color=discord.Color.blue()  # Choose any color you'd like
        )
        await interaction.followup.send(embed=embed)
    
    if voice_client is None:
        return

    await saveSong(interaction.user.name, video_title, YTvideo_url)
    source = FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)

    async def play_recommended_song(err):
        global was_stopped
        if was_stopped:  # Check if playback was stopped intentionally
            was_stopped = False  # Reset the flag for future playback
            return  # Exit if playback was stopped     
        if err:
            print(f"Error occurred while playing: {str(err)}")
        else:
            try:
                print("Scheduling the next recommended song...")
                
                await continuePlaying(nextType)
            except Exception as e:
                print(f"Error occurred while scheduling the next song: {str(e)}")
    async def play_next_song(err):
            global was_stopped
            if was_stopped:  # Check if playback was stopped intentionally
                was_stopped = False  # Reset the flag for future playback
                return  # Exit if playback was stopped     
            if err:
                print(f"Error occurred while playing: {str(err)}")
            else:
                not_playlist = False
                #next_video_url = await getNextPlaylistSong(YTplaylist_url)
                next_video_url = ""
                nextType = 'playlist'
                try:
                    print("Scheduling the next playlist song...")               
                    await continuePlaying(nextType)
                except Exception as e:
                    print(f"Error occurred while scheduling the next song: {str(e)}")               
    if not_playlist:
        nextType = 'recommended'
        voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_recommended_song(e), client.loop))
    else:
        nextType = 'playlist' 
        voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(continuePlaying(e), client.loop))  # Just play the first video in the playlist
        # Wait until the song finishes
        #while voice_client.is_playing():
        #    await asyncio.sleep(1)  # Wait in a loop until the song finishes    
    #print(f"Playing audio: {audio_url}")

# Slash command to stop playing and disconnect from the voice channel
async def stop_music(interaction: discord.Interaction, client):
    global was_stopped
    await interaction.response.defer()
    voice_client = discord.utils.get(client.voice_clients, guild=interaction.guild)
    if voice_client is not None:
        was_stopped = True
        voice_client.stop()  # Stop the current audio
        await voice_client.disconnect()
        await interaction.followup.send("Ballīte beidzās. *disconnecting..*")
    else:
        await interaction.followup.send("No active voice connection.")

### Slash commands ###      