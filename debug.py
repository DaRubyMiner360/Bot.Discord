import runtime
import discord
import lex
import parse

async def error(text, channel=None):
  if channel == None:
    print("\033[1m" + "\033[91m" + text + "\033[0m")
  else:
    [await runtime.runtime.channel.send(text)]

if __name__ == "__main__":
  code = open("main.dis", "r").read()

  print("\nCODE:")
  print(code)
  
  print("\nTOKENS:")
  tokens = lex.lex(code)
  for i in tokens:
    print(i)
  
  print("\nTREE:")
  tree = parse.parse(tokens)
  print(tree) 
  
  print("\nRUNTIME:")
  r = tree.runtime()
  r.run()