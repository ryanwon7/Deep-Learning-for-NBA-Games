from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import mysql.connector
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import re

database = mysql.connector.connect(host='localhost', user='nbauser', passwd='', database='dlnba')
db_cursor = database.cursor()


def team_rating_calc(pts, fga, oreb, tov, fta):
	rtg = 100*pts/(fga-oreb+tov+(0.4*fta))
	return '%.2f' % rtg


def get_vorp_data(driver, team):
	sp = BeautifulSoup(driver.page_source, 'html.parser')
	adv = sp.find('div', id='div_advanced')
	sql_data = []
	for i in range(0,10):
		player = adv.find('tr', {'data-row':re.compile(str(i))})
		name = player.find('td', {'data-stat':re.compile('player')}).text
		vorp = player.find('td', {'data-stat':re.compile('vorp')}).text
		sql_data.append([team, name, vorp])
	return sql_data


def sql_insert_vorp(table, sql_data):
	sql_string = 'INSERT IGNORE INTO ' + table + ' VALUES '

	for i, sql_val in enumerate(sql_data):
		if i==0:
			sql_string += "('" + sql_val[0] + "', '" + sql_val[1].replace("'", "''") + "', " + sql_val[2] + ")"
		else:
			sql_string += ", ('" + sql_val[0] + "', '" + sql_val[1].replace("'", "''") + "', " + sql_val[2] + ")"
	sql_string += ";"
	db_cursor.execute(sql_string)
	database.commit()


def main():
	team_list = ['ATL', 'BRK', 'BOS', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
	year_list = [2020, 2021]
	table_list = ['2020vorp', '2021vorp']

	driver = webdriver.Chrome()
	base_url = 'https://www.basketball-reference.com/teams/'

	for year, table in zip(year_list, table_list):
		vorp_data = []
		for team in team_list:
			driver.get(base_url+team+'/'+str(year) + '.html')
			WebDriverWait(driver, 5).until(ec.visibility_of_element_located(
				(By.XPATH, "//div[@id='div_advanced' and @class='table_container is_setup']")))
			vorp_data += get_vorp_data(driver, team)
		sql_insert_vorp(table, vorp_data)

	print('\nCompleted scraping all player VORPs. Closing SQL and Selenium connections.')

	db_cursor.close()
	database.close()
	driver.close()


if __name__ == '__main__':
	main()
