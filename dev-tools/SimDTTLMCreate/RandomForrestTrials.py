# Designed to take an x and y to play with regression settings
# Author: Jeff Schloemer
# Date: 03/10/2023

import argparse
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score,mean_squared_error
from sklearn import metrics
from tqdm import tqdm

# Define the command line arguments
parser = argparse.ArgumentParser(description='Take in x and y data and run random forrest trials')
parser.add_argument('--xdata', help='a pandas csv file for the x data')
parser.add_argument('--ydata', help='a pandas csv file for the y data')

# Parse the command-line arguments
args = parser.parse_args()
xdf = []
ydf = []

if args.xdata.endswith('csv'):
    # Load the JSON file into a pandas DataFrame
    xdf = pd.read_csv(args.xdata)
else:
    print("Other sources not supported yet")
    exit()
    
if args.ydata.endswith('csv'):
    # Load the JSON file into a pandas DataFrame
    ydf = pd.read_csv(args.ydata)
else:
    print("Other sources not supported yet")
    exit()
    
estimators = [10, 50, 100, 150, 200, 250, 300]
randomState = [0, 10, 20, 30, 42, 50, 60, 70, 80, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
features = ['sqrt', 'log2', None, 2, 20, 200]
leafNodes = [None, 2, 20, 200, 2000]

rows = len(estimators)

x_array = xdf.to_numpy()
y_array = xdf.to_numpy()

e_best = 0
f_best = 0
l_best = 0
score_best = 0
vebest = 0
tebest = 0

X_train, X_test, y_train, y_test = train_test_split(x_array, y_array, test_size=0.3)

for est in tqdm(estimators, desc="Processing Regression Trials", bar_format="{l_bar}{bar:50}{r_bar}", total=rows):
    for feat in features:
        for leaf in leafNodes:
            tesum = 0
            vesum = 0
            delta = 0
            score = 0
            for rand in randomState:
                modelTest = RandomForestRegressor(n_estimators=est, random_state=rand, max_features=feat, max_leaf_nodes=leaf, n_jobs=-1)
                modelTest.fit(X_train, y_train)
                predictionsTest = modelTest.predict(X_test)
                ResTest = modelTest.predict(X_train)
                teacc = modelTest.score(X_train, y_train)
                veacc = modelTest.score(X_test, y_test)
                tesum = tesum + teacc
                vesum = vesum + veacc
                delta = delta + (teacc - veacc)
            score = tesum / len(randomState) + vesum / len(randomState) + (1 - (delta / len(randomState)))
            if score > score_best:
                score_best = score
                e_best = est
                f_best = feat
                l_best = leaf
                vebest = vesum / len(randomState)
                tebest = tesum / len(randomState)
                
print('Results:')
print('Verification Accuracy Best: ', str(vebest))
print('Test Accuracy Best: ', str(tebest))
print('Estimators: ', str(e_best))
print('Features: ', str(f_best))
print('Max Leaf Nodes: ', str(l_best))

                
# Results:
# Verification Accuracy Best:  0.9598204875996195
# Test Accuracy Best:  0.9876996555094459
# Estimators:  50
# Features:  2
# Max Leaf Nodes:  None       
        