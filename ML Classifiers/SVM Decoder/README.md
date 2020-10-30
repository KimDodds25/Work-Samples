This program uses a model file created with LibSVM to give a binary classification to documents using support vector machine (SVM) decoding. Decoding can be run using linear, polynomial, RBF, or sigmoid kernel functions. This decoder produces the same accuracy results as LibSVMs decoder.

Files: 
- train: training data in libSVM vector format
- test: test data in libSVM vector format
- run_results: parameters and results for various runs
- model.id: libSVM model produced with parameters found in run_results
- sys.id: system output produced by each model

To run:
./svm_classify.sh test_data model_file system_output
