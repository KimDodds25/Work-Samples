This program creates a simple probabilistic n-gram language model. ngram_count.sh first compiles counts for every token in the input data and outputs the counts in descending order. build_lm.sh uses this counts to output probabilities for all unigrams, bigrams, and trigrams in the data. 
Files: 
- training_data: tokenized text which will be used to create LM probabilities
- ngram_count_file: output of ngram_count.sh | the counts of all unigram, bigram, and trigram counts in descending order
- lm_file: the probabilities of all unigrams, bigrams, and trigrams

To run:
./ngram_count.sh training_data ngram_count_file
./build_lm.sh ngram_count_file lm_file
