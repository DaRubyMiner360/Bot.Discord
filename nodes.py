import runtime

class Program:
  def __init__(self, events):
    self.events = events

  def __repr__(self, depth = 0):
    res = ""
    res += ("\t" * depth) + "program"  + "\n"
    for e in self.events:
      res += e.__repr__(depth + 1)
      
    return res

  # returns runtime object
  def runtime(self):
    res = runtime.Runtime()

    # add listeners to runtime object
    for e in self.events:
      e.runtime = res

      res.listeners.append(
        [
          e.conditionMethod,
          e.statementMethod
        ]
      )

    return res

class Event:
  def __init__(self, condition, statement):
    self.condition = condition
    self.statement = statement

  def __repr__(self, depth = 0):
    res = ""
    res += ("\t" * depth) + "event" + "\n"
    res += self.condition.__repr__(depth + 1)
    res += self.statement.__repr__(depth + 1)
    return res

  # returns true if statement should run, and false if it should not
  async def conditionMethod(self):
    return await self.condition.check(self.runtime)

  # runs statement
  async def statementMethod(self):
    return await self.statement.run(self.runtime)

class Statement:
  def __init__(self, lines):
     self.lines = lines

  def __repr__(self, depth = 0):
    res = ""
    res += ("\t" * depth) + "statement: " + "\n"
    for m in self.lines:
      res += m.__repr__(depth + 1)
    return res
  
  # runs all lines
  async def run(self, runtime):
    for l in self.lines:
      await l.run(runtime)

class Command:
  def __init__(self, name, args):
    self.name = name
    self.args = args

  def __repr__(self, depth = 0):
    res = ""
    res += ("\t" * depth) + "command: " + self.name + "\n"
    for arg in self.args:
      res += arg.__repr__(depth + 1)
    return res

  # runs a command according to the methods array in runtime
  async def run(self, runtime):
    # runtime.convertToDict(runtime)

    newArgs = []

    # run all args
    for arg in self.args:
      newArgs.append(await arg.run(runtime))

    # call
    if not "igrequest" in self.name:
        if runtime.requestedMessage == "" or runtime.requestedMessage == runtime.vars["message"]:
          pass
        else:
          return

        if len(runtime.requestedNotMessage) != 0:
          for m in runtime.requestedNotMessage:
            if (m != runtime.vars["message"]):
              pass
            else:
              if m == runtime.requestedNotMessage[-1]:
                return
        
        if len(runtime.requestedAuthor) != 0:
          for a in runtime.requestedAuthor:
            if ("#" in a):
              if (a == str(runtime.author)):
                pass
            elif ("#" not in a):
              if (a == runtime.vars["authorName"]):
                pass
              else:
                return
            else:
              if a == runtime.requestedAuthor[-1]:
                return

        if len(runtime.requestedNotAuthor) != 0:
          for b in runtime.requestedNotAuthor:
            if ("#" in b):
              if (b != str(runtime.author)):
                pass
            elif ("#" not in b):
              if (b != runtime.vars["authorName"]):
                pass
              else:
                return
            else:
              if b == runtime.requestedNotAuthor[-1]:
                return

        if len(runtime.requestedRole) != 0:
          for c in runtime.requestedRole:
            if (c == runtime.vars["authorRoles"]):
              pass
            else:
              if c == runtime.requestedRole[-1]:
                return

        if len(runtime.requestedNotRole) != 0:
          for d in runtime.requestedNotRole:
            if (d != runtime.vars["authorRoles"]):
              pass
            else:
              if d == runtime.requestedNotRole[-1]:
                return

        if len(runtime.requestedChannel) != 0:
          for e in runtime.requestedChannel:
            if (e != runtime.channel):
              pass
            else:
              if e == runtime.requestedChannel[-1]:
                return

        if len(runtime.requestedNotChannel) != 0:
          for f in runtime.requestedNotChannel:
            if (f != runtime.channel):
              pass
            else:
              if f == runtime.requestedNotChannel[-1]:
                return

        """for a in runtime.requestedAuthor:
          if ("#" in a):
            if (a == str(runtime.author)):
              pass
          elif ("#" not in a):
            if (a == runtime.vars["authorName"]):
              if (b == runtime.vars["authorRoles"] for b in runtime.requestedRole):
                pass
              elif len(runtime.requestedRole) == 0:
                pass
            else:
              return
          elif len(runtime.requestedAuthor) == 0:
            if (b == runtime.vars["authorRoles"] for b in runtime.requestedRole):
              pass
            elif len(runtime.requestedRole) == 0:
              pass
            else:
              return
          else:
            return"""

        if runtime.vars["isBot"] == "True" and runtime.requestedBot == 1:
          return
        elif runtime.vars["isBot"] == "False" and runtime.requestedBot == 2:
          return
    
        if runtime.vars["channelType"] == "Guild" and runtime.requestedChannelType == 2:
          return
        elif runtime.vars["channelType"] == "DM" and runtime.requestedChannelType == 1:
          return

    # print(self.name)
    # print("requestedAuthor")
    # print(runtime.requestedAuthor)
    # print("requestedNotAuthor")
    # print(runtime.requestedNotAuthor)
    # print("requestedRole")
    # print(runtime.requestedRole)
    # print("requestedNotRole")
    # print(runtime.requestedNotRole)
    # print("requestedChannel")
    # print(runtime.requestedChannel)

    await (runtime.methods[self.name])(newArgs, runtime)

class Assignment:
  def __init__(self, name, value):
    self.name = name
    self.value = value

  def __repr__(self, depth = 0):
    res = ""
    res += ("\t" * depth) + "assignment: " + self.name + "\n"
    res += self.value.__repr__(depth + 1)
    return res

  # sets variable
  async def run(self, runtime):
    runtime.vars[self.name] = self.value

class Name:
  def __init__(self, id):
    self.id = id

  def __repr__(self, depth = 0):
    res = ("\t" * depth) + "name: " + self.id + "\n" 
    return res

  # returns value behind name
  async def run(self, runtime):
    try:
      return await runtime.vars[self.id].run(runtime)
    except:
      return

  # returns check method result of value behind name
  async def check(self, runtime):
    try:
      return await runtime.vars[self.id].check(runtime)
    except:
      return False

class String:
  def __init__(self, value):
    self.value = value

  def __repr__(self, depth = 0):
    res = ("\t" * depth) + "string: " + self.value + "\n" 
    return res

  # return string
  async def run(self, runtime):
    return self.value

  # check if string is message
  async def check(self, runtime):
    if runtime.event and self.value == runtime.vars["message2"]:
      return True
    # if (self.value == "Bot.OnReady" and runtime.vars["message"] == "Bot.OnReady") or (self.value == "Bot.OnMemberJoin" and runtime.vars["message"] == "Bot.OnMemberJoin") or (self.value == "Bot.OnMemberLeave" and runtime.vars["message"] == "Bot.OnMemberLeave") or (self.value == "Bot.OnRawReactionAdd" and runtime.vars["message"] == "Bot.OnRawReactionAdd") or (self.value == "Bot.OnRawReactionRemove" and runtime.vars["message"] == "Bot.OnRawReactionRemove") or (self.value == "Bot.OnBegin" and runtime.vars["message"] == "Bot.OnBegin"):
    #   if runtime.event:
    #     return True
    #   else:
    #     return False
    ignorePrefix = False
    if self.value.startswith("${noprefix}"):
      self.value = self.value.replace("${noprefix}", "")
      ignorePrefix = True
    if runtime.vars["message2"] == "":
      if self.value.endswith(" "):
        v = ""
        for i in range(len(self.value)):
          if i != len(self.value) - 1:
            v = v + self.value[i]
        if runtime.autoPrefix and not ignorePrefix:
          return runtime.prefix + v.lower() in runtime.vars["message"].lower()
        else:
          return v.lower() in runtime.vars["message"].lower()
      if runtime.autoPrefix and not ignorePrefix:
        return runtime.prefix + self.value.lower() == runtime.vars["message"].lower()
      else:
        return self.value.lower() == runtime.vars["message"].lower()
    return False
