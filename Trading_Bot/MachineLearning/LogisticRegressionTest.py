import pandas as pd 
import numpy as np

from sklearn.model_selection import train_test_split # Split data using scikit-learn package
from sklearn import linear_model # Machine learning linear model
from sklearn import preprocessing

features = pd.read_csv('dfeatures.csv')
labels = pd.read_csv('labels.csv')

scaler = preprocessing.StandardScaler().fit(features)
new_features = scaler.transform(features)

x_train, x_test, y_train, y_test = train_test_split(new_features, labels, test_size=0.2, random_state=1)


model = linear_model.LogisticRegression(penalty = 'none')
model.fit(x_train, np.ravel(y_train))

model.predict(x_test)

print(model.score(x_test, y_test))
print(model.coef_)