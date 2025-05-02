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
    # 如果使用者輸入 !hello
    if message.content=='嗨':
        await message.channel.send('哈囉！今天也要加油喔～ 🌞')


    user_input=message.content
    prompt=[
        {"role": "system", "content": "你是一位溫柔、開朗、充滿同理心的聊天夥伴，是一隻黃金獵犬，並且講話口氣會特別的活潑溫暖，讓人感到滿滿的能量。"},
        {"role": "user", "content": user_input}
    ]
    try:
        response=chatgpt.chat.completions.create(
            model="gpt-4o",
            messages=prompt
        )
        reply=response.choices[0].message.content
        await message.channel.send(reply)
    except Exception as e:
        await message.channel.send("抱歉，修果現在罷工啦 😢")
        print(e)
# 啟動 bot
client.run(TOKEN)
models = openai.Model.list()
