from discord.ext import commands
import json
import re
import random
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
async def on_message(msg):
    content = msg.content
    response = ''
    words = content.split(' ')
    if not msg.author.id == botID and re.search(r'[0-9]+ .*', content):
        for i in range(1, len(words)):
            if re.search(r'inch', words[i]) and re.match(r'-?([0-9]\.)*[0-9]+', words[i-1]):
                value = convert(words[i], float(words[i-1]))
                response += words[i-1] + " " + words[i] + ' -> ' + str(value)[:5] + ' cm.\n'
            if re.match(r'f(ee)?t', words[i]) and re.match(r'-?([0-9]\.)*[0-9]+', words[i-1]):
                value = convert(words[i], float(words[i - 1]))
                response += words[i - 1] + " " + words[i] + ' -> ' + str(value)[:5] + ' m.\n'
            if re.match(r'(((f|F)$)|((f|F) ))', words[i]) and re.match(r'-?([0-9]\.)*[0-9]+', words[i - 1]):
                value = convert(words[i], float(words[i - 1]))
                response += words[i - 1] + " " + words[i] + ' -> ' + str(value)[:5] + ' C.\n'
            if re.match(r'(lb|pounds)', words[i]) and re.match(r'-?([0-9]\.)*[0-9]+', words[i - 1]):
                value = convert(words[i], float(words[i - 1]))
                response += words[i - 1] + " " + words[i] + ' -> ' + str(value)[:5] + ' kg.\n'
            if re.match(r'mile', words[i]) and re.match(r'-?([0-9]\.)*[0-9]+', words[i - 1]):
                value = convert(words[i], float(words[i - 1]))
                response += words[i - 1] + " " + words[i] + ' -> ' + str(value)[:5] + ' km.\n'
            if re.match(r'freedom', words[i]) and re.match(r'-?([0-9]\.)*[0-9]+', words[i - 1]):
                value = random.randint(1, 100000)
                units = ['m', 'kg', 'V', 'C', 'mol', 's']
                index = random.randint(0, 5)
                response += words[i - 1] + " " + words[i] + ' -> ' + str(value)[:5] + ' ' + units[index] + '.\n'
        await bot.send_message(msg.channel, response)
    elif not msg.author.id == botID and re.search(r'[0-9]+(a|A|p|P)[mM] [a-zA-Z]', content):
        for i in range(1, len(words)):
            if re.match(r'(CET|cet)', words[i]) and re.match(r'[0-9]+(a|A|p|P)[mM]', words[i - 1]):
                value = convertTimezone(words[i], words[i - 1])
                response += words[i - 1] + " " + words[i] + ' -> ' + value + ' UTC.\n'
            if re.match(r'(CST|cst)', words[i]) and re.match(r'[0-9]+(a|A|p|P)[mM]', words[i - 1]):
                value = convertTimezone(words[i], words[i - 1])
                response += words[i - 1] + " " + words[i] + ' -> ' + value + ' UTC.\n'
            if re.match(r'(EST|est)', words[i]) and re.match(r'[0-9]+(a|A|p|P)[mM]', words[i - 1]):
                value = convertTimezone(words[i], words[i - 1])
                response += words[i - 1] + " " + words[i] + ' -> ' + value + ' UTC.\n'
        await bot.send_message(msg.channel, response)
    else:
        await bot.process_commands(msg)

def convert(freedomUnit, value):
    if re.match(r'inch', freedomUnit):
        return value/0.39370
    if re.match(r'f(ee)?t', freedomUnit):
        return value*0.3048
    if re.match(r'(((f|F)$)|((f|F) ))', freedomUnit):
        return (value - 32.0) / 1.8
    if re.match(r'(lb|pounds)', freedomUnit):
        return value/ 2.2046
    if re.match(r'mile', freedomUnit):
        return value / 0.62137

def convertTimezone(zone, value):
    time24h = 0
    if re.match(r'(p|P)[mM]', value[len(value)-2:]):
        time24h = int(value[:1]) + 12
    else:
        time24h = int(value[:1])
    if re.match(r'(CET|cet)', zone):
        time24h -= 1
    if re.match(r'(CST|cst)', zone):
        time24h += 6
    if re.match(r'(EST|est)', zone):
        time24h += 5

    return str(time24h) + ':00'

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
