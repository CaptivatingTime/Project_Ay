import asyncio
import random
import time
from bot_Chatting import Chatbot,get_similar_response
import json
import discord
from openai import OpenAI

import os
from functions import getTime, getDate
    #Pats aizsuta random bildi
async def post_random_image(channel, client, pairs, response_list):

    image_message  = []
    with open("CB_images.json", 'r', encoding='utf-8') as file: #@#
        image_message = json.load(file) #@#

    random.seed(time.time())
    response = random.choice(image_message)
    await channel.typing()
    await asyncio.sleep(2)
    await channel.send(response)
    try:
        next_message = await client.wait_for('message', timeout=120.0, check=lambda m: m.channel == channel and m.author != client.user and not m.reference)
        response = get_similar_response(next_message.content, pairs, threshold=0.3)
        if not response:
            random.seed(time.time())
            response = random.choice(response_list)
        await channel.typing()
        await asyncio.sleep(2)
        await next_message.reply(response)
    except asyncio.TimeoutError:
        print('No response from user')

    # Pats aizsūta kādu ziņu
async def post_random_message(channel, client, pairs, response_list):

    person_message = []
    with open("CB_person_message.json", 'r', encoding='utf-8') as file: #@#
        person_message = json.load(file) #@#

    random.seed(time.time())
    response = random.choice(person_message)
    await channel.typing()
    await asyncio.sleep(2)
    await channel.send(response)
    try:
        next_message = await client.wait_for('message', timeout=120.0, check=lambda m: m.channel == channel and m.author != client.user and not m.reference)
        response = get_similar_response(next_message.content, pairs, threshold=0.3)
        if not response:
            random.seed(time.time())
            response = random.choice(response_list)
        await channel.typing()
        await asyncio.sleep(2)
        await next_message.reply(response)
    except asyncio.TimeoutError:
        print('No response from user')

    # Pats ietago kādu un uzdod jautājumu
async def post_mention_message(channel, client, pairs, response_list, question_list):
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
        await channel.typing()
        await asyncio.sleep(2)
        await channel.send(f"{random_member.mention} {random_response}")
        try:
            # Wait for a response from the mentioned user within 60 seconds
            next_message = await client.wait_for('message', timeout=120.0, check=lambda m: m.author == random_member and m.channel == channel and not m.reference)           
            response = get_similar_response(next_message.content, pairs, threshold=0.3)
            if not response:
                random.seed(time.time())
                response = random.choice(response_list)
            await channel.typing()
            await asyncio.sleep(2)
            await next_message.reply(response)
        except asyncio.TimeoutError:
            print('No response from user')      

    # Pats atbild uz pēdējo ziņu
async def post_reply_message(channel, client, pairs, response_list):
    await channel.typing()
    recent_message = await discord.utils.get(channel.history())
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
            await channel.typing()
            await asyncio.sleep(2)
            await next_message.reply(response)
        except asyncio.TimeoutError:
            print('No response from user')
################ NEW ##########################
    else:
        print('I wont answer to my own message!')  

    # Koemntē kādu ziņu, piedalās sarunā
async def post_comment_message(channel, client, pairs, response_list, thread_id):

    tones = ["sarcastic", "assertive", "sad", "cynical", "indignant", "contemplative", "witty", "persuasive", "rude", "angry", "romantic", "humorous", "adventurous", "creative", "friendly", "optimistic", "pessimistic", "nostalgic", "hopeful", "enthusiastic", "ambivalent", "descriptive", "suspenseful", "factual", "informative", "playful", "inspiring", "melancholic", "mysterious", "objective", "subjective", "sympathetic", "empathetic", "reflective", "confident", "satirical", "ironic", "sincere", "cautious", "credible", "informal", "formal", "professional", "scholarly", "inspirational", "controversial", "diplomatic", "nurturing", "authoritative", "didactic", "patronizing", "dismissive", "unemotional", "nihilistic"]
    #tones = ["assertive", "cynical", "indignant", "rude", "angry", "pessimistic", "ambivalent", "authoritative", "dismissive"]

    random.seed(time.time())
    selected_tone_self = random.choice(tones)
    selected_tone_self = selected_tone_self.upper()

    #random.seed(time.time())
    #response = random.choice(person_message)
    await channel.typing()
    gpt_key               = os.getenv("GPT")
    client_chat = OpenAI(api_key=gpt_key)    

   # file =  client_chat.files.create(
    #    file=open("IDs.txt", "rb"),
    #    purpose='assistants'
   # )
    assistant = client_chat.beta.assistants.create(
        name="Coding MateTest",
        instructions=f"Use {selected_tone_self} TONE! Your name is mamma Elizabete. You must always tag users using their ID not username using this format: '<@UserID>'. get 'UserID' from txt file! Todays date is {getDate()}. Precīzs pulkstens šobrīd ir {getTime()}.   You keep record of peoples chat in discord. New messages are being added to your memory.You pretend that you have given response, recieved an answer from user and reply  in context. Respond only with one message with format as simple message without quotes. Sometimes use random emoji.",
        model="gpt-4-turbo",
        tools=[{"type": "file_search"}]
        #file_ids=[file.id]
    )
    vector_store = client_chat.beta.vector_stores.create(name="User IDs")

    file_paths = ["IDs.txt"]
    file_streams = [open(path, "rb") for path in file_paths]

    file_batch = client_chat.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    assistant = client_chat.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
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
        await channel.typing()
        await asyncio.sleep(2)
        await next_message.reply(response)
    except asyncio.TimeoutError:
        print('No response from user')            