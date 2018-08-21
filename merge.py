import os
import json

dir = "sent/"
if __name__ == "__main__":
    a = {}
    for file in os.listdir(dir):
        print(file)
        with open(dir + file, "r") as f:
            read = json.load(f)
            #print(read)
            a.update(read)
           # print(a)
    print(a)
    with open("stru_sent_all.json", "w") as f:
        json.dump(a, f)