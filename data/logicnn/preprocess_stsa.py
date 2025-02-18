import numpy as np
import pickle
from collections import defaultdict
import sys, re
import pandas as pd
from random import randint
np.random.seed(7294258)

def build_data(data_folder, clean_string=True):
    """
    Loads data
    """
    revs = []
    [train_file,dev_file,test_file] = data_folder
    vocab = defaultdict(float)
    with open(train_file, "r") as f:
        for line in f:
            line = line.strip()
            y = int(line[0])
            rev = []
            rev.append(line[2:].strip())
            if clean_string:
                orig_rev = clean_str(" ".join(rev))
            else:
                orig_rev = " ".join(rev).lower()
            words = set(orig_rev.split())
            for word in words:
                vocab[word] += 1
            datum  = {"y":y,
                      "text": orig_rev,                             
                      "num_words": len(orig_rev.split()),
                      "split": 0} # 0-train, 1-dev, 2-test
            revs.append(datum)
    with open(dev_file, "r") as f:
        for line in f:       
            line = line.strip()
            y = int(line[0])
            rev = []
            rev.append(line[2:].strip())
            if clean_string:
                orig_rev = clean_str(" ".join(rev))
            else:
                orig_rev = " ".join(rev).lower()
            words = set(orig_rev.split())
            for word in words:
                vocab[word] += 1
            datum  = {"y":y, 
                      "text": orig_rev,                             
                      "num_words": len(orig_rev.split()),
                      "split": 1}
            revs.append(datum)
    with open(test_file, "r") as f:
        for line in f:       
            line = line.strip()
            y = int(line[0])
            rev = []
            rev.append(line[2:].strip())
            if clean_string:
                orig_rev = clean_str(" ".join(rev))
            else:
                orig_rev = " ".join(rev).lower()
            words = set(orig_rev.split())
            for word in words:
                vocab[word] += 1
            datum  = {"y":y, 
                      "text": orig_rev,                             
                      "num_words": len(orig_rev.split()),
                      "split": 2}
            revs.append(datum)
    return revs, vocab
    
def get_W(word_vecs, k=200):
    """
    Get word matrix. W[i] is the vector for word indexed by i
    """
    vocab_size = len(word_vecs)
    word_idx_map = dict()
    W = np.zeros(shape=(vocab_size+1, k), dtype='float32')            
    W[0] = np.zeros(k, dtype='float32')
    i = 1
    for word in word_vecs:
        W[i] = word_vecs[word]
        word_idx_map[word] = i
        i += 1
    return W, word_idx_map

def load_bin_vec(fname, vocab):
    """
    Loads 300x1 word vecs from Google (Mikolov) word2vec
    """
    word_vecs = {}
    with open(fname, "r") as f:
        for line in f:
            segs = line.split(" ")
            word = segs[0]
            if word in vocab:
                word_vecs[word] = np.asarray(segs[1:-1], dtype='float32')
    return word_vecs

def add_unknown_words(word_vecs, vocab, min_df=1, k=200):
    """
    For words that occur in at least min_df documents, create a separate word vector.    
    0.25 is chosen so the unknown vectors have (approximately) same variance as pre-trained ones
    """
    for word in vocab:
        if word not in word_vecs and vocab[word] >= min_df:
            word_vecs[word] = np.random.uniform(-0.25,0.25,k)  

def clean_str(string, TREC=False):
    """
    Tokenization/string cleaning for all datasets except for SST.
    Every dataset is lower cased except for TREC
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)     
    string = re.sub(r"\'s", " \'s", string) 
    string = re.sub(r"\'ve", " \'ve", string) 
    string = re.sub(r"n\'t", " n\'t", string) 
    string = re.sub(r"\'re", " \'re", string) 
    string = re.sub(r"\'d", " \'d", string) 
    string = re.sub(r"\'ll", " \'ll", string) 
    string = re.sub(r",", " , ", string) 
    string = re.sub(r"!", " ! ", string) 
    string = re.sub(r"\(", " \( ", string) 
    string = re.sub(r"\)", " \) ", string) 
    string = re.sub(r"\?", " \? ", string) 
    string = re.sub(r"\s{2,}", " ", string)    
    return string.strip() if TREC else string.strip().lower()

def clean_str_sst(string):
    """
    Tokenization/string cleaning for the SST dataset
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)   
    string = re.sub(r"\s{2,}", " ", string)    
    return string.strip().lower()

if __name__=="__main__":
    w2v_file = "../wikipedia-pubmed-and-PMC-w2v-bio.txt"

    train_data_file = "raw/stsa.binary.phrases.train"
    dev_data_file = "raw/stsa.binary.dev"
    test_data_file = "raw/stsa.binary.test"

    data_folder = [train_data_file, dev_data_file, test_data_file]
    print ("loading data...")
    revs, vocab = build_data(data_folder, clean_string=True)


    max_l = np.max(pd.DataFrame(revs)["num_words"])
    print ("data loaded!")
    print ("number of sentences: " + str(len(revs)))
    print ("vocab size: " + str(len(vocab)))
    print ("max sentence length: " + str(max_l))

    print ("loading word2vec vectors...")
    w2v = load_bin_vec(w2v_file, vocab)
    print ("word2vec loaded!")
    print ("num words already in word2vec: " + str(len(w2v)))

    add_unknown_words(w2v, vocab)
    W, word_idx_map = get_W(w2v)
    rand_vecs = {}
    add_unknown_words(rand_vecs, vocab)
    W2, _ = get_W(rand_vecs)

    pickle.dump([revs, W, W2, word_idx_map, vocab], open("./stsa.binary.p", "wb"))
    print ("dataset created!")
    
