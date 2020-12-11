import parse
import sys
import os
from keepAlive import keepAlive
import lex

os.system("")

code = ""
code2 = ""
code3 = ""
codelines = []
file = ""
imported = []
isImported = False
code0 = open(sys.argv[1] if len(sys.argv) > 1 else "main.dis", "r").read()
codelines = code0.splitlines()
code = code0
# while any("import " in s for s in codelines):
for line in codelines:
  if line.replace("	", "").replace(" ", "").startswith("#"):
    code = code.replace(line, "")
  elif 'import ' in line:
    file = line.split('import ', 1)[-1]
    file = file.replace('"', "")
    file = file.replace("\n", "")
    file = file.replace(".dis", "")
    file = file.replace(".", "/")
    file += ".dis"
    for q in imported:
      if file == q:
        isImported = True
    if not isImported:
      if code2 != "":
        code2 += "\n"
      codelines2 = open(file, "r").read()
      code2 += codelines2

      code = code.replace(line, "")
      imported.append(file)
    
    isImported = False
  elif 'importend ' in line:
    file = line.split('importend ', 1)[-1]
    file = file.replace('"', "")
    file = file.replace("\n", "")
    file = file.replace(".dis", "")
    file = file.replace(".", "/")
    file += ".dis"
    for q in imported:
      if file == q:
        isImported = True
    if not isImported:
      if code3 != "":
        code3 += "\n"
      codelines3 = open(file, "r").readlines()
      for line3 in codelines3:
        code3 += line3

      code = code.replace(line, "")
      imported.append(file)

    isImported = False
  # else:
  #   # code += line[:-1]
  #   code += line

  codelines = code.splitlines()

while any("import " in s for s in code2.splitlines()):
  for line in code2.splitlines():
    if line.replace("	", "").replace(" ", "").startswith("#"):
      code2 = code2.replace(line, "")
    elif 'import ' in line:
      file = line.split('import ', 1)[-1]
      file = file.replace('"', "")
      file = file.replace("\n", "")
      file = file.replace(".dis", "")
      file = file.replace(".", "/")
      file += ".dis"
      if code2 != "":
        code2 += "\n"
      codelines2 = open(file, "r").readlines()
      for line2 in codelines2:
        code2 += line2

      code2 = code2.replace(line, "")
    elif 'importend ' in line:
      file = line.split('importend ', 1)[-1]
      file = file.replace('"', "")
      file = file.replace("\n", "")
      file = file.replace(".dis", "")
      file = file.replace(".", "/")
      file += ".dis"
      if code3 != "":
        code3 += "\n"
      codelines3 = open(file, "r").readlines()
      for line3 in codelines3:
        code3 += line3

      code2 = code2.replace(line, "")
    # else:
    #   # code += line[:-1]
    #   code2 += line

while any("import " in s for s in code3.splitlines()):
  for line in code3.splitlines():
    if line.replace("	", "").replace(" ", "").startswith("#"):
      code3 = code3.replace(line, "")
    elif 'import ' in line:
      file = line.split('import ', 1)[-1]
      file = file.replace('"', "")
      file = file.replace("\n", "")
      file = file.replace(".dis", "")
      file = file.replace(".", "/")
      file += ".dis"
      if code2 != "":
        code2 += "\n"
      codelines2 = open(file, "r").readlines()
      for line2 in codelines2:
        code2 += line2

      code3 = code3.replace(line, "")
    elif 'importend ' in line:
      file = line.split('importend ', 1)[-1]
      file = file.replace('"', "")
      file = file.replace("\n", "")
      file = file.replace(".dis", "")
      file = file.replace(".", "/")
      file += ".dis"
      if code3 != "":
        code3 += "\n"
      codelines3 = open(file, "r").readlines()
      for line3 in codelines3:
        # code3 += line3[:-1]
        code3 += line3

        code3 = code3.replace(line, "")
    # else:
    #   # code += line[:-1]
    #   code3 += line
if code2 != "":
  code2 += code
  code = code2
if code3 != "":
  code += code3
tokens = lex.lex(code)
tree = parse.parse(tokens)
runtime = tree.runtime()

keepAlive()
runtime.run()
