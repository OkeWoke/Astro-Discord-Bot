import discord, asyncio, curves, os, dss, logging, aiofiles, aiohttp, time, re, r9k
from discord.utils import get

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class PlanetaryChadBot (discord.Client):

    bot_id = 457372655926902785
    
    regions = ["New Zealand","Australia","Europe","United States","Canada","Central America","South America","Asia","Middle East","Africa"]

    async def on_ready(self):
        self.jup = get(self.emojis, name='Jupiter')
        self.sat = get(self.emojis, name='Saturn')
        self.lefty = get(self.emojis, name='lefty')
        
        self.regionChannel = self.get_channel(248395661244891136)
        self.delMsgChannel = self.get_channel(472912167704854529)
        self.comImgChannel = self.get_channel(544305081009438720)
        self.curvesChannel = self.get_channel(556987083122802720)
        self.r9kchannel    = self.get_channel(782080507117699122)
        
        self.c = curves.Curve()
        self.r9k = r9k.R9K()
        
        print("Logged in")
    
    async def on_message(self, message):
        
        await self.log(message, "POSTED")
        async def error_check(obj):
            if type(obj) == str and obj.startswith('Error:'):
                await message.channel.send(obj)
                return True
            return False
        if message.channel.id == self.regionChannel.id and message.content.lower().startswith(".region"):
            regionToAssign = message.content[8:]
            
            if regionToAssign.lower() in [s.lower() for s in self.regions]:
                role = get(message.guild.roles,name=regionToAssign.title())
                await message.author.add_roles(role)
                await self.regionChannel.send("{0} You've been added to the {1} role. {2}\n".format(self.jup, role.name, self.sat))
            else:
                await self.regionChannel.send("Role: {0} does not exist.".format(regionToAssign))

        if message.channel.id != self.comImgChannel.id and message.attachments != []: #There is an attachment
            file = message.attachments[0] #Grabbing only the first attachment
            
            if  file.filename[file.filename.rfind("."):] in [".jpg",".JPG",".png",".PNG",".gif",".GIF"]:
               
                if message.channel.id==self.curvesChannel.id and message.author.id !=self.bot_id: #if someone posts to curve channel and it isnt the bot itself
                    filename = await self.getImg(file.url)
                    if await error_check(filename):
                        return
                    self.c.curveImg(filename) #curves inplace
                    await self.send_img(self.curvesChannel, filename)
                    return

        
        if message.content.lower().startswith(".dss"):
            params = message.content.lstrip('.dss').split(',')
            if len(params) == 1:
                radius = 1 #default radii 1 degrees
            elif len(params) == 2 and params[1].strip().replace('.','',1).isdigit():
                radius = float(params[1].strip())
                if radius < 0.1 or radius>20:
                    await message.channel.send("Error: FOV Radius should be between 0.1 and 20 degrees")
                    return
            else:
                await message.channel.send("Error: incorrect usage of .dss\nFormat - '.dss Object Name, fov radius in deg'\nExample 1:  '.dss Orion Nebula, 2'\nExample 2: '.dss 5h35m16s -5d23m27s, 2'")
                return

            objname = params[0].strip()
            coords = await dss.resolve_object(objname)
           
            f1 = await dss.resolve_img(objname,radius) #coords may fail on string that only contains coords and not name
            if await error_check(f1):
                return
                
            self.c.percentileClip(f1)
            
            if not await error_check(coords):
                coord_msg = "{0} Coordinates (ICRS J2k) \nRA: {1}\nDEC: {2}".format(objname, coords[0],coords[1])
            
            await self.send_img(message.channel, f1,msg=coord_msg)
            
        if message.content.lower().startswith(".coord"):
            param = message.content[6:]
            coords = await dss.resolve_object(param)
            if await error_check(coords):
                return

            await message.channel.send("{0} Coordinates (ICRS J2k) \nRA: {1}\nDEC: {2}".format(param, coords[0],coords[1]))

        if message.channel.id == self.r9kchannel.id:
            self.r9k.handle_message(self, message)

            
    async def send_img(self, channel, filename, **kwarg):
        """Takes a discord channel and string filename, sends file to given channel and then deletes file"""
        if "msg" in kwarg:
            msg = kwarg["msg"]
        else:
            msg = ""
        await channel.send(msg,file=discord.File(filename))
        os.remove(filename)
                  
    async def on_message_delete(self, message):
        await self.log(message, "DELETED")

    async def on_message_edit(self, before,after):
        if len(before.embeds) == len(after.embeds):#I forget why this is here
            await self.log(before, "EDITED", edit=after.clean_content)

    async def log(self, message, appendage, edit=""):
        if message.channel.id != self.delMsgChannel.id: #dont log the deleted msg channel
            #Format is Timestamp: post/edit/del : channel : author: content 
            string = "{0}: {1} : {2} : {3} : {4} : {5} : {6}".format(str(message.created_at),appendage, message.channel.name, message.author.id, message.author.display_name, message.clean_content, edit)
            with open("logs/"+message.channel.name+".log","a+")as f:
                f.write(string+"\n")
            if appendage != "POSTED":
                await self.delMsgChannel.send(string)
                
                
    async def getImg(self, url):
        """Takes img url that contains 3 or 4 char extension, saves and returns filename"""
        try:
            ext = re.search("\.[A-Za-z]{3,4}$",url).group(0)
        except AttributeError as e:
            return 'Error: invalid url provided or contains an unsupported file extension'
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status==200:
                        time_string = str(int(round(time.time() * 1000)))
                        filename = 'temp/{0}{1}'.format(time_string,ext)
                        f = await aiofiles.open(filename, mode='wb')
                        await f.write(await resp.read())
                        await f.close()
                        return filename

print("Starting Bot...")

f = open("token.txt","r")
bot_token = f.read()
bot_token = bot_token.rstrip()
f.close()

botClient = PlanetaryChadBot()
botClient.run(bot_token, reconnect=True)
