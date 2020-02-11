"""
Kim Dodds - LING 571 - Winter 2020
HW 4 Implementation File

The purpose of this project is to implement
a CYK parser for a fragment of the ATIS corpus.
"""

#PREPROCESSOR DIRECTIVES
import sys
import os
import re
import nltk
import numpy as np
import pandas as pd
from collections import Counter
import math

class CKYIndex:
    index = None
    terminal = None
    nonterminal = None

    def __init__(self):
        self.index = []
        self.terminal = ''
        self.nonterminal = []

class CKYParser:
    left_right = None
    right_left = None

    def __init__(self):
        self.left_right = {}
        self.right_left = {}
        self.probabilities = Counter()
        self.vocab = Counter()
        self.output = None
        self.top = None

    def initialize_grammar(self, raw_grammar):
        grammar = raw_grammar.strip(" ").split('\n')
        if "%start" in grammar[0]:
            self.top = grammar[0].split(" ")[1]
        for g in grammar:
            g = g.split(' -> ')
            if len(g) > 1:
                left = g[0]
                temp = g[1].split(" ")
                if len(temp) == 2:
                    right = temp[0].strip("'")
                    self.vocab[right] = 1
                    prob = float(temp[1].strip("[]"))
                else:
                    right = temp[0] + " " + temp[1]
                    prob = float(temp[2].strip("[]"))
                self.probabilities[(left + " -> " + right)] = math.log(prob, 10)
                if left not in self.left_right:
                   self.left_right[left] = []
                if right not in self.left_right[left]:
                    self.left_right[left].append(right)
                if right not in self.right_left:
                    self.right_left[right] = []
                if left not in self.right_left[right]:
                    self.right_left[right].append(left)

        return

    def initialize_table(self, tokens):
        tokens = list(filter(None, tokens))
        table = np.empty( (len(tokens), len(tokens)), dtype=object )
        i = 0
        while i < len(tokens):
            if self.vocab[tokens[i]] != 1:
                self.output.write("\n")
                return
            table[i,i] = CKYIndex()
            table[i,i].terminal = tokens[i]
            table[i,i].index = [i,i+1]
            i += 1

        return self.parse(table)

    def parse(self, table):
        row = 0
        col = 0
        while col < len(table[0,:]):
            while row >= 0:
                if row == col:
                    term = table[row,col].terminal
                    for nt in self.right_left[term]:
                        table[row,col].nonterminal.append((nt,"("+nt+" "+term+")", self.probabilities[nt+" -> "+term]))
                else:
                    table[row,col] = CKYIndex()
                    table[row,col].index = [row,col+1]
                    ctemp = col - 1
                    rtemp = col
                    while rtemp != row:
                        index1 = table[row, ctemp]
                        index2 = table[rtemp, col]
                        for i in index1.nonterminal:
                            for j in index2.nonterminal:
                                production = i[0] + " " + j[0]
                                if production in self.right_left:
                                    for lhs in self.right_left[production]:
                                        rule = lhs + " -> " + production
                                        table[row,col].nonterminal.append((lhs,"("+lhs+" "+i[1]+" "+j[1]+")", self.probabilities[rule] + i[2] + j[2]))
                        ctemp -= 1
                        rtemp -= 1

                row -= 1
            col += 1
            row = col

        parses = []
        for top in table[0,col-1].nonterminal:
            if top[0] == self.top: parses.append(top[1])
        return self.output_parses(parses)

    def output_parses(self, parses):
        if len(parses) < 1:
            self.output.write("\n")
        else:
            parses = sorted(parses, key=lambda x:x[2], reverse=True)
            self.output.write(parses[0]+'\n')
        return

#MAIN FUNCTION
def main():
    grammar = open(sys.argv[1]).read().strip()
    test = open(sys.argv[2]).read().strip()
    output = open(sys.argv[3], 'w')

    CKY = CKYParser()
    CKY.output = output
    CKY.initialize_grammar(grammar)

    for line in test.split('\n'):
        l = line.split(' ')
        CKY.initialize_table(l)


    output.close()

if __name__ == '__main__':
    main()
