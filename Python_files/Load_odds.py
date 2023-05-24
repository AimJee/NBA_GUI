import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
import os

current_directory = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))
relative_path = os.path.join(current_directory, 'CSV_files')

def load_odds():
    """
    We are scratching data to get the odds of the matches
    CARE !!!!!
    You have to manually change in the CSV file the Neutral grounds of some matches.
    """
    # Team name
    original_array = np.array(
        ['Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets',
         'Chicago Bulls','Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets', 
         'Detroit Pistons', 'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers',
         'Los Angeles Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies','Miami Heat',
         'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans', 
         'New York Knicks','Oklahoma City Thunder', 'Orlando Magic', 
         'Philadelphia 76ers', 'Phoenix Suns','Portland Trail Blazers',
         'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors', 'Utah Jazz', 
         'Washington Wizards'])
    
    # Changing the team name to match the url style
    new_array = np.empty_like(original_array)
    for i in range(len(original_array)):
        new_array[i] = original_array[i].replace(' ', '-').lower()
    
    # Empty list and count parameter
    all_data = []
    i = 0
    
    # We scrape the data of a betting website to get the old odds
    # Would prefer something else but API seems all to be too expensive for an
    # Univerity project.
    
    for team in new_array:
        i += 1
        print(team)
        # Acess the url of each team
        url = 'https://www.teamrankings.com/nba/team/' + team
        r = requests.get(url)
        # Beautiful soup to get the HTML code of the page
        soup = BeautifulSoup(r.text, 'html.parser')
       # We looking for tables in the code (<table>)
        tables = soup.find_all('table')
        
        # Get the second table as the first one in the head table
        table = tables[1]
        
        # Get all rows in the table except for the header row
        rows = table.find_all('tr')[1:]
        
        # Create an empty list to store the data
        data = []
        
        # Loop through each row and extract the data
        for row in rows:
            # Only the matches from regular season
            if len(data) < 82:
                # To retrieve the data with the other dataframes
                # we add the game_num and the team_name
                # with the date it'll be easy to cross the dfs
                game_num = 1 + len(data) 
                team_name = original_array[i-1]
                # Get all the columns in the row
                cols = row.find_all('td')
                # Extract the data from each column
                date = cols[0].text.strip()
                opponent = cols[1].text.strip()
                score = cols[2].text.strip()
                location = cols[3].text.strip()
                record = cols[4].text.strip()
                home_record = cols[5].text.strip()
                spread = cols[6].text.strip()
                over_under = cols[7].text.strip()
                # str into float
                money_line = float(cols[8].text.strip()) 
                # Money line into European odds
                if money_line > 0:
                    money_line = (money_line/100) + 1
                else:
                    money_line = (100/-money_line) + 1
                # Append the data of the row team
                data.append(
                    (game_num, team_name, date, opponent, score, location,
                     record, home_record, spread, over_under, money_line))
        # Append the data of every teams
        all_data.extend(data)
        # Dataframe
    df = pd.DataFrame(
        all_data, columns=[
            'Match_num','Team_name','Date', 'Opponent','Score', 'Location', 
            'Record', 'Home Record', 'Spread', 'Over/Under', 'Money Line'])
    df.to_csv(relative_path + "/odds.csv")

    return df
