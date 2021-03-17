import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import mysql.connector
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import re


def get_splits_data(driver, team):
	sp = BeautifulSoup(driver.page_source, 'html.parser')
	home = sp.find('tr', {'data-row':re.compile('3')})
	print(home)


def main(): 
	#database = mysql.connector.connect(host='localhost', user='dbuser', passwd='', database='dlnba')
	#db_cursor = database.cursor()

	team_list = ['ATL', 'BKN', 'BOS', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
	year_list = [2017, 2018, 2019, 2020, 2021]

	driver = webdriver.Chrome()
	base_url = 'https://www.basketball-reference.com/teams/'

	for team in team_list:
		for year in year_list:
			driver.get(base_url + team + '/' + year +'/splits/') #Get season split totals
			get_splits_data(driver, team)
			break
		break

	print('\nCompleted scraping all games from the season. Closing SQL and Selenium connections.')
	#db_cursor.close()
	#database.close()
	driver.close()


if __name__ == '__main__':
    main()
