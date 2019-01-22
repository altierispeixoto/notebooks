#  Fuzzy C-means clustering (FCM) Algorithm.
# https://pythonhosted.org/scikit-fuzzy/auto_examples/plot_cmeans.html#example-plot-cmeans-py

import numpy as np
import skfuzzy as fuzz
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd


data_types = {
    "wti_variance": "float",
    "wti_skewness": "float",
    "wti_curtosis": "float",
    "image_entropy": "float",
    "class": "int"
}

columns = ["wti_variance", "wti_skewness", "wti_curtosis", "image_entropy", "class"]
dataset = pd.read_csv("dados_autent_bancaria.txt", dtype=data_types, names=columns)
print(dataset.head())

print(dataset.groupby('class').count())

X = dataset.drop('class', axis=1)
y = dataset['class']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

# Cluster using correct number of clusters (3)
cntr, U, U0, d, Jm, p, fpc = fuzz.cluster.cmeans(data=X_train.transpose(), c=2, m=2, error=0.0005, maxiter=10000, init=None,seed=42)

print("centers")
print(cntr)

print("Data trained")
print(U)

labels = [np.argmax(elem) for elem in U.transpose()]
print("Labels")
print(labels)

# Predict fuzzy memberships, U, for all points in test_data
U, _, _, _, _, fpc = fuzz.cluster.cmeans_predict(
    X_test.transpose(), cntr, m=2, error=0.0005, maxiter=10000, seed=1234)


labels = [np.argmax(elem) for elem in U.transpose()]



clusters = pd.Series(labels)
cluster_membership_0 = pd.Series(U[0])
cluster_membership_1 = pd.Series(U[1])

# The fuzzy partition coefficient (FPC)
print("FPC = {}".format(fpc))


X_test = X_test.assign(cluster_membership_0=cluster_membership_0.values)
X_test = X_test.assign(cluster_membership_1=cluster_membership_1.values)
X_test = X_test.assign(classe=y_test)
X_test = X_test.assign(cluster=clusters.values)

predicted_dataset = pd.DataFrame(X_test)

print(predicted_dataset.head(10))


print(predicted_dataset.groupby('classe').count())

predicted_dataset.to_csv("predicted.csv",encoding='utf-8',index=False)
print("Acuracy Score {}".format(accuracy_score(predicted_dataset['classe'],predicted_dataset['cluster'])))
# 0.578181818182


