This program implements a multinomial naive bayes document classifier.
Training and test data takes the form: gold_class f1:count f2:count f3:count ... fn:count
To run the program: ./build_NB2.sh train_file test_file class_delta conditional_delta model_output system_output

train_file: A large collection of feature vectors used to train the classifier
test_file: Feature vectors that will be classified
class_delta: the smoothing variable for the class prior class probability
conditional_delta: the smoothing variable for the conditional probability P(f|c)
model_output: The file name where the classifier model will be output
system_output: the classification results including the probability for each possible class
acc_file: An output file produced by the system which contains a confusion matrix and accuracy result for train and test data

The result files in the folder are run on the following command line:
./build_NB2.sh train.vectors.txt test.vectors.txt 0 0.5 model sys_output

train.vectors.txt and test.vectors.txt can be found in the folder Multivariate Bernoulli Classifier
