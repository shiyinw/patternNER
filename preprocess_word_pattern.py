from utils import *

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

res = pmatch("id00", "DISEASE therapy",
           "the DISEASE_D013923_Thromboembolic and other complications of oral contraceptive therapy in relationship to pretreatment levels of DISEASE_D001778_blood_coagulation factors: summary report of a ten-year study.During a ten-year period, 348 SPECIES_9606_women were studied for a total of 5,877 SPECIES_9606_patient months in four separate studies relating oral contraceptives to changes in hematologic parameters.Significant increases in certain factors of the DISEASE_D001778_blood_coagulation and fibrinolysin systems (factors I,II,VII,GENE_1351_VIII,IX, and X and plasminogen) were observed in the treated groups.Severe complications developed in four SPECIES_9606_patients.")
print("TEST pmatch   ------  ", res)

ne = load_ne("180815/train1_all.tsv")  # named entities and their types
docu = load_text("180815/train1.ner.txt")  # raw text document
patt = load_pattern("180815/patternlist.xlsx") # patterns
matches = []


def run (pattern):
    p = pattern[1]
    id = pattern[0]
    print (p)
    for s in docu:
        match = pmatch(id, p, s)
        if (match != None):
            matches.append(match)
    with open("pairs/" + str(id) + ":" + "_".join(p.split(" ")) + ".json", "w") as f:
        json.dump(matches, f)
    return



with Pool(20) as p:
    print(p.map(run, patt))
