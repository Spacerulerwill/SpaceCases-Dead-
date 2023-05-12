import os

with open("LICENCE.txt", "r") as f:
    LICENCE_SRC = "\n\n\"\"\"\n"  + f.read() + "\n\"\"\""

root = os.getcwd() + "/test_files"
for path, subdirs, files in os.walk(root):
    for name in files:
        if name.endswith(".py"):
            with open(os.path.join(path, name), "a") as f:
                f.write(LICENCE_SRC)