import discord, asyncio, curves, os
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
            
            if regionToAssign.lower() in [s.lower() for s in regions]:
                role = get(message.guild.roles,name=regionToAssign.title())
                await message.author.add_roles(role)
                await self.regionChannel.send("{0} You've been added to the {1} role. {2}\n".format(jup, role.name, sat))
            else:
                await self.regionChannel.send("Role: {0} does not exist.".format(regionToAssign))

        if message.channel.id != self.comImgChannel.id and message.attachments != []: #There is an attachment
            file = message.attachments[0] #Grabbing only the first attachment
            
            if  file.filename[file.filename.rfind("."):] in [".jpg",".JPG",".png",".PNG"]:
            
                async def send_img(channel):
                    curvedFilename = self.c.curveImg(file.url) #Curves image, writes and then returns filename written for later access.
                    await channel.send(file=discord.File(curvedFilename))
                    os.remove(curvedFilename)
    
                if message.channel.id != self.curvesChannel.id: #its an image posted and not in curve channel
                    c_1 = await self.curve_reaction()
                    c_2 = await self.curve_reaction()
                    if c_1 and c_2:
                        await send_img(message.channel)
                
                elif message.channel.id==self.curvesChannel.id and message.author.id !=self.bot_id: #if someone posts to curve channel and it isnt the bot itself
                    await send_img(self.curvesChannel)
    
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
f.close()
botClient = PlanetaryChadBot()
botClient.run(bot_token, reconnect=True)