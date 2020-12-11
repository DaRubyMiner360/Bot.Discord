import smtplib, ssl
import json
import uuid
import atexit
import shared

import asyncio
import debug

import discord
from discord.ext import commands
import os

class Runtime():
  # def __init__(self):
  #   global methods
  #   coms = {}
  #   for i in range(len(shared.commands)):
  #     coms[shared.commands[i]] = ""
  #     if shared.commands[i] == "print":
  #       coms[shared.commands[i]] = self.eprint
  #     else:
  #       if shared.commands[i].startswith("ig"):
  #         coms[shared.commands[i]] = eval("self." + shared.commands[i].replace("ig", "", 1))
  #       else:
  #         coms[shared.commands[i]] = eval("self." + shared.commands[i])
  #   methods = coms

  def convertToDict(runtime):
    # possibles = globals().copy()
    # possibles.update(locals())
    # coms = {shared.commands[i]: possibles.get(shared.commands[i]) for i in range(0, len(shared.commands), 2)}
    
    # global methods
    coms = {}
    for i in range(len(shared.commands)):
      coms[shared.commands[i]] = ""
      if shared.commands[i] == "print":
        coms[shared.commands[i]] = runtime.eprint
      else:
        if shared.commands[i].startswith("ig"):
          coms[shared.commands[i]] = eval("runtime." + shared.commands[i].replace("ig", "", 1))
        else:
          coms[shared.commands[i]] = eval("runtime." + shared.commands[i])
    runtime.methods = coms

  reaction_roles_data = {}

  try:
    with open("reactionRoles.json") as file:
      reaction_roles_data = json.load(file)
  except (FileNotFoundError, json.JSONDecodeError) as ex:
    with open("reactionRoles.json", "w") as file:
      json.dump({}, file)

  status = discord.Status.online
  activity = discord.Game("")

	# current channel
  channel = None

	# current guild
  guild = None

  event = False

  requestedAuthor = []
  requestedNotAuthor = []
  
  requestedRole = []
  requestedNotRole = []

  requestedChannel = []
  requestedNotChannel = []

  payload = None

  requestedMessage = ""
  requestedNotMessage = []

  args = []
	
	# 0 = Either
	# 1 = Guild
	# 2 = DM
  requestedChannelType = 0

	# 0 = Either
	# 1 = Not Bot
	# 2 = Bot
  requestedBot = 0

  author = None

  autoPrefix = True
  prefix = ""

  client = commands.Bot(command_prefix="")
  # client = discord.Client()
  token = os.environ["TOKEN"]

	# all variables are global
  vars = {}

  clearing = False

	# listeners is an array of arrays of size 2
	# first item in each array is condition method
	# second is statement method
  listeners = []

  @atexit.register
  def store_reaction_roles(self):
    with open("reactionRoles.json", "w") as file:
      json.dump(self.reaction_roles_data, file)

  def replaceVars(self, string):
    string2 = string.replace("${prefix}", self.prefix).replace("${timestamp}", str(self.vars["timestamp"])).replace("${message}", self.vars["message"]).replace("${authorname}", self.vars["authorName"]).replace("${author}", self.vars["authorName"]).replace("\\", "\\\\")
    if self.guild is not None:
      string2 = string2.replace("${guild}", self.guild.name)
    if self.channel is not None:
      string2 = string2.replace("${channel}", self.channel.name)
    if self.author is not None:
      string2 = string2.replace("${mention}", str(self.author.mention))
    if self.args is not None:
      string2 = string2.replace("${args.count}", str(len(self.args) - 1)).replace("${mesargs.count}", str(len(self.args)))
    
    if "${args[" in string2 and "]}" in string2:
      string2 = string2.replace("${args[", "args[").replace("]}", "]")
      start = 'args['
      end = ']'
      index = string2[string2.find(start)+len(start):string2.rfind(end)]
      if int(index) < len(self.args) - 1:
        string2 = string2.split(start)[0] + eval("self.args[" + str(int(index) + 1) + "]") + string2.split(end)[-1]
      else:
        string2 = string2.split(start)[0] + eval("self.args[-1]") + string2.split(end)[-1]
    
    if "${mesargs[" in string2 and "]}" in string2:
      string2 = string2.replace("${mesargs[", "mesargs[").replace("]}", "]")
      start = 'mesargs['
      end = ']'
      index = string2[string2.find(start)+len(start):string2.rfind(end)]
      if int(index) < len(self.args) - 2:
        string2 = string2.split(start)[0] + eval("self.args[" + index + "]") + string2.split(end)[-1]
      else:
        string2 = string2.split(start)[0] + eval("self.args[-1]") + string2.split(end)[-1]
    return string2

	# methods
  async def setprefix(args, runtime):
    prefix = runtime.replaceVars(args[0])
    while prefix.startswith(" "):
      prefix.replace(" ", "", 1)
    runtime.prefix = prefix

    if len(args) > 1:
      runtime.autoPrefix = bool(args[1])
    else:
      runtime.autoPrefix = True

  async def eprint(args, runtime):
    for i in args:
      print(runtime.replaceVars(i))
  
  async def say(args, runtime):
    if runtime.channel is not None:
      [await runtime.channel.send(runtime.replaceVars(i)) for i in args]

  async def reply(args, runtime):
    if runtime.channel is not None:
      [await runtime.channel.send(str(runtime.author.mention) + runtime.replaceVars(i)) for i in args]
		
  async def replypos(args, runtime):
    if runtime.channel is not None:
      [await runtime.channel.send(i.replace("${mention}", runtime.replaceVars(str(runtime.author.mention)))) for i in args]

  async def replyend(args, runtime):
    if runtime.channel is not None:
      [await runtime.channel.send(runtime.replaceVars(i) + str(runtime.author.mention)) for i in args]

  async def createtextchannel(args, runtime):
    if runtime.guild is not None:
      [await runtime.guild.create_text_channel(runtime.replaceVars(i)) for i in args]

  async def createvoicechannel(args, runtime):
    if runtime.guild is not None:
      [await runtime.guild.create_voice_channel(runtime.replaceVars(i)) for i in args]

  async def requestauthor(args, runtime):
    runtime.requestedAuthor = args
    if args[0] == "":
      runtime.requestedAuthor.clear()

  async def requestnotauthor(args, runtime):
    runtime.requestedNotAuthor = args
    if args[0] == "":
      runtime.requestedNotAuthor.clear()

  async def requestrole(args, runtime):
    runtime.requestedRole = args
    if args[0] == "":
      runtime.requestedRole.clear()

  async def requestnotrole(args, runtime):
    runtime.requestedNotRole = args
    if args[0] == "":
      runtime.requestedNotRole.clear()

  async def requestchannel(args, runtime):
    runtime.requestedChannel = args
    if args[0] == "":
      runtime.requestedChannel.clear()

  async def requestnotchannel(args, runtime):
    runtime.requestedNotChannel = args
    if args[0] == "":
      runtime.requestedNotChannel.clear()

  async def requestbot(args, runtime):
    if args[0] == "1" or args[0].lower() == "useronly" or args[0].lower(
		) == "user" or args[0].lower() == "nobot" or args[0].lower(
		) == "nobots":
      runtime.requestedBot = 1
    elif args[0] == "2" or args[0].lower() == "botonly" or args[0].lower(
		) == "bot" or args[0].lower() == "nouser" or args[0].lower(
		) == "nousers":
      runtime.requestedBot = 2
    else:
      runtime.requestedBot = 0

  async def embed(args, runtime):
    if len(args) < 3:
     [await debug.error(
			    "Too few arguments! First arg should be 'title', Second arg should be 'description', Third arg should be 'color'"
			), runtime.channel]
    title = runtime.replaceVars(args[0]).replace("\\_", "\\||//++\\||//").replace("_", " ").replace("\\||//++\\||//", "_").replace("\\", "\\\\")
    desc = runtime.replaceVars(args[1]).replace("\\_", "\\||//++\\||//").replace("_", " ").replace("\\||//++\\||//", "_").replace("\\", "\\\\")
    color = runtime.replaceVars(args[2]).replace("\\_", "\\||//++\\||//").replace("_", " ").replace("\\||//++\\||//", "_").replace("\\", "\\\\")
    embed = None

    embed = discord.Embed(title=title, description=desc, color=int(color, 16))

    for i in args:
      arg = runtime.replaceVars(i).replace("\\_", "\\||//++\\||//").replace("_", " ").replace("\\||//++\\||//", "_").replace("\\", "\\\\")
      if arg.startswith("addField: "):
        arg = arg.replace("addField: ", "", 1).replace("name: ", "", 1)
        if " value: " in arg:
          embed.add_field(
					    name=arg.split(" value: ", 1)[0],
					    value=arg.split(" value: ", 1)[1],
					    inline=False)
        else:
          embed.add_field(name=arg, value="", inline=False)
				# embed.add_field(name=arg.split(", value = ", 1)[0], value=arg.split(", value = ", 1)[1].replace(", value = ", "", 1).replace(", value=", "", 1))
				# embed.add_field(name="Fiel1", value="hi", inline=False)
    if runtime.channel is not None:
      [await runtime.channel.send(embed=embed)]
		
  async def requestchanneltype(args, runtime):
    if args[0] == "Guild":
      runtime.requestedChannelType = 1
    elif args[0] == "DM":
      runtime.requestedChannelType = 2
    else:
	    runtime.requestedChannelType = 0

  async def clear(args, runtime):
    number = int(runtime.replaceVars(args[0]))
    number2 = runtime.replaceVars(args[0])
    if runtime.channel is not None:
      if number == 1:
        runtime.clearing = True
        await runtime.channel.send(f'Clearing {number2} message...')
      else:
        runtime.clearing = True
        await runtime.channel.send(f'Clearing {number2} messages...')
      i = 1
      while i <= number + 2 and i > -1:
        if i == number + 2:
          i = -1
        if i > -1:
          runtime.clearing = True
          await runtime.channel.purge(limit = i)
          i += 1
      if number == 1:
        runtime.clearing = True
        tmp = await runtime.channel.send(f'Cleared {number2} message.')
        await asyncio.sleep(1)
        runtime.clearing = True
        await tmp.delete()
      else:
        runtime.clearing = True
        tmp = await runtime.channel.send(f'Cleared {number2} messages.')
        await asyncio.sleep(1)
        runtime.clearing = True
        await tmp.delete()

  async def replykick(args, runtime):
    if len(args) > 0:
      await runtime.author.kick(reason=args[0])
    else:
      await runtime.author.kick()
  
  async def kick(args, runtime):
    if len(args) > 1:
      await discord.Member(args[0].replace("${author}", runtime.author)).kick(reason=args[1])
    else:
      await discord.Member(args[0].replace("${author}", runtime.author)).kick()

  async def replyban(args, runtime):
    if len(args) > 0:
      await runtime.author.ban(reason=args[0])
    else:
      await runtime.author.ban()

  async def ban(args, runtime):
    if len(args) > 1:
      await discord.Member(args[0].replace("${author}", runtime.author)).ban(reason=args[1])
    else:
      await discord.Member(args[0].replace("${author}", runtime.author)).ban()

  async def opendm(args, runtime):
    [await runtime.author.send(runtime.replaceVars(i)) for i in args]

  async def requestmessage(args, runtime):
    runtime.requestedMessage = args[0]

  async def requestnotmessage(args, runtime):
    runtime.requestedNotMessage = args
    if args[0] == "":
      runtime.requestedNotMessage.clear()

  async def setstatus(args, runtime):
    runtime.status = eval("discord.Status." + runtime.replaceVars(args[0].lower()))
    await runtime.client.change_presence(status=runtime.status, activity=runtime.activity)

  async def setactivity(args, runtime):
    activityType = "discord." + runtime.replaceVars(args[0])
    runtime.activity = eval(activityType + "('" + runtime.replaceVars(args[1]) + "')")
    await runtime.client.change_presence(status=runtime.status, activity=runtime.activity)
    # if runtime.status != None:
      # await self.client.change_presence(status=runtime.status)
    # else:
    #   await self.client.change_presence(status=discord.Status.online)

  async def sleep(args, runtime):
    await asyncio.sleep(int(args[0]))

  async def reaction(args, runtime):
    emote = args[0]
    role = discord.utils.find(lambda g: g.name == args[1], runtime.guild.roles)
    channel = discord.utils.find(lambda g: g.name == args[2], runtime.guild.text_channels)
    title = args[3]
    message = args[4]

    embed = discord.Embed(title=title, description=message)
    msg = await channel.send(embed=embed)
    await msg.add_reaction(emote)
    runtime.add_reaction(runtime.guild.id, emote, role.id, channel.id, msg.id)

  async def reaction_add(args, runtime):
    emote = args[0]
    role = discord.utils.find(lambda g: g.name == args[1], runtime.guild.roles)
    channel = discord.utils.find(lambda g: g.name == args[2], runtime.guild.text_channels)
    messageID = args[3]

    runtime.add_reaction(runtime.guild.id, emote, role.id, channel.id, messageID)

  async def reactions(args, runtime):
    guild_id = runtime.guild.id
    data = runtime.reaction_roles_data.get(str(guild_id), None)
    embed = discord.Embed(title="Reaction Roles")
    if data is None:
      embed.description = "There are no reaction roles set up right now."
    else:
      for index, rr in enumerate(data):
        emote = rr.get("emote")
        role_id = rr.get("roleID")
        role = runtime.guild.get_role(role_id)
        channel_id = rr.get("channelID")
        message_id = rr.get("messageID")
        embed.add_field(
          name=index,
          value=f"{emote} - @{role} - [message](https://www.discordapp.com/channels/{guild_id}/{channel_id}/{message_id})",
          inline=False,
        )
    await runtime.channel.send(embed=embed)
  
  async def reaction_remove(args, runtime):
    index = args[0]

    guild_id = runtime.guild.id
    data = runtime.reaction_roles_data.get(str(guild_id), None)
    embed = discord.Embed(title=f"Remove Reaction Role {index}")
    rr = None
    if data is None:
      embed.description = "Given Reaction Role was not found."
    else:
      embed.description = (
        "Do you wish to remove the reaction role below? Please react with 🗑️."
      )
      rr = data[index]
      emote = rr.get("emote")
      role_id = rr.get("roleID")
      role = runtime.guild.get_role(role_id)
      channel_id = rr.get("channelID")
      message_id = rr.get("messageID")
      _id = rr.get("id")
      embed.set_footer(text=_id)
      embed.add_field(
        name=index,
        value=f"{emote} - @{role} - [message](https://www.discordapp.com/channels/{guild_id}/{channel_id}/{message_id})",
        inline=False,
      )
    msg = await runtime.channel.send(embed=embed)
    if rr is not None:
        await msg.add_reaction("🗑️")

        def check(reaction, user):
          return (
            reaction.vars["messageID"] == msg.id
            and user == runtime.author
            and str(reaction.emoji) == "🗑️"
          )

        reaction, user = await runtime.client.wait_for("reaction_add", check=check)
        data.remove(rr)
        runtime.reaction_roles_data[str(guild_id)] = data
        runtime.store_reaction_roles()

  async def add_reaction(args, runtime):
    guild_id = args[0]
    emote = args[1]
    role_id = args[2]
    channel_id = args[3]
    message_id = args[4]
    
    if not str(guild_id) in runtime.reaction_roles_data:
        runtime.reaction_roles_data[str(guild_id)] = []
        runtime.reaction_roles_data[str(guild_id)].append(
        {
          "id": str(uuid.uuid4()),
          "emote": emote,
          "roleID": role_id,
          "channelID": channel_id,
          "messageID": message_id,
        }
    )
    runtime.store_reaction_roles()

  async def parse_reaction_payload(args, runtime):
    payload = runtime.payload
    
    guild_id = payload.guild_id
    data = runtime.reaction_roles_data.get(str(guild_id), None)
    if data is not None:
      for rr in data:
        emote = rr.get("emote")
        if payload.message_id == rr.get("messageID"):
          if payload.channel_id == rr.get("channelID"):
            if str(payload.emoji) == emote:
              guild = runtime.client.get_guild(guild_id)
              role = guild.get_role(rr.get("roleID"))
              user = guild.get_member(payload.user_id)
              return role, user
    return None, None

  async def readjson(args, runtime):
    with open(args[0], "r") as f:
      data = json.load(f)
      return data

  async def writejson(args, runtime):
    with open(args[0], "w") as f:
      json.dump(args[1], f)

  # methods = {}
  methods = {
      "setprefix": setprefix,
	    "print": eprint,
      "say": say,
	    "reply": reply,
	    "replypos": replypos,
	    "replyend": replyend,
	    "createtextchannel": createtextchannel,
	    "createvoicechannel": createvoicechannel,
      "requestauthor": requestauthor,
      "requestnotauthor": requestnotauthor,
      "requestrole": requestrole,
      "requestnotrole": requestnotrole,
      "requestchannel": requestchannel,
      "requestnotchannel": requestnotchannel,
	    "requestbot": requestbot,
	    "embed": embed,
	    "requestchanneltype": requestchanneltype,
      "clear": clear,
      "replykick": replykick,
      "kick": kick,
      "replyban": replyban,
      "ban": ban,
      "opendm": opendm,
      "igrequestauthor": requestauthor,
      "igrequestnotauthor": requestnotauthor,
      "igrequestrole": requestrole,
      "igrequestnotrole": requestnotrole,
      "igrequestchannel": requestchannel,
      "igrequestnotchannel": requestnotchannel,
	    "igrequestbot": requestbot,
	    "igrequestchanneltype": requestchanneltype,
      "requestmessage": requestmessage,
      "requestnotmessage": requestnotmessage,
      "igrequestmessage": requestmessage,
      "igrequestnotmessage": requestnotmessage,
      "setstatus": setstatus,
      "setactivity": setactivity,
      "sleep": sleep,
      "reaction": reaction,
      "reactionadd": reaction_add,
      "reactions": reactions,
      "reactionremove": reaction_remove,
      "addreaction": add_reaction,
      "parsereactionpayload": parse_reaction_payload,
      "readjson": readjson,
      "writejson": writejson
  }

  # shared.commands = methods.keys()
  # print(shared.commands)

  def run(self):
    @self.client.event
    async def on_ready():
      self.event = True

      self.vars["message2"] = "Bot.OnReady"
      self.vars["message"] = "Bot.OnReady"
      self.args = "Bot.OnReady".split()
      self.vars["authorName"] = self.client.user.name
      self.author = self.client.user

      self.vars["timestamp"] = ""

      self.vars["isBot"] = ""
      self.vars["channelType"] = ""

      # go through listeners
			# i[0] is a condition method
			# i[1] is a statement method
      for i in self.listeners:
        if await (i[0])():
          await (i[1])()

      print(f"Your Bot, '{self.client.user.name}', Is Online!")

    @self.client.event
    async def on_member_join(member):
      self.event = True

      self.vars["message2"] = "Bot.OnMemberJoin"
      self.vars["message"] = "Bot.OnMemberJoin"
      self.args = "Bot.OnMemberJoin".split()
      self.author = member
      self.vars["authorName"] = member.name

      self.vars["timestamp"] = ""

      if member.bot:
        self.vars["isBot"] = "True"
      else:
        self.vars["isBot"] = "False"

      self.guild = member.guild
      self.vars["channelType"] = "Guild"
      self.channel = self.guild.default_channel

      # go through listeners
			# i[0] is a condition method
			# i[1] is a statement method
      for i in self.listeners:
        if await (i[0])():
          await (i[1])()

    @self.client.event
    async def on_member_remove(member):
      self.event = True

      self.vars["message2"] = "Bot.OnMemberLeave"
      self.vars["message"] = "Bot.OnMemberLeave"
      self.args = "Bot.OnMemberLeave".split()
      self.author = member
      self.vars["authorName"] = member.name

      self.vars["timestamp"] = ""

      if member.bot:
        self.vars["isBot"] = "True"
      else:
        self.vars["isBot"] = "False"

      self.guild = member.guild
      self.vars["channelType"] = "Guild"
      self.channel = self.guild.default_channel

      # go through listeners
			# i[0] is a condition method
			# i[1] is a statement method
      for i in self.listeners:
        if await (i[0])():
          await (i[1])()

    @self.client.event
    async def on_guild_channel_create(channel):
      self.event = True

      self.vars["message"] = "Bot.OnGuildChannelCreate"
      self.vars["message2"] = "Bot.OnGuildChannelCreate"
      self.args = "Bot.OnGuildChannelCreate".split()
      # self.author = member
      # self.vars["authorName"] = member.name

      self.vars["timestamp"] = ""

      # if member.bot:
        # self.vars["isBot"] = "True"
      # else:
        # self.vars["isBot"] = "False"

      self.guild = channel.guild
      self.vars["channelType"] = "Guild"
      self.channel = channel

      # go through listeners
			# i[0] is a condition method
			# i[1] is a statement method
      for i in self.listeners:
        if await (i[0])():
          await (i[1])()

    @self.client.event
    async def on_guild_channel_delete(channel):
      self.event = True

      self.vars["message2"] = "Bot.OnGuildChannelDelete"
      self.vars["message2"] = "Bot.OnGuildChannelDelete"
      self.args = "Bot.OnGuildChannelDelete".split()
      # self.author = member
      # self.vars["authorName"] = member.name

      self.vars["timestamp"] = ""

      # if member.bot:
        # self.vars["isBot"] = "True"
      # else:
        # self.vars["isBot"] = "False"

      self.guild = channel.guild
      self.vars["channelType"] = "Guild"
      self.channel = channel

      # go through listeners
			# i[0] is a condition method
			# i[1] is a statement method
      for i in self.listeners:
        if await (i[0])():
          await (i[1])()

    @self.client.event
    async def on_raw_reaction_add(payload):
      self.event = True

      channel = self.client.get_channel(payload.channel_id)
      message = await channel.fetch_message(payload.message_id)

      self.vars["message2"] = "Bot.OnRawReactionAdd"
      self.vars["message"] = message.content
      self.args = message.content.split()

      self.payload = payload
      
      role, user = self.parse_reaction_payload(payload)
      if role is not None and user is not None:
        await user.add_roles(role, reason="ReactionRole")
      
      self.author = user
      
      self.vars["authorName"] = user.name

      self.vars["timestamp"] = ""

      if user.bot:
        self.vars["isBot"] = "True"
      else:
        self.vars["isBot"] = "False"

      self.guild = user.guild
      self.vars["channelType"] = "Guild"
      self.channel = self.guild.default_channel

      # go through listeners
			# i[0] is a condition method
			# i[1] is a statement method
      for i in self.listeners:
        if await (i[0])():
          await (i[1])()

      await on_raw_message_event(message)

    
    @self.client.event
    async def on_raw_reaction_remove(payload):
      self.event = True

      channel = self.client.get_channel(payload.channel_id)
      message = await channel.fetch_message(payload.message_id)

      self.vars["message2"] = "Bot.OnRawReactionRemove"
      self.vars["message"] = message.content
      self.args = message.content.split()

      self.payload = payload
      
      role, user = self.parse_reaction_payload(payload)
      if role is not None and user is not None:
        await user.remove_roles(role, reason="ReactionRole")

      self.author = user
      self.vars["authorName"] = user.name

      self.vars["timestamp"] = ""

      if user.bot:
        self.vars["isBot"] = "True"
      else:
        self.vars["isBot"] = "False"

      self.guild = user.guild
      self.vars["channelType"] = "Guild"
      self.channel = self.guild.default_channel

      # go through listeners
			# i[0] is a condition method
			# i[1] is a statement method
      for i in self.listeners:
        if await (i[0])():
          await (i[1])()

      await on_raw_message_event(message)

    
    @self.client.event
    async def on_message(message):
      self.event = True

      # ignore messages sent by self
      if message.author == self.client.user:
        return

      self.vars["message2"] = "Bot.OnMessage"
      self.vars["message"] = message.content
      self.vars["messageID"] = message.id
      self.args = message.content.split()
      self.author = message.author
      self.vars["authorName"] = message.author.name

      self.vars["timestamp"] = message.created_at

      # set current channel
      self.channel = self.client.get_channel(message.channel.id)

      # set current guild
      if not isinstance(message.channel, discord.channel.DMChannel):
        self.guild = self.client.get_guild(message.channel.guild.id)
        self.vars["channelType"] = "Guild"
      else:
        self.vars["channelType"] = "DM"
			  
      if message.author.bot:
        self.vars["isBot"] = "True"
      else:
        self.vars["isBot"] = "False"

			# go through listeners
			# i[0] is a condition method
			# i[1] is a statement method
      for i in self.listeners:
        if await (i[0])():
          await (i[1])()

      self.vars["message2"] = ""
      self.event = False
      
      # go through listeners
			# i[0] is a condition method
			# i[1] is a statement method
      for i in self.listeners:
        if await (i[0])():
          await (i[1])()

      await on_message_event(message)
          

    @self.client.event
    async def on_message_edit(before, after):
      self.event = True

      if before.content == after.content:
        return
      
      # ignore messages sent by self
      if before.author == self.client.user:
        return

      if self.clearing:
        self.clearing = False
        return

      self.vars["message2"] = "Bot.OnMessageEdit"
      self.vars["message"] = after.content
      self.vars["messageID"] = after.id
      self.args = after.content.split()
      self.author = before.author
      self.vars["authorName"] = before.author.name

      self.vars["timestamp"] = after.created_at

      # set current channel
      self.channel = self.client.get_channel(after.channel.id)

      # set current guild
      if not isinstance(after.channel, discord.channel.DMChannel):
        self.guild = self.client.get_guild(after.channel.guild.id)
        self.vars["channelType"] = "Guild"
      else:
        self.vars["channelType"] = "DM"
			  
      if before.author.bot:
        self.vars["isBot"] = "True"
      else:
        self.vars["isBot"] = "False"

			# go through listeners
			# i[0] is a condition method
			# i[1] is a statement method
      for i in self.listeners:
        if await (i[0])():
          await (i[1])()

      await on_message_event(after)

    
    @self.client.event
    async def on_message_delete(message):
      self.event = True

      if not self.clearing:
        # ignore messages sent by self
        # if message.author == self.client.user:
        #   return

        self.vars["message2"] = "Bot.OnMessageDelete"
        self.vars["message"] = message.content
        self.vars["messageID"] = message.id
        self.args = message.content.split()
        self.author = message.author
        self.vars["authorName"] = message.author.name

        self.vars["timestamp"] = message.created_at

        # set current channel
        self.channel = self.client.get_channel(message.channel.id)

        # set current guild
        if not isinstance(message.channel, discord.channel.DMChannel):
          self.guild = self.client.get_guild(message.channel.guild.id)
          self.vars["channelType"] = "Guild"
        else:
          self.vars["channelType"] = "DM"
  
        if message.author.bot:
          self.vars["isBot"] = "True"
        else:
          self.vars["isBot"] = "False"

			  # go through listeners
			  # i[0] is a condition method
			  # i[1] is a statement method
        for i in self.listeners:
          if await (i[0])():
            await (i[1])()

        await on_message_event(message)
      else:
        self.clearing = False

    
    @self.client.event
    async def on_raw_message_delete(payload):
      self.event = True

      channel = self.client.get_channel(payload.channel_id)
      message = await channel.fetch_message(payload.message_id)

      if not self.clearing:
        # ignore messages sent by self
        # if message.author == self.client.user:
        #   return

        self.vars["message2"] = "Bot.OnRawMessageDelete"
        self.vars["message"] = message.content
        self.vars["messageID"] = payload.message_id
        self.args = message.content.split()
        self.author = message.author
        self.vars["authorName"] = message.author.name

        self.payload = payload

        self.vars["timestamp"] = message.created_at

        # set current channel
        self.channel = channel

        # set current guild
        if not isinstance(message.channel, discord.channel.DMChannel):
          self.guild = self.client.get_guild(message.channel.guild.id)
          self.vars["channelType"] = "Guild"
        else:
          self.vars["channelType"] = "DM"
  
        if message.author.bot:
          self.vars["isBot"] = "True"
        else:
          self.vars["isBot"] = "False"

			  # go through listeners
			  # i[0] is a condition method
			  # i[1] is a statement method
        for i in self.listeners:
          if await (i[0])():
            await (i[1])()

        await on_raw_message_event(message)
      else:
        self.clearing = False

    
    @self.client.event
    async def on_raw_message_event(message):
      self.event = True

      # ignore messages sent by self
      # if message.author == self.client.user:
      #   return

      self.vars["message2"] = "Bot.OnRawMessageEvent"
      self.vars["message"] = message.content
      self.vars["messageID"] = message.id
      self.args = message.content.split()
      self.author = message.author
      self.vars["authorName"] = message.author.name

      self.vars["timestamp"] = message.created_at

      # set current channel
      self.channel = self.client.get_channel(message.channel.id)

      # set current guild
      if not isinstance(message.channel, discord.channel.DMChannel):
        self.guild = self.client.get_guild(message.channel.guild.id)
        self.vars["channelType"] = "Guild"
      else:
        self.vars["channelType"] = "DM"
			  
      if message.author.bot:
        self.vars["isBot"] = "True"
      else:
        self.vars["isBot"] = "False"

			# go through listeners
			# i[0] is a condition method
			# i[1] is a statement method
      for i in self.listeners:
        if await (i[0])():
          await (i[1])()

      on_message_event(message)

    
    @self.client.event
    async def on_message_event(message):
      self.event = True

      # ignore messages sent by self
      # if message.author == self.client.user:
      #   return

      self.vars["message2"] = "Bot.OnMessageEvent"
      self.vars["message"] = message.content
      self.vars["messageID"] = message.id
      self.args = message.content.split()
      self.author = message.author
      self.vars["authorName"] = message.author.name

      self.vars["timestamp"] = message.created_at

      # set current channel
      self.channel = self.client.get_channel(message.channel.id)

      # set current guild
      if not isinstance(message.channel, discord.channel.DMChannel):
        self.guild = self.client.get_guild(message.channel.guild.id)
        self.vars["channelType"] = "Guild"
      else:
        self.vars["channelType"] = "DM"
			  
      if message.author.bot:
        self.vars["isBot"] = "True"
      else:
        self.vars["isBot"] = "False"

			# go through listeners
			# i[0] is a condition method
			# i[1] is a statement method
      for i in self.listeners:
        if await (i[0])():
          await (i[1])()
    
    # os.system("python -m smtpd -c DebuggingServer -n localhost:1025")
    # atexit.register(self.st, self.token)
    self.client.run(self.token)
