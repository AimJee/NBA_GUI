import pandas as pd
import requests
from bs4 import BeautifulSoup
import string
import time
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno
import numpy as np
import calendar
import datetime
import re
from tqdm import trange
from tkinter import scrolledtext
import threading 
import statsmodels.api as sm
import os


def Stats_Seasons():
    """
    This function is used to scratch data from a website.
    It then saves the result into a df and into a CSV file to avoid having
    to run this function every time
    First we ask the user if he wants to update the file with a yes_no
    """
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))
    relative_path = os.path.join(current_directory, 'CSV_files')
    # yes or no question
    answer = askyesno(title="Update Seasons list ?",
                      message="Do you want to update the seasons list ?")
    # We update ba scratching data
    if answer == True:
    
        attempts = 0
        while attempts<5:
            try:
                # url and read the dtata
                url = "https://www.basketball-reference.com/leagues/"
                df = pd.read_html(url, header=1)
                # only first table
                df = df[0]
                break
            except requests.exceptions.RequestException:
                attempts+=1
                time.sleep(2)
        df.to_csv(relative_path + "/seasons_list.csv", index=False)
        return df
    # Juste use what's already there
    else:
        df = pd.read_csv(relative_path + "/seasons_list.csv")
        return df

def Stats_Players():
    """
    This function is used to scratch data from a website.
    It then saves the result into a df and into a CSV file to avoid having
    to run this function every time
    First we ask the user if he wants to update the file with a yes_no   
    """  
    
    answer = askyesno(title="Update Players list ?",
                      message="Do you want to update the players list ? It may take 2 minutes.")
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))
    relative_path = os.path.join(current_directory, 'CSV_files')
    # If you want to update :
    if answer == True:
        
        list_players = []
        # url
        text = "https://www.basketball-reference.com/players/"
        i=0
        # Progress bar 
        progress_window = tk.Toplevel()
        progress_window.title("Updating player list...")
        progress_window.geometry("300x100")
        progress_bar = ttk.Progressbar(progress_window, orient="horizontal",
                                       length=200, mode="determinate")   
        progress_bar.pack(pady=20)
        
        # for every letter take each player's informations 
        for idx, letter in enumerate(list(string.ascii_lowercase)):
            
            # progressbar
            progress_bar["value"] = (idx/26)*100
            progress_bar.update()
            
            # url, wait and then try to get data while trying 5 times   
            url = text + letter + "/"
            attempts = 0
            
            time.sleep(2.5)
            # try 5 times
            while attempts<5:
                try:
                    # acess the data, find the table, then the rows
                    r = requests.get(url)
                    soup = BeautifulSoup(r.text, "html.parser")
                    table = soup.find("tbody")
                    rows = table.find_all("tr")
                    # loop in each rows to find the players
                    for row in rows:
                        cols = row.find_all("td")
                        # find the head and find the url of the player'stats
                        cols2 = row.find("th")
                        player = cols2.text.strip()
                        # find the html unique code of the player
                        player_url = cols2.find("a")["href"]
                        beginning = cols[0].text.strip()
                        end = cols[1].text.strip()
                        birthday = cols[5].text.strip()
                        list_players.append(
                            (i, player, beginning, end, birthday, player_url))
                        i+=1
                    # leave
                    break
                # retry
                except requests.exceptions.RequestException:
                    attempts+=1
                    time.sleep(2)
        
        # destroy progress window
        progress_window.destroy()
        
        # create the df
        df = pd.DataFrame(list_players, 
                          columns=[
                              "Id", "Name and Surname", "Beginning year", 
                              "Played until", "Birthday", "html"])
        # save the df into CSV to save time next times
        df.to_csv(relative_path + "/players_list.csv", index=False)
        
        return df
    
    # otherwise use previous list of players
    else:
        df = pd.read_csv(relative_path + "/players_list.csv")
        
        return df
   
def Stats_Teams():
    """ 
    This function is used to scratch data from a website.
    It then saves the result into a df and into a CSV file to avoid having
    to run this function every time
    First we ask the user if he wants to update the file with a yes_no 
    """
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))
    relative_path = os.path.join(current_directory, 'CSV_files')
    answer = askyesno(title="Update teams list ?",
                      message="Do you want to update the teams list ?")
    if answer == True:
        list_teams = []
        # url
        url = "https://www.basketball-reference.com/teams/"
        time.sleep(2)
        attempts = 0
        while attempts<5:
            try:
                # access data and find table
                r = requests.get(url)
                soup = BeautifulSoup(r.text, "html.parser")
                table = soup.find("tbody")
                rows = table.find_all("tr")
                for row in rows:
                    if row.get("class") and "full_table" in row["class"]:
                        actual_team = "Total"
                    else:
                        actual_team = "Partial"
                    cols = row.find_all("td")
                    cols2 = row.find("th")
                    Franchise = cols2.text.strip()
                    Lg = cols[0].text.strip()
                    From = cols[1].text.strip()
                    To = cols[2].text.strip()
                    Yrs = cols[3].text.strip()
                    G = cols[4].text.strip()
                    W = cols[5].text.strip()
                    L = cols[6].text.strip()
                    WL = cols[7].text.strip()
                    Playoffs = cols[8].text.strip()
                    Div = cols[9].text.strip()
                    Conf = cols[10].text.strip()
                    Champ = cols[11].text.strip()
                    list_teams.append(
                        (actual_team, Franchise, Lg, From, To, Yrs, G, W,
                         L, WL, Playoffs, Div, Conf, Champ))
                break
            except requests.exceptions.RequestException:
                attempts+=1
                time.sleep(2)
        df = pd.DataFrame(list_teams, columns=["Total or partial",
            "Franchise", "League", "From", "To", "Years", "G", "W", "L","WL",
            "Playoffs", "Div", "Conf", "Champ"])
        df.to_csv(relative_path + "/teams_list.csv", index=False)
        return df    
    else:
        df = pd.read_csv(relative_path + "/teams_list.csv", index=False)
        return df

def load_matches(Season: int, Debut_date: datetime, End_date: datetime):
    """
    This function is used to scratch data from a website.
    It then saves the result into a df and into a CSV file to avoid having
    to run this function every time
    We are finding the results and the matches of the NBA played between
    2 dates. The user also need to input the Season as matches played in 2022
    can be from 2 different seasons. Here we ask the user to input the 
    greater value of the years season. Meaning that the season 2021-2022 is 
    viewed as the season 2022 in our system.
    First we find the lists of all the games played in each months. These months
    are found via the functions months_between using the  input the user 
    provided. After having scratching all the months, we can go through
    each matchs to find the statistics of the individual match.
    As the website only allow 20 requests per minute, the loading can be slow
    Because of the time, the function create a progress window displaying
    some informations and a progress bar.
    After having scraping all the stats, the function rearranges them to match
    the style of the original CSV file. This function "updates" the CSV file
    "game.csv" by adding the matches scratched.
    Note that to allow the user to use the database while the function is
    running, the function uses threading. This is why the function scratching
    has been created
    """
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))
    relative_path = os.path.join(current_directory, 'CSV_files')
    start_time = time.time()
    # Progress window and text
    progress_window = tk.Toplevel()
    progress_window.title("Updating matches ...")
    progress_window.geometry("700x400")
    text_widget = scrolledtext.ScrolledText(progress_window)
    text_widget.place(x=50,y=20, width=600, height=300)
    # Progress bar
    progress_bar = ttk.Progressbar(progress_window, orient="horizontal",
                                   length=600, mode="determinate")
    progress_bar.place(x=50, y=325, width=600, height=30)
    
    # Find the months between 2 dates, and use set to drop duplicates
    def months_between(start_date, end_date):
        start_month = start_date.month
        end_month = end_date.month
        # We need to sort the months in a chronological order
        if start_month <= end_month:
            months = range(start_month, end_month + 1)
        else:
                months = list(range(start_month, 13)) + list(range(1, end_month + 1))
        return [datetime.date(1900, month, 1).strftime('%B') for month in months]

    def scratching():
        Months = months_between(Debut_date, End_date)
        
        # Teams and their abrv for the URL 
        Teams_tuple = [
                ("ATL", "Atlanta Hawks"), ("BRK", "Brooklyn Nets"), 
                ("BOS", "Boston Celtics"), ("CHO", "Charlotte Hornets"), 
                ("CHI", "Chicago Bulls"), ("CLE", "Cleveland Cavaliers"),
                ("DAL", "Dallas Mavericks"), ("DEN", "Denver Nuggets"), 
                ("DET", "Detroit Pistons"), ("GSW", "Golden State Warriors"), 
                ("HOU", "Houston Rockets"), ("IND", "Indiana Pacers"), 
                ("LAC", "Los Angeles Clippers"), ("LAL", "Los Angeles Lakers"),
                ("MEM", "Memphis Grizzlies"), ("MIA", "Miami Heat"),
                ("MIL", "Milwaukee Bucks"), ("MIN", "Minnesota Timberwolves"),
                ("NOP", "New Orleans Pelicans"), ("NYK", "New York Knicks"),
                ("OKC", "Oklahoma City Thunder"), ("ORL", "Orlando Magic"),
                ("PHI", "Philadelphia 76ers"), ("PHO", "Phoenix Suns"),
                ("POR", "Portland Trail Blazers"), ("SAC", "Sacramento Kings"), 
                ("SAS", "San Antonio Spurs"), ("TOR", "Toronto Raptors"), 
                ("UTA", "Utah Jazz"), ("WAS", "Washington Wizards")]
    
        # Create a dictionnary
        Teams = []
        abrv_team = []
        for i in range(len(Teams_tuple)):
            abrv_team.append(Teams_tuple[i][0])
            Teams.append(Teams_tuple[i][1])
        # Dictionnary to swap from their team name to their abr
        dict_team = dict(zip(Teams, abrv_team)) 
            
        # Two steps now. First we need to find all the matches played each months
        # Then we can scratch each games 
        
        # Empty list
        data = []
        failed_urls = []
        text_widget.insert(tk.END, "\nLoading the monthly matches...\n")
        
        # For every months go get the url
        for i in Months:
            text = "NBA_" + str(Season) + "_games-" + i.lower() + ".html"
            url = "https://www.basketball-reference.com/leagues/" + text
            # Sleep to respect the 20 requests by minute
            time.sleep(2.4)
            attempts = 0
            while attempts < 5:  
                try: 
                    # get the url
                    r = requests.get(url)
                    # Sucess
                    text_widget.insert(tk.END, i.lower() + " is a success.\n")
                    soup = BeautifulSoup(r.text, "html.parser")
                    # find the <tbody> and then cut into rows
                    table = soup.find('tbody')
                    rows = table.find_all('tr')
                    # For every row in the table we loop
                    for row in rows:
                        # pure text, cut into columns
                        cols = row.find_all('td')
                        # the heads
                        cols2 = row.find_all('th')
                        away_team = cols[1].text.strip()
                        home_team = cols[3].text.strip()
                        date = cols2[0].text.strip()
                        date = date.split(", ")
                        year = int(date[2])
                        month = date[1].split(" ")[0]
                        month = int(list(calendar.month_abbr).index(month))
                        day = int(date[1].split(" ")[1])
                        # No need of passed data
                        # We need the match of tomorrow to predict but not after
                        if datetime.datetime(year, month, day) > datetime.timedelta(days=1) + End_date:
                            break
                        # Month is in string format on the webstite -> into integer
                        month = '%02d' % month
                        # day as to be 02 and not just 2
                        day = '%02d' % day
                        # Add the abrv of the home_team (for url purpose)
                        abrv = str(dict_team[home_team])
                        # add into the data list
                        data.append((year, month, day, away_team, home_team, abrv))
                    # dont loop if it works
                    break
                except requests.exceptions.RequestException:
                    attempts+=1
                    text_widget.insert(tk.END, url + " is a failure.\n Retry attempt: "+ str(attempts) +"\n")
                    time.sleep(2.4)
                    failed_urls.append(url)
            else:
                text_widget.insert(tk.END, url + " reached the maximum number of attempts.\n")
                data.append(())
                
        text_widget.insert(tk.END, "\nMonthly matches finished !\n")
        
        # Now we have the list of all matches !
        # Now we use this information to find the url of each match and we loop
        
        # Empty lists
        empty_home = []
        empty_away = []
        failed_urls2 = []
        text_widget.insert(tk.END, "\nLoading the stats of each matches...\n")
        
    
        # Progress maximum
        progress_bar["maximum"]= len(data)
       
        for j in trange(len(data), unit="items", unit_scale=True):
            # The future matches doesnt have to be looked up
            if datetime.datetime(
                    int(data[j][0]), int(data[j][1]), int(data[j][2])) <= End_date:
                # respect the 20 requests by minute
                time.sleep(2.4)
                text = str(data[j][0]) + data[j][1] + data[j][2] + "0" + data[j][5] +".html"
                url = "https://www.basketball-reference.com/boxscores/" + text
                # try 5 times
                attempts = 0
                while attempts<5 :
                    try:
                       # get the matches url
                        r = requests.get(url)
                        soup = BeautifulSoup(r.text, "html.parser")
                        # Need to find the table of the game and not of q1,..., overtime
                        regex = re.compile(r".*game.*")
                        # id has to contain game
                        tables = soup.find_all("table", {"id":regex})
                        # we need only the <tfoot> as it's the aggregate of the team
                        # Loop to put the tfoot in a list
                        tfoot_data_list = []
                        for table in tables:
                            # looking for the tfoot in tables
                            tfoot = table.find("tfoot")
                            if tfoot:
                                tfoot_data = [td.text for td in tfoot.find_all("td")] 
                                tfoot_data_list.append(tfoot_data)
                        cols_home = tfoot_data_list[2]
                        cols_away = tfoot_data_list[0]
                        empty2_home = []
                        empty2_away = []
                        
                        # Extract each stats for each team
                        for i in range(len(cols_home)):
                            empty2_home.append(cols_home[i].strip())
                        for i in range(len(cols_away)):
                            empty2_away.append(cols_away[i].strip())
                        empty_home.append(empty2_home)
                        empty_away.append(empty2_away)
                       
                        # progress bar update
                        progress_bar["value"] = j
                        progress_window.update()
                        break
                    except:
                        attempts+=1
                        text_widget.insert(tk.END, "\n" + url + "\n is a failure\nRetry attempts: " + str(attempts))
                        failed_urls2.append(url)
                        time.sleep(2.4)
                        continue
                
        progress_bar["value"] = len(data)+1
        progress_window.update()
        
        total_time = time.time() - start_time
        text_widget.insert(tk.END, f'Total time: {total_time:.1f} seconds')
        text_widget.insert(tk.END, "\nStats matches finished !\n")
        

        
        # We need to rearrange the data from before into the file we know !
        #####################################################################
    
        text_widget.insert(tk.END, "We are putting everything in the right order, a second please...")
        
        # Load original data to keep the same parameters 
        df_ori = pd.read_csv(relative_path + "/game.csv")
        df_ori = df_ori.dropna(subset=["season_id"])
        new_data = data
        
        # Dict to go from name to id and abbreviation
        team_id_dict = {}
        for i in df_ori["team_name_home"].unique():
            team_id_dict[i] = (df_ori[df_ori["team_name_home"]==i].iloc[0, 1],
                               df_ori[df_ori["team_name_home"]==i].iloc[0, 2])
        # Season id
        season_id = len(new_data)*[Season-1]
        
        # Find the id and the abr with the name of the team
        team_name_home = []
        team_name_away = []
        team_id_home = []
        team_abbreviation_home = []
        team_id_away = []
        team_abbreviation_away = []
        game_id = []
        game_date = []
        
        
        # To keep a trace
        df_cut = df_ori.copy()
        # Drop the data after the End_date
        # This is useful to get rid of the duplicates and also if 
        # we want to try the database "back in time" 
        df_cut["game_date"] = pd.to_datetime(df_cut["game_date"], 
                                             format="%d/%m/%Y")   
        df_cut = df_cut[df_cut["game_date"] < Debut_date]
        # Get the index of old df to continue in new df
        index_Organized = []
        index_max = max(df_cut.index)
        
        # Continued index
        for i in range(len(new_data)):
            index_Organized.append(index_max+i+1)
        
        for i in range(len(new_data)):
            # Find the name of the Home team and their team_id
            temp = new_data[i][4]
            team_name_home.append(temp)
            team_id_home.append(team_id_dict[temp][0])
            # Find the name of the Away team and their team_id
            temp = new_data[i][3]
            team_name_away.append(temp)
            team_id_away.append(team_id_dict[temp][0])
            # Find the abbreviation of the home team
            temp = new_data[i][4]
            team_abbreviation_home.append(team_id_dict[temp][1])
            # Find the abbreviation of the away team
            temp = new_data[i][3]
            team_abbreviation_away.append(team_id_dict[temp][1])
            # Create the game id
            temp = int(str(2)+str(new_data[i][0])[2:]+"00000")
            game_id.append(temp+i+1)
            # Create the game date
            temp = [int(new_data[i][0]), int(new_data[i][1]), 
                    int(new_data[i][2])]
            game_date.append(datetime.datetime(temp[0], temp[1], temp[2])) 
            
        # Lazy but works
        minutes = []
        fgm_home = []
        fga_home = []
        fg_pct_home = []
        fg3m_home = []
        fg3a_home = []
        fg3_pct_home = []
        fta_home = []
        ftm_home = []
        ft_pct_home = []
        oreb_home = []
        dreb_home = []
        reb_home = []
        ast_home = []
        stl_home = []
        blk_home = []
        tov_home = []
        pf_home = []
        pts_home = []
        
        # We do in each matches to find the data from each stats
        for i in range(len(empty_home)):
            minutes.append(empty_home[i][0])
            fgm_home.append(empty_home[i][1])
            fga_home.append(empty_home[i][2])   
            fg_pct_home.append(empty_home[i][3])   
            fg3m_home.append(empty_home[i][4])
            fg3a_home.append(empty_home[i][5])
            fg3_pct_home.append(empty_home[i][6])
            fta_home.append(empty_home[i][7])
            ftm_home.append(empty_home[i][8])
            ft_pct_home.append(empty_home[i][9])
            oreb_home.append(empty_home[i][10])
            dreb_home.append(empty_home[i][11])
            reb_home.append(empty_home[i][12])
            ast_home.append(empty_home[i][13])
            stl_home.append(empty_home[i][14])
            blk_home.append(empty_home[i][15])
            tov_home.append(empty_home[i][16])
            pf_home.append(empty_home[i][17])
            pts_home.append(int(empty_home[i][18]))
            
        # Lazy but works
        min_away = []
        fgm_away = []
        fga_away = []
        fg_pct_away = []
        fg3m_away = []
        fg3a_away = []
        fg3_pct_away = []
        fta_away = []
        ftm_away = []   
        ft_pct_away = []
        oreb_away = []
        dreb_away = []
        reb_away = []
        ast_away = []
        stl_away = []
        blk_away = []
        tov_away = []
        pf_away = []
        pts_away = []
        
        # Same for away teams
        for i in range(len(empty_away)):
            min_away.append(empty_away[i][0])
            fgm_away.append(empty_away[i][1])
            fga_away.append(empty_away[i][2])   
            fg_pct_away.append(empty_away[i][3])   
            fg3m_away.append(empty_away[i][4])
            fg3a_away.append(empty_away[i][5])
            fg3_pct_away.append(empty_away[i][6])
            fta_away.append(empty_away[i][7])
            ftm_away.append(empty_away[i][8])
            ft_pct_away.append(empty_away[i][9])
            oreb_away.append(empty_away[i][10])
            dreb_away.append(empty_away[i][11])
            reb_away.append(empty_away[i][12])
            ast_away.append(empty_away[i][13])
            stl_away.append(empty_away[i][14])
            blk_away.append(empty_away[i][15])
            tov_away.append(empty_away[i][16])
            pf_away.append(empty_away[i][17])
            pts_away.append(int(empty_away[i][18]))
            
        # Who won ? 
        wl_home = []
        wl_away = []
        for i in range(len(empty_home)):
            if pts_home[i] > pts_away[i]:
                wl_home.append("W")
                wl_away.append("L")
            else:
                wl_home.append("L")
                wl_away.append("W")
        
        # Rechange the type of data
        df_cut["game_date"] = df_cut["game_date"].dt.strftime('%d/%m/%Y')


        Organized = pd.DataFrame.from_dict(
            {"index_organized": np.int32(index_Organized),
             "season_id": np.int32(season_id),
             "team_id_home": np.int32(team_id_home),
             "team_abbreviation_home": team_abbreviation_home,
             "team_name_home": team_name_home,
             "game_id": np.int32(game_id),
             "game_date": pd.to_datetime(pd.Series(game_date)).dt.strftime('%d/%m/%Y'),
             "wl_home": wl_home,
             "min": np.longlong(minutes),
             "fgm_home": np.longlong(fgm_home),
             "fga_home": np.longlong(fga_home),
             "fg_pct_home": np.float64(fg_pct_home),
             "fg3m_home": np.longlong(fg3m_home),
             "fg3a_home": np.longlong(fg3a_home),
             "fg3_pct_home": np.float64(fg3_pct_home),
             "ftm_home": np.longlong(ftm_home),
             "fta_home": np.longlong(fta_home),
             "ft_pct_home": np.float64(ft_pct_home),
             "oreb_home": np.longlong(oreb_home),
             "dreb_home": np.longlong(dreb_home),
             "reb_home": np.longlong(reb_home),
             "ast_home": np.longlong(ast_home),
             "stl_home": np.longlong(stl_home),
             "blk_home": np.longlong(blk_home),
             "tov_home": np.longlong(tov_home),
             "pf_home": np.longlong(pf_home),
             "pts_home": np.longlong(pts_home),
             "team_id_away": np.int32(team_id_away),
             "team_abbreviation_away": team_abbreviation_away,
             "team_name_away": team_name_away,
             "wl_away": wl_away,
             "fgm_away": np.longlong(fgm_away),
             "fga_away": np.longlong(fga_away),
             "fg_pct_away": np.float64(fg_pct_away),
             "fg3m_away": np.longlong(fg3m_away),
             "fg3a_away": np.longlong(fg3a_away),
             "fg3_pct_away": np.float64(fg3_pct_away),
             "ftm_away": np.longlong(ftm_away),
             "fta_away": np.longlong(fta_away),
             "ft_pct_away": np.float64(ft_pct_away),
             "oreb_away": np.longlong(oreb_away),
             "dreb_away": np.longlong(dreb_away),
             "reb_away": np.longlong(reb_away),
             "ast_away": np.longlong(ast_away),
             "stl_away": np.longlong(stl_away),
             "blk_away": np.longlong(blk_away),
             "tov_away": np.longlong(tov_away),
             "pf_away": np.longlong(pf_away),
             "pts_away": np.longlong(pts_away)}, orient="index").T
        
        Organized = Organized.astype(
            { "index_organized": int }).set_index("index_organized")
        
        Organized_complete = pd.concat([df_cut, Organized])
        Organized_complete.to_csv(relative_path + '/game.csv', index=False)
        
        
        text_widget.insert(tk.END, "\nNew file uploaded in CSVs/game.csv !")
        text_widget.insert(tk.END, "\nThe file is ready !")
        text_widget.insert(tk.END, "\nPress Close to quit")
        Button = tk.Button(progress_window, text="Close", 
                           command=lambda:progress_window.destroy())
        Button.place(x=330, y=360, width=40, height=35)
        
        
        
    # threading to avoid laggy window
    try:
        thread = threading.Thread(target=scratching)
        thread.start()
    except:
        print("Something went wrong, please retry...")
            
def Data_predictions(Entry_season, Length_long=20, Length_short=3):
    """
    Entry season is the season we want to predict the outcomes.
    Length_long is the len of the moving average used for some parameters
    Length_short is the len of the moving average used for some parameters
    This function is used to create the data used for the regressions.
    First we only have the matches on a matches POV, meaning that we have
    the lists of all matches and its datas/statistics but we need to calculate
    the moving averages of each team. So we need to work around the data 
    to display it in the format we need. 
    First we are creating 2 dataframes from the original one, the first one
    is the stats of the away teams, the second the stats of the home team
    Then they are merged together. So of the orginal dataframe have 20 matches
    the away df would have also 20 matches but only showing the stats of the 
    away teame. Same idea for the df_home. In the end the merged df (df_all)
    is twice as long (40 games in this case). 
    After creating df_all, we loop through each team to find the Moving average
    of each team at a certain point in time. If the Mavs played 27 games,
    we find the moving average of the games 8 to 27.
    If we need to predict the output of away team game 28, we need to find
    the moving average of away team game 27. Same idea applies to home team.
    The second loop is doing that task, it finds the MAs of the previous match
    find their difference and return 5 df.
    The first one is the complete df of the difference between the MA, so it
    includes nan data. The second one is the complete df of the result.
    3rd and 4th dfs are copies of the 1st and 2nd ones but dont include the
    nan data so it's usable right away to predict. The result_vector also 
    dropped the result for which we had nan data. Finally the 5th df is the 
    Matches_list, it's the df_all. It's useful to find the odds later on
    """
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))
    relative_path = os.path.join(current_directory, 'CSV_files')

    # read file and only take the season we need
    df_games = pd.read_csv(relative_path + "/game.csv")
    df_games = df_games[df_games["season_id"] == Entry_season-1]
    
    # we drop the linearly dependent columns : fg, fg3, ft, reb, pts
    df_games = df_games.drop(
        ["fga_away","fgm_away", "fga_home", "fgm_home", "fg3a_away", "fg3a_home", 
         "fg3m_away", "fg3m_home","fta_away", "ftm_away", "fta_home", "ftm_home", 
         "reb_away", "reb_home", "pts_away", "pts_home", "min"],
        axis=1)
    
    # away df
    df_away = df_games[
        ["season_id", "game_id", "game_date", 'team_id_away',
         'team_abbreviation_away', 'team_name_away', 'wl_away',
         'fg_pct_away', 'fg3_pct_away', 'ft_pct_away',
         'oreb_away', 'dreb_away', 'stl_away', 'tov_away',
         'ast_away',"pf_away","blk_away"
         ]].copy()
    
    # home df
    df_home = df_games[
        ["season_id", "game_id", "game_date", 'team_id_home',
         'team_abbreviation_home', 'team_name_home', 'wl_home',
         'fg_pct_home', 'fg3_pct_home', 'ft_pct_home',
         'oreb_home', 'dreb_home', 'stl_home', 'tov_home',
         'ast_home',"pf_home","blk_home"
         ]].copy()
    
    # adding information of the team being home or away
    df_away["home_team"] = np.zeros(len(df_away))
    df_home["home_team"] = np.ones(len(df_home))
    
    # global new names as the fact of being away or home is inside "home" col.
    cols_name = ["season_id", "game_id", "game_date", "team_id",
                 "team_abbreviation", "team_name", "wl", "fg_pct", "fg3_pct", 
                 "ft_pct", "oreb", "dreb",
                 "stl", "tov", "ast", "pf", "blk", "home_team"]
    df_away.columns = cols_name
    df_home.columns = cols_name
    
    # new df where we have all the matches from a team perspective
    df_all = pd.concat([df_away, df_home])
    # from string to 1 and 0
    df_all["wl"] = df_all["wl"].replace(["W", "L"], [1, 0])
    # list of team's name
    team_list = df_all["team_name"].unique()
    
    # loop through each team to get their Moving average
    MA_dict = {}
    Matches_list = pd.DataFrame()
    cols_ma_long = ["fg_pct", "fg3_pct", "ft_pct", "oreb", 
                    "dreb", "stl", "tov", "ast", "pf", "blk"]
    cols_ma_short = ["home_team"]
    
    for i in team_list:
        # temp df
        temp_df = df_all[df_all["team_name"] == i]
        temp_df = temp_df.sort_values(by="game_id")
        # column of % of win looses and column of matches played
        temp_df.insert(0, "match_num", range(1, 1 + len(temp_df)))
        temp_df.insert(len(temp_df.columns), "wl_pct", 
                       temp_df["wl"].cumsum()/temp_df["match_num"])
        
        temp_df = temp_df.drop("wl", axis=1)
        # MA of two length
        temp = temp_df[cols_ma_long].rolling(Length_long).mean()
        temp = pd.merge(temp, temp_df[cols_ma_short].rolling(Length_short).mean(),
                        left_index=True, right_index=True)
        
        # merge the temp_df execpt what we used + the MA
        MA_dict[i] = pd.merge(
            temp_df.loc[:, ~temp_df.columns.isin(cols_ma_long+cols_ma_short)], temp,
            left_index=True, right_index=True)
        MA_dict[i] = pd.merge(
            temp_df["home_team"], MA_dict[i], left_index=True, right_index=True)
        Matches_list = pd.concat((Matches_list, temp_df[[
            "match_num", "game_id", "game_date", "team_name", "home_team"]]))
    
    # Sort by game_id and then by home_x
    Matches_list = Matches_list.sort_values(by=["game_id", "home_team"])
    # Predict
    Predictions_data = pd.DataFrame(
        columns=cols_ma_long+cols_ma_short)

    for i in range(0, len(Matches_list), 2):
        # condition for predicting, we need Lenght long matches
        cond1 = Matches_list["match_num"].iloc[i] > Length_long
        cond2 = Matches_list["match_num"].iloc[i+1] > Length_long
    
        if cond1 == True and cond2 == True:
            # find the MA of the previous match for the match incoming
            # You need the MA of the 20th match to predict match 21
            temp = MA_dict[Matches_list["team_name"].iloc[i]]
            # quick fix, cant find why it happens
            temp['home_team'] = temp['home_team_y']
            temp = temp.drop(["home_team_x","home_team_y"], axis=1)
            temp = temp[temp["match_num"] == Matches_list["match_num"].iloc[i]-1]
            temp = temp.iloc[:, 7:]
            temp.index = [Matches_list.index[i]]
            
            temp1 = MA_dict[Matches_list["team_name"].iloc[i+1]]
            # quick fix, cant find why it happens
            temp1['home_team'] = temp1['home_team_y']
            temp1 = temp1.drop(["home_team_x","home_team_y"], axis=1)
            temp1 = temp1[temp1["match_num"] == Matches_list["match_num"].iloc[i+1]-1]
            temp1 = temp1.iloc[:, 7:]
            temp1.index = [Matches_list.index[i+1]]
            # find the delta between the MA of each team (home-away)
            temp2 = temp1 - temp
            Predictions_data = pd.concat((Predictions_data, temp2))
            
        else:
            # add empty lines to be sure of the size
            Predictions_data = pd.concat(
                (Predictions_data, pd.DataFrame
                 (columns=Predictions_data.columns, index=[Matches_list.index[i]])))
    
    # Output is the data used to predict
    Predictions_data = sm.add_constant(Predictions_data.sort_index())
    # Out is the results
    Result_vector = df_home["wl"].replace(["W","L"], [1,0]).sort_index()
    # Index removed when dropping nan 
    removed = Predictions_data.index.difference(Predictions_data.dropna().index)
    # Output is the data used to predict cleared
    Predictions_data_cleared = Predictions_data.dropna()
    # Output is the results cleared
    Result_vector_cleared = Result_vector.drop(removed)
    
    return Predictions_data, Result_vector, Predictions_data_cleared, Result_vector_cleared, Matches_list
       
def Predict_df(Year_predicted, Long=10, Short=5, Upper_B=0.5, Lower_B=0.5): 
    """
    This function predicts the outcomes of the matches of the season 
    Year_predicted-1-Year_predicted (2022-2023 for ex)
    Long and short are len of the MA, Upper and Lower are bounds for rounding
    after the predictions have been made.
    This function simply creates predictions based on the last 3 seasons
    The predictions are then put into a df. To allow a better readibility
    some informations are added. Also the column "together" is a column used
    to give predictions based on the result of the 3 years.
    """
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))
    relative_path = os.path.join(current_directory, 'CSV_files')
    answer = askyesno(title="Predictions?",
                      message="Do you want to predict the outcomes ? It could take up to 1 min")

    # If you want to update :
    if answer == True:
        # Cols name
        Cols_name = []
        # Predictions based on 3 individual years
        df = pd.DataFrame()
        # Data of predicted year
        Data_to_use, y_result, Matches = get_year_data(Year_predicted, Long, Short)    
        
        # Find parameters of last 3 years individually
        for i in range(int(Year_predicted)-3, int(Year_predicted), 1):
            # Data to get and regress
            x, y, data = get_year_data(i, Long, Short)
            Regr_result = sm.Logit(y, x).fit(cov_type="HC3")
            # Only predicts if data is not nan
            Predicts = Regr_result.predict(Matches[0])
            Cols_name.append(i)
            # Limits
            Upper = Upper_B
            Lower = Lower_B
            # Round based on the Bounds
            Predicts[(Predicts<Lower)] = 0
            Predicts[(Predicts>Upper)] = 1
            Predicts[((Predicts<=Upper) & (Predicts>=Lower))] = np.nan
            df = pd.concat([df, Predicts], axis=1)
    
        # into a df
        df.columns = Cols_name
        df.index = Matches[0].index
        
        # add more information
        df_comp = pd.read_csv(relative_path + "/game.csv")
        df_comp = df_comp[df_comp["season_id"]==Year_predicted-1][
            ["team_abbreviation_home", "team_abbreviation_away", "game_date"]]
        df = pd.concat([df_comp, df], axis=1).reset_index()
        
        df.columns = ["Index", "Home", "Away", "Game Date"] + Cols_name
        # row counts
        df["count1"] = (df[Cols_name] == 1).sum(axis=1)
        df["count0"] = (df[Cols_name] == 0).sum(axis=1)
        # comparaison between the bets 
        df["together"] = np.where(
            (df["count1"]>0) & (df["count0"]==0), 1, 
            np.where((df["count0"]>0) & (df["count1"]==0), 0, 
                     np.nan))
        df = df.drop(["count1", "count0"], axis=1)
        
        df = df.replace([1, 0, np.nan], ["Home", "Away", "/"])
        df.to_csv(relative_path + "/predictions.csv")
    
    return df

def get_year_data(year, Long, Short):
    """ 
    This function is used to facilitate the access to data while doing
    regressions and predictions
    Function to get the data for a particular year
    """
    data = Data_predictions(year, Long, Short)
    x = np.asarray(data[2], dtype=float)
    y = np.asarray(data[3])
    return x, y, data
