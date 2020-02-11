"""
Kim Dodds - LING 571 - Winter 2020
HW 4 Implementation File

The purpose of this project is to implement
a probabilistic CKY parser. This file reads in
a CNF treebank, extracts probabilities, and
outputs a probabilistic grammar.
"""

#PREPROCESSOR DIRECTIVES
import sys
import os
import re
from nltk.tree import Tree
from collections import Counter
import numpy as np
import pandas as pd

class PCFG:
    def __init__(self):
        self.rule_count = Counter()
        self.top = ''

    def get_rules(self, treebank):
        lhs = rhs = rules = []
        self.top = re.findall("^\((\w+)",treebank)[0]
        for t in treebank.split('\n'):
            for pro in Tree.fromstring(t).productions():
                rules.append(str(pro))

        temp = "#".join(rules)
        lhs = set(re.findall("([^#\->]+) ->", temp))
        rhs = set(re.findall("-> ([^#\->]+)", temp))

        self.rule_count = pd.DataFrame(0, index=rhs, columns=lhs)
        for r in rules:
            r = r.split(" -> ")
            self.rule_count.at[r[1],r[0]] += 1

        self.calc_probabilities()

        return

    def calc_probabilities(self):
        counts = self.rule_count.sum(axis=0)
        for col in counts.keys():
            self.rule_count[col] = self.rule_count[col].map(lambda val: val/counts[col])
        return

    def output_grammar(self):
        print("%start {}".format(self.top))
        for lhs in self.rule_count.columns:
            for rhs in self.rule_count.index:
                if self.rule_count.at[rhs,lhs] != 0:
                    print("{} -> {} [{}]".format(lhs,rhs,self.rule_count.at[rhs,lhs]))


#MAIN FUNCTION
def main():
    treebank = open(sys.argv[1]).read().strip()

    pcfg = PCFG()
    pcfg.get_rules(treebank)
    pcfg.output_grammar()


if __name__ == '__main__':
    main()
