import nose
import numpy as np
import skfuzzy as fuzz

global features, x_corr, y_corr

# Set random seed
np.random.seed(42)

# Generate pseudo-random reasonably well distinguished clusters
xpts = np.zeros(0)
ypts = np.zeros(0)

x_corr = [7, 1, 4]
y_corr = [3, 2, 1]

for x, y, in zip(x_corr, y_corr):
    xpts = np.concatenate((xpts, np.r_[np.random.normal(x, 0.5, 200)]))
    ypts = np.concatenate((ypts, np.r_[np.random.normal(y, 0.5, 200)]))

# Combine into a feature array
features = np.c_[xpts, ypts].T

print(features)

# Cluster using correct number of clusters (3)
cntr, U, U0, d, Jm, p, fpc = fuzz.cluster.cmeans(data=features, c=3, m=2., error=0.005, maxiter=1000, init=None)

print("centers")
print(cntr)
test_data = features

U, _, _, _, _, fpc = fuzz.cluster.cmeans_predict(
    test_data, cntr, 2., error=0.005, maxiter=1000, seed=1234)


print("predicted")
print(U)