"""
Kim Dodds - LING 572 - Winter 2020
HW 7 Implementation File

The purpose of this project is to give documents a
binary classification using a model created by libSVM.
"""

# PREPROCESSOR DIRECTIVES
import sys
import os
import re
from collections import Counter
import numpy as np
import pandas as pd
import math


class SVM:
    def __init__(self):
        #  array to hold weight for each SV
        self.sv_weights = []
        #  array for SVs from model
        self.train_vectors = None
        #  variables from the model file
        self.gamma = None
        self.coef = None
        self.degree = None
        self.kernel = None
        self.intercept = None
        self.labels = []
        #  stores classification results
        self.results = []

    #  function to extract info from the model and initialize variables
    #  input: model file and test data
    #  output: n/a
    def init_model(self, model, test):
        #  seperate model format data from support vectors
        format, model = model.split("SV")
        #  call function to extract format data
        self.extract_model_info(format)

        #  find the number of features and create the vector
        model = model.strip()
        model_features = max([int(x) for x in re.findall("(\d+):", model)])
        test_features = max([int(x) for x in re.findall("(\d+):", " ".join(test))])
        num_features = max(model_features, test_features)
        model_lines = model.split('\n')

        self.train_vectors = np.zeros((len(model_lines), num_features + 1), dtype=float)

        #  fill vector with data from SVs in model
        for line in range(len(model_lines)):
            feats = model_lines[line].split(' ')
            self.sv_weights.append(float(feats[0]))
            for f in feats[1:]:
                f = f.split(":")
                if len(f) > 1:
                    self.train_vectors[line, int(f[0])] += float(f[1])

    #  function to extract model format data and save it to class variables
    #  input: header of model file
    #  output: n/a
    def extract_model_info(self, info):
        if 'kernel' in info:
            self.kernel = re.findall("kernel_type (\w+)", info)[0]
        if 'gamma' in info:
            self.gamma = float(re.findall("gamma ([\w.\-]+)", info)[0])
        if 'coef0' in info:
            self.coef = float(re.findall("coef0 ([\w.\-]+)", info)[0])
        if 'degree' in info:
            self.degree = float(re.findall("degree ([\w.\-]+)", info)[0])
        if 'rho' in info:
            self.intercept = float(re.findall("rho ([\w.\-]+)", info)[0])
        if 'label' in info:
            self.labels = re.findall("label ([\d ]+)", info)[0]
            self.labels = self.labels.split(' ')

    #  function to classify one test instance
    #  input: one line from the test data
    #  output: n/a
    def classify(self, test):
        #  create new vector for test instance
        test_vector = np.zeros((len(self.train_vectors[0, :])))
        #  extract gold label
        test = test.split(' ')
        test_gold = test[0]

        #  fill vector with features
        for t in test[1:]:
            t = t.split(":")
            if len(t) > 1:
                test_vector[int(t[0])] += float(t[1])

        #  calculate f(x)
        classification = 0
        #  loop through all train vectors
        for train_item in range(len(self.train_vectors[:, 0])):
            #  calculate kernel function
            k = self.kernel_function(self.train_vectors[train_item, :], test_vector)
            #  add weighted kernel value to sum
            classification += self.sv_weights[train_item] * k
        #  subtract the intercept, p
        classification -= self.intercept

        #  check which side of the plane the value is on and assign label
        if classification >= 0:
            sys_label = 0
        else:
            sys_label = 1
        #  append result to list of results
        self.results.append((test_gold, sys_label, classification))

    #  function to calculate kernel values
    #  input: one train vector and test vector
    #  output: the calculated value of the kernel
    def kernel_function(self, train, test):
        #  check which kernel function should be used and apply the function with the values
        #  extracted from the model
        if self.kernel == 'linear':
            k = np.dot(train, test)
        elif self.kernel == 'polynomial':
            k = (self.gamma * np.dot(train, test) + self.coef) ** self.degree
        elif self.kernel == 'rbf':
            #  take length of each then subtract? or subtract vectors then take length?
            vec_len = np.subtract(train, test)
            vec_len = math.sqrt(np.dot(vec_len, vec_len))
            k = math.exp(-self.gamma * (vec_len) ** 2)
        elif self.kernel == 'sigmoid':
            k = math.tanh(self.gamma * np.dot(train, test) + self.coef)
        else:
            print("Kernel type not recognized")
        return k

    #  function to output result file and print confusion matrix to stdout
    #  input: output file
    #  output: prints result in format: gold sys_label fx | and confusion matrix to stdout
    def output_results(self, out):
        confusion_matrix = pd.DataFrame(0, index=self.labels, columns=self.labels)
        print("Confusion matrix for test data\nRows are gold labels, columns are system output.")

        accuracy = 0
        for r in self.results:
            out.write(str(r[0]) + " " + str(r[1]) + " " + str(r[2]) + '\n')
            confusion_matrix.at[str(r[0]),str(r[1])] += 1
            if int(r[0]) == int(r[1]): accuracy += 1
        accuracy /= len(self.results)

        print(confusion_matrix.to_string())
        print("Test accuracy: {}".format(accuracy))

# MAIN FUNCTION
def main():
    #  load parameters
    test_data = open(sys.argv[1]).read().strip().split('\n')
    model_file = open(sys.argv[2]).read().strip()
    out = open(sys.argv[3], 'w')

    #  create class object
    svm_decode = SVM()
    #  initialize model
    svm_decode.init_model(model_file, test_data)

    #  send test instances to classifer one at a time
    for t in test_data:
        svm_decode.classify(t)

    #  output results
    svm_decode.output_results(out)


if __name__ == '__main__':
    main()
