import json
import os

a = {}
if __name__ == "__main__":
    for file in os.listdir("./"):
        if(file.endswith(".json")):
            print(file)
            with open(file, "r") as f:
                read = json.load(f)
                a[read["pattern"]] = {"id":read["id"], "matches":read["matches"]}


with open("../contextual_match.json", "w") as f:
    json.dump(a, f)