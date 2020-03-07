"""
Kim Dodds - LING 570 - Fall 2019
HW 6 Implementation File

The purpose of this project is to extract unigrams,
bigrams, and trigrams from a tokenized input file.
This program output first unigrams then bigrams
and lastly trigrams, each set sorted by frequency
and grams with matching frequencies sorted alphbetically.
"""

#PREPROCESSOR DIRECTIVES
import sys
import os
import re
from collections import Counter

#MAIN FUNCTION
def main():
  #open file and read in line
  f = open(sys.argv[1])
  line = f.readline().lower()

  #initialize counters
  unigrams = Counter()
  bigrams = Counter()
  trigrams = Counter()

  #loop through each line in the file
  while line:
    #stip input of newline character
    line = line.strip('\n')
    #insert "beginning of sentence" character
    sentence = ["<bos>"]
    #split tokens by spaces 
    sentence += line.split(" ")
    #add "end of sentence" character
    sentence += ["<eos>"]

    #loop through each token in the line
    for token in sentence:
      #add each token to unigram counter
      unigrams[token] += 1 
      index = sentence.index(token)
      #add two tokens to bigram counter
      if index + 1 < len(sentence):
        bi = token + " " + sentence[index + 1]
        bigrams[bi] += 1
      #add three tokens to trigram counter
      if index + 2 < len(sentence):
        tri = bi + " " + sentence[index + 2]
        trigrams[tri] += 1
    
    #read in next line
    line = f.readline().lower()

  #get tuple list with all items and frequencies
  uni_total = unigrams.items()
  #sort by frequency and then alphabetically
  uni_total = sorted(uni_total, key=lambda element: (-element[1], element[0]))
  bi_total = bigrams.items()
  bi_total = sorted(bi_total, key=lambda element: (-element[1], element[0]))
  tri_total = trigrams.items()
  tri_total = sorted(tri_total, key=lambda element: (-element[1], element[0]))

  #print each item
  for uni in uni_total:
    print(uni[1], '\t', uni[0])

  for bi in bi_total:
    print(bi[1], '\t', bi[0])

  for tri in tri_total:
    print(tri[1], '\t', tri[0])




if __name__ == '__main__':
  main()
