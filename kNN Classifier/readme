This program builds a k-nearest-neighbor document classifier and provides accuracy results in the form of a confusion matrix. Additionally, the program 'rank_feat_by_chi_square' provides a list of the most contrastive features between classes which could be used to apply weights to the features in the kNN classifier.

The command line to run the classifier is:
./build_kNN.sh training_data test_data k_val similarity_func sys_output > acc_file
Where training_data and test_data: vector files in txt format
k_val: the number of nearest neighbors to be considered when classifying
similarity_func: determines which distance function will be used to compute NN; 1=euclidean 2=cosine
sys_output: classification output
acc_file: confusion matrices for train and test data

The command line for chi_squared is:
cat input_file | rank_feat_by_chi_square.sh > output_file
input_file: feature vector file in txt format
output_file: features in descending order with the format "featName score docFrequency"
