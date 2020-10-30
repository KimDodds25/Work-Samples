This project is an experiment in reperesenting semantic meaning during parsing using first-order logic. This directory contains:

hw6_semantic_grammar.fcfg: a small hand-written context-free grammar with semantic features
hw6_semantics.py: A script that loads the grammar into NLTK and uses the grammar and a chart parser to parse the examples sentences
sentences.txt: A set of simple sentences to be parsed with the grammar
hw6_output: output from the script showing only the final semantic representation of the parsed sentences

To run:
./hw6_semantics.sh grammar_file test_file output_file
