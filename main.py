from random import randint
import discord
from discord import app_commands 
from pymongo import MongoClient
import math

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents = discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        print(f"Logged in as {self.user}.")

client = aclient()
tree = app_commands.CommandTree(client)


#connect to database
mongo_url = ""
cluster = MongoClient(mongo_url)
db = cluster['']
collection = db['']

@tree.command(name = 'login', description='login to your account') #create login command because its cool
async def login(interaction: discord.Interaction):
    user = interaction.user.id
    valid = False
    user_info = collection.find({"user": user})
    for user_info in user_info:
        valid = True
    if valid == True:
        em = discord.Embed(description=f'**<@{user}>You are already logged in.**',color=0x0025ff)
        await interaction.response.send_message(embed=em)
        return 0
    else:
        post = {'user':user, "balance":500.00}
        collection.insert_one(post)
        em = discord.Embed(description='**Logged in!**\nBalance: 500',color=0x0025ff)
        await interaction.response.send_message(embed=em)


@tree.command(name = 'balance', description='check your balance')
async def balance(interaction: discord.Interaction, user : discord.Member = None):
    if user == None:
        user = interaction.user.id
        valid = False
        user_info = collection.find({"user": user})
        for user_info in user_info:
            valid = True
        if not valid:
            em = discord.Embed(description='**You are not logged in use /login to login**',color=0x0025ff)
            await interaction.response.send_message(embed=em)
            return 0
        balance = user_info['balance']
        if balance <= 0:
            em = discord.Embed(description=f'Balance: {balance} reseting bal', color=0x0025ff)
            collection.update_one({"user": user}, {"$set":{"balance":500}})
            await interaction.response.send_message(embed=em)
            return 0
        balance = f"${balance:.2f} :money_with_wings:"
        em = discord.Embed(description=f'**Balance: ${balance}**',color=0x0025ff)
        await interaction.response.send_message(embed=em)
        return 0
    else:
        userid = user.id
        valid = False
        user_info = collection.find({"user": userid})
        for user_info in user_info:
            valid = True
        if valid == True:
            balance = user_info['balance']
            em = discord.Embed(description=f"**{user.mention}'s Balance: ${balance}**",color=0x0025ff)
            await interaction.response.send_message(embed=em)
            return 0

@tree.command(name = 'mines', description='Mines gamemode: 5x5 grid possible mines')
async def mines(interaction: discord.Interaction, bomb_amount : int, bet_amount : int):
    if bet_amount < 5:
        em = discord.Embed(description='Bet amount must be higher than 5', color=0x0025ff)
        await interaction.response.send_message(embed=em)
        return 0
    if bomb_amount > 24 or bomb_amount < 1:
        em = discord.Embed(description='To high of number', color=0x0025ff)
        return 0

    user = interaction.user.id
    valid = False
    user_info = collection.find({"user": user})
    for user_info in user_info:
        valid = True
    balance = user_info['balance']
    if balance < 0:
        em = discord.Embed(description=f'Balance: {balance} reseting bal', color=0x0025ff)
        collection.update_one({"user": user}, {"$set":{"balance":500}})
        await interaction.response.send_message(embed=em)
        return 0
    if bet_amount > balance:
        em = discord.Embed(description='To high of bet amount', color=0x0025ff)
        await interaction.response.send_message(embed=em)
        return 0

    def nCr(n,r):
        f = math.factorial
        return f(n) // f(r) // f(n-r)

    def multiplier_math(bombs, clicks):
        return 0.94 * nCr(25, clicks) / nCr(25 - bombs, clicks)


    if valid == False:
        em = discord.Embed(description='**You are not logged in use /login to login**',color=0x0025ff)
        await interaction.response.send_message(embed=em)
        return 0

    balance = user_info['balance']
    take_away = balance - bet_amount
    collection.update_one({"user": user}, {"$set":{"balance":take_away}})
    balance = user_info['balance']
    bomb_location = []
    grid = ['🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩']
    s_grid = ['🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩','🟩']

    count = 0
    while bomb_amount > count:
        a = randint(0, 24)
        b = a + 1
        if b in bomb_location:
            continue
        bomb_location.append(b)
        grid[a] = '💥'
        count += 1

    em = discord.Embed(color=0x0025ff)
    em.add_field(name='Grid',value=s_grid[0]+s_grid[1]+s_grid[2]+s_grid[3]+s_grid[4]+"\n"+s_grid[5]+s_grid[6]+s_grid[7]+s_grid[8]+s_grid[9]+"\n"+s_grid[10]+s_grid[11]+s_grid[12]+s_grid[13]+ \
        s_grid[14]+'\n'+s_grid[15]+s_grid[16]+s_grid[17]+s_grid[18]+s_grid[19]+"\n"+ \
        s_grid[20]+s_grid[21]+s_grid[22]+s_grid[23]+s_grid[24] + "\n" + f"Bomb Amount: {bomb_amount}\nBet Amount: {bet_amount}\nMultiplier: 0.00\nMines Location (for testing)  \
            {bomb_location}Where do you want to click? (1,25)\n")
    await interaction.response.send_message(embed=em)

    clicked_spots = []
    def check(m):
        return m.author.id == interaction.user.id

    global mutliplier
    multiplier = 1
    multi = -0.5
    while True:
        message = await client.wait_for('message', check=check)
        if message.content == 'yes':
            balance = user_info['balance']
            collection.update_one({"user": user}, {"$set":{"balance":balance + (bet_amount * multi)}})
            em = discord.Embed(description='**Cashed out!** \n ' + grid[0]+grid[1]+grid[2]+grid[3]+grid[4]+"\n"+grid[5]+grid[6]+grid[7]+grid[8]+grid[9]+"\n"+grid[10]+grid[11]+grid[12]+grid[13] \
                +grid[14]+'\n'+grid[15]+grid[16]+grid[17]+grid[18]+grid[19]+"\n"+grid[20]+grid[21]+grid[22]+grid[23]+grid[24] + f"\nProfit: {bet_amount * multi:.2f}", color=0x0025ff)
            await interaction.followup.send(embed=em)
            return 0

        spot = message.content
        if spot in clicked_spots:
            balance = user_info['balance']
            collection.update_one({"user": user}, {"$set":{"balance":balance + (bet_amount * multi)}})
            em = discord.Embed(description='Already clicked there. giving current profit and ending game', color=0x0025ff)
            await interaction.followup.send(embed=em)
            clicked_spots.remove(spot)
            return 0
        clicked_spots.append(spot)

        try:
            if int(spot) in bomb_location:
                spot = int(spot) - 1
                grid[int(spot)] = '❌'
                owner_info = collection.find_one({'user':1021501304461348864})
                owner_balance = owner_info['balance']
                collection.update_one({"user":1021501304461348864}, {"$set":{"balance": owner_balance + bet_amount}})
                mention = interaction.user.mention
                em = discord.Embed(description=f'**{mention}\nYou Lost!**\n' +"\n"+ grid[0]+grid[1]+grid[2]+grid[3]+grid[4]+"\n"+grid[5]+grid[6]+grid[7]+grid[8]+grid[9]+"\n"+grid[10]+grid[11]+ \
                    grid[12]+grid[13]+grid[14]+ \
                    '\n'+grid[15]+grid[16]+grid[17]+grid[18]+grid[19]+"\n"+grid[20]+grid[21]+grid[22]+grid[23]+grid[24] + f"\nLost: {bet_amount}", color=0xff2500)
                await interaction.followup.send(embed=em)
                return 0
        except:
            await interaction.followup.send("Try again")
            balance = user_info['balance']
            collection.update_one({"user": user}, {"$set":{"balance":balance + (bet_amount * multi)}})
            return 0
        temp_s = int(spot) - 1
        try:
            s_grid[int(temp_s)] = '🟦'
        except:
            await interaction.followup.send("to high of a number try again")
            balance = user_info['balance']
            collection.update_one({"user": user}, {"$set": {"balance": balance + bet_amount}})
            return 0

        #spot = int(spot) - 1
        grid[int(spot) - 1] = '🟦'

        multiplier += 1
        multi = multiplier_math(bomb_amount, multiplier)
        em = discord.Embed(description=s_grid[0]+s_grid[1]+s_grid[2]+s_grid[3]+s_grid[4]+"\n"+s_grid[5]+s_grid[6]+s_grid[7]+s_grid[8]+s_grid[9]+"\n"+s_grid[10]+s_grid[11]+s_grid[12]+s_grid[13]+ \
            s_grid[14]+'\n'+s_grid[15]+s_grid[16]+s_grid[17]+s_grid[18]+s_grid[19]+"\n"+s_grid[20]+s_grid[21]+s_grid[22]+s_grid[23]+s_grid[24] + \
            f"\nMultiplier: {multi:.2f}\nCashout? (yes) or (1,25)", color=0x0025ff)
        await interaction.followup.send(embed=em)


client.run('bot token')
