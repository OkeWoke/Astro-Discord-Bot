import discord, asyncio, curves, os, dss
from discord.utils import get

class PlanetaryChadBot (discord.Client):

    bot_id = 457372655926902785
    
    regions = ["New Zealand","Australia","Europe","United States","Canada","Central America","South America","Far East","Middle East"]

    async def on_ready(self):
        self.jup = get(self.emojis, name='Jupiter')
        self.sat = get(self.emojis, name='Saturn')
        self.lefty = get(self.emojis, name='lefty')
        
        self.regionChannel = self.get_channel(248395661244891136)
        self.delMsgChannel = self.get_channel(472912167704854529)
        self.comImgChannel = self.get_channel(544305081009438720)
        self.curvesChannel = self.get_channel(556987083122802720)
        
        self.c = curves.Curve()
        
        print("Logged in")
    
    async def on_message(self, message):
        
        await self.log(message, "POSTED")
        
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
            
            if  file.filename[file.filename.rfind("."):] in [".jpg",".JPG",".png",".PNG"]:
                if message.channel.id != self.curvesChannel.id: #its an image posted and not in curve channel
                    c_1 = await self.curve_reaction()
                    c_2 = await self.curve_reaction()
                    if c_1 and c_2:
                        curvedFilename = self.c.curveImg(file.url) #Curves image, writes and then returns filename written for later access.
                        await self.send_img(message.channel, curvedFilename)
                
                elif message.channel.id==self.curvesChannel.id and message.author.id !=self.bot_id: #if someone posts to curve channel and it isnt the bot itself
                    curvedFilename = self.c.curveImg(file.url) 
                    await send_img(self.curvesChannel, curvedFilename)
            
        if message.content.lower().startswith(".dss"):
            
            async def error(msg):
                if msg=="":
                    msg = "Error: incorrect usage of .dss\nFormat - '.dss Object Name, fov radius in deg'\nExample 1:  '.dss Orion Nebula, 2'\nExample 2: '.dss 5h35m16s -5d23m27s, 2'"
                await message.channel.send(msg)
            params = message.content.lstrip('.dss').split(',')

            if len(params) == 1:
                radius = 1 #default radii 1 degrees
            elif len(params) == 2:
                if params[1].strip().replace('.','',1).isdigit():
                    radius = float(params[1].strip())
                    if radius < 0.1 or radius>20:
                        print("fov err")
                        await error("Error: FOV Radius should be between 0.1 and 20 degrees")
                        return
                else:
                    await error("")
                    return
            else:
                await error("")
                return

            objname = params[0].strip()
            f1 = await dss.reqImg(objname,radius)
            if f1.startswith("Error:"):
                await error(f1)
                return
            self.c.percentileClip(f1)
            await self.send_img(message.channel, f1)
            
    async def send_img(self, channel, filename):
        """Takes a discord channel and string filename, sends file to given channel and then deletes file"""
        await channel.send(file=discord.File(filename))
        os.remove(filename)
        
    async def curve_reaction(self):
        def check(reaction,user):
            return reaction.emoji == self.lefty
            
        try:
            reaction, user = await self.wait_for('reaction_add', timeout=600, check=check)
        except asyncio.TimeoutError:
            return False
        return True
            
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

print("Starting Bot...")

f = open("token.txt","r")
bot_token = f.read()
bot_token = bot_token.rstrip()
f.close()

botClient = PlanetaryChadBot()
botClient.run(bot_token, reconnect=True)
