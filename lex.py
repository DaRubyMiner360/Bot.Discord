import shared

# Constant variables
EQUAL, EVENT, STRING, COLON, COMMAND, SEPERATOR = 'EQUAL', 'EVENT', 'STRING', 'COLON', 'COMMAND', 'SEPERATOR'

# Array of commands that the user can use
"""commands = [
  "say",
  "reply",
  "replypos",
  "replyend",
  "createtextchannel",
  "createvoicechannel",
  "requestauthor",
  "requestnotauthor",
  "requestrole",
  "requestnotrole",
  "requestchannel",
  "requestnotchannel"
  "requestbot",
  "embed",
  "requestchanneltype",
  "clear",
  "replykick",
  "kick",
  "replyban",
  "ban",
]"""
commands = shared.commands
# print(commands)

# Token class used to create token object with two attributes: type & value
class Token:
  def __init__(self, type, value):
    self.type = type
    self.value = value

  def __str__(self):
    return 'Token({type}, {value})'.format(type = self.type, value=repr(self.value))

  def __repr__(self):
    return self.__str__()

# Array of tokens which is the output
tokens = []

# Takes code and outputs tokens
def lex(text):
  text = text
  pos = 0
  
  isString = False
  isString2 = False
  isString3 = False
  currentString = ""

  isName = False
  currentName = ""

  # Iterate through each character in code and convert into tokens one-by-one
  while pos < len(text):

    current_item = text[pos]

    # if is name and will not be name
    if isName and not (current_item in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"):
      isName = False

      if currentName != "not":
      # add name to tokens
        tokens.append(Token("COMMAND" if currentName in commands else "NAME", currentName))

      # reset
      currentName = ""

    # Logic to find if current token is a string
    if current_item == '"' or current_item == "'":

      # toggle string
      if not isString3 and current_item == "'":
        isString2 = not isString2
        isString = isString2
      elif not isString2 and current_item == '"':
        isString3 = not isString3
        isString = isString3

      # if toggled to false
      if isString == False: 

        # add to tokens
        tokens.append(Token(STRING, currentString))

      # reset
      currentString = ""
        
    elif isString:
      # if is string, add to currentString
      currentString += current_item

    elif text[pos:pos + 3] == "on ":
      # on token
      pos += 2
      tokens.append(Token(EVENT, "on"))

    # elif text[pos:pos + 7] == "onjoin ":
    #   # onjoin token
    #   pos += 6
    #   tokens.append(Token(EVENT, "onjoin"))

    # Create equal token
    elif current_item == "=":
      tokens.append(Token(EQUAL, "="))

    # Create colon token
    elif current_item == ":":
      # colon token
      tokens.append(Token(COLON, ":"))

    # Create comma token
    elif current_item == ",":
      # seperator token
      tokens.append(Token(SEPERATOR, ","))
    
    # Check if current_item is a Name Token
    elif current_item in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
      # set isName
      isName = True

      # add char
      currentName += current_item

    # incremenent
    pos += 1

  # Create string token
  if (len(currentString) > 0):
    tokens.append(Token(STRING, currentString))

  # Create command token
  if (len(currentName) > 0):
    tokens.append(Token("COMMAND" if currentName in commands else "NAME", currentName))

  # Output
  return tokens
