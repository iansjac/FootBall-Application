"""
This script downloads 16 JSON files and parses them into JSON Objects. Then, these objects are used to insert
all the data to a SQLite Database.
Author: Ian Jacobs
Last Edited: November 16, 2016
"""
import sqlite3
import urllib
import json
from Tkinter import *
import ttk
import tkMessageBox

# Connect to the DB
conn = sqlite3.connect('footballdb.sqlite')
cur = conn.cursor()

# Execute a script , use triple quotes to include spaces.
# Drop table if exists is necessary to run the code more than one time.
cur.executescript('''
DROP TABLE IF EXISTS club;
DROP TABLE IF EXISTS club_year;
DROP TABLE IF EXISTS game;
DROP TABLE IF EXISTS league;
DROP TABLE IF EXISTS match;

CREATE TABLE club (
    id     TEXT NOT NULL PRIMARY KEY,
    club_name   TEXT,
    abbr    CHAR(3),
    league_name TEXT,
    FOREIGN KEY(league_name) REFERENCES league(league_name)
);

CREATE TABLE club_year (
    club_key     TEXT NOT NULL,
    club_year   INTEGER(4) NOT NULL,
    PRIMARY KEY(club_key, club_year),
    FOREIGN KEY(club_key) REFERENCES club(id)
);

CREATE TABLE league (
    league_name TEXT NOT NULL PRIMARY KEY
);

CREATE TABLE match  (
    match_name NOT NULL PRIMARY KEY
);

CREATE TABLE game (
    id  INTEGER NOT NULL PRIMARY KEY,
    match_name  TEXT,
    team_one  TEXT,
    team_two  TEXT,
    score_one INTEGER(3),
    score_two INTEGER(3),
    game_date   DATE,
    season_year INT(4),
    league_name TEXT,
    FOREIGN KEY(team_one) REFERENCES club(id),
    FOREIGN KEY(team_two) REFERENCES club(id),
	FOREIGN KEY(league_name) REFERENCES league(league_name)
	FOREIGN KEY(match_name) REFERENCES match(match_name)
);
''')

# This statement turns on the foreign keys contraint. If this is not turned on, the constraint does not work even
# If you define it in the schema
cur.execute('PRAGMA foreign_keys = ON;')


# **********************************************************************************************************************
# Function Definitions


# This function gets the club names from the JSON url given and inserts the club into the club table
def insert_club_to_db(url, year):
    response = urllib.urlopen(url)
    data_dictionary = json.loads(response.read())

    # Read the league name and do substring to get correct name and then insert it
    league_name = data_dictionary['name']
    league_name = league_name[0:len(league_name) - 8]
    cur.execute('''INSERT OR IGNORE INTO league(league_name) VALUES(?)''', (league_name,))

    # Deal with the clubs
    clubs_dictionary = data_dictionary['clubs']

    # For each club in the clubs dictionary, get the values and insert them to the club table
    for club in clubs_dictionary:
        club_id = club['key']
        club_name = club['name']
        club_code = club['code']
        cur.execute('''INSERT OR IGNORE INTO club(id, club_name, abbr, league_name)
        VALUES(?, ?, ?, ?)''', (club_id, club_name, club_code, league_name))
        insert_club_year(club_id, year)  # Insert the club and year as well


# This function is called from the 'insert_club_to_db' function. Once a club is created in the club table, this
# Function takes the club and assigns it a year. This is because some clubs that played in 2015, did not play in 2016
# And vise-versa. So we need to know which clubs played in which year
def insert_club_year(club_key, year):
    cur.execute('''INSERT OR IGNORE INTO club_year(club_key, club_year)
            VALUES(?, ?)''', (club_key, year))


# This function takes an url of matches and a season year of the matches given. Then, these matches are inserted into
# The database.
def insert_matches(url, season_year):
    response = urllib.urlopen(url)
    matches_dictionary = json.loads(response.read())
    matches_rounds = matches_dictionary['rounds']  # Get the rounds
    league_name = matches_dictionary['name']  # Get the league name and do a substring to remove unnecessary data
    league_name = league_name[0:len(league_name) - 8]

    # For each match in the rounds
    for match in matches_rounds:
        match_dict = match['matches']  # Get the matches dictionary
        match_name = match['name']  # Get the match name

        cur.execute('''INSERT OR IGNORE INTO match(match_name)
                    VALUES(?)''', (match_name,))

        # For each item in the matches dictionary, get the corresponding data to insert into the database
        for item in match_dict:
            match_date = item['date']
            score1 = item['score1']
            score2 = item['score2']
            team1_dict = item['team1']
            team2_dict = item['team2']
            team1_key = team1_dict['key']
            team2_key = team2_dict['key']

            # Insert values of matches in the database
            cur.execute('''INSERT INTO game(team_one, team_two, score_one, score_two, game_date, match_name,
                season_year, league_name) VALUES(?, ?, ?, ?, ?, ?, ?, ?)''',
                        (team1_key, team2_key, score1, score2, match_date, match_name, season_year, league_name))


# **********************************************************************************************************************
# Main Code where functions are called to download the JSONs, parse them, and insert them into the database

# English Premier League
english_league15_clubs = 'https://raw.githubusercontent.com/openfootball/football.json/master/2015-16/en.1.clubs.json'
english_league16_clubs = 'https://raw.githubusercontent.com/openfootball/football.json/master/2016-17/en.1.clubs.json'
english_matches2015 = 'https://raw.githubusercontent.com/openfootball/football.json/master/2015-16/en.1.json'
english_matches2016 = 'https://raw.githubusercontent.com/openfootball/football.json/master/2016-17/en.1.json'

insert_club_to_db(english_league15_clubs, 2015)  # Insert unique clubs and leagues to the DB for 2015
insert_club_to_db(english_league16_clubs, 2016)  # Insert unique clubs and leagues to the DB for 2016
insert_matches(english_matches2015, 2015)  # Insert matches for 2015
insert_matches(english_matches2016, 2016)  # Insert matches for 2016

# Deutsche Bundesliga
deutsche_league15_clubs = 'https://raw.githubusercontent.com/openfootball/football.json/master/2015-16/de.1.clubs.json'
deutsche_league16_clubs = 'https://raw.githubusercontent.com/openfootball/football.json/master/2016-17/de.1.clubs.json'
deutsche_matches2015 = 'https://raw.githubusercontent.com/openfootball/football.json/master/2015-16/de.1.json'
deutsche_matches2016 = 'https://raw.githubusercontent.com/openfootball/football.json/master/2016-17/de.1.json'

insert_club_to_db(deutsche_league15_clubs, 2015)  # Insert unique clubs and leagues to the DB for 2015
insert_club_to_db(deutsche_league16_clubs, 2016)  # Insert unique clubs and leagues to the DB for 2016
insert_matches(deutsche_matches2015, 2015)  # Insert matches for 2015
insert_matches(deutsche_matches2016, 2016)  # Insert matches for 2016

# Spanish Primera Division ("La Liga")
spanish_league15_clubs = 'https://raw.githubusercontent.com/openfootball/football.json/master/2015-16/es.1.clubs.json'
spanish_league16_clubs = 'https://raw.githubusercontent.com/openfootball/football.json/master/2016-17/es.1.clubs.json'
spanish_matches2015 = 'https://raw.githubusercontent.com/openfootball/football.json/master/2015-16/es.1.json'
spanish_matches2016 = 'https://raw.githubusercontent.com/openfootball/football.json/master/2016-17/es.1.json'

insert_club_to_db(spanish_league15_clubs, 2015)  # Insert unique clubs and leagues to the DB for 2015
insert_club_to_db(spanish_league16_clubs, 2016)  # Insert unique clubs and leagues to the DB for 2016
insert_matches(spanish_matches2015, 2015)
insert_matches(spanish_matches2016, 2016)

# Italian Serie A
italian_league15_clubs = 'https://raw.githubusercontent.com/openfootball/football.json/master/2015-16/it.1.clubs.json'
italian_league16_clubs = 'https://raw.githubusercontent.com/openfootball/football.json/master/2016-17/it.1.clubs.json'
italian_matches2015 = 'https://raw.githubusercontent.com/openfootball/football.json/master/2015-16/it.1.json'
italian_matches2016 = 'https://raw.githubusercontent.com/openfootball/football.json/master/2016-17/it.1.json'

insert_club_to_db(italian_league15_clubs, 2015)  # Insert unique clubs and leagues to the DB for 2015
insert_club_to_db(italian_league16_clubs, 2016)  # Insert unique clubs and leagues to the DB for 2016
insert_matches(italian_matches2015, 2015)
insert_matches(italian_matches2016, 2016)

# commit
conn.commit()



# League Section Button Listeners***************************************************************************************
# This function is called when the 'Search League' button is clicked
def search_league_click():
    league_input = searchLeagueEntry.get()  # Get the user input from the Entry

    # Execute the query. Used 'LIKE' so you can search for half a word if you want to
    cur.execute('''SELECT league_name FROM league WHERE league_name LIKE ?''', ('%' + league_input + '%',))

    columns = [column[0] for column in cur.description]  # Get the column names from the cursor
    results = []

    for row in cur.fetchall():
        results.append(row)  # Append results in the array

    create_tree(columns, results)  # Create the treeview

    searchLeagueEntry.delete(0, END)  # Empty the Entry field
    global updateSection  # Update the global variable in case user decides to update also
    updateSection = 'league'


# This function is called when the 'Add League' button is clicked
def add_league_click():
    league_input = searchLeagueEntry.get()  # Get the user input from the Entry

    try:
        if len(league_input) > 0:
            cur.execute('''INSERT INTO league(league_name) VALUES (?)''', (league_input,))
            conn.commit()
            tkMessageBox.showinfo("League Addition", league_input + ' added!')
    except sqlite3.Error as er:  # Catch exceptions if any, such as UNIQUE
        tkMessageBox.showinfo("Error Adding", er)

    searchLeagueEntry.delete(0, END)  # Empty the Entry


# This function is called when the 'Delete League' is clicked
def delete_league_click():
    league_input = searchLeagueEntry.get()  # Get the user input from the Entry
    if len(league_input) > 0:
        try:
            cur.execute('''DELETE FROM league WHERE league_name = ?''', (league_input,))
            conn.commit()
            tkMessageBox.showinfo("Delete League", league_input + ' deleted!')
            updateLeagueButton['state'] = 'disabled'  # Disable the 'Update' button again
            addLeagueButton['state'] = 'normal'  # Enable these buttons now and the rest below
            searchLeagueButton['state'] = 'normal'
            deleteLeagueButton['state'] = 'disabled'
        except sqlite3.Error as er:  # Catch exceptions if any, such as FOREIGN KEY, CANNOT DELETE
            tkMessageBox.showinfo("Error Deleting", er)
            updateLeagueButton['state'] = 'disabled'
            addLeagueButton['state'] = 'normal'
            searchLeagueButton['state'] = 'normal'
            deleteLeagueButton['state'] = 'disabled'

    searchLeagueEntry.delete(0, END)  # Empty the Entry


# This function is called when the 'Update League' button is clicked
def update_league_click():
    league_input = searchLeagueEntry.get()  # Get the user input from the Entry
    if len(league_input) > 0:
        try:
            cur.execute("""UPDATE league SET league_name = ? WHERE league_name = ?""", (league_input, updateKey))
            tkMessageBox.showinfo("Update", 'Record updated!')
            updateLeagueButton['state'] = 'disabled'  # Disable the 'Update' button again
            addLeagueButton['state'] = 'normal'  # Enable these buttons now and the rest below
            searchLeagueButton['state'] = 'normal'
            deleteLeagueButton['state'] = 'disabled'
        except sqlite3.Error as er:
            tkMessageBox.showinfo("Error Updating", er)
            updateLeagueButton['state'] = 'disabled'
            addLeagueButton['state'] = 'normal'
            searchLeagueButton['state'] = 'normal'
            deleteLeagueButton['state'] = 'disabled'

    else:
        tkMessageBox.showinfo("Update Failed", 'Cannot be empty!')

    searchLeagueEntry.delete(0, END)  # Empty the Entry field


# Match Section Button Listeners****************************************************************************************
# This function is called when the 'Search Match' button is clicked
def search_match_click():
    match_input = matchNameEntry.get()  # Get the user input from the Entry
    cur.execute('''SELECT match_name FROM match WHERE match_name LIKE ?''', ('%' + match_input + '%',))

    columns = [column[0] for column in cur.description]  # Column descriptions from the cursor
    results = []
    for row in cur.fetchall():
        results.append(row)

    create_tree(columns, results)  # Create the treeview and populate
    matchNameEntry.delete(0, END)
    global updateSection
    updateSection = 'match'  # Update this global variable in case user decides to update in this section


# This function is called when the user clicks the 'Add Match' button
def add_match_click():
    match_input = matchNameEntry.get()  # Get the user input from the Entry
    try:
        if len(match_input) > 0:
            cur.execute('''INSERT INTO match(match_name) VALUES (?)''', (match_input,))
            conn.commit()
            tkMessageBox.showinfo("Match Addition", match_input + ' added!')  # Inform user of success

        matchNameEntry.delete(0, END)  # Empty field
    except sqlite3.Error as er:  # Handle exceptions
        tkMessageBox.showinfo("Error Adding", er)


# This function is called when the user clicks the 'Delete Match' button
def delete_match_click():
    match_input = matchNameEntry.get()  # Get the user input from the Entry
    if len(match_input) > 0:
        try:
            cur.execute('''DELETE FROM match WHERE match_name = ?''', (match_input,))
            conn.commit()
            tkMessageBox.showinfo("Delete", match_input + ' deleted!')
            updateMatchButton['state'] = 'disabled'
            addMatchButton['state'] = 'normal'
            searchMatchButton['state'] = 'normal'
            deleteMatchButton['state'] = 'disabled'

        except sqlite3.Error as er:
            tkMessageBox.showinfo("Error Deleting", er)
            updateMatchButton['state'] = 'disabled'
            addMatchButton['state'] = 'normal'
            searchMatchButton['state'] = 'normal'
            deleteMatchButton['state'] = 'disabled'

    matchNameEntry.delete(0, END)


# This function is called when the user clicks the 'Update Match' button
def update_match_click():
    match_input = matchNameEntry.get()  # Get the user input from the Entry
    if len(match_input) > 0:
        try:
            cur.execute("""UPDATE match SET match_name = ? WHERE match_name = ?""", (match_input, updateKey))
            tkMessageBox.showinfo("Update", 'Record updated!')
            updateMatchButton['state'] = 'disabled'
            addMatchButton['state'] = 'normal'
            searchMatchButton['state'] = 'normal'
            deleteMatchButton['state'] = 'disabled'
        except sqlite3.Error as er:
            tkMessageBox.showinfo("Error Updating", er)
            updateMatchButton['state'] = 'disabled'
            addMatchButton['state'] = 'normal'
            searchMatchButton['state'] = 'normal'
            deleteMatchButton['state'] = 'disabled'

    else:
        tkMessageBox.showinfo("Update Failed", 'Cannot be empty!')

    matchNameEntry.delete(0, END)


# Club Section Button Listeners*****************************************************************************************
# This function is called when the user clicks the 'Search Club' Button
def search_club_click():
    clubID = clubIDEntry.get()  # Get the user input from the Entry
    clubName = clubNameEntry.get()  # Get the user input from the Entry
    clubAbbr = clubAbbrEntry.get()  # Get the user input from the Entry
    clubLeague = clubLeagueEntry.get()  # Get the user input from the Entry

    cur.execute('''SELECT * FROM club WHERE id LIKE ? AND club_name LIKE ? AND abbr LIKE ? AND league_name LIKE ?'''
                , ('%' + clubID + '%', '%' + clubName + '%', '%' + clubAbbr + '%', '%' + clubLeague + '%',))

    columns = [column[0] for column in cur.description]  # Get Columns
    results = []
    for row in cur.fetchall():
        results.append(row)

    create_tree(columns, results)  # Create treeview

    clubIDEntry.delete(0, END)  # Empty fields
    clubNameEntry.delete(0, END)
    clubAbbrEntry.delete(0, END)
    clubLeagueEntry.delete(0, END)
    global updateSection
    updateSection = 'club'  # In case the user decides to update, this needs to be assigned


# This function is called when the user clicks the 'Add Club' button
def add_club_click():
    clubID = clubIDEntry.get()  # Get the user input from the Entry
    clubName = clubNameEntry.get()  # Get the user input from the Entry
    clubAbbr = clubAbbrEntry.get()  # Get the user input from the Entry
    clubLeague = clubLeagueEntry.get()  # Get the user input from the Entry

    # Nothing can be empty
    if len(clubID) > 0 and len(clubName) > 0 and len(clubAbbr) > 0 and len(clubLeague) > 0:
        try:
            cur.execute('''INSERT INTO club(id, club_name, abbr, league_name) VALUES (?, ?, ?, ?)''',
                        (clubID, clubName, clubAbbr, clubLeague))
            conn.commit()
            tkMessageBox.showinfo("Add Club", 'Club added!')
            clubIDEntry.delete(0, END)
            clubNameEntry.delete(0, END)
            clubAbbrEntry.delete(0, END)
            clubLeagueEntry.delete(0, END)
        except sqlite3.Error as er:
            tkMessageBox.showinfo("Error Adding", er)

    else:
        tkMessageBox.showinfo('Cannot Insert Club', 'Fields cannot be empty!')


# This function is called when the user clicks the 'Delete Club' option
# Note: Only deletes by primary key club_id
def delete_club_click():
    clubID = clubIDEntry.get()  # Get the user input from the Entry

    if len(clubID) > 0:
        try:
            cur.execute('''DELETE FROM club WHERE id = ?''', (clubID,))
            conn.commit()
            tkMessageBox.showinfo("Delete Club", clubID + ' deleted!')
            clubIDEntry.delete(0, END)
            clubNameEntry.delete(0, END)
            clubAbbrEntry.delete(0, END)
            clubLeagueEntry.delete(0, END)
            updateClubButton['state'] = 'disabled'
            addClubButton['state'] = 'normal'
            searchClubButton['state'] = 'normal'
            deleteClubButton['state'] = 'disabled'
        except sqlite3.Error as er:
            tkMessageBox.showinfo("Error Deleting", er)
            clubIDEntry.delete(0, END)
            clubNameEntry.delete(0, END)
            clubAbbrEntry.delete(0, END)
            
            clubLeagueEntry.delete(0, END)
            updateClubButton['state'] = 'disabled'
            addClubButton['state'] = 'normal'
            searchClubButton['state'] = 'normal'
            deleteClubButton['state'] = 'disabled'

    else:
        tkMessageBox.showinfo('Cannot Delete Club', 'Club ID cannot be empty!')


# This function is called when the user clicks the 'Update Club' button
def update_club_click():
    clubID = clubIDEntry.get()  # Get the user input from the Entry
    clubName = clubNameEntry.get()  # Get the user input from the Entry
    clubAbbr = clubAbbrEntry.get()  # Get the user input from the Entry
    clubLeague = clubLeagueEntry.get()  # Get the user input from the Entry
    if len(clubID) > 0:
        try:
            cur.execute("""UPDATE club SET id = ?, club_name = ?, abbr = ?, league_name = ? WHERE id = ?""",
                        (clubID, clubName, clubAbbr, clubLeague, updateKey))
            tkMessageBox.showinfo("Update", 'Record updated!')
            updateClubButton['state'] = 'disabled'
            addClubButton['state'] = 'normal'
            searchClubButton['state'] = 'normal'
            deleteClubButton['state'] = 'disabled'
        except sqlite3.Error as er:
            tkMessageBox.showinfo("Error Updating", er)
            updateClubButton['state'] = 'disabled'
            addClubButton['state'] = 'normal'
            searchClubButton['state'] = 'normal'
            deleteClubButton['state'] = 'disabled'

    else:
        tkMessageBox.showinfo("Update Failed", 'Cannot be empty!')

    clubIDEntry.delete(0, END)
    clubNameEntry.delete(0, END)
    clubAbbrEntry.delete(0, END)
    clubLeagueEntry.delete(0, END)


# Game Section Button Listeners*****************************************************************************************
# This method runs a search query that depend upon the parameters input from the user. It is called once the search game
# button is clicked and will retrun everything in the table if no user input.
def search_game_click():
    # Get the user input from the Entries
    matchName = gameMatchNameEntry.get()
    gameDate = gameDateEntry.get()
    teamOne = teamOneEntry.get()
    teamTwo = teamTwoEntry.get()
    scoreOne = scoreOneEntry.get()
    scoreTwo = scoreTwoEntry.get()
    seasonYear = seasonYearEntry.get()
    leagueName = gameLeagueEntry.get()

    # execute the search query
    cur.execute('''SELECT * FROM game WHERE match_name LIKE ? AND team_one LIKE ? AND team_two LIKE ? AND (score_one is null OR score_one
            LIKE ?) AND  (score_two is null OR score_two LIKE ?) AND game_date LIKE ? AND season_year LIKE ? AND league_name LIKE ?'''
                , ('%' + matchName + '%', '%' + teamOne + '%', '%' + teamTwo + '%', '%' + scoreOne + '%',
                   '%' + scoreTwo + '%', '%' + gameDate + '%', '%' + seasonYear + '%', '%' + leagueName + '%'))

    columns = [column[0] for column in cur.description]
    results = []

    # collect the results
    for row in cur.fetchall():
        results.append(row)
        # print row

    create_tree(columns, results)  # Create the table

    gameMatchNameEntry.delete(0, END)  # clear the data from the input fields
    gameDateEntry.delete(0, END)
    teamOneEntry.delete(0, END)
    teamTwoEntry.delete(0, END)
    scoreOneEntry.delete(0, END)
    scoreTwoEntry.delete(0, END)
    seasonYearEntry.delete(0, END)
    gameLeagueEntry.delete(0, END)
    global updateSection
    updateSection = 'game'  # Update this global variable in case the user wants to update record


# this is called when you press the add game button it loads the game into the database
def add_game_click():
    matchName = gameMatchNameEntry.get()
    gameDate = gameDateEntry.get()
    teamOne = teamOneEntry.get()
    teamTwo = teamTwoEntry.get()
    scoreOne = scoreOneEntry.get()
    scoreTwo = scoreTwoEntry.get()
    seasonYear = seasonYearEntry.get()
    leagueName = gameLeagueEntry.get()

    # Nothing can be empty user must input all fields for the game to be added
    # The user must insure that the proper fields match the foreign keys constaints
    if len(matchName) > 0 and len(gameDate) > 0 and len(teamOne) > 0 and len(teamTwo) > 0 and len(scoreOne) > 0 and len(
            scoreTwo) > 0 and len(seasonYear) > 0 and len(leagueName) > 0:
        try:
            # execute the insert query
            cur.execute(
                '''INSERT INTO game(match_name, game_date, team_one, team_two, score_one, score_two, season_year, league_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (matchName, gameDate, teamOne, teamTwo, scoreOne, scoreTwo, seasonYear, leagueName))
            conn.commit()
            tkMessageBox.showinfo("Add Game", 'Game added!')  # illustrate that the game addition was successful

            # clear the input fields
            gameMatchNameEntry.delete(0, END)
            gameDateEntry.delete(0, END)
            teamOneEntry.delete(0, END)
            teamTwoEntry.delete(0, END)
            scoreOneEntry.delete(0, END)
            scoreTwoEntry.delete(0, END)
            seasonYearEntry.delete(0, END)
            gameLeagueEntry.delete(0, END)
        except sqlite3.Error as er:
            tkMessageBox.showinfo("Error Adding", er)

    else:
        tkMessageBox.showinfo('Cannot Insert game', 'Must Fill all Fields')  # error case if missing input from the user


# Game Delete Listener*******************************************************************************
# This method is executed upon the press of the delete game method. The method takes the data from the
# user and checks if there is a row within the Game table and if so deletes that from the game table.
def delete_game_click():
    # collect user input
    matchName = gameMatchNameEntry.get()
    gameDate = gameDateEntry.get()
    teamOne = teamOneEntry.get()
    teamTwo = teamTwoEntry.get()

    # IF the neccessary fields are completed
    if len(matchName) > 0 and len(gameDate) > 0 and len(teamOne) > 0 and len(teamTwo) > 0:
        try:
            # execute a delete query
            cur.execute(
                '''DELETE FROM game WHERE match_name = ? AND game_date = ? AND team_one = ? AND team_two = ? ''',
                (matchName, gameDate, teamOne, teamTwo))
            conn.commit()
            updateGameButton['state'] = 'disabled'
            addGameButton['state'] = 'normal'
            searchGameButton['state'] = 'normal'
            deleteGameButton['state'] = 'disabled'
            tkMessageBox.showinfo("Deleted Game!", 'Game deleted!')  # use text alert to signify that row was deleted
            gameMatchNameEntry.delete(0, END)
            gameDateEntry.delete(0, END)
            teamOneEntry.delete(0, END)
            teamTwoEntry.delete(0, END)
            scoreOneEntry.delete(0, END)
            scoreTwoEntry.delete(0, END)
            seasonYearEntry.delete(0, END)
            gameLeagueEntry.delete(0, END)


        except sqlite3.Error as er:
            tkMessageBox.showinfo("Error Deleting", er)

    else:
        tkMessageBox.showinfo('Cannot Delete Game',
                              'Game Match Name, Game Date, Team One, Team Two cannot be empty!')  # text alert if fields are empty


# Treeview**************************************************************************************************************
# This function is called whenever the user double-clicks a record in the treeview. The double click will be used as a
# way to let the system know that this record will be updated
def onDoubleClick(event):
    curItem = tree.focus()  # focus on the tree
    values = tree.item(curItem)['values']  # get the values in an array or the row double-clicked
    global updateKey  # This is the primary key of the value. To use when updating a row

    if updateSection == 'league':  # If you want to update a row from the 'League Section'
        if len(values) > 0:
            updateLeagueButton['state'] = 'normal'
            addLeagueButton['state'] = 'disabled'
            searchLeagueButton['state'] = 'disabled'
            deleteLeagueButton['state'] = 'normal'
            league_name = values[0]  # The 0-th item is always the primary key
            updateKey = league_name
            searchLeagueEntry.delete(0, END)  # Erase the field
            searchLeagueEntry.insert(0, league_name)  # Now insert into the field

    if updateSection == 'match':  # If you want to update a row from the 'Match Section'
        if len(values) > 0:
            updateMatchButton['state'] = 'normal'
            addMatchButton['state'] = 'disabled'
            searchMatchButton['state'] = 'disabled'
            deleteMatchButton['state'] = 'normal'
            match_name = values[0]  # The 0-th item is always the primary key
            updateKey = match_name
            matchNameEntry.delete(0, END)
            matchNameEntry.insert(0, match_name)

    if updateSection == 'club':  # If you want to update a row from the 'Club Section'
        if len(values) > 0:
            updateClubButton['state'] = 'normal'
            addClubButton['state'] = 'disabled'
            searchClubButton['state'] = 'disabled'
            deleteClubButton['state'] = 'normal'
            clubID = values[0]  # The 0-th item is always the primary key
            clubName = values[1]
            clubAbbr = values[2]
            clubLeagueName = values[3]
            updateKey = clubID
            clubIDEntry.delete(0, END)
            clubNameEntry.delete(0, END)
            clubAbbrEntry.delete(0, END)
            clubLeagueEntry.delete(0, END)
            clubIDEntry.insert(0, clubID)
            clubNameEntry.insert(0, clubName)
            clubAbbrEntry.insert(0, clubAbbr)
            clubLeagueEntry.insert(0, clubLeagueName)

    if updateSection == 'game':  # If you want to update a row from the 'Club Section'
        if len(values) > 0:
            updateGameButton['state'] = 'normal'
            addGameButton['state'] = 'disabled'
            searchGameButton['state'] = 'disabled'
            deleteGameButton['state'] = 'normal'
            gameID = values[0]  # The 0-th item is always the primary key
            gameMatchName = values[1]
            teamOne = values[2]
            teamTwo = values[3]
            scoreOne = values[4]
            scoreTwo = values[5]
            gameDate = values[6]
            seasonYear = values[7]
            leagueName = values[8]
            updateKey = gameID
            gameMatchNameEntry.delete(0, END)
            gameDateEntry.delete(0, END)
            teamOneEntry.delete(0, END)
            teamTwoEntry.delete(0, END)
            scoreOneEntry.delete(0, END)
            scoreTwoEntry.delete(0, END)
            seasonYearEntry.delete(0, END)
            gameLeagueEntry.delete(0, END)
            gameMatchNameEntry.insert(0, gameMatchName)
            gameDateEntry.insert(0, gameDate)
            teamOneEntry.insert(0, teamOne)
            teamTwoEntry.insert(0, teamTwo)
            scoreOneEntry.insert(0, scoreOne)
            scoreTwoEntry.insert(0, scoreTwo)
            seasonYearEntry.insert(0, seasonYear)
            gameLeagueEntry.insert(0, leagueName)


# Update Game Listener********************************************************************************************
# This function is called when the user clicks the 'Update game' button. Once a game has been selected from the
# and has focus the user can edit the parameters and upon the click of teh update game button will commit those
# updates to the database.

def update_game_click():
    # collect user input
    gameMatchName = gameMatchNameEntry.get()
    gameDate = gameDateEntry.get()
    teamOne = teamOneEntry.get()
    teamTwo = teamTwoEntry.get()
    scoreOne = scoreOneEntry.get()
    scoreTwo = scoreTwoEntry.get()
    seasonYear = seasonYearEntry.get()
    leagueName = gameLeagueEntry.get()

    # check the fields are completed
    if len(gameMatchName) > 0:
        try:
            # query to update the field with the newly input data
            cur.execute(
                """UPDATE game SET match_name = ?, team_one = ?, team_two = ?, score_one = ?, score_two = ?, game_date = ?, season_year = ?, league_name = ? WHERE id = ?""",
                (gameMatchName, teamOne, teamTwo, scoreOne, scoreTwo, gameDate, seasonYear, leagueName, updateKey))
            # alert to illustrate the record has been added
            tkMessageBox.showinfo("Update", 'Record updated!')

            # The game update button should only appear once a element is
            # selected from seach this is completed through toggling the
            # state of the button to normal when it should be used and diasbled
            # when the button cannot be used.
            updateGameButton['state'] = 'disabled'
            addGameButton['state'] = 'normal'
            searchGameButton['state'] = 'normal'
            deleteGameButton['state'] = 'disabled'
        except sqlite3.Error as er:
            tkMessageBox.showinfo("Error Updating", er)
            updateGameButton['state'] = 'disabled'
            addGameButton['state'] = 'normal'
            searchGameButton['state'] = 'normal'
            deleteGameButton['state'] = 'disabled'

    else:
        tkMessageBox.showinfo("Update Failed", 'Cannot be empty!')

    # clear the input fields
    gameMatchNameEntry.delete(0, END)
    gameDateEntry.delete(0, END)
    teamOneEntry.delete(0, END)
    teamTwoEntry.delete(0, END)
    scoreOneEntry.delete(0, END)
    scoreTwoEntry.delete(0, END)
    seasonYearEntry.delete(0, END)
    gameLeagueEntry.delete(0, END)


# This function creates the treeview (table) and displays it to the user. There are two ways of creating a tree:
# 1. If it is a first time: create a treeview normally
# 2. If there is a tree already created: destroy previous tree and create a new one
def create_tree(cols, data):
    global tree  # Tell the method that you'll be using the global variable 'tree' here
    if tree != NoneType:  # If there's a tree view showing, destroy it and create the new one
        tree.destroy()  # Destroy the treeview

    tree = ttk.Treeview(columns=cols, show='headings')  # cols is gotten from the cursor
    tree.pack(expand=YES, fill=BOTH)

    for c in cols:  # Configure column headings
        tree.heading(c, text=c.title())  # Add the column names to the treeview
        tree.column(c, width=115, stretch=True)

    for item in data:  # Add data to the tree
        tree.insert('', 'end', values=item)

    ysb = ttk.Scrollbar(orient=VERTICAL, command=tree.yview)
    xsb = ttk.Scrollbar(orient=HORIZONTAL, command=tree.xview)
    tree['yscroll'] = ysb.set
    tree['xscroll'] = xsb.set

    # Places the treeview in row 14 stuck to the WEST
    tree.grid(row=14, column=0, columnspan=100, sticky=W)
    tree.bind("<Double-1>", onDoubleClick)  # Bind the double click function to this treeview


# GUI CODE STARTS*******************************************************************************************************
conn = sqlite3.connect('footballdb.sqlite')
cur = conn.cursor()
cur.execute('PRAGMA foreign_keys = ON;')
updateSection = 'league'  # Global variable so when table is double clicked, it knows to which Entries assign values to
tree = NoneType  # Treeview (Table) as global to destroy it and create it again when necessary
updateKey = ''  # Global variable to save the table primary key so it can be used to update the record

top = Tk()  # Top frame
top.minsize(width=1040, height=600)  # Set size
top.maxsize(width=1040, height=600)  # Set size
top.resizable(width=True, height=True)
top.title('Football')
top.configure(background='forest green')

# Top Title
searchLabel = Label(top, text='European Football Information Center', background='forest green')
searchLabel.config(font=("Symbol", 20))
searchLabel.grid(row=0, column=3, sticky=W, columnspan=2)
searchLabel.configure(background='forest green', foreground='white')

# Search League GUI Section*********************************************************************************************
Label(top, text='Leagues', background='forest green', foreground='white').grid(row=1, column=0, sticky=W)

Label(top, text='League Name:', background='forest green', foreground='white').grid(row=2, sticky=W)

searchLeagueEntry = Entry(top)
searchLeagueEntry.grid(row=2, column=1)
# searchLeagueEntry.configure(background='forest green')

addLeagueButton = Button(text='Add League', command=add_league_click)
addLeagueButton.grid(row=3, column=0, sticky=W + E + N + S, columnspan=2)
addLeagueButton.configure(background='forest green', foreground='white')
searchLeagueButton = Button(text='Search League', command=search_league_click)
searchLeagueButton.grid(row=4, column=0, sticky=W + E + N + S, columnspan=2)
deleteLeagueButton = Button(text='Delete League', state=DISABLED, command=delete_league_click)
deleteLeagueButton.grid(row=5, column=0, sticky=W + E + N + S, columnspan=2)
updateLeagueButton = Button(text='Update League', state=DISABLED, command=update_league_click)
updateLeagueButton.grid(row=6, column=0, sticky=W + E + N + S, columnspan=2)

# Search Match GUI Section**********************************************************************************************
Label(top, text='Matches', background='forest green', foreground='white').grid(row=7, column=0, sticky=W)

Label(top, text='Match Name:', background='forest green', foreground='white').grid(row=8, column=0, sticky=W)
matchNameEntry = Entry(top)
matchNameEntry.grid(row=8, column=1)

addMatchButton = Button(text='Add Match', command=add_match_click)
addMatchButton.grid(row=9, column=0, columnspan=2, sticky=W + E + N + S)
searchMatchButton = Button(text='Search Match', command=search_match_click)
searchMatchButton.grid(row=10, column=0, sticky=W + E + N + S, columnspan=2)
deleteMatchButton = Button(text='Delete Match', state=DISABLED, command=delete_match_click)
deleteMatchButton.grid(row=11, column=0, sticky=W + E + N + S, columnspan=2)
updateMatchButton = Button(text='Update Match', state=DISABLED, command=update_match_click)
updateMatchButton.grid(row=12, column=0, sticky=W + E + N + S, columnspan=2)

# Search Club GUI Section***********************************************************************************************
Label(top, text='Clubs', background='forest green', foreground='white').grid(row=1, column=2, sticky=W)

Label(top, text='Club ID:', background='forest green', foreground='white').grid(row=2, column=3, sticky=W)
clubIDEntry = Entry(top)
clubIDEntry.grid(row=2, column=4)

Label(top, text='Club Name:', background='forest green', foreground='white').grid(row=3, column=3, sticky=W)
clubNameEntry = Entry(top)
clubNameEntry.grid(row=3, column=4)

Label(top, text='Club Abbr:', background='forest green', foreground='white').grid(row=4, column=3, sticky=W)
clubAbbrEntry = Entry(top)
clubAbbrEntry.grid(row=4, column=4)

Label(top, text='League Name:', background='forest green', foreground='white').grid(row=5, column=3, sticky=W)
clubLeagueEntry = Entry(top)
clubLeagueEntry.grid(row=5, column=4)

addClubButton = Button(text='Add Club', command=add_club_click)
addClubButton.grid(row=7, column=3, columnspan=2, sticky=W + E + N + S)
searchClubButton = Button(text='Search Club', command=search_club_click)
searchClubButton.grid(row=8, column=3, sticky=W + E + N + S, columnspan=2)
deleteClubButton = Button(text='Delete Club', state=DISABLED, command=delete_club_click)
deleteClubButton.grid(row=9, column=3, sticky=W + E + N + S, columnspan=2)
updateClubButton = Button(text='Update Club', state=DISABLED, command=update_club_click)
updateClubButton.grid(row=10, column=3, sticky=W + E + N + S, columnspan=2)

# Search Game GUI Section***********************************************************************************************
Label(top, text='Games', background='forest green', foreground='white').grid(row=1, column=6, sticky=W)

Label(top, text='Match Name:', background='forest green', foreground='white').grid(row=2, column=7, sticky=W)
gameMatchNameEntry = Entry(top)
gameMatchNameEntry.grid(row=2, column=8)

Label(top, text='Game Date:', background='forest green', foreground='white').grid(row=3, column=7, sticky=W)
gameDateEntry = Entry(top)
gameDateEntry.grid(row=3, column=8)

Label(top, text='Team One:', background='forest green', foreground='white').grid(row=4, column=7, sticky=W)
teamOneEntry = Entry(top)
teamOneEntry.grid(row=4, column=8)

Label(top, text='Team Two:', background='forest green', foreground='white').grid(row=5, column=7, sticky=W)
teamTwoEntry = Entry(top)
teamTwoEntry.grid(row=5, column=8)

Label(top, text='Score One:', background='forest green', foreground='white').grid(row=6, column=7, sticky=W)
scoreOneEntry = Entry(top)
scoreOneEntry.grid(row=6, column=8)

Label(top, text='Score Two:', background='forest green', foreground='white').grid(row=7, column=7, sticky=W)
scoreTwoEntry = Entry(top)
scoreTwoEntry.grid(row=7, column=8)

Label(top, text='Season Year:', background='forest green', foreground='white').grid(row=8, column=7, sticky=W)
seasonYearEntry = Entry(top)
seasonYearEntry.grid(row=8, column=8)

Label(top, text='League Name:', background='forest green', foreground='white').grid(row=9, column=7, sticky=W)
gameLeagueEntry = Entry(top)
gameLeagueEntry.grid(row=9, column=8)

addGameButton = Button(text='Add Game', background='forest green', foreground='white', command=add_game_click)
addGameButton.grid(row=10, column=7, columnspan=2, sticky=W + E + N + S)
searchGameButton = Button(text='Search Game', command=search_game_click)
searchGameButton.grid(row=11, column=7, sticky=W + E + N + S, columnspan=2)
deleteGameButton = Button(text='Delete Game', background='forest green', foreground='white', state=DISABLED,
                          command=delete_game_click)
deleteGameButton.grid(row=12, column=7, sticky=W + E + N + S, columnspan=2)
updateGameButton = Button(text='Update Game', state=DISABLED, command=update_game_click)
updateGameButton.grid(row=13, column=7, sticky=W + E + N + S, columnspan=2)

top.mainloop()  # GUI Main Loop

# Close Connections
cur.close()
conn.commit()
conn.close()
