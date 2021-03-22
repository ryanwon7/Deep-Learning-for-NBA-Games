from numpy import loadtxt
import tensorflow as tf
import numpy as np
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
import tensorflow_model_optimization as tfmot
from keras.wrappers.scikit_learn import KerasClassifier


dataset=loadtxt('../data/dl_features_cut.csv', delimiter=',')
scaler = MinMaxScaler()

y = dataset[:, 0]

x_un = dataset[:, 1:]
normalized_x = scaler.fit_transform(x_un)
accuracy_list = []
for i in range(0,50):
	x_train, x_test, y_train, y_test = train_test_split(normalized_x, y, test_size=0.33)

	model = keras.models.Sequential()
	model.add(keras.layers.Dense(20, input_dim=50, activation='linear'))
	model.add(keras.layers.Dense(10, activation='relu'))
	model.add(keras.layers.Dense(1, activation='sigmoid'))

	model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

	model.fit(x_train, y_train, epochs=10, batch_size=10, verbose=0)

	_, accuracy = model.evaluate(x_test, y_test, verbose=0)
	print('Accuracy: %.2f' % (accuracy*100))
	accuracy_list.append(accuracy*100)
print('Overall Accuracy: %.2f' % (sum(accuracy_list)/50))
print('Best Accuracy: %.2f' % (max(accuracy_list)))