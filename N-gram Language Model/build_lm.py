"""
Kim Dodds - LING 570 - Fall 2019
HW 6 Implementation File

The purpose of this project is to build a 
language model using the output of the 
program ngram_count. This program outputs
the count, probability, log probability,
and ngram for each ngram provided by the 
input file.
"""

#PREPROCESSOR DIRECTIVES
import sys
import os
import math
import re

#MAIN FUNCTION
def main():
  #read in file
  f = open(sys.argv[1])
  f = f.read()
  all_data = f.split('\n')

  #initialize varaibles
  uni_types = 0
  uni_tokens = 0
  uni_freq = {}
  uni_sorted = []

  bi_types = 0
  bi_tokens = 0
  bi_freq = {}
  bi_sorted = []

  tri_types = 0
  tri_tokens = 0
  tri_freq = {}
  tri_sorted = []

  #loop through each line of ngram data
  for line in all_data:
    #prepare data
    line = line.strip('\n')
    line = re.sub('\t', ' ', line)
    temp = line.split(" ")
    temp.remove('')

    #check if unigram, bigram, or trigram
    if len(temp) == 3:
      #append data list with just count and tokens
      uni_freq[temp[2]] = temp[0]
      uni_sorted.append(temp[2])
      #increment type
      uni_types += 1
      #add count to total tokens
      uni_tokens += int(temp[0])
    if len(temp) == 4:
      two_word = (temp[2], temp[3])
      bi_freq[two_word] = temp[0]
      bi_types += 1
      bi_tokens += int(temp[0])
      bi_sorted.append(two_word)
    if len(temp) == 5:
      three_word = (temp[2], temp[3], temp[4])
      tri_freq[three_word] = temp[0]
      tri_types += 1
      tri_tokens += int(temp[0])
      tri_sorted.append(three_word)

  #print total counts for each ngram
  print("\\data\\")
  print("ngram 1: type={0} token={1}".format(uni_types, uni_tokens))
  print("ngram 2: type={0} token={1}".format(bi_types, bi_tokens))
  print("ngram 3: type={0} token={1}\n".format(tri_types, tri_tokens))

  #print data for each ngram
  print(r"\1-grams:")
  for u in uni_sorted:
    #calculte probability and log probability and truncate to 10
    prob = truncate(float(uni_freq[u])/float(uni_tokens))
    logprob = truncate(math.log(prob, 10))
    #print
    print(uni_freq[u], "\t", prob, "\t", logprob, "\t", u)

  print("\n\\2-grams:")
  for b in bi_sorted:
    prob = truncate(float(bi_freq[b])/float(uni_freq[b[0]]))
    logprob = truncate(math.log(prob, 10))
    print(bi_freq[b], "\t", prob, "\t", logprob, "\t", b[0] + " " + b[1])

  print("\n\\3-grams:")
  for t in tri_freq:
    search_bi = (t[0], t[1])
    prob = truncate(float(tri_freq[t])/float(bi_freq[search_bi]))
    logprob = truncate(math.log(prob, 10))
    print(tri_freq[t], "\t", prob, "\t", logprob, "\t", t[0] + " " + t[1] + " " + t[2])
  
#function to truncate to 10 decimal places
def truncate(p):
  multiplier = 10 ** 10
  return int(p * multiplier)/multiplier


if __name__ == '__main__':
  main()
