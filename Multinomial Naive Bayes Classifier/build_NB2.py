"""
Kim Dodds - LING 572 - Winter 2020
HW 3 Implementation File

The purpose of this project is to implement
a Multinomial Naive Bayes document classifier.
"""

# PREPROCESSOR DIRECTIVES
import sys
import os
import re
from collections import Counter
import math
import numpy as np
import pandas as pd


class BernoulliNB:
    def __init__(self, classd, condd):
        self.class_delta = classd
        self.cond_delta = condd
        # contains the log((count(c) + delta)/(count(total) + # of classes))
        self.class_prior = Counter()
        # contains simple count of class instances
        self.class_count = Counter()
        # contains log((count(fc) + delta)/(2 + count(c))
        self.conditional_prob = Counter()
        self.class_wordcount = Counter()
        self.classes = []
        self.features = []
        self.total_sample = 0

    def initialize_model(self, train):
        self.features = set(re.findall("([\w\-.,]+):", train))
        temp_feats = Counter()
        for t in train.split('\n'):
            # get class tag
            c = re.findall('^[\w\-.,]+', t)
            # load into counter
            if len(c) > 0:
                self.class_count[c[0]] += 1

            # load features into counter
            doc_feats = t.split(' ')
            for df in doc_feats:
                pair = df.split(":")
                if len(pair) > 1:
                    self.class_wordcount[c[0]] += int(pair[1])
                    temp_feats[(pair[0], c[0])] += int(pair[1])


            self.total_sample += 1

        self.classes = list(self.class_count)
        for cl in self.classes:
            temp = self.class_count[cl]
            self.class_prior[cl] = math.log((temp + self.class_delta) / (self.total_sample + len(self.classes)), 10)
            for k in self.features:
                # laplace smoothing says we add one to the numerator and add the number of outcomes to the denominator
                self.conditional_prob[(k,cl)] = math.log((self.cond_delta + float(temp_feats[(k,cl)]))/(len(self.features) + self.class_wordcount[cl]), 10)
            #print(self.conditional_prob.values())
                #self.conditional_prob[(k,cl)] = math.log((self.cond_delta + count_fc) / (2 + self.class_count[cl]), 10)

        print(self.conditional_prob["isreal", "talk.politics.guns"])

    def output_model(self, model):
        model.write("%%%%% PRIOR PROB P(c) %%%%%" + '\n')
        for p in self.class_prior:
            model.write(p + " ")
            model.write(str(10 ** self.class_prior[p]) + " ")
            model.write(str(self.class_prior[p]) + "\n")

        model.write("%%%%% CONDITIONAL PROBABILITY P(f|c) %%%%%")
        last = ''
        for e in list(self.conditional_prob):
            if e[1] != last:
                model.write("%%%%% CONDITIONAL PROBABILITY c=" + str(e[1]) + " %%%%%")
                last = e[1]
            model.write(str(e[0]) + " " + str(e[1]) + " ")
            model.write(str(10 ** self.conditional_prob[e]) + " " + str(self.conditional_prob[e]) + '\n')

        return

    def classify(self, doc):
        gold = doc.split(" ")
        gold = gold[0]
        results = []
        feat_count = Counter()
        feats = doc.split(" ")
        for e in feats:
            e = e.split(":")
            if len(e) > 1:
                feat_count[e[0]] = e[1]

        for c in self.classes:
            classprob = self.class_prior[c]
            for f in self.features:
                classprob += float(feat_count[f])*(self.conditional_prob[(f,c)])

            results.append((c, classprob))
        results = sorted(results, key=lambda x: x[1], reverse=True)

        return (gold + " " + " ".join("%s %s" % tup for tup in results))

    def evaluate(self, train, test):
        grid1 = np.zeros((len(self.classes), len(self.classes)))
        grid2 = np.zeros((len(self.classes), len(self.classes)))
        train_matrix = pd.DataFrame(grid1, columns=self.classes, index=self.classes)
        train_matrix.rename_axis("SYSTEM OUTPUT", axis=0)
        train_matrix.rename_axis("GOLD LABELS", axis=1)
        test_matrix = pd.DataFrame(grid2, columns=self.classes, index=self.classes)
        test_acc = train_acc = 0

        for t in train:
            t = t.split(" ")
            if len(t) > 1:
                train_matrix[t[1]][t[0]] += 1
                if t[0] == t[1]: train_acc += 1

        for e in test:
            e = e.split(" ")
            if len(e) > 1:
                test_matrix[e[1]][e[0]] += 1
                if e[0] == e[1]: test_acc += 1

        train_acc = train_acc / len(train)
        test_acc = test_acc / len(test)

        print("CONFUSION MATRIX FOR TRAINING DATA:\nRows are gold, columns are system output.\n")
        print(train_matrix.to_string() + "\n")
        print("Training accuracy: {}\n\n".format(train_acc))
        print("CONFUSION MATRIX FOR TEST DATA:\nRows are gold, columns are system output.\n")
        print(test_matrix.to_string() + "\n")
        print("Test accuracy: {}".format(test_acc))


# MAIN FUNCTION
def main():
    print("IMPORTING FILES")
    train = open(sys.argv[1]).read().strip()
    test = open(sys.argv[2]).read().strip()
    class_prior_delta = float(sys.argv[3])
    cond_prob_delta = float(sys.argv[4])
    model = open(sys.argv[5], 'w')
    output = open(sys.argv[6], 'w')

    NB = BernoulliNB(class_prior_delta, cond_prob_delta)
    print("INITIALIZING MODEL")
    NB.initialize_model(train)
    print("OUTPUTTING MODEL")
    NB.output_model(model)

    train_result = []
    test_result = []

    print("RUNNING TRAINING DATA")
    #print(NB.conditional_prob)
    count = 0
    output.write("%%%%% TRAINING DATA %%%%%\n")
    for doc in train.split('\n'):
        classified = NB.classify(doc)
        output.write("Document {}: {}\n".format(count, classified))
        train_result.append(classified)
        count += 1

    print("RUNNING TEST DATA")
    count = 0
    output.write("%%%%% TEST DATA %%%%%\n")
    for ument in test.split("\n"):
        classified = NB.classify(ument)
        output.write("Document {}: {}\n".format(count, classified))
        test_result.append(classified)
        count += 1

    print("EVALUATING")
    NB.evaluate(train_result, test_result)

    for B in NB.conditional_prob:
        check.write(str(B) + " " + str(NB.conditional_prob[B]) + "\n")
    check.close()
    model.close()
    output.close()


if __name__ == '__main__':
    main()
