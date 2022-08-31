import discord
import time
from discord.ext import tasks
import os
import urllib.request
import base64
import hmac
import re
from dotenv import load_dotenv # pip install python-dotenv

load_dotenv()

APIURL = os.getenv("APIURL")
TOKEN = os.getenv("TOKEN")
APIKEY = os.getenv("APIKEY")
SECRETKEY = os.getenv("SECRETKEY")
COIN = os.getenv("COIN")

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # an attribute we can access from our task
        self.counter = 0
#        self.loop_bal.start()
        self.orderId = ""
        self.data = eval(re.findall("{.*}", str(self.getHistory()))[0])["data"]

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        if message.content == '.ping':
            await message.reply("pong!!")
        elif message.content == '.bal':
            await message.reply(str(self.getBalance()).split(',')[5].replace('"balance":', '')) # ["data"]["account"]["balance"]


#    @tasks.loop(seconds=5.0)
#    async def loop_bal(self):
#        channel = self.get_channel(1008240231876661358)
#
#        self.data = eval(re.findall("{.*}", str(self.getHistory()))[0])["data"]
#        if self.orderId != self.data["orders"][0]["orderId"]:
#            self.data = eval(re.findall("{.*}", str(self.getHistory()))[0])["data"]
#            self.orderId = self.data["orders"][0]["orderId"]
#
#            embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)
#            embedVar.add_field(name="Field1", value="hi", inline=True)
#            embedVar.add_field(name="Field2", value="hi2", inline=True)
#            embedVar.add_field(name="Field3", value=self.data, inline=False)
#            await  channel.send(embed=embedVar)

#    @loop_bal.before_loop
#    async def before_loop_bal(self):
#        await self.wait_until_ready()  # wait until the bot logs in


    def genSignature(self, path, method, paramsMap):
        sortedKeys = sorted(paramsMap)
        paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
        paramsStr = method + path + paramsStr
        return hmac.new(SECRETKEY.encode("utf-8"), paramsStr.encode("utf-8"), digestmod="sha256").digest()

    def post(self, url, body):
        req = urllib.request.Request(url, data=body.encode("utf-8"), headers={'User-Agent': 'Mozilla/5.0'})
        return urllib.request.urlopen(req).read()

    def getBalance(self):
        paramsMap = {
            "apiKey": APIKEY,
            "timestamp": int(time.time()*1000),
            "currency": "USDT",
        }
        sortedKeys = sorted(paramsMap)
        paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
        paramsStr += "&sign=" + urllib.parse.quote(base64.b64encode(self.genSignature("/api/v1/user/getBalance", "POST", paramsMap)))
        url = "%s/api/v1/user/getBalance" % APIURL
        return self.post(url, paramsStr)

    def getHistory(self):
        paramsMap = {
            "symbol": COIN.upper()+"-USDT",
            "lastOrderId": 0,
            "length": 1,
            "apiKey": APIKEY,
            "timestamp": int(time.time()*1000),
        }
        sortedKeys = sorted(paramsMap)
        paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
        paramsStr += "&sign=" + urllib.parse.quote(base64.b64encode(self.genSignature("/api/v1/user/historyOrders", "POST", paramsMap)))
        url = "%s/api/v1/user/historyOrders" % APIURL
        return self.post(url, paramsStr)

client = MyClient(intents=discord.Intents.default())
client.run(TOKEN)
