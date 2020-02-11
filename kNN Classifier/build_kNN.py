"""
Kim Dodds - LING 572 - Winter 2020
HW 4 Implementation File

The purpose of this project is to implement a
k nearest neighbor document classifier.
This program takes the parameters:
train_vector, test_vector, dist_function, k_value, output_path
"""

#PREPROCESSOR DIRECTIVES
import sys
import os
import re
from collections import Counter
import numpy as np
import pandas as pd
from scipy.spatial import distance

class kNN:
    def __init__(self, k=5, func_type=1):
        #  how many neighbors are being considered
        self.k = k
        #  which distance func to use: 1 for euclidian, 2 for cosine
        self.function_type = func_type
        #  list of classes extracted from train data
        self.classes = []
        #  dicts that convert class/feat name string to int value and vice versa
        self.class_key = Counter()
        self.feature_key = Counter()
        #  vectors created from train and test input
        self.train_vector = None
        self.test_vector = None

    def init_train_vector(self, train):
        col = self.init_keys(train)
        self.train_vector = self.load_vector(train, len(train.split('\n')), (col+1))
        return

    #  function to create integer aliases for feats and classes and store them in dicts
    def init_keys(self, train):
        self.classes = list(set(re.findall("\n([\w\-,.]+) ", train)))
        features = list(set(re.findall("([\w\-.,]+):", train)))
        for c in range(len(self.classes)):
            self.class_key[c] = self.classes[c]
            self.class_key[self.classes[c]] = int(c)
        for f in range(len(features)):
            self.feature_key[f+1] = features[f]
            self.feature_key[features[f]] = int(f)+1
        return len(features)

    def init_test_vector(self, test):
        self.test_vector = self.load_vector(test, len(test.split('\n')), len(self.train_vector[0,:]))
        return

    #  function to load counts into vectors where rows are the document, vector[row, 0] is the class label, and
    #  column is the feature
    def load_vector(self, data, row, col):
        vector = np.zeros( (row, col) )
        data = data.split('\n')
        gold_list = []
        for doc in range(len(data)):
            feat = data[doc].split(" ")
            gold = self.class_key[feat[0]]
            gold_list.append(gold)
            for f in range(len(feat)):
                if f != 0:
                    f = feat[f].split(":")
                    if len(f) >= 2:
                        f_col = self.feature_key[f[0]]
                        vector[doc, f_col] += int(f[1])
        vector[:, 0] = gold_list
        return vector

    def run_train_data(self, out):
        out.write("%%%%%TRAINING DATA:\n")
        if self.function_type == 1:
            result = distance.squareform(distance.pdist(self.train_vector[:,1:], 'euclidean'))
        else:
            result = distance.squareform(distance.pdist(self.train_vector[:,1:], 'cosine'))
        print("CONFUSION MATRIX FOR TRAINING DATA:")
        self.confusion_matrix(self.process_results(result.argsort()[:,0:self.k], self.train_vector, out))

    #  function that takes a vector of distance measures, gathers the k closest items, and store sys output labels
    def process_results(self, closest, vector, out):
        sys_gold = []
        for r in range(len(closest[:,0])):
            count = Counter()
            for c in self.classes:
                count[self.class_key[c]] = 0
            out.write("Document " + str(r) + ": ")
            for value in closest[r,:]:
                count[self.train_vector[value,0]] += 1
            closest_sorted = sorted(count.items(), key=lambda x:x[1], reverse=True)
            label = closest_sorted[0]
            out.write(self.class_key[label[0]] + " ")
            for s in closest_sorted:
                out.write(self.class_key[s[0]] + " " + str(s[1]/self.k) + " ")
            out.write("\n")
            #print(self.test_vector[r,0])
            sys_gold.append((str(self.class_key[label[0]]), str(self.class_key[vector[r,0]])))
        return(sys_gold)

    def run_test_data(self, out):
        out.write("%%%%%TEST DATA:\n")
        #  concat = np.concatenate((self.train_vector, self.test_vector), axis=0)
        if self.function_type == 1:
            result = distance.cdist(self.test_vector, self.train_vector, 'euclidean')
        else:
            result = distance.cdist(self.test_vector, self.train_vector, 'cosine')
        #  result = result[len(self.train_vector):, 0:len(self.train_vector)]

        print("CONFUSION MATRIX FOR TEST DATA:")
        self.confusion_matrix(self.process_results(result.argsort()[:,0:self.k], self.test_vector, out))
        return

    #  function to print confusion matrix using sys output and gold lables
    def confusion_matrix(self, sys_gold):
        print("Rows represent system output; columns represent gold labels\n")
        grid = np.zeros( (len(self.classes),len(self.classes)) )
        confusion_matrix = pd.DataFrame(data=grid, index=self.classes, columns=self.classes)
        accuracy = 0
        for s in sys_gold:
            confusion_matrix.at[s[0],s[1]] += 1
            if s[0] == s[1]: accuracy += 1
        accuracy /= len(sys_gold)

        print(confusion_matrix.to_string())
        print("Accuracy = {}\n\n".format(accuracy))
        return

#MAIN FUNCTION
def main():
    #  read in parameters
    train = open(sys.argv[1]).read().strip()
    test = open(sys.argv[2]).read().strip()
    k = int(sys.argv[3])
    func_type = int(sys.argv[4])
    out = open(sys.argv[5], 'w')

    #  create class object
    knn = kNN(k, func_type)

    #  initialize train and test vectors
    knn.init_train_vector(train)
    knn.init_test_vector(test)

    #  run train and test data through classifier and print results
    knn.run_train_data(out)
    knn.run_test_data(out)

    out.close()

if __name__ == '__main__':
  main()
