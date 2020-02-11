"""
Kim Dodds - LING 571 - Winter 2020
HW _ Implementation File

The purpose of this project is to implement
a CYK parser for a fragment of the ATIS corpus.
"""

#PREPROCESSOR DIRECTIVES
import sys
import os
import re
import numpy as np

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

    def initialize_grammar(self, raw_grammar):
        grammar = raw_grammar.strip(" ").split('\n')
        for g in grammar:
            g = g.split(' -> ')
            if len(g) > 1:
                left = g[0]
                right = g[1]
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
            table[i,i] = CKYIndex()
            table[i,i].terminal = "'" + tokens[i].strip(".!?,") + "'"
            table[i,i].index = [i,i+1]
            i += 1
        return table

    def parse(self, table):
        row = 0
        col = 0
        while col < len(table[0,:]):
            while row >= 0:
                if row == col:
                    term = table[row,col].terminal
                    for nt in self.right_left[term]:
                        table[row,col].nonterminal.append((nt,"("+term+"/"+nt+")"))
                else:
                    table[row,col] = CKYIndex()
                    table[row,col].index = [row,col+1]
                    ctemp = col- 1
                    rtemp = col
                    while rtemp != row:
                        index1 = table[row, ctemp]
                        index2 = table[rtemp, col]
                        for i in index1.nonterminal:
                            for j in index2.nonterminal:
                                production = i[0] + " " + j[0]
                                if production in self.right_left:
                                    for lhs in self.right_left[production]:
                                        table[row,col].nonterminal.append((lhs,"("+lhs+" "+i[1]+" "+j[1]+")"))
                        ctemp -= 1
                        rtemp -= 1

                row -= 1
            col += 1
            row = col

        parses = []
        for top in table[0,col-1].nonterminal:
            if top[0] == 'TOP': parses.append(top[1])
        return parses

#MAIN FUNCTION
def main():
    grammar = open(sys.argv[1]).read().strip()
    test = open(sys.argv[2]).read().strip()
    output = open(sys.argv[3], 'w')

    CKY = CKYParser()
    CKY.initialize_grammar(grammar)

    for line in test.split('\n'):
        l = line.split(' ')
        table = CKY.initialize_table(l)
        parses = CKY.parse(table)
        output.write(line+'\n')
        for p in parses:
            output.write(p+'\n')
        output.write("Number of parses:"+str(len(parses)))
        output.write("\n\n")


    output.close()

if __name__ == '__main__':
    main()
