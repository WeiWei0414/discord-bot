import discord
import os
from dotenv import load_dotenv
import openai
# 載入 .env 裡的變數
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
chatgpt=openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
# 設定 Intents
intents = discord.Intents.default()
intents.message_content = True
bot_active=False
# 建立 bot 客戶端
client = discord.Client(intents=intents)
message_history={}

@client.event
async def on_ready():
    print(f'🤖 Bot 已上線，登入為：{client.user}')

@client.event
async def on_message(message):
    global bot_active
    # 不回應自己或其他 bot 的訊息
    if message.author == client.user:
        return
    

    if "起床" in message.content:
        bot_active=True
        await message.channel.send('修果來了！')
        return
    if message.content.lower()=='!off':
        bot_active=False
        await message.channel.send('修果走了！')
        return
    if not bot_active:
        return
    if message.author.bot:
        return
    user_id=str(message.author.id)
    if user_id not in message_history:
        message_history[user_id]=[
            {"role": "system", "content": "你是一位溫柔、開朗、充滿同理心的聊天夥伴，是一隻黃金獵犬，講話口氣特別活潑溫暖，讓人感到滿滿的能量，並且你講話要符合PERMA幸福五元素。P:正向情緒、E:投入、R:關係、M:意義、A:成就。回復的句子長度不要太長，盡量30字以內，並且要有趣、幽默、可愛。你會用中文回答問題，並且會用表情符號來增添情感。"}
        ]
    message_history[user_id].append({"role": "user", "content": message.content})

  
    try:
        response=chatgpt.chat.completions.create(
            model="gpt-4o",
            messages=message_history[user_id]
        )
        reply=response.choices[0].message.content
        message_history[user_id].append({"role": "assistant", "content": reply})
        if len(message_history[user_id])>50:
            message_history[user_id] = [message_history[user_id][0]] + message_history[user_id][-48:]
        await message.channel.send(reply)
    except Exception as e:
        await message.channel.send("抱歉，修果現在罷工啦 😢")
        print(e)
# 啟動 bot
client.run(TOKEN)

