from utils import ContextPatt
import json
from multiprocessing import Pool

"""
### Input
detected pattern patternlist.xlsx
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

contextpatt = ContextPatt()

ne = contextpatt.load_ne("data/train1_all.tsv")  # named entities and their types
docu = contextpatt.load_text("data/sents.json")  # raw text document
patt = contextpatt.load_pattern("data/patternlist.xlsx") # patterns
if REUSE:
    patt = contextpatt.filter_exist("data/pairs/") # remains patterns
matches = []


def run (pattern):
    p = pattern[1]
    id = pattern[0]
    print (p)
    matches = []
    dict = {}
    for s in contextpatt.context_segs:
        if(len(s[1])==0):
            pass
        match = contextpatt.pmatch(id, p, s[0], s[1])
        if (match != None):
            matches = matches + match["matches"]
    dict = {"id":id, "pattern":p, "matches":matches}
    with open("data/pairs/" + str(id) + ":" + "_".join(p.split(" ")) + ".json", "w") as f:
        json.dump(dict, f)
    return


with Pool(20) as p:
    print(p.map(run, patt))



#TODO: 15 undetected items
""" 
nan
DISEASE and/or
c57bl/6j SPECIES
and/or DISEASE
min/+ SPECIES
/+ ) SPECIES
and/or GENE
male c57bl/6j SPECIES
male c57bl/6 SPECIES
and/or CHEMICAL
[ effect of CHEMICAL on expression
CHEMICAL and/or
[ effect of CHEMICAL
female c57bl/6 SPECIES
c57bl/6 SPECIES
"""
