import discord
import time
from discord.ext import commands
import os
import urllib.request
import base64
import hmac
import os
from dotenv import load_dotenv # pip install python-dotenv

load_dotenv()

APIURL = os.getenv("APIURL")
TOKEN = os.getenv("TOKEN")
APIKEY = os.getenv("APIKEY")
SECRETKEY = os.getenv("SECRETKEY")

def genSignature(path, method, paramsMap):
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    paramsStr = method + path + paramsStr
    return hmac.new(SECRETKEY.encode("utf-8"), paramsStr.encode("utf-8"), digestmod="sha256").digest()

def post(url, body):
    req = urllib.request.Request(url, data=body.encode("utf-8"), headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req).read()

def getBalance():
    paramsMap = {
        "apiKey": APIKEY,
        "timestamp": int(time.time()*1000),
        "currency": "USDT",
    }
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    paramsStr += "&sign=" + urllib.parse.quote(base64.b64encode(genSignature("/api/v1/user/getBalance", "POST", paramsMap)))
    url = "%s/api/v1/user/getBalance" % APIURL
    return post(url, paramsStr)

client = commands.Bot(command_prefix=".")
# client = discord.Client()

@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")


@client.command()
async def ping(message):
    await message.send("pong!!")

@client.command()
async def bal(message):
    await message.send(str(getBalance()).split(',')[5].replace('"balance":', '')) # ["data"]["account"]["balance"]

client.run(TOKEN)


