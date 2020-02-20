"""
Kim Dodds - LING 571 - Winter 2020
HW 6 Implementation File

The purpose of this program is to
"""

import sys
import os
import re
import nltk

def main():
    fcfg = open(sys.argv[1]).read().strip()
    test = open(sys.argv[2]).read().strip()

    grammar = nltk.grammar.FeatureGrammar.fromstring(fcfg)
    parser = nltk.parse.FeatureEarleyChartParser(grammar)
    for t in test.split('\n'):
        result = parser.parse(t.split())
        parse_flag = 0
        for tree in result:
            result = nltk.Tree._pformat_flat(tree, nodesep='', parens="()", quotes="''")
            parse_flag = 1
        if parse_flag == 0:
            print(' ')
        if parse_flag ==1:
            #print(result)
            print(tree.label()['SEM'].simplify())

if __name__ == '__main__':
    main()