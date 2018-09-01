# $ cd stanford-corenlp-full-2015-12-09/
# $ java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer



sent_data = []
cnt = 0
import time
start = time.time()
from pycorenlp import StanfordCoreNLP
import json
nlp = StanfordCoreNLP('http://localhost:9000')
# total 302736
with open("../train1.ner.txt", "r") as f:
	for sent in f:
		cnt += 1
		if(cnt>0):
			if(cnt % 1e3==0):
				print (cnt, time.time()-start)
			sent = sent.replace("\n", "")
			res = nlp.annotate(sent, properties={'annotators':"pos", 'outputFormat':'json'})
			res = res["sentences"]
			#print(sent)
			noun_list = []
			for word in res[0]['tokens']:
				if(word['pos'][0]=='N'):
					noun_list.append(word['word'])
			sent_format = (sent, noun_list)
			sent_data.append(sent_format)
			if(cnt % 1e4 == 0):
				with open("sents_noun_" + cnt + ".json", "w") as f:
					json.dump(sent_data, f)
					sent_data = []
with open("sents_noun_final.json", "w") as f:
	json.dump(sent_data, f)

