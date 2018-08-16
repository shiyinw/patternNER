import pandas as pd
import numpy as np
import re
import nltk
from textblob import TextBlob
import time
import json
import sys

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

dirty = ["the", "other", "a", "an", "is", "are"]

def pmatch(id, pattern, document):
    """
    This function matchs a pattern containing "CHEMICAL", "GENE", "DISEASE" to a given document
    """

    res = {"id":id, "content": pattern, "matches": []}

    # generate re query for search
    match_query = re.sub('CHEMICAL|GENE|DISEASE', "(.*?)", pattern)
    if (match_query[-5:] == "(.*?)"):
        match_query = match_query[:-5] + "(.*)"
    if(match_query[:4] == "(.*?)"):
        match_query = "(.*)" + match_query[4:]

    # search pattern in the document
    matches = re.search(match_query, document)
    if(matches == None):
        return
    pos_pattern = list(re.finditer("CHEMICAL|GENE|DISEASE", pattern))

    index = 1
    for p in pos_pattern[1:-1]:
        res["matches"].append((p.group(0), matches.group(index)))
        index += 1
    try:
        tail = matches.group(index).split(" ")
        index = 0
        while(tail[index] in dirty and index<len(tail)):
            index += 1
        if (tail[index] not in dirty):
            res["matches"].append((pos_pattern[-1].group(0), tail[index]))
    except:
        pass

    try:
        head = matches.group(index).split(" ")
        index = -1
        while (tail[index] in dirty and index + len(tail) >=0):
            index -= 1
        if (tail[index] not in dirty):
            res["matches"].append((pos_pattern[-1].group(0), tail[index]))
    except:
        pass

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
    for index, r in df.iterrows():
        pattern[r["id"]] = r["pattern"]
    print("finish loading patterns: ", len(pattern))
    return pattern


if __name__ == "__main__":


    res = pmatch("id00", "DISEASE therapy",
           "the DISEASE_D013923_Thromboembolic and other complications of oral contraceptive therapy in relationship to pretreatment levels of DISEASE_D001778_blood_coagulation factors: summary report of a ten-year study.During a ten-year period, 348 SPECIES_9606_women were studied for a total of 5,877 SPECIES_9606_patient months in four separate studies relating oral contraceptives to changes in hematologic parameters.Significant increases in certain factors of the DISEASE_D001778_blood_coagulation and fibrinolysin systems (factors I,II,VII,GENE_1351_VIII,IX, and X and plasminogen) were observed in the treated groups.Severe complications developed in four SPECIES_9606_patients.")
    print("TEST pmatch   ------  ", res)

    ne = load_ne("180815/train1_all.tsv")  # named entities and their types
    docu = load_text("180815/train1.ner.txt")  # raw text document
    pattern = load_pattern("180815/patternlist.xlsx") # patterns


    matches = []
    # matching patterns
    time_start = time.time()
    cnt = 0
    n = 0
    for i, p in pattern.items():
        cnt += 1
        print(p)
        for s in docu:
            match = pmatch(i, p, s)
            if(match != None):
                matches.append(match)
                n += 1
                if(n%100==0):
                    print(cnt, n, time.time() - time_start)
        if(cnt % 1 == 0):
            with open("pairs/matches1_" + str(cnt) + "_" + "_".join(p.split(" ")) + ".json", "w") as f:
                json.dump(matches, f)
                matches = []

    with open("pairs/matches1_" + str(cnt) + "_final" + ".json", "w") as f:
        json.dump(matches, f)





