This is an updated version of the baseline CKY parser. The program first induces a probabilistic CFG grammar using set of pre-parsed sentences from a treebank. The induced grammar is then used by the updated CKY parser to parse the test sentences. parses_base.eval contains an evaluation of the parse results from evalb.

The command line to induce the grammar is:
./hw4_topcfg.sh treebank_file output_pcfg
treebank_file: a txt file with parsed sentences in flat bracket notation
output_pcfg: a CFG grammar in the form X -> A B [prob] | X -> 'y' [prob]

The command line to run the parser is:
./hw4_parser.sh input_PCFG test_sentences output_file
input_PCFG: the PCFG produced by hw4_topcfg.sh
test_sentences: txt file of English sentences to be parsed, one per line
output_file: The most likely parse for each input sentences; unparsable sentences leave a blank line
