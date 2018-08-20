import pandas as pd
import numpy as np
import re
import nltk
from textblob import TextBlob
import time
import json
import sys
from multiprocessing import Pool
import os


dirty = ["the", "other", "a", "an", "is", "are"]




class ContextPatt:
    def __init__(self):
        self.context_segs = []
        self.named_entities = {}
        self.patt = []
        self.patt_remain = []
        pass

    def status(self):
        print("number of named entities with labels: ", len(self.named_entities))
        print("total number of context: ", len(self.context_segs))
        print("number of patterns: ", len(self.patt))
        print("number of patterns to be processed: ", len(self.patt_remain))


    def load_text(self, filename):
        """
        :param filename:
        :return: the content of the document, divided into sentences
        """
        with open(filename) as f:
            whole_context = f.read()
            self.context_segs = whole_context.split("\n")
        print("finish loading sentences from document: ", len(self.context_segs))


    def load_ne(self, filename):
        """
        :param filename:
        :return: named entity list
        such as {'atorvastatin': ['S-Chemical'], 'simvastatin': ['S-Chemical'], 'thioredoxin': ['I-GENE', 'S-GENE', 'B-GENE'], 'TrxR': ['S-GENE', 'E-GENE', 'B-GENE']}
        """
        self.named_entities = {}
        with open(filename, "r") as f:
            for line in f:
                segs = line[:-1].split("\t")
                named_entity = " ".join(segs[:-1])
                entity_label = segs[-1]

                # check if there is a collision
                try:
                    if (self.named_entities[named_entity]):
                        pass
                except:
                    self.named_entities[named_entity] = []

                if (entity_label != "O" and entity_label not in self.named_entities[named_entity]):
                    self.named_entities[named_entity].append(entity_label)

        print("finish loading named entities with labels: ", len(self.named_entities.keys()))

    def filter_exist(self, dir):
        filenames = [x for x in os.listdir(dir) if x.endswith(".json")]
        pa = []
        for file in filenames:
            segs = file.split(":")
            id = segs[0]
            name = segs[1]
            if (len(segs) != 2):  # only 1 filename contain ":" ->  PATTERN3440:background_:_DISEASE.json
                name = ":".join(segs[1:])
            name = name.replace("_", " ")
            pa.append((id, name[:-5]))
        self.patt_remain = []
        for p in self.patt:
            if (p not in pa):
                self.patt_remain.append(p)
        print("still need to process: ", len(self.patt_remain))
        return self.patt_remain

    def load_pattern(self, filename):
        """
        :param filename:
        :return: pattern list, such as [('PATTERN10', 'CHEMICAL therapy'), ('PATTERN100', 'transcriptional activity of GENE')]
        """
        self.patt = []
        df = pd.read_excel(filename, header=None, names=["id", "pattern"])
        for index, r in df.iterrows():
            self.patt.append((r["id"], r["pattern"]))
        print("finish loading context patterns: ", len(self.patt))
        return self.patt

    def pmatch(self, id, pattern, document):
        """
        This function matchs a pattern containing "CHEMICAL", "GENE", "DISEASE" to a given document
        """

        res = {"id": id, "content": pattern, "matches": []}

        # process ) and ( in the pattern
        pattern = str(pattern)
        pattern = pattern.replace(")", "\)")
        pattern = pattern.replace("(", "\(")
        pattern = pattern.replace(".", "\.")
        pattern = pattern.replace("]", "\]")
        pattern = pattern.replace("[", "\[")
        pattern = pattern.replace("\\", "\\\\")
        pattern = pattern.replace("/", "\/")

        # generate re query for search
        match_query = re.sub('CHEMICAL|GENE|DISEASE|SPECIES', "(.*?)", pattern)
        if (match_query[-5:] == "(.*?)"):
            match_query = match_query[:-5] + "(.*)"
        if (match_query[:4] == "(.*?)"):
            match_query = "(.*)" + match_query[4:]

        # search pattern in the document
        matches = re.search(match_query, document)
        if (matches == None):
            return
        pos_pattern = list(re.finditer("CHEMICAL|GENE|DISEASE|SPECIES", pattern))

        index = 1
        for p in pos_pattern[1:-1]:
            res["matches"].append((p.group(0), matches.group(index)))
            index += 1
        try:
            tail = matches.group(index).split(" ")
            index = 0
            while (tail[index] in dirty and index < len(tail)):
                index += 1
            if (tail[index] not in dirty):
                res["matches"].append((pos_pattern[-1].group(0), tail[index]))
        except:
            pass

        try:
            head = matches.group(index).split(" ")
            index = -1
            while (tail[index] in dirty and index + len(tail) >= 0):
                index -= 1
            if (tail[index] not in dirty):
                res["matches"].append((pos_pattern[-1].group(0), tail[index]))
        except:
            pass

        return res





class StructPatt:
    def __init__(self):
        self.words = []  # a list of named entities
        self.patt = []
        self.patt_remain = []

    def load_pattern(self, filename):
        """
        :param filename:
        :return: pattern list such as [['$N$ , $N$ - $W$ - $N$ - $W$', 'Chemical', '47'], ['$W$ [ $W$ ] $W$', 'Chemical', '44']]
        """
        self.patt = []
        with open(filename, "r") as f:
            for line in f:
                segs = line[:-1].split("\t")  # delete the '\n' at the end of each line
                if (len(segs) != 3):
                    # print(line)
                    pass
                else:
                    self.patt.append(segs)
        # print (pattern)
        print("finish loading structure pattern: ", len(self.patt))
        return self.patt

    def load_words(self, filename):
        """
        :param filename:
        :return: entity names and types
        """



        self.words = []

        with open(filename, "r") as f:
            type_e = ""
            tmp = []
            for line in f:
                segs = line.split("\t")
                if (len(segs) == 2 and segs[0]!=""):
                    if (segs[1] == "O\n" or type_e !=segs[1][2:-1]):
                        if (len(tmp) > 0):
                            w = " ".join(tmp)
                            w = self.standardize(w)
                            self.words.append(w)
                            #print(" ".join(tmp))
                        tmp = []
                        type_e = segs[1][2:-1]
                    else:
                        tmp.append(segs[0])
                        type_e = segs[1][2:-1]

        self.words = set(self.words)
        print("finish loading words: ", len(self.words))
        return self.words

    def type(self, seg):
        if (seg.isdigit()):
            return "digit"
        elif(seg.isnumeric()):
            return "numeric"
        else:
            return "other"


    def standardize(self, string):
        segs = string.split(" ")
        s = ""
        cur_type = ""
        for i in segs:
            i.replace(" ", "")
            if(type(i)==cur_type and type(i) != "other"):
                s = s + " " + i
            else:
                s = s + i
            cur_type = type(i)
        return s


    def pmatch(self, pattern, string):
        # check whether a string is a word
        matches = []

        query = pattern
        query = query.replace(")", "\)")
        query = query.replace("(", "\(")
        query = query.replace("]", "\]")
        query = query.replace("[", "\[")
        query = query.replace("+", "\+")
        query = query.replace(".", "\.")

        query = query.replace(" ", "")
        query = query.replace("$W$$W$", "$W$ $W$")
        query = query.replace("$N$$N$", "$N$ $N$")
        query = query.replace("$W$$W$", "$W$ $W$")
        query = query.replace("$N$$N$", "$N$ $N$")

        query = query.replace("$W$", "([a-z]+)")
        query = query.replace("$N$", "([0-9]+)")


        string = self.standardize(string)
        pos = []
        try:
            pos = list(re.finditer(query, string, flags=re.IGNORECASE))
        except:
            print("pattern", pattern)
            print("string", string)
        for p in pos:
            matches.append(p.group(0))
        return matches, query







if __name__ == "__main__":

    # contextpatt = ContextPatt()
    # res = contextpatt.pmatch("id00", "DISEASE therapy",
    #        "the DISEASE_D013923_Thromboembolic and other complications of oral contraceptive therapy in relationship to pretreatment levels of DISEASE_D001778_blood_coagulation factors: summary report of a ten-year study.During a ten-year period, 348 SPECIES_9606_women were studied for a total of 5,877 SPECIES_9606_patient months in four separate studies relating oral contraceptives to changes in hematologic parameters.Significant increases in certain factors of the DISEASE_D001778_blood_coagulation and fibrinolysin systems (factors I,II,VII,GENE_1351_VIII,IX, and X and plasminogen) were observed in the treated groups.Severe complications developed in four SPECIES_9606_patients.")
    # print("TEST pmatch   ------  ", res)
    #
    # ne = contextpatt.load_ne("180815/train1_all.tsv")  # named entities and their types
    # docu = contextpatt.load_text("180815/train1.ner.txt")  # raw text document
    # patt = contextpatt.load_pattern("180815/patternlist.xlsx") # patterns
    # pattn = contextpatt.filter_exist("pairs/")
    #
    #
    # print("-"*50)


    structpatt = StructPatt()


    wpatt = structpatt.load_pattern(filename="180815/train_CRAFT_cnt_N_p.tsv")
    wne = structpatt.load_words(filename="180815/train1_all.tsv")  # named entities and their types
    res = structpatt.pmatch(pattern="$W$$W$$W$-$N$", string="we here have-54  have-66 iu(9)uis")
    print("TEST pmatch   ------  ", res)
