from random import randint
import discord
from discord import app_commands
from pymongo import MongoClient
import math

#simple code to use slash commands
class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents = discord.Intents.all())
        self.synced = False
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        print("Bot is online")

client = aclient()
tree = app_commands.CommandTree(client)

#connect to database
mongo_url = '' #connection string
cluster = MongoClient(mongo_url)
db = cluster[''] #collection name
collection = db[''] #database name

@tree.command(name = 'login', description='login to your account') #simple login command to get user id and set balance
async def login(interaction: discord.Interaction):
    user = interaction.user.id
    valid = False
    user_info = collection.find({"user": user})
    for user_info in user_info:
        valid = True
    if valid == True:
        em = discord.Embed(description=f"**<@{user}>**You are already logged in.", color=0x0025ff)
        await interaction.response.send_message(embed=em)
        return 0
    else:
        post = {'user': user, 'balance': 500.00}
        collection.insert_one(post)
        em = discord.Embed(description=f"**<@{user}>**Logged in!\nBalance $500", color=0x0025ff)
        await interaction.response.send_message(embed=em)

@tree.command(name = 'balance', description='checm your balance')
async def balance(interaction: discord.Interaction, user : discord.Member = None):
    if user == None:
        user = interaction.user.id
        valid = False
        user_info = collection.find({"user": user})
        for user_info in user_info:
            valid = True
        if not valid:
            em = discord.Embed(description='**You are not logged in, use /login to login**', color=0x0025ff)
            await interaction.response.send_message(embed=em)
            return 0
        balance = user_info['balance']
        if balance <= 0:
            em = discord.Embed(description=f'**Balance: {balance}, resetting to 500**', color=0x0025ff)
            await interaction.response.send_message(embed=em)
            return 0
        balance = f"{balance:.2f}"
        em = discord.Embed(description=f'**Balance: ${balance}**', color=0x0025ff)
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
            em = discord.Embed(description=f"** {user.mention}'s Balance: ${balance}**", color=0x0025ff)
            await interaction.response.send_message(embed=em)
            return 0
    

@tree.command(name = 'tip', description='tip')
async def tip(interaction: discord.Interaction, amount : int, recipient : discord.Member):
    local_user = interaction.user.id
    recipient_id = recipient.id
    valid = False
    local_user_info = collection.find({"user": local_user}) #check if person sending money is logged in
    for local_user_info in local_user_info:
        valid = True

    if valid == True:
        recipient_info = collection.find({"user": recipient_id}) #get all needed info the the user we need to send money to
        valid = False

        for recipient_info in recipient_info:
            valid = True
        
        if valid == True:
            local_balance = local_user_info['balance']
            new_balance = local_balance - amount

            recipient_balance = recipient_info['balance']
            recipient_new_bal = recipient_balance + amount

            collection.update_one({"user": recipient_id}, {"$set": {"balance": recipient_new_bal}}) #give the money to the person
            collection.update_one({"user": local_user}, {"$set": {"balance": new_balance}}) #take the money from the person sending it

            em = discord.Embed(description=f'{interaction.user.mention} sent ${amount} to {recipient.mention}', color=0x0025ff)
            await interaction.response.send_message(embed=em)

@tree.command(name = 'mines', description='Mines gamemode: 5x5 grid of possible mines')
async def mines(interaction: discord.Interaction, bomb_amount : int, bet_amount : int):
    if bet_amount < 5: #bet amt check
        em = discord.Embed(description=f"Bet amount must be higher than 5", color=0x0025ff)
        await interaction.response.send_message(embed=em)
        return 0
    if bomb_amount > 24 or bomb_amount <= 0:
        em = discord.Embed(description='Number to high', color=0x0025ff)
        await interaction.response.send_message(embed=em)
        return 0
    
    user = interaction.user.id
    valid = False
    user_info = collection.find({"user": user})
    for user_info in user_info:
        valid = True

    if valid == False:
        em = discord.Embed(description='You are not logged in, use /login to login', color=0x0025ff)
        await interaction.response.send_message(embed=em)
        return 0
    
    balance = user_info['balance']

    if bet_amount > balance:
        em = discord.Embed(description='You do not have enough', color=0x0025ff)
        await interaction.response.send_message(embed=em)
        return 0
    
    #math stuff to find the multiplier of mines and click amount stake multi cus they same
    def nCr(n,r):
        f = math.factorial
        return f(n) // f(r) // f(n-r)

    #also math stuff to find multi stake multi cus they same
    def multiplier_math(bombs, clicks):
        return 0.94 * nCr(25, clicks) / nCr(25 - bombs, clicks)

    #take the bet amt from the users balance
    take_away = balance - bet_amount
    collection.update_one({"user": user}, {"$set": {"balance": take_away}})
    balance = user_info['balance']
    
    #grid stuff
    bomb_location = []
    #25 total (0,24)
    grid = ['🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦']
    #another grid to use when sending clicked spots without revealing bomb location
    s_grid = ['🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦','🟦']

    #convert bomb amt to actual bombs
    count = 0
    while bomb_amount > count:
        a = randint(0,24) #0,24 since grid starts at 0
        b = a + 1 # + 1 so its the same as 1,25
        if b in bomb_location:
            continue
        bomb_location.append(b)
        grid[a] = '💥' #make bomb locations equal to emoji on the grid
        count += 1 # add 1 so we can keep track of how much times we ran it
    
    em = discord.Embed(color=0x0025ff)
    #this part will be in the description
    em.add_field(name = 'Grid', value = s_grid[0]+s_grid[1]+s_grid[2]+s_grid[3]+s_grid[4]+"\n"+s_grid[5]+s_grid[6]+s_grid[7]+s_grid[8]+s_grid[9] + "\n" +
        s_grid[10]+s_grid[11]+s_grid[12]+s_grid[13]+s_grid[14] + "\n" + s_grid[15]+s_grid[16]+s_grid[17]+s_grid[18]+s_grid[19] + '\n' + s_grid[20] + s_grid[21] + \
            s_grid[22] + s_grid[23] + s_grid[24] + f"\nBomb Amount: {bomb_amount}\nBet Amount: {bet_amount}\nWhere do you want to click? (1,25)") #prob a better way to do this, its jus the way i do it
    await interaction.response.send_message(embed=em)

    #command to check who used message
    def check(m):
        return m.author.id == interaction.user.id

    clicked_spots = []
    global multiplier
    multiplier = 1
    multi = -0.5
    while True:
        #get user input and check if its equal to person who did command
        message = await client.wait_for('message', check=check)

        #check if user wants to cash out
        if message.content == 'yes':
            balance = user_info['balance']
            collection.update_one({"user":user}, {"$set": {"balance": balance + (bet_amount * multi)}}) # add the mone to the users bal
            #use grid instead of s_grid bcs grid has bomb location saved
            em = discord.Embed(description='**Cashed out!** \n' + grid[0]+grid[1]+grid[2]+grid[3]+grid[4]+"\n"+grid[5]+grid[6]+grid[7]+grid[8]+grid[9] + "\n" + \
        grid[10]+grid[11]+grid[12]+grid[13]+grid[14] + "\n" + grid[15]+grid[16]+grid[17]+grid[18]+grid[19] + '\n' + grid[20] + grid[21] + \
            grid[22] + grid[23] + grid[24] + f"\nProfit: {bet_amount * multi:.2f}", color=0x0025ff)
            await interaction.followup.send(embed=em)
            return 0
        
        #check if user already clicked in spot they want to click
        spot = message.content
        if spot in clicked_spots:
            balance = user_info['balance']
            collection.update_one({"user":user}, {"$set": {"balance": balance + (bet_amount * multi)}}) #give them current profit and end game
            em = discord.Embed(description='Already clicked there \n', color=0x0025ff)
            await interaction.followup.send(embed=em)
            return 0
        clicked_spots.append(spot)

        try:
            if int(spot) in bomb_location:
                spot = int(spot) - 1
                grid[int(spot)] = '❌' #what u want the spot do be if u click and theres a bomb

                # add money to someones balance when users lose (cant let money go in void :))
                owner_info = collection.find_one({"user": 1021501304461348864})
                owner_balance = owner_info['balance']
                collection.update_one({"user": 1021501304461348864}, {"$set": {"balance": owner_balance + bet_amount}}) #send money to owner balance
                mention = interaction.user.mention
                em = discord.Embed(description=f'**{mention}\nYou Lost!**\n' + grid[0]+grid[1]+grid[2]+grid[3]+grid[4]+"\n"+grid[5]+grid[6]+grid[7]+grid[8]+grid[9] + "\n" + \
        grid[10]+grid[11]+grid[12]+grid[13]+grid[14] + "\n" + grid[15]+grid[16]+grid[17]+grid[18]+grid[19] + '\n' + grid[20] + grid[21] + \
            grid[22] + grid[23] + grid[24] + f"\nLost: {bet_amount}", color=0x0025ff)
                await interaction.followup.send(embed=em)
                return 0
        except:
            await interaction.followup.send("Try again")
            balance = user_info['balance']
            collection.update_one({"user":user}, {"$set": {"balance": balance + bet_amount}})
            return 0
        temp_s = int(spot) - 1
        #we use a try incase they put a number larger than 25 meaning out of range for the list
        try:
            s_grid[int(temp_s)] = '🟩' #make the clicked spot equal to specific emoji
        except:
            await interaction.followup.send("to high of numeber try again")
            balance = user_info['balance']
            collection.update_one({"user":user}, {"$set": {"balance": balance + bet_amount}})
            return 0

        grid[int(spot) - 1] = '🟩'

        multiplier += 1
        multi = multiplier_math(bomb_amount, multiplier)
        em = discord.Embed(description= s_grid[0]+s_grid[1]+s_grid[2]+s_grid[3]+s_grid[4]+"\n"+s_grid[5]+s_grid[6]+s_grid[7]+s_grid[8]+s_grid[9] + "\n" + \
        s_grid[10]+s_grid[11]+s_grid[12]+s_grid[13]+s_grid[14] + "\n" + s_grid[15]+s_grid[16]+s_grid[17]+s_grid[18]+s_grid[19] + '\n' + s_grid[20] + s_grid[21] + \
            s_grid[22] + s_grid[23] + s_grid[24] + f"\nMultiplier: {multi:.2f}\nCashout? (yes) or (1,25)", color=0x0025ff)
        await interaction.followup.send(embed=em)



client.run('discord bot token')
