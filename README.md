# Deep-Learning-for-NBA-Games
A Deep Learning project that aims to predict the winner of a basketball game between two NBA teams.

# Required Libraries
Python 3

Data Collection:
-selenium
-bs4
-mysql
Data Analysis:
-numpy
-sklearn
-tensorflow
-keras

# How to Run
Data Collection:
You must have the MySQL database and tables set up with the correct table setup first. The vorp_webscraper must be run before the gamelog_webscraper, as the gamelog references VORP values for player. Each must be run separately with python, preferably through command line.

Data Processing:
All data must be correctly placed, and you must have the correct tables in place in MySQL. Running this script will generate the features required based on the tables produced from data collection. This can be run on the command line with python.

Data Analysis:
The ann_gridsearch.py analyzes the model to determine what the most effective batch size and epochs to run the model are. After obtaining these, you can run the ann_keras model with different data csv files, which will run 50 different models and produce the accuracy results, posting both the best accuracy and average accuracy from hte 50 models.
