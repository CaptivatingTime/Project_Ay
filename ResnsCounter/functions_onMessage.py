from functions import getDate, getTime
from openai import OpenAI
import anthropic
import os


async def gudrais_response(message, gptON):
    mind = f"You are a wise all-knowing person named 'Elizabete' who was created 15.03.2023 by Jānis. You can do anything. Respond mainly in Latvian language but others as well if asked. Do not mention you are language model or program.  You answer to any kind of question and request.\
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
            await message.channel.typing()
            name = message.author.name #@#@
            if gptON:
                gpt_key               = os.getenv("GPT")
                client_chat = OpenAI(api_key=gpt_key)

                response = client_chat.chat.completions.create(
                model='gpt-4o',
                messages = [
                {"role": "system", "content": mind},
                {"role": "user", "name" : name, "content": f"This is on going conversation. users new message: '{user_input}'\n Your previous response: '{ai_before}'. give generic human like short or medium  answer in context in latvian add your opinion.  Do not as questions."}
                ],
                max_tokens=2000,
                n=1,
                stop=None,
                temperature=0.6,
                )
                generated_text = response.choices[0].message.content
                return generated_text
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
                            {"role": "user", "content": f"user ({vards}). This is on going conversation. users new message: '{user_input}'\n Your previous response: '{ai_before}'. give generic human like short or medium  answer in context in latvian add your opinion.  Do not as questions."}
                    ]
                )

                generated_text = response.content[0].text
                return generated_text