"""
Kim Dodds - LING 572 - Winter 2020
HW 3 Implementation File

The purpose of this project is to implement
a Bernoulli Naive Bayes document classifier.
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
        self.minus_prob = Counter()
        self.classes = []
        self.features = []
        self.total_sample = 0

    def initialize_model(self, train):
        #gather all features in training data
        self.features = set(re.findall("([\w\-.,]+):", train))
        temp_feats = Counter()
        for t in train.split('\n'):
            # get class tag
            c = re.findall('^[\w\-.,]+', t)
            # load class counts into counter
            if len(c) > 0:
                self.class_count[c[0]] += 1

            # load feature class pairs into counter
            doc_feats = t.split(' ')
            for df in doc_feats:
                pair = df.split(":")
                if len(pair) > 1:
                    temp_feats[(pair[0], c[0])] += 1
            
            #increment total number of test docs
            self.total_sample += 1

        self.classes = list(self.class_count)
        #loop through classes
        for cl in self.classes:
            temp = self.class_count[cl]
            #calc class prior
            self.class_prior[cl] = math.log((temp + self.class_delta) / (self.total_sample + len(self.classes)), 10)
            minus_temp = 0
            #loop through features
            for k in self.features:
                #calculate conditional probability and precalculate sum(1-P(f|c)
                self.conditional_prob[(k,cl)] = math.log((self.cond_delta + temp_feats[(k,cl)])/(2 + self.class_count[cl]), 10)
                minus_temp += math.log(1 - ((self.cond_delta + temp_feats[(k,cl)])/(2 + self.class_count[cl])), 10)
            self.minus_prob[cl] = minus_temp


    #function to output model to model file
    def output_model(self, model):
        model.write("%%%%% PRIOR PROB P(c) %%%%%" + '\n')
        for p in self.class_prior:
            model.write(p + " ")
            model.write(str(10 ** self.class_prior[p]) + " ")
            model.write(str(self.class_prior[p]) + "\n")

        model.write("%%%%% CONDITIONAL PROBABILITY P(f|c) %%%%%" + '\n')
        last = ''
        for e in list(self.conditional_prob):
            if e[1] != last:
                model.write("%%%%% CONDITIONAL PROBABILITY c=" + str(e[1]) + " %%%%%" + '\n')
                last = e[1]
            model.write(str(e[0]) + " " + str(e[1]) + " ")
            model.write(str(10 ** self.conditional_prob[e]) + " " + str(self.conditional_prob[e]) + '\n')

        return

    #function to classify document
    def classify(self, doc):
        gold = doc.split(" ")
        gold = gold[0]
        yesprob = noprob = 0
        results = []
        #find all features in document
        feats = re.findall("([\w\-,.]+):", doc)
        #loop through classes
        for c in self.classes:
            #initialize probability as class prior plus minus prob
            classprob = self.class_prior[c] + self.minus_prob[c]
            #loop through feats and sum probability
            for f in feats:
                classprob += self.conditional_prob[(f,c)] - (1 - self.conditional_prob[(f,c)])

            #sort and return results
            results.append((c, classprob))
        results = sorted(results, key=lambda x: x[1], reverse=True)

        return (gold + " " + " ".join("%s %s" % tup for tup in results))

    #function to evaluate and create confusion matrix
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
    #open parameters
    train = open(sys.argv[1]).read().strip()
    test = open(sys.argv[2]).read().strip()
    class_prior_delta = float(sys.argv[3])
    cond_prob_delta = float(sys.argv[4])
    model = open(sys.argv[5], 'w')
    output = open(sys.argv[6], 'w')

    #create class instance, initialize and output model
    NB = BernoulliNB(class_prior_delta, cond_prob_delta)
    NB.initialize_model(train)
    NB.output_model(model)

    train_result = []
    test_result = []

    #classify and output training set
    count = 0
    output.write("%%%%% TRAINING DATA %%%%%\n")
    for doc in train.split('\n'):
        classified = NB.classify(doc)
        output.write("Document {}: {}\n".format(count, classified))
        train_result.append(classified)
        count += 1
    
    #classify and output test set
    count = 0
    output.write("%%%%% TEST DATA %%%%%\n")
    for ument in test.split("\n"):
        classified = NB.classify(ument)
        output.write("Document {}: {}\n".format(count, classified))
        test_result.append(classified)
        count += 1
    
    #run evaluation on results
    NB.evaluate(train_result, test_result)

    model.close()
    output.close()


if __name__ == '__main__':
    main()
