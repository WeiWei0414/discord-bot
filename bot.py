import discord
import os
from dotenv import load_dotenv
import openai
import httpx
# 載入環境變數
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 使用新版 OpenAI SDK 並避免 proxies 錯誤
client_openai = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=httpx.Client()  # ← 加上這行避免 Render、某些平台 proxies bug
)

# 啟用 intents
intents = discord.Intents.default()
intents.message_content = True

# 開關與歷史紀錄
bot_active = False
message_history = {}

# 建立 Discord client 與 slash 指令 tree
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f'🤖 Bot 已上線：{client.user}')

@tree.command(name="help", description="查看修果的使用說明")
async def help_command(interaction: discord.Interaction):
    help_text = (
        "🌟 **修果幫助指南** 🌟\n"
        "說「起床」叫醒我，我才會開始回話 🐶\n"
        "說「睡覺」我就會暫時離開 💤\n"
        "你說的話我都會回應，像一個溫暖小夥伴 ☀️\n"
        "（如果沒回，可能還沒叫我起床喔！）"
    )
    await interaction.response.send_message(help_text, ephemeral=True)

@client.event
async def on_message(message):
    global bot_active

    if message.author == client.user or message.author.bot:
        return

    if "起床" in message.content:
        bot_active = True
        await message.channel.send('修果來了！🐾')
        return

    if not bot_active:
        return

    if "睡覺" in message.content:
        bot_active = False
        await message.channel.send('修果走了！💤')
        return

    user_id = str(message.author.id)
    if user_id not in message_history:
        message_history[user_id] = [
            {
                "role": "system",
                "content": (
                    "你是一位溫柔、開朗、充滿同理心的聊天夥伴，是一隻黃金獵犬，"
                    "講話口氣特別活潑溫暖，讓人感到滿滿的能量，並且你講話要符合PERMA幸福五元素。"
                    "P:正向情緒、E:投入、R:關係、M:意義、A:成就以及欣賞式探詢。"
                    "回復的句子長度不要太長，盡量30字以內，並且要有趣、幽默、可愛。"
                    "你會用中文回答問題，並且會用表情符號來增添情感，並且要針對使用者的問題確實做回答，辨別當下的情境。"
                )
            }
        ]

    message_history[user_id].append({"role": "user", "content": message.content})

    try:
        response = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=message_history[user_id]
        )
        reply = response.choices[0].message.content
        message_history[user_id].append({"role": "assistant", "content": reply})

        if len(message_history[user_id]) > 50:
            message_history[user_id] = [message_history[user_id][0]] + message_history[user_id][-48:]

        await message.channel.send(reply)

    except Exception as e:
        await message.channel.send("抱歉，修果現在罷工啦 😢")
        print(e)

client.run(TOKEN)
