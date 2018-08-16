import pandas as pd
import numpy as np
import re
import nltk
from textblob import TextBlob
import time

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

def pmatch(pattern, document):
    """
    This function matchs a pattern containing "CHEMICAL", "GENE", "DISEASE" to a given document
    """

    res = {"content": pattern, "matches": []}

    # generate re query for search
    match_query = re.sub('CHEMICAL|GENE|DISEASE', "(.*?)", pattern)
    if (match_query[-5:] == "(.*?)"):
        match_query = match_query[:-5] + "(.*)"

    # search pattern in the document
    matches = re.search(match_query, document)
    if(matches==None):
        return
    pos_pattern = list(re.finditer("CHEMICAL|GENE|DISEASE", pattern))

    index = 1
    for p in pos_pattern[:-1]:
        res["matches"].append((p.group(0), matches.group(index)))
        index += 1
    tail = matches.group(index).split(" ")
    if (tail[0] in ["the", "a", "in"]):
        last_word = tail[1]
    else:
        last_word = tail[0]
    res["matches"].append((pos_pattern[-1].group(0), last_word))

    return res


def load_ne(filename):
    """
    :param filename:
    :return: named entity list
    such as {'atorvastatin': ['S-Chemical'], 'simvastatin': ['S-Chemical'], 'thioredoxin': ['I-GENE', 'S-GENE', 'B-GENE'], 'TrxR': ['S-GENE', 'E-GENE', 'B-GENE']}
    """
    named_entity_list = {}
    with open(filename, "r") as f:
        for line in f:
            segs = line[:-1].split("\t")
            named_entity = " ".join(segs[:-1])
            entity_label = segs[-1]

            # check if there is a collision
            try:
                if (named_entity_list[named_entity]):
                    pass
            except:
                named_entity_list[named_entity] = []

            if (entity_label != "O" and entity_label not in named_entity_list[named_entity]):
                named_entity_list[named_entity].append(entity_label)

    print("finish loading named entities with labels: ", len(named_entity_list.keys()))
    return named_entity_list


def load_text(filename):
    """
    :param filename:
    :return: the content of the document, divided into sentences
    """
    with open(filename) as f:
        whole_context = f.read()
        context_segs = whole_context.split("\n")
    print("finish loading sentences from document: ", len(context_segs))
    return context_segs

def load_pattern(filename):
    """
    :param filename:
    :return: pattern list, such as {'PATTERN10': 'CHEMICAL therapy', 'PATTERN100': 'transcriptional activity of GENE'}
    """
    pattern = {}
    df = pd.read_excel(filename, header=None, names=["id", "pattern"])
    for r in df.iterrows():
        pattern[r[1]["id"]] = r[1]["pattern"]
    print("finish loading patterns: ", len(pattern))
    return pattern


if __name__ == "__main__":


    res = pmatch("development of DISEASE such as GENE will DISEASE",
           "The development of the last proteins such as we will king of all the issue")
    print("TEST pmatch   ------  ", res)

    ne = load_ne("180815/train1_all.tsv")  # named entities and their types
    docu = load_text("180815/train1.ner.txt")  # raw text document
    pattern = load_pattern("180815/patternlist.xlsx") # patterns


    # matching patterns
    time_start = time.time()
    cnt = 0
    for p in pattern:
        cnt += 1
        for s in docu:
            match = pmatch(p, s)
            if(match != None):
                print(match)
        if(cnt % 1e1==0):
            print (cnt, time.time()-time_start)