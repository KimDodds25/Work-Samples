"""
Kim Dodds - LING 572 - Winter 2020
HW _ Implementation File

The purpose of this project is to rate features
based on chi squared values.
"""

#PREPROCESSOR DIRECTIVES
import sys
import os
import re
import numpy as np
import pandas as pd
from collections import Counter

class ChiSquared:
    def __init__(self):
        self.feature_count = Counter()
        self.class_feat_count = Counter()
        self.classes = []
        self.features = []

    def init_counts(self, data):
        self.classes = list(set(re.findall("\n([\w\-,.]+) ", data)))
        self.features = list(set(re.findall("([\w\-.,]+):", data)))

        for d in data.split("\n"):
            feats = d.split(" ")
            label = feats[0]
            for f in feats:
                f = f.split(":")
                if len(f) >= 2:
                    self.feature_count[f[0]] += 1
                    self.class_feat_count[(label,f[0])] += 1

        return

    def calc_chi_square(self):
        chi = 0
        scores = []
        for f in self.features:
            contingency = np.zeros( (2,len(self.classes)) )
            for c in range(len(self.classes)):
                contingency[0,c] = self.class_feat_count[(self.classes[c],f)]
                contingency[1,c] = self.feature_count[f] - contingency[0,c]
            expectation = np.zeros( (2,len(self.classes)) )
            for row in range(len(expectation[:,0])):
                for col in range(len(expectation[0,:])):
                    expectation[row,col] = np.sum(contingency[row,:])*np.sum(contingency[:,col])/np.sum(contingency)
            for r in range(len(contingency[:,0])):
                for c in range(len(contingency[0,:])):
                    chi += (((contingency[r,c]-expectation[r,c])**2)/expectation[r,c])

            scores.append((f,chi,np.sum(contingency[0,:])))
        return scores

#MAIN FUNCTION
def main():
    file_in = sys.stdin.read().strip()

    x2 = ChiSquared()
    x2.init_counts(file_in)
    scores = x2.calc_chi_square()

    scores = sorted(scores, key=lambda x:x[1], reverse=True)
    for s in scores:
        print("{} {} {}".format(s[0],s[1],s[2]))



if __name__ == '__main__':
    main()
