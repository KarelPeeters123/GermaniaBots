from discord.ext import commands
import json
import os
commandPrefix = '*'
bot = commands.Bot(command_prefix=commandPrefix)

maxVotes = {"vote": 1,
            "consul": 2,
            "senator": 3,
            "centurion": 5}
emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫',
          '🇬', '🇭', 'ℹ', '🇯', '🇰', '🇱',
          '🇲', '🇳', '🇴', '🇵', '🇶', '🇷',
          '🇸', '🇹']
letters = ['A', 'B', 'C', 'D', 'E', 'F',
           'G', 'H', 'I', 'J', 'K', 'L',
           'M', 'N', 'O', 'P', 'Q', 'R',
           'S', 'T']
botID = '518766307194175509'

@bot.event
async def on_ready():
    print('bot is ready')

def isHigherUp(role):
    return  role == 'Praefectus Germanicus' or role == 'Patricii Romani' or role == 'Senatus Germanicum'

@bot.event
async def on_reaction_add(reaction, user):
    if not user.id == botID:
        with open('userids.json') as f:
            userids = json.load(f)
        channel = reaction.message.channel
        with open('voteID.txt', 'r') as f:
            text = f.read()
            voteId = text.split('|')[0]
            voteType = text.split('|')[1]
        candidates = []
        with open('elections.txt', 'r') as file:
            for line in file.readlines():
                if line.startswith(voteType):
                    candidates.append(line[(len(voteType)+3):].strip('\n'))
        if voteId == reaction.message.id:
            print(userids.keys())
            if user.id not in userids.keys():
                print(user.id)
                with open('userids.json', 'w') as f:
                    userids[user.id] = []
                    json.dump(userids, f)
            for i in range(len(emojis)):
                if reaction.emoji == emojis[i]:

                    if candidates[i] not in userids[user.id] and len(userids[user.id]) < maxVotes[voteType]:
                        print('reached this point')
                        with open('results.json') as f:
                            results = json.load(f)
                        results[candidates[i]] = results[candidates[i]] + 1
                        await bot.remove_reaction(reaction.message, reaction.emoji, user)
                        with open('userids.json', 'w') as f:
                            print(candidates[i])
                            userids[user.id].append(candidates[i])
                            json.dump(userids, f)
                        scoreboard = '```python\n'
                        for i in range(len(candidates)):
                            scoreboard = scoreboard + candidates[i] + ' has ' + str(results[candidates[i]]) + ' votes. (' + letters[i] + ')\n'
                        scoreboard = scoreboard + '```'
                        await bot.edit_message(await bot.get_message(channel, voteId), scoreboard)
                        with open('results.json', 'w') as f:
                            json.dump(results, f)
            if voteType == 'vote' and len(userids[user.id]) < 1:
                if reaction.emoji == '✅':
                    with open('results.json') as f:
                        results = json.load(f)
                    results['aye'] = results['aye'] + 1
                    await bot.remove_reaction(reaction.message, reaction.emoji, user)
                    await bot.edit_message(await bot.get_message(channel, voteId), '```python\n' +
                            str(results['aye']) + ' romans have voted AYE. (✅)\n' +
                            str(results['nay']) + ' romans have voted NAY. (❎)\n'
                            '```')
                    with open('userids.json', 'w') as f:
                        userids[user.id].append('aye')
                        json.dump(userids, f)
                elif reaction.emoji == '❎':
                    with open('results.json') as f:
                        results = json.load(f)
                    results['nay'] = results['nay'] + 1
                    await bot.remove_reaction(reaction.message, reaction.emoji, user)
                    await bot.edit_message(await bot.get_message(channel, voteId), '```python\n' +
                            str(results['aye']) + ' romans have voted AYE. (✅)\n' +
                            str(results['nay']) + ' romans have voted NAY. (❎)\n'
                            '```')
                    with open('userids.json', 'w') as f:
                        userids[user.id].append('nay')
                        json.dump(userids, f)
                with open('results.json', 'w') as f:
                    json.dump(results, f)


@bot.command(pass_context = True)
async def vote(ctx):
    top_role = ctx.message.author.top_role.name
    if isHigherUp(top_role):
        id = int(str(ctx.message.content)[6:].lstrip())
        motion = ''
        with open("motions.txt", 'r') as file:
            for line in file:
                if '#' + str(id) + ' ' in line:
                    motion = line.split(' : ')[1]
                    print(motion)
        emptyDict = {}
        emptyResultsDict = {"aye": 0, "nay": 0}
        with open('userids.json', 'w') as f:
            json.dump(emptyDict, f)
        with open('results.json', 'w') as f:
            json.dump(emptyResultsDict, f)
        await bot.say('__***' + motion + '***__')
        msg = await bot.say('```python\n' +
                            '0 romans have voted AYE. (✅)\n' +
                            '0 romans have voted NAY. (❎)\n'
                            '```')
        voteId = msg.id + '|vote'
        with open('voteID.txt', 'w') as f:
            f.write(voteId)
        await bot.add_reaction(msg, '✅')
        await bot.add_reaction(msg, '❎')
    else:
        await bot.say('You are not authorised to organise a vote. Speak to a higher-up to organise a vote')

@bot.command(pass_context = True)
async def motion(ctx):
    msg = str(ctx.message.content)[8:]
    num_lines = sum(1 for line in open('motions.txt'))
    num_lines += sum(1 for line in open('resolved.txt'))
    id = num_lines + 1
    motion = '#' + str(id) + ' | ' + str(ctx.message.author) + ' @ ' + \
             ctx.message.timestamp.strftime('%d/%m/%Y %H:%M:%S') + ' : ' + msg + '\n'
    with open('motions.txt', 'a') as file:
        file.write(motion)
    print(motion)
    # logging.info(motion)
    await bot.say("Motion is noted. view all motions with the [*motions] command")
@bot.command(pass_context = True)
async def resolve(ctx):
    top_role = ctx.message.author.top_role.name
    index = str(ctx.message.content)
    index = index.split(' ')[1]
    if index == 'all':
        lines = []
        with open('motions.txt', 'r') as file:
            for line in file:
                if '#' not in line:
                    lines.append(line)
                if '#' in line:
                    with open('resolved.txt', 'a') as file:
                        file.write(line)
        with open('motions.txt', 'w') as file:
            file.writelines(lines)
        await bot.say('All motions are resolved.')
    else:
        resolvedMotion = ''
        index = int(index)
        lines = []
        with open('motions.txt', 'r') as file:
            for line in file:
                if '#' + str(index) not in line:
                    lines.append(line)
                if '#' + str(index) in line:
                    resolvedMotion = line
        owner = resolvedMotion.split(' ')[2]
        user = str(ctx.message.author)
        if isHigherUp(top_role) or owner == user:
            with open('resolved.txt', 'a') as file:
                file.write(resolvedMotion)
            with open('motions.txt', 'w') as file:
                file.writelines(lines)
            await bot.say("Motion is resolved.")
        else:
            await bot.say("You do not have the authority to resolve this motion")
@bot.command()
async def motions():
    motions = {}
    with open("motions.txt", 'r') as file:
        for line in file:
            motions[str(line[1:].split(' | ')[0])] = line
    if len(motions) == 0:
        await bot.say('There are no standing motions right now')
    allMotions = ""
    keyList = motions.keys()
    keyList = sorted(keyList)
    for i in keyList:
        allMotions += motions[i]
    await bot.say(allMotions)

bot.run(os.environ.get('GERMANTOKEN'))
