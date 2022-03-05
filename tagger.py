import os
import io
import sys
import re
import numpy as np
from collections import defaultdict

class Tagger:

	def __init__(self):
		self.initial_tag_probability = None
		self.transition_probability = None
		self.emission_probability = None

	def load_corpus(self, path):
		if not os.path.isdir(path):
			sys.exit("Input path is not a directory")
		pos_counts={}
		pos_counts['<S>']=0
		word_hash = {}
		pos_hash = {}
		
		filectr = 0
		for filename in os.listdir(path):
			filename = os.path.join(path, filename)
			try:
				reader = io.open(filename)
				#word_hash = {}
				#pos_hash={}
				filectr += 1
				print(filename)
				sent_count = 0

				lines = list(reader.read().splitlines())
				

				for line in lines:
					if not re.match('^([a-zA-Z!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~])',line): continue
					sent_count += 1
					prev_tag = '<S>'
					pos_counts['<S>'] += 1
					word_tag = []
					word_tag = line.split()

					for w in word_tag:
						temp = w.split('/')
						word = temp[0]
						pos = temp[-1]

						#populate the word hash
						if (word,pos) in word_hash:
							word_hash[(word,pos)] += 1
						else:
							word_hash[(word,pos)] = 1

						#populate pos hash
						if (prev_tag,pos) in pos_hash:
							pos_hash[(prev_tag,pos)] += 1
						else:
							pos_hash[(prev_tag,pos)] = 1

						#populate pos counter
						if pos in pos_counts:
							pos_counts[pos] += 1
						else:
							pos_counts[pos] = 1

						prev_tag = pos



				"""
				YOUR CODE GOES HERE: Complete the rest of the method so that it outputs a list of lists as described in the question
				"""
			except IOError:
				sys.exit("Cannot read file")

		return(word_hash,pos_hash,pos_counts)

	def initialize_probabilities(self,word_hash,pos_hash,pos_counts):
		#if type(sentences) != list:
		#	sys.exit("Incorrect input to method")
		"""
		YOUR CODE GOES HERE: Complete the rest of the method so that it computes the probability matrices as described in the question
		"""
		#Computinging initial probabilities
		init_prob = {}
		#print(pos_counts['<S>'])
		#print(len(pos_counts))
		noOfTags = len(pos_counts) - 1 #to avoid counting the start tag as one of the tags
		#print(noOfTags)
		for (pos1,pos2) in pos_hash.keys():
			#print(pos_counts['<S>'])
			if pos1 == '<S>':
				init_prob[pos2] = (pos_hash[pos1,pos2]+1)/(pos_counts['<S>'])
		#computing Emission Probabilities
		for (word,pos) in word_hash.keys():
			#print(pos,word)
			word_hash[(word,pos)] = (word_hash[(word,pos)]+1)/(pos_counts[pos]+noOfTags)

		#computing transition probabilities
		for (pos1,pos2) in pos_hash.keys():
			pos_hash[(pos1,pos2)] = (pos_hash[(pos1,pos2)]+1)/(pos_counts[pos1]+noOfTags)

		return init_prob,word_hash,pos_hash



	#implement 3
	def viterbi_algorithm(self,sentence, states, start_p, trans_p, emit_p,pos_counts):

		observations = sentence.split()
		V = [{}]
		for st in states:
			#print(st)
			#print(emit_p[st])
			if observations[0] not in emit_p[st]:
				#print(pos_counts[st])
				emit_p[st][observations[0]] = 0.0001
			V[0][st] = {"prob": start_p[st] * emit_p[st][observations[0]], "prev": None}
   
		for t in range(1, len(observations)):
			V.append({})
			for st in states:
				if st not in trans_p[states[0]]:
					#print(pos_counts[st])
					trans_p[states[0]][st] = 0.0001
				max_tr_prob = V[t - 1][states[0]]["prob"] * trans_p[states[0]][st]
				prev_st_selected = states[0]
		        
				for prev_st in states[1:]:
					#print(trans_p[prev_st][st])
					if st not in trans_p[prev_st]:
						#print(pos_counts[st])
						trans_p[prev_st][st] = 0.0001
					tr_prob = V[t - 1][prev_st]["prob"] * trans_p[prev_st][st]
					if tr_prob > max_tr_prob:
						max_tr_prob = tr_prob
						prev_st_selected = prev_st

				if observations[t] not in emit_p[st]:
					#print(pos_counts[st])
					emit_p[st][observations[t]] = 0.0001
				max_prob = max_tr_prob * emit_p[st][observations[t]]
				V[t][st] = {"prob": max_prob, "prev": prev_st_selected}
		#for line in self.dptable(V):
		#	print(line)
 
		opt = []
		max_prob = 0.0
		best_st = None
 
		for st, data in V[-1].items():
			if data["prob"] > max_prob:
				max_prob = data["prob"]
				best_st = st
		opt.append(best_st)
		previous = best_st
 
 
		for t in range(len(V) - 2, -1, -1):
			opt.insert(0, V[t + 1][previous]["prev"])
			previous = V[t + 1][previous]["prev"]
 
		print ("The steps of states are " + " ".join(opt) + " with highest probability of %s" % max_prob)
 
	def dptable(self,V):
	
		yield " ".join(("%12d" % i) for i in range(len(V)))
		for state in V[0]:
			yield "%.7s: " % state + " ".join("%.7s" % ("%f" % v[state]["prob"]) for v in V)

tag1 = Tagger()
word_hash,pos_hash,pos_counts = tag1.load_corpus('train/modified_brown')
#print(word_hash)
init_prob1,word_hash1,pos_hash1 = tag1.initialize_probabilities(word_hash,pos_hash,pos_counts)
#print(init_prob1)
#print(word_hash1)
#Tagger.load_corpus('modified_brown')



#x,T1,T2= tag1.viterbi_decode('People Race Tomorrow',pos_hash1,word_hash1,init_prob1)


emit_p = defaultdict(dict) # dict where the default values are dicts.
for (x, y) in word_hash1: # Each tuple is "key1, key2, value"
    emit_p[y][x] = word_hash1[(x,y)]

trans_p = defaultdict(dict)

for (s, t) in pos_hash1: # Each tuple is "key1, key2, value"
    trans_p[t][s] = pos_hash1[(s,t)]

#print(trans_p)


states = []
for i in pos_counts:
	if(i !='<S>'):
		states.append(i)

#print(states)
#print(emit_p[])


tag1.viterbi_algorithm('computers process programs accurately .', states, init_prob1, trans_p, emit_p,pos_counts)




