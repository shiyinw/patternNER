import os
import json

dir = "sent/"
a = {}
if __name__ == "__main__":
    for file in os.listdir(dir):
        print(file)
        with open(dir + file, "r") as f:
            read = json.load(f)
            #print(read)
            a.update(read)


for i in a:
    print(i)
with open("stru_sent_all.json", "w") as f:
    json.dump(a, f)