import pandas as pd 
import numpy as np

from sklearn.model_selection import train_test_split # Split data using scikit-learn package
from sklearn.neural_network import MLPClassifier
from sklearn import preprocessing

features = pd.read_csv('dfeatures.csv')
labels = pd.read_csv('labels.csv')

scaler = preprocessing.StandardScaler().fit(features)
new_features = scaler.transform(features)

x_train, x_test, y_train, y_test = train_test_split(new_features, labels, test_size=0.2, random_state=1)

model = MLPClassifier(max_iter=600, learning_rate = 'invscaling', learning_rate_init = 0.002, hidden_layer_sizes=(100, 100, 100, 25)) # Create a neural net with a relatively high initial learning rate which is gradually decreasing to help ensure convergence
model.fit(x_train, np.ravel(y_train))

model.predict(x_test)

print(model.score(x_test, y_test))

    