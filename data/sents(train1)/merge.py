import json
import os

a = []
if __name__ == "__main__":
    for file in os.listdir("./"):
        if(file.endswith(".json")):
            print(file)
            with open(file, "r") as f:
                read = json.load(f)
                a.extend(read)


with open("../sents_train1.json", "w") as f:
    json.dump(a, f)