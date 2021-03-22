import mysql.connector

database = mysql.connector.connect(host='localhost', user='nbauser', passwd='', database='dlnba')
db_cursor = database.cursor()


def retrieve_box(table):
	sql_string = "SELECT date, team, opp, t_win, vorp FROM " + table + " where loc='home';"

	db_cursor.execute(sql_string)
	boxscores = db_cursor.fetchall()
	return boxscores

def retrieve_away_vorp(table, date, awayteam):
	sql_string_v = "SELECT vorp FROM "+ table + " where date='" + str(date) + "' and team='" + awayteam + "';"

	db_cursor.execute(sql_string_v)
	vorp = db_cursor.fetchall()
	return vorp[0][0]


def retrieve_splits(year, team, loc):
	sql_string_y2 = "SELECT * FROM " + str(year-2) + "teamsplits where loc = '" + loc + "' and team = '" + team + "';"
	db_cursor.execute(sql_string_y2)
	split_y2 = db_cursor.fetchall()[0][2:]

	sql_string_y1 = "SELECT * FROM " + str(year-1) + "teamsplits where loc = '" + loc + "' and team = '" + team + "';"
	db_cursor.execute(sql_string_y1)
	split_y1 = db_cursor.fetchall()[0][2:]

	return [split_y2, split_y1]


def retrieve_curr_cumulative(table, year, date, loc, team):
	sql_string_curr = ("SELECT avg(t_pts), avg(t_reb), avg(t_ast),avg(t_stl), avg(t_blk), avg(o_pts), avg(o_rpg)," 
		" avg(o_ast), avg(o_stl), avg(o_blk), avg(ortg), avg(drtg) FROM " + table + 
		" where date<'" + str(date) + "' and loc='" + loc + "' and team='" + team + "';")
	db_cursor.execute(sql_string_curr)
	curr_cumulative = db_cursor.fetchall()

	if curr_cumulative[0][0] == None:
		sql_string_yp = "SELECT * FROM " + str(year-1) + "teamsplits where loc = '" + loc + "' and team = '" + team + "';"
		db_cursor.execute(sql_string_yp)
		split_yp = db_cursor.fetchall()[0][2:]
		return split_yp
	else:
		return curr_cumulative[0]


def sql_feature_write(year, h_win, h_vorp, a_vorp, home_splits, away_splits, home_cumulative, away_cumulative):
	full_list= [h_win] + list(home_splits[0]) + list(away_splits[0]) + list(home_splits[1]) + list(away_splits[1]) + list(home_cumulative) + list(away_cumulative) + [h_vorp] + [a_vorp]

	sql_string_write = 'INSERT INTO dl_features VALUES (' + str(full_list[0])
	for i in range(1, len(full_list)):
		sql_string_write += ', ' + str(full_list[i])
	sql_string_write += ');'
	db_cursor.execute(sql_string_write)
	database.commit()

def main():
	year_list = [2020, 2021]
	table_list = ['2020teamboxscores', '2021teamboxscores']

	for year, table in zip(year_list, table_list):
		boxscores = retrieve_box(table)
		for game in boxscores:
			gamedate = game[0]
			hometeam = game[1]
			awayteam = game[2]
			h_win = game[3]
			h_vorp = game[4]
			a_vorp = retrieve_away_vorp(table, gamedate, awayteam)
			home_splits = retrieve_splits(year, hometeam, 'home')
			away_splits = retrieve_splits(year, awayteam, 'away')
			home_cumulative = retrieve_curr_cumulative(table, year, gamedate, 'home', hometeam)
			away_cumulative = retrieve_curr_cumulative(table, year, gamedate, 'away', awayteam)
			sql_feature_write(year, h_win, h_vorp, a_vorp, home_splits, away_splits, home_cumulative, away_cumulative)

	db_cursor.close()
	database.close()

if __name__ == '__main__':
	main()