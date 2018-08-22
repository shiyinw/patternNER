from utils import StructPatt
import time
import json

"""
### Input
detected pattern in **train_CRAFT_cnt_N_p.tsv**
tagged named entities (chemical, gene and fuzzy"O") train0_truth.tsv

### Output
confidence of patterns and named entities
Then evaluate them by the matching them to train1.ner.txt

### data location
tagged file from fuzzy-ner: /shared/data/shizhi2/data_fuzzyCRF/case/train0_all.tsv, train1_all.tsv (edited) **train0_gene.tsv**, **train1_chem.tsv**
ground truth: /shared/data/shizhi2/data_fuzzyCRF/bio-ner/**train0_all.tsv**, **train1_all.tsv** contain all the gene and chemical labels
patternlist: **patternlist.xlsx**
"""


REUSE = 1

structpatt = StructPatt()
structpatt.load_words("data/train_CRAFT.tsv")  # named entities and their types
# structpatt.load_words("data/train1_all.tsv")
# structpatt.load_words("data/train0_all.tsv")
structpatt.load_sentence("data/train_CRAFT.tsv")
patt = structpatt.load_pattern("data/train_CRAFT_cnt_N_p.tsv") # patterns

start = time.time()
cnt = 0

word_matches = {}
for i in patt:
    name = str(i[0])
    word_matches[name]={"matches":[], "type":i[1], "cnt":i[2]}
    cnt += 1
    for w in structpatt.words:
        m = structpatt.pmatch(i[0], w[0], withtype=0)
        if(len(m)>0):
            word_matches[name]["matches"].extend(m)


    word_matches[name]["matches"] = list(set(word_matches[name]["matches"]))
    if (len(word_matches[name]["matches"]) == 0):
        del word_matches[name]["matches"]
    #print("pattern", i)
    #print("match", word_matches[name]["matches"])
    if(cnt%100==0):
        print(cnt, time.time()-start)

with open("stru_word_matches.json", "w") as f:
    json.dump(word_matches, f)



sent_matches = {}

for cnt in range(0, len(patt)):
    i = patt[cnt]
    name = str(i[0])
    sent_matches[name]={"matches":{}, "type":i[1], "cnt":i[2]}

    for w in structpatt.sent:
        # print(i[0], w)
        m = structpatt.pmatch(i[0], w, withtype=1)
        for x in m:
            if(x[0] not in sent_matches[name]["matches"].keys()):
                sent_matches[name]["matches"][x[0]] = [0, 0, 0]
            sent_matches[name]["matches"][x[0]][0] += x[1][0]
            sent_matches[name]["matches"][x[0]][1] += x[1][1]
            sent_matches[name]["matches"][x[0]][2] += x[1][2]
    # print("pattern", i)
    # print("match", sent_matches[name]["matches"])
    if(len(sent_matches[name]["matches"])==0):
        del sent_matches[name]["matches"]
    if((cnt+1)%100==0):
        with open("sent/stru_sent_matches"+str(cnt) + ".json", "w") as f:
            json.dump(sent_matches, f)
        print(cnt, time.time()-start)
        sent_matches = {}

with open("sent/stru_sent_matches_final.json", "w") as f:
    json.dump(sent_matches, f)


