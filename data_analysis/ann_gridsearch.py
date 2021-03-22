from numpy import loadtxt
import tensorflow as tf
import numpy as np
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
import tensorflow_model_optimization as tfmot
from keras.wrappers.scikit_learn import KerasClassifier


def create_model():
	model = keras.models.Sequential()
	model.add(keras.layers.Dense(20, input_dim=74, activation='linear'))
	model.add(keras.layers.Dense(10, activation='relu'))
	model.add(keras.layers.Dense(1, activation='sigmoid'))
	model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
	return model

dataset=loadtxt('../data/dl_features.csv', delimiter=',')
scaler = MinMaxScaler()

y = dataset[:, 0]

x_un = dataset[:, 1:]
normalized_x = scaler.fit_transform(x_un)

x_train, x_test, y_train, y_test = train_test_split(normalized_x, y, test_size=0.33)

model = KerasClassifier(build_fn=create_model, verbose=0)
batch_size = [10, 20, 40, 60, 80, 100]
epochs = [10, 50, 100]
param_grid = dict(batch_size=batch_size, epochs=epochs)
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1, cv=3)
grid_result = grid.fit(x_train, y_train)
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))

print(grid_result.best_params_)