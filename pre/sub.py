'''
    input: word\tlabel. sentence is separated by \n
    output: token token token\tlabel

    function: 
    - get labeled entity from data; 
    - mine word form patterns from incomplete training data;
    - map patterns back to original text;
    - check pattern quality based on the golden labels and the predicted labels
    - check if patterns can help with detecting the errors in test data
'''
import model.utils as utils
import sys
import string

class pattern:

    def __init__(self):
        #self.infile = sys.argv[1]
        #self.outfile = sys.argv[2]
        self.infile = 'train_01C_all.tsv'
        self.outfile='train_CRAFT_out_rep.tsv'

    def read_file(self): 
        with open(self.infile) as inf:
            inlines = inf.readlines()
        self.features, self.labels = utils.read_corpus(inlines)
    
    def print(self):
        self.read_file()
        print(self.features, self.labels)
        # features: array of sentences, sentence: token array

    def find_pattern(self, word):
        '''
            We find some named entity contains roman number, which is confusing. We treat them simply as word.
        '''
        if word.isdigit():
            return '$N$'
        elif word in string.punctuation:
            return word
        else: # check if subword is $NUMBER$ or $PUNCT$
            ret = ''
            prev = ''
            for w in word:
                if w in string.punctuation:
                    ret += w
                    prev = ''
                elif w.isdigit():
                    if prev == '$W$':
                        ret += '$W$'
                    prev = '$N$'
                else:
                    if prev =='$N$':
                        ret += '$N$'
                    prev = '$W$'
            ret += prev
        return ret

    def get_chunks(self, sent, labels):
        '''
            IOBES to span. each word is represented by word form.
        '''
        #print(sent, labels)
        current = [] # label sequence
        st = [] # token sequence
        cur = ''
        tmp = ''
        for word, label0 in zip(sent, labels):
            word=self.find_pattern(word)
            label = label0[0]
            if label.startswith('B-'):
                tmp = word
                cur = label[2:]

            elif label.startswith('S-'):
                st.append(word)
                current.append(label[2:])

            elif label.startswith('I-'):
                tmp += ' ' + word

            elif label.startswith('E-'):
                st.append(tmp+' '+word)
                current.append(cur)
            #print(tmp, cur)
        return st, current

    def write_file(self):
        with open(self.outfile, 'w') as outf:
            for sent, seq in zip(self.features, self.labels):
                entities, labels = self.get_chunks(sent, seq)
                #print(entities, labels)
                for e, l in zip(entities, labels):
                    outf.write(e+'\t'+l+'\n')
    
    def filter_word(self, st):
        ret = False
        for s in st:
            if s!='$' and s in string.punctuation:
                ret = True
        return ret or '$N$' in st

if __name__ == '__main__':
    P = pattern()
    #P.read_file()
    #P.write_file()
    dic = {}
    with open(P.outfile) as inf:
        for line in inf.readlines():
            st = line.strip()
            if st not in dic:
                dic[st] = 1
            else:
                dic[st] += 1
    with open('train_CRAFT_cnt.tsv', 'w') as outf, open('train_CRAFT_cnt_N_p.tsv','w') as outf1:
        sorted_dic = sorted(dic.items(), key=lambda kv: kv[1], reverse=True)
        for s, v in sorted_dic:
            l = s+'\t'+str(v)+'\n'
            outf.write(l)
            if P.filter_word(s):
                outf1.write(l)
