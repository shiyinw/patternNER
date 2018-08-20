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
words = structpatt.load_words("data/train_CRAFT.tsv")  # named entities and their types
patt = structpatt.load_pattern("data/train_CRAFT_cnt_N_p.tsv") # patterns

start = time.time()
cnt = 0

word_matches = {}
for i in patt:
    name = str(i[0])
    word_matches[name]={"matches":[], "type":i[1], "cnt":i[2]}
    cnt += 1
    for w in structpatt.words:
        m, q = structpatt.pmatch(i[0], w)
        word_matches[name]["matches"].extend(m)
    word_matches[name]["matches"] = list(set(word_matches[name]["matches"]))
    print("pattern", i)
    print("query", q)
    print("match", word_matches[name]["matches"])
    if(cnt%1==0):
        print(cnt, time.time()-start)

with open("stru_matches.json", "w") as f:
    json.dump(word_matches, f)
