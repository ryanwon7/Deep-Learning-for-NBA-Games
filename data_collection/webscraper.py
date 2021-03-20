import time
import datetime
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


def get_splits_data(driver, team):
	sp = BeautifulSoup(driver.page_source, 'html.parser')
	home = sp.find('tr', {'data-row':re.compile('3')})
	away = sp.find('tr', {'data-row':re.compile('4')})
	splits = [home, away]
	sql_data = []

	for split in splits:
		t_ppg = split.find('td', {'data-stat':re.compile('pts')}).text
		t_rpg = split.find('td', {'data-stat':re.compile('trb')}).text
		t_apg = split.find('td', {'data-stat':re.compile('ast')}).text
		t_spg = split.find('td', {'data-stat':re.compile('stl')}).text
		t_bpg = split.find('td', {'data-stat':re.compile('blk')}).text
		t_fga = float(split.find('td', {'data-stat':re.compile('fga')}).text)
		t_orb = float(split.find('td', {'data-stat':re.compile('orb')}).text)
		t_tov = float(split.find('td', {'data-stat':re.compile('tov')}).text)
		t_fta = float(split.find('td', {'data-stat':re.compile('fta')}).text)

		o_ppg = split.find('td', {'data-stat':re.compile('opp_pts')}).text
		o_rpg = split.find('td', {'data-stat':re.compile('opp_trb')}).text
		o_apg = split.find('td', {'data-stat':re.compile('opp_ast')}).text
		o_spg = split.find('td', {'data-stat':re.compile('opp_stl')}).text
		o_bpg = split.find('td', {'data-stat':re.compile('opp_blk')}).text
		o_fga = float(split.find('td', {'data-stat':re.compile('opp_fga')}).text)
		o_orb = float(split.find('td', {'data-stat':re.compile('opp_orb')}).text)
		o_tov = float(split.find('td', {'data-stat':re.compile('opp_tov')}).text)
		o_fta = float(split.find('td', {'data-stat':re.compile('opp_fta')}).text)

		ortg = team_rating_calc(float(t_ppg), t_fga, t_orb, t_tov, t_fta)
		drtg = team_rating_calc(float(o_ppg), o_fga, o_orb, o_tov, o_fta)

		sql_data.append([team, t_ppg, t_rpg, t_apg, t_spg, t_bpg, o_ppg, o_rpg, o_apg, o_spg, o_bpg, ortg, drtg])
	return sql_data


def sql_insert_split(table, sql_data, loc):
	sql_string = 'INSERT IGNORE INTO ' + table + ' VALUES '

	for i, sql_val in enumerate(sql_data):
		if i == 0:
			val_string = "('" + sql_val + "', '" + loc
		elif i == 1:
			val_string = "', " + sql_val
		else:
			val_string = ", " + sql_val
		sql_string += val_string
	sql_string += ');'
	db_cursor.execute(sql_string)
	database.commit()


def get_gamelog_data(driver, team):
	sp = BeautifulSoup(driver.page_source, 'html.parser')
	gamelogs = sp.find_all('tr', id=re.compile("^tgl_basic.\d+"))
	sql_data = []

	for gamelog in gamelogs:
		date = gamelog.find('td', {'data-stat': re.compile('date_game')}).text
		if gamelog.find('td', {'data-stat': re.compile('game_location')}).text == '@':
			loc = 'away'
		else:
			loc = 'home'
		opp = gamelog.find('td', {'data-stat': re.compile('opp_id')}).contents[0].text
		t_ppg = gamelog.find('td', {'data-stat': re.compile('pts')}).text
		t_rpg = gamelog.find('td', {'data-stat': re.compile('trb')}).text
		t_apg = gamelog.find('td', {'data-stat': re.compile('ast')}).text
		t_spg = gamelog.find('td', {'data-stat': re.compile('stl')}).text
		t_bpg = gamelog.find('td', {'data-stat': re.compile('blk')}).text
		t_fga = float(gamelog.find('td', {'data-stat': re.compile('fga')}).text)
		t_orb = float(gamelog.find('td', {'data-stat': re.compile('orb')}).text)
		t_tov = float(gamelog.find('td', {'data-stat': re.compile('tov')}).text)
		t_fta = float(gamelog.find('td', {'data-stat': re.compile('fta')}).text)

		o_ppg = gamelog.find('td', {'data-stat': re.compile('opp_pts')}).text
		o_rpg = gamelog.find('td', {'data-stat': re.compile('opp_trb')}).text
		o_apg = gamelog.find('td', {'data-stat': re.compile('opp_ast')}).text
		o_spg = gamelog.find('td', {'data-stat': re.compile('opp_stl')}).text
		o_bpg = gamelog.find('td', {'data-stat': re.compile('opp_blk')}).text
		o_fga = float(gamelog.find('td', {'data-stat': re.compile('opp_fga')}).text)
		o_orb = float(gamelog.find('td', {'data-stat': re.compile('opp_orb')}).text)
		o_tov = float(gamelog.find('td', {'data-stat': re.compile('opp_tov')}).text)
		o_fta = float(gamelog.find('td', {'data-stat': re.compile('opp_fta')}).text)

		ortg = team_rating_calc(float(t_ppg), t_fga, t_orb, t_tov, t_fta)
		drtg = team_rating_calc(float(o_ppg), o_fga, o_orb, o_tov, o_fta)

		if gamelog.find('td', {'data-stat': re.compile('game_result')}).text == 'W':
			t_win = '1'
		else:
			t_win = '0'

		sql_data.append([date, team, opp, loc, t_ppg, t_rpg, t_apg, t_spg, t_bpg, o_ppg, o_rpg, o_apg, o_spg, o_bpg, ortg, drtg, t_win])

	return sql_data


def sql_insert_gamelog(table, sql_data):
	sql_string = 'INSERT IGNORE INTO ' + table + ' VALUES '
	flag = 0
	for gamelog in sql_data:
		if flag == 0:
			flag = 1
		else:
			sql_string += ', '
		for i, sql_val in enumerate(gamelog):
			if i == 0:
				val_string = "('" + sql_val
			elif i == 1 or i == 2 or i == 3:
				val_string = "', '" + sql_val
			elif i == 4:
				val_string = "', " + sql_val
			else:
				val_string = ", " + sql_val
			sql_string += val_string
		sql_string += ')'
	sql_string += ';'
	db_cursor.execute(sql_string)
	database.commit()


def main():
	team_list = ['ATL', 'BRK', 'BOS', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
	year_list = [2018, 2019, 2020]
	table_list = ['2018teamsplits', '2019teamsplits', '2020teamsplits']

	driver = webdriver.Chrome()
	base_url = 'https://www.basketball-reference.com/teams/'

	for team in team_list:
		for year, table in zip(year_list, table_list):
			driver.get(base_url + team + '/' + str(year) +'/splits/') #Get season split totals
			WebDriverWait(driver, 5).until(ec.visibility_of_element_located(
				(By.XPATH, "//div[@id='div_team_splits' and @class='table_container is_setup']")))
			sql_data = get_splits_data(driver, team)
			sql_insert_split(table, sql_data[0], 'home')
			sql_insert_split(table, sql_data[1], 'away')

	for team in team_list:
		for year, table in zip([2020, 2021], ['2020teamboxscores', '2021teamboxscores']):
			driver.get(base_url + team + '/' + str(year) +'/gamelog/')
			WebDriverWait(driver, 5).until(ec.visibility_of_element_located(
				(By.XPATH, "//div[@id='div_tgl_basic' and @class='table_container is_setup']")))
			sql_data = get_gamelog_data(driver, team)
			sql_insert_gamelog(table, sql_data)

	print('\nCompleted scraping all games from the season. Closing SQL and Selenium connections.')

	db_cursor.close()
	database.close()
	driver.close()


if __name__ == '__main__':
	main()
