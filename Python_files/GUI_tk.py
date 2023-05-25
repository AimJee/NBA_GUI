import tkinter as tk
from tkinter import ttk
from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import GUI_data
import os


def GUI():
    """
    Here we are crating the Graphical User Interface
    We are fixing a certain fixed size of our interface, it'll be 700x700
    This is easier to create a simple GUI
    We are creating a window on which we place Pages
    These Pages will appear thanks to the function show_frame
    We also add Titles, Labels and Buttons to create an interactive GUI
    In the end this file is quite messy as we are adding many informations
    on many pages. It could have been done more cleanly if I was
    more advanced with the classes and Tkinter in geneal
    """
    
    #%% Constants
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))
    relative_path = os.path.join(current_directory, 'CSV_files')
    
    width_700 = 700
    height_700 = 700
    heigth_500 = 500
    # Create root
    window = tk.Tk()
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)
    # Title
    window.title("NBA Database / Advanced Programming / by Matthieu Gisler")
    # Fix size
    window.geometry("700x700")
    window.minsize(height_700, width_700)
    window.maxsize(height_700, width_700)
    
    # All pages needed to be created 
    StartPage = tk.Frame(window, height=height_700, width=width_700)
    Stats01 = tk.Frame(window, height=height_700, width=width_700)
    Stats01a = tk.Frame(window, height=height_700, width=width_700)
    Stats01b = tk.Frame(window, height=height_700, width=width_700)
    Stats01b2 = tk.Frame(window, height=height_700, width=width_700)
    Stats01c = tk.Frame(window, height=height_700, width=width_700)
    Bets01 = tk.Frame(window, height=height_700, width=width_700)
    Bets01b = tk.Frame(window, height=height_700, width=width_700)
        
    # List of the pages
    L_frames = [StartPage, Stats01, Stats01a, Stats01b, Stats01c, Bets01, 
                Stats01b2, Bets01b]
    # Frames into the root
    for i in L_frames:
        i.grid(row=0, column=0, sticky='nsew')
    
#%% Functions

    def show_frame(frame):
        """
        Function to show a frame / will be used in
        the buttons
        """
        frame.tkraise()
    

    def my_search(df, entry, tree):
        """
        Search function has 3 parameters one is the dataframe it needs to use
        , the second is the entry used to search and the 3rd is the tree it
        needs to be linked to
        """
        
        # find the keyword
        keyword = entry.get()
        # if no entry then returns complete tree
        if keyword=="":
            tree.delete(*tree.get_children())
            for index, row in df.iterrows():
                tree.insert("", "end", values=row.tolist())
            return
        # if there is something in "keyword" we search
        # clean existing treeview as we use many times the function
        for row in tree.get_children():
            tree.delete(row)
        # search through the df
        for index, row in df.iterrows():
            if keyword.lower() in str(row).lower():
                tree.insert("", "end", values=row.tolist())
    
    
    def my_stats_player(entry):
        """
        Search the stats of a player using entry as parameter
        Then we will acess a website and scrap its data on the player
        Then we update the tree object and finally show the results
        """
        
        data = []
        keyword = entry.get()
        # find the html and the data into list
        text = html_df.iloc[int(keyword)]
        url = "https://www.basketball-reference.com" + text
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"id" : "per_game"})
        rows = table.find_all("tr")
        # go through each row to get the data
        for row in rows:
            data2 = []
            cols2 = row.find("th")
            cols = row.find_all("td")
           
            if cols2 is not None:
                data2.append(cols2.text.strip())
            for col in cols:
                try:
                    data2.append(col.text.strip())
                except AttributeError:
                    data2.append("")
           
            data.append(data2)
        # Create a df
        df = pd.DataFrame(data, 
                          columns=["Season", "Age", "Team", "Lg", "Pos", "G",
                                   "GS", "MP", "FG", "FGA", "FG%", "3P",
                                   "3PA", "3P%", "2P", "2PA", "2P%", "eFG%",
                                   "FT", "FTA", "FT%", "ORB", "DREB", "TRB",
                                   "AST", "STL", "BLK", "TOV", "PF","PTS"])
        # Drop useless stuff
        df = df.drop(0)
        # Clean the treeview object
        tree_player.delete(*tree_player.get_children())
        # Give the heads a name
        tree_player["columns"] = list(df.columns)
        # Hide empty 1st column
        tree_player["show"] = 'headings'
        # create the columns and the values to show      
        for col in tree_player["columns"]:
            tree_player.column(col, width=50, stretch=False)
            tree_player.heading(col, text=col)
        # put data into the treeview object
        for i, row in df.iterrows():
            tree_player.insert("", "end", text=i, values=list(row))
            
        # Scrollbar
        scrollbar_x_tree_player = ttk.Scrollbar(
            Sub_Frame6, orient="horizontal", command=tree_player.xview)
        tree_player.configure(xscrollcommand=scrollbar_x_tree_player.set)
        scrollbar_x_tree_player.place(x=31, y=320, width=639)
        # Title
        Title_Stats01a6 = tk.Label(
            Stats01b2, text=df_players["Name and Surname"].iloc[int(keyword)],
            font=("Verdana", 20, "bold"))
        Title_Stats01a6.place(x=0, y=50, width=width_700, height=90)
        
        # Show the page
        Stats01b2.tkraise()
        
    def my_predictions_page(Entry_season, tree_bets):
        """
        We are updating the tree_bets to show the predictions on the matches
        First we find the dataframe of the predictions using the function
        Then we input the result in the treeview object and show the result
        """
        
        # Use function to get the df
        df = GUI_data.Predict_df(Entry_season)
        
        # Clean the treeview object
        tree_bets.delete(*tree_bets.get_children())
        # Give the heads a name
        tree_bets["columns"] = list(df.columns)
        # Hide empty 1st column
        tree_bets["show"] = 'headings'
        # create the columns and the values to show      
        for col in tree_bets["columns"]:
            tree_bets.column(col, width=79, stretch=False)
            tree_bets.heading(col, text=col)
        # put data into the treeview object
        for i, row in df.iterrows():
            tree_bets.insert("", "end", text=i, values=list(row))
        
        # Search label and place it
        Search_label5 = tk.Label(
            Sub_Frame8, text="Search :", font=("Verdana", 9))
        Search_label5.place(x=30, y=20, width=150, height=30)
        # Search entry and place it
        Search_entry5 = tk.Entry(
            Sub_Frame8, bg="#9fd3e0", font=("Verdana", 9))
        Search_entry5.place(x=200, y=20, width=300, height=30)
        # Search button and place it
        Search_button5 = tk.Button(
            Sub_Frame8, text="Search", font=("Verdana", 9),
            command=lambda: my_search(df, Search_entry5, tree_bets))
        Search_button5.place(x=550, y=20, width=80, height=30)     
        
        
        
        # Show the page
        Bets01b.tkraise()
        
        
#%% Pages   
    #%% Start Page 
    
    # Frame
    Sub_Frame = tk.Frame(StartPage, bg="#CCC" )
    Sub_Frame.place(x=0, y=200, width=700, height=500)
    
    # Titles
    Title_StartPage = tk.Label(
         StartPage, 
         text="Welcome to the NBA database !", font=("Verdana", 24,"bold"))
    Title_StartPage.place(x=0, y=0, width=700, height=90)
    
    Title_StartPage2 = tk.Label(
        StartPage, 
        text="Advanced Programming Project", font=("Verdana", 18, "bold"))
    Title_StartPage2.place(x=0, y=80, width=700, height=70)
    
    Title_StartPage3 = tk.Label(
        StartPage, 
        text="Matthieu Gisler\nActuarial Science Student\nUniversity of Lausanne", 
        font=("Verdana", 9, "bold"))
    Title_StartPage3.place(x=0, y=150, width=700, height=40)

    # Buttons
    ButtonStartPage1 = tk.Button(
        Sub_Frame, text="Visit\nNBA Statistics", font=("Verdana", 11), 
        bg="#c3c9ec", relief="ridge", borderwidth=5, 
        command=lambda:show_frame(Stats01))
    ButtonStartPage1.place(x=100, y=150, width=200, height=200)
    
    ButtonStartPage2 = tk.Button(
        Sub_Frame, text="Visit the\nBetting Predictions", 
        font=("Verdana", 10),
        bg="#c3c9ec", relief="ridge", borderwidth=5, 
        command=lambda:show_frame(Bets01))
    ButtonStartPage2.place(x=400, y=150, width=200, height=200)

    #%% Stats01
    
    # Sub Frame
    Sub_Frame2 = tk.Frame(Stats01, bg="#CCC")
    Sub_Frame2.place(x=0, y=200, width=width_700, height=heigth_500)
    
    # Titles
    Title_Stats01 = tk.Label(
        Stats01, text="The NBA's statistics", font=("Verdana", 20,"bold"))
    Title_Stats01.place(x=0, y=0, width=width_700, height=90)
    Title_Stats01_2 = tk.Label(
        Stats01, text="You can access Season, Team or Player statistics !", 
        font=("Verdana", 14))
    Title_Stats01_2.place(x=0, y=100, width=width_700, height=50)
    
    # Buttons
    ButtonSeason = tk.Button(
        Sub_Frame2, text="Season\nStatistics", font=("Verdana", 9), 
        bg="#c3c9ec", relief="ridge", borderwidth=5, 
        command=lambda:show_frame(Stats01a))
    ButtonSeason.place(x=50, y=115, width=500/3, height=500/3)
    
    ButtonTeam = tk.Button(
        Sub_Frame2, text="Team\n Statistics", font=("Verdana", 9),
        bg="#c3c9ec", relief="ridge", borderwidth=5, 
        command=lambda:show_frame(Stats01c))
    ButtonTeam.place(x=(100+500/3), y=115, width=500/3, height=500/3)
    
    ButtonPlayer = tk.Button(
        Sub_Frame2 , text="Player\n Statistics",font=("Verdana", 9),
        bg="#c3c9ec", relief="ridge", borderwidth=5,
        command=lambda:show_frame(Stats01b))
    ButtonPlayer.place(x=150+1000/3, y=115, width=500/3, height=500/3)
    
    ButtonReturn1 = tk.Button(
        Sub_Frame2, text="Return", font=("Verdana", 7),
        bg="#c3c9ec", relief="ridge", borderwidth=5, 
        command=lambda:show_frame(StartPage))
    ButtonReturn1.place(x=300, y = 400, width=100, height=50)
    
    #%% Season page
    
    # Frame and place it
    Sub_Frame4 = tk.Frame(Stats01a, bg="#CCC")
    Sub_Frame4.place(x=0, y=200, width=width_700, height=heigth_500)
    
    #Titles and place them
    Title_Stats01a = tk.Label(
        Stats01a, text="Season Statistics", font=("Verdana", 20, "bold"))
    Title_Stats01a.place(x=0, y=0, width=width_700, height=90)
    
    Title_Stats01a2 = tk.Label(
        Stats01a, text="Select a season to find its statistics !", 
        font=("Verdana", 14, "bold"))
    Title_Stats01a2.place(x=0, y=90, width=width_700, height=90)

    # Button to return and place it
    ButtonReturn2 = tk.Button(
        Sub_Frame4, text="Return", font=("Verdana", 7),
        bg="#c3c9ec", relief="ridge", borderwidth=5, 
        command=lambda:show_frame(Stats01))
    ButtonReturn2.place(x=300, y = 400, width=100, height=50)
    # Search label and place it
    Search_label1 = tk.Label(
        Sub_Frame4, text="Search a season :", font=("Verdana", 9))
    Search_label1.place(x=30, y=50, width=150, height=50)
    # Search entry and place it
    Search_entry1 = tk.Entry(
        Sub_Frame4, bg="#9fd3e0", font=("Verdana", 9))
    Search_entry1.place(x=200, y=50, width=300, height=50)
    # Search button and place it
    Search_button1 = tk.Button(
        Sub_Frame4, text="Search", font=("Verdana", 9),
        command=lambda: my_search(df_seasons, Search_entry1, tree_seasons))
    Search_button1.place(x=550, y=50, width=80, height=50)
    
    # Third title and fourth one and place it
    Title_Stats01a3 = tk.Label(
        Stats01a, 
        text="Write a text in the box and then press 'Search', please use the scrollbar to see all the stats available!",
        font=("Verdana", 7, "italic"))
    Title_Stats01a4 = tk.Label(
        Stats01a, 
        text="To reset the dataframe, leave the box empty and press 'Search'",
        font=("Verdana", 7, "italic"))
    Title_Stats01a3.place(x=0, y= 160, width=width_700, height=15)
    Title_Stats01a4.place(x=0, y= 180, width=width_700, height=15)
   
    # find the df to show in the treeview using function in GUI_data
    df_seasons = pd.read_csv(relative_path + "/seasons_list.csv")
  
    
    # treview create it and place it
    tree_seasons = ttk.Treeview(Sub_Frame4)
    tree_seasons.place(x=31, y=110, width=639, height=250)
    
    # Give the heads a name
    tree_seasons["columns"] = list(df_seasons.columns)
    # Hide empty 1st column
    tree_seasons["show"] = 'headings'
    
    # Scrollbar
    scrollbar_x_tree_seasons = ttk.Scrollbar(
        Sub_Frame4, orient="horizontal", command=tree_seasons.xview)
    tree_seasons.configure(xscrollcommand=scrollbar_x_tree_seasons.set)
    scrollbar_x_tree_seasons.place(x=31, y=360, width=639)
    
    # create the columns and the values to show in the tree
    for col in tree_seasons["columns"]:
        tree_seasons.column(col, width=150)
        tree_seasons.heading(col, text=col)
    for i, row in df_seasons.iterrows():
        tree_seasons.insert("", "end", text=i, values=list(row))
  
    # If we need to update
    Update_button1 = tk.Button(
        Sub_Frame4, text="Update list", font=("Verdana", 9),
        command=lambda: update_tree_seasons(tree_seasons))
    Update_button1.place(x=30, y=10, width=150, height=30)


    def update_tree_seasons(tree):
        # We update the background dataframe using the function
        # clean tree data
        for row in tree.get_children():
            tree.delete(row)
        # new data
        df_seasons = GUI_data.Stats_Seasons()
        for i, row in df_seasons.iterrows():
            tree.insert("", "end", text=i, values=list(row))
        return df_seasons    
    
    #%% Players Page
    
    # Frame
    Sub_Frame5 = tk.Frame(Stats01b, bg="#CCC")
    Sub_Frame5.place(x=0, y=200, width=width_700, height=heigth_500)
    # Titles
    Title_Stats01b = tk.Label(
        Stats01b, text="Player Statistics", font=("Verdana", 20, "bold"))
    Title_Stats01b.place(x=0, y=0, width=width_700, height=90)
     
    Title_Stats01b2 = tk.Label(
        Stats01b, text="Select a player to find its statistics !", 
        font=("Verdana", 14, "bold"))
    Title_Stats01b2.place(x=0, y=90, width=width_700, height=90)
    
    # Buttons
    ButtonReturn3 = tk.Button(
        Sub_Frame5, text="Return", font=("Verdana", 7),
        bg="#c3c9ec", relief="ridge", borderwidth=5, 
        command=lambda:show_frame(Stats01))
    ButtonReturn3.place(x=300, y=400, width=100, height=50)
    
    # Third title and fourth one and place it
    Title_Stats01b3 = tk.Label(
        Stats01b, 
        text="Write a text in the box and then press 'Search', please use the scrollbar to see all the stats available!",
        font=("Verdana", 7, "italic"))
    Title_Stats01b4 = tk.Label(
        Stats01b, 
        text="To reset the dataframe, leave the box empty and press 'Search'",
        font=("Verdana", 7, "italic"))
    Title_Stats01b3.place(x=0, y= 160, width=width_700, height=15)
    Title_Stats01b4.place(x=0, y= 180, width=width_700, height=15)
    
    # Search label and place it
    Search_label2 = tk.Label(
        Sub_Frame5, text="Search a player :", font=("Verdana", 9))
    Search_label2.place(x=30, y=50, width=150, height=50)
    # Search entry and place it
    Search_entry2 = tk.Entry(
        Sub_Frame5, bg="#9fd3e0", font=("Verdana", 9))
    Search_entry2.place(x=200, y=50, width=300, height=50)
    # Search button and place it
    Search_button2 = tk.Button(
        Sub_Frame5, text="Search", font=("Verdana", 9),
        command=lambda: my_search(df_players, Search_entry2, tree_players))
    Search_button2.place(x=550, y=50, width=80, height=50)
    
    # find the df to show in the treeview using function in GUI_data
    df_players = pd.read_csv(relative_path + "/players_list.csv")

    html_df = df_players["html"]
    df_players2 = df_players.drop("html", axis=1)
    
    # If we need to update
    Update_button2 = tk.Button(
        Sub_Frame5, text="Update list", font=("Verdana", 9),
        command=lambda: update_tree_players(tree_players))
    Update_button2.place(x=30, y=10, width=150, height=30)
    
    
    def update_tree_players(tree):
        # We update the background dataframe
        # clean tree data
        for row in tree.get_children():
            tree.delete(row)
        # new data
        df_players = GUI_data.Stats_Players()
        for i, row in df_players.iterrows():
            tree.insert("", "end", text=i, values=list(row))
        return df_players
    # treview create it and place it
    tree_players = ttk.Treeview(Sub_Frame5)
    tree_players.place(x=31, y=110, width=639, height=150)
    # Give the heads a name
    tree_players["columns"] = list(df_players2.columns)
    # Hide empty 1st column
    tree_players["show"] = 'headings'
    # Scrollbar
    scrollbar_x_tree_players = ttk.Scrollbar(
        Sub_Frame5, orient="horizontal", command=tree_players.xview)
    tree_players.configure(xscrollcommand=scrollbar_x_tree_players.set)
    scrollbar_x_tree_players.place(x=31, y=260, width=639)
    # create the columns and the values to show
    for col in tree_players["columns"]:
        tree_players.column(col, width=150)
        tree_players.heading(col, text=col)
    for i, row in df_players2.iterrows():
        tree_players.insert("", "end", text=i, values=list(row))
        
     # Label to get the Stats of the player
    Search_label3 = tk.Label(
       Sub_Frame5, text="ID of the player:", font=("Verdana", 9))
    Search_label3.place(x=50, y=340, width=200, height=50)
    Search_entry3 = tk.Entry(
        Sub_Frame5, bg="#9fd3e0", font=("Verdana", 9))
    Search_entry3.place(x=300, y=340, width=100, height=50)
    # Button to find the stats
    Search_button3 = tk.Button(
        Sub_Frame5, text="Stats", font=("Verdana", 9),
        command=lambda: my_stats_player(Search_entry3))
    Search_button3.place(x=450, y=340, width=200, height=50)
    # Title
    Title_Stats01a5 = tk.Label(
        Sub_Frame5, 
        text="Input the ID of the player you want to search, then press 'Stats'",
        font=("Verdana", 9, "italic"))
    Title_Stats01a5.place(x=0, y=290, width=700, height=30)
      
     # Create the Stats01b2 where we'll show the player's stats
    Sub_Frame6 = tk.Frame(Stats01b2, bg="#CCC")
    Sub_Frame6.place(x=0, y=200, width=width_700, height=heigth_500)
    tree_player = ttk.Treeview(Sub_Frame6)
    tree_player.place(x=31, y=20, width=639, height=300)    
    # Return button
    ButtonReturn4 = tk.Button(
        Sub_Frame6, text="Return", font=("Verdana", 7, "bold"),
        bg="#c3c9ec", relief="ridge", borderwidth=5, 
        command=lambda:show_frame(Stats01b))
    ButtonReturn4.place(x=300, y=400, width=100, height=50)
    
    #%%
    # Team page
    Sub_Frame7 = tk.Frame(Stats01c, bg="#CCC")
    Sub_Frame7.place(x=0, y=200, width=width_700, height=heigth_500)
    
    Title_Stats01c = tk.Label(
        Stats01c, text="Team Statistics", font=("Verdana", 20, "bold"))
    Title_Stats01c.place(x=0, y=0, width=width_700, height=90)
     
    Title_Stats01c2 = tk.Label(
        Stats01c, text="Select a team to find its statistics !", 
        font=("Verdana", 14, "bold"))
    Title_Stats01c2.place(x=0, y=90, width=width_700, height=90)
    
    ButtonReturn4 = tk.Button(
        Sub_Frame7, text="Return", font=("Verdana", 7),
        bg="#c3c9ec", relief="ridge", borderwidth=5, 
        command=lambda:show_frame(Stats01))
    ButtonReturn4.place(x=300, y=400, width=100, height=50)   
    
    # dataframe and create treeview object
    df_teams = pd.read_csv(relative_path + "/teams_list.csv")
    tree_teams = ttk.Treeview(Sub_Frame7)
    tree_teams.place(x=31, y=110, width=639, height=250)
    # Give the heads a name
    tree_teams["columns"] = list(df_teams.columns)
    # Hide empty 1st column
    tree_teams["show"] = 'headings'
    # Scrollbar
    scrollbar_x_tree_teams = ttk.Scrollbar(
        Sub_Frame7, orient="horizontal", command=tree_teams.xview)
    tree_teams.configure(xscrollcommand=scrollbar_x_tree_teams.set)
    scrollbar_x_tree_teams.place(x=31, y=360, width=639)
    # create the columns and the values to show
    for col in tree_teams["columns"]:
        tree_teams.column(col, width=150)
        tree_teams.heading(col, text=col)
    for i, row in df_teams.iterrows():
        tree_teams.insert("", "end", text=i, values=list(row))
    
    # Search label and place it
    Search_label4 = tk.Label(
        Sub_Frame7, text="Search a team :", font=("Verdana", 9))
    Search_label4.place(x=30, y=50, width=150, height=50)
    # Search entry and place it
    Search_entry4 = tk.Entry(
        Sub_Frame7, bg="#9fd3e0", font=("Verdana", 9))
    Search_entry4.place(x=200, y=50, width=300, height=50)
    # Search button and place it
    Search_button4 = tk.Button(
        Sub_Frame7, text="Search", font=("Verdana", 9),
        command=lambda: my_search(df_teams, Search_entry4, tree_teams))
    Search_button4.place(x=550, y=50, width=80, height=50)
    
    # If we need to update
    Update_button3 = tk.Button(
        Sub_Frame7, text="Update list", font=("Verdana", 9),
        command=lambda: update_tree_teams(tree_teams))
    Update_button3.place(x=30, y=10, width=150, height=30)
    
    Title_Stats01c3 = tk.Label(
        
        Stats01c, 
        text="Write a text in the box and then press 'Search', please use the scrollbar to see all the stats available!",
        font=("Verdana", 7, "italic"))
    Title_Stats01c4 = tk.Label(
        Stats01c, 
        text="To reset the dataframe, leave the box empty and press 'Search'",
        font=("Verdana", 7, "italic"))
    Title_Stats01c3.place(x=0, y= 160, width=width_700, height=15)
    Title_Stats01c4.place(x=0, y= 180, width=width_700, height=15)

    # update the file
    def update_tree_teams(tree):
        # clean tree data
        for row in tree.get_children():
            tree.delete(row)
        # new data
        df_teams = GUI_data.Stats_Teams()
        for i, row in df_teams.iterrows():
            tree.insert("", "end", text=i, values=list(row))
        return df_teams

#%%
    # Betting page
    
    Sub_Frame3 = tk.Frame(Bets01, bg='#CCC')
    Sub_Frame3.place(x=0, y=200, width=width_700, height=heigth_500)
    
    Title_Bets01 = tk.Label(
        Bets01, text="Betting predicitons", font=("Verdana", 22, "bold"))
    Title_Bets01.place(x=0, y=0, width=width_700, height=90)
    
    Title_Bets02 = tk.Label(
        Bets01, 
        text="You can load the NBA matches and then find the winner predictions !",
        font=("Verdana", 10, "bold"))
    Title_Bets02.place(x=0, y=100, width=700, height=20)
        
    ButtonReturn5 = tk.Button(
        Sub_Frame3, text="Return", font=("Verdana", 7),
        bg="#c3c9ec", relief="ridge", borderwidth=5, 
        command=lambda:show_frame(StartPage))
    ButtonReturn5.place(x=300, y=400, width=100, height=50)
    # Loading button
    ButtonLoad = tk.Button(
        Sub_Frame3, text="Load Matches",
        font=("Verdana", 9),
        command=lambda:GUI_data.load_matches(
            int(Entry_season.get()), 
            datetime.datetime(
                int(Entry_year_beg.get()), int(Entry_month_beg.get()), int(Entry_day_beg.get())),
            datetime.datetime(
                int(Entry_year_end.get()), int(Entry_month_end.get()), int(Entry_day_end.get()))))
    ButtonLoad.place(x=500/3, y=270, width=100, height=100)
    # Button predictions
    ButtonPred = tk.Button(
        Sub_Frame3, text="Predictions", 
        font=("Verdana", 9), 
        command=lambda:my_predictions_page(int(Entry_season.get()), tree_bets))
    ButtonPred.place(x=1000/3+100, y=270, width=100, height=100)
    
    Label_buttons = tk.Label(
        Sub_Frame3, 
        text="First load the matches and then do the predicitons.",
        font=("Verdana", 9))
    Label_buttons.place(x=25, y=225, width=650, height=20)
    
    Label_season = tk.Label(
        Sub_Frame3, 
        text="Enter the season of the games. For ex. Season 2022-2023, please enter 2023",
        font=("Verdana", 9))
    Label_season.place(x=25, y=25, width=650, height=20)
    # Entries
    Entry_season = tk.Entry(Sub_Frame3, bg="#9fd3e0", 
                            font=("Verdana", 9))
    Entry_season.place(x=550/2+50, y=55, width=50, height=20)
    
    
    Label_beg = tk.Label(
        Sub_Frame3, 
        text="Enter the year, the month and the day of the first match",
        font=("Verdana",  9))
    Label_beg.place(x=25, y=85, width=650, height=20)
    
    Entry_year_beg = tk.Entry(Sub_Frame3, bg="#9fd3e0", 
                              font=("Verdana", 9))
    Entry_year_beg.place(x=550/4, y=115, width=50, height=20)

    Entry_month_beg = tk.Entry(Sub_Frame3, bg="#9fd3e0", 
                               font=("Verdana", 9))
    Entry_month_beg.place(x=550/2+50, y=115, width=50, height=20)
    
    Entry_day_beg = tk.Entry(Sub_Frame3, bg="#9fd3e0", 
                             font=("Verdana", 9))
    Entry_day_beg.place(x=825/2+100, y=115, width=50, height=20)
    
    
    Label_end = tk.Label(
        Sub_Frame3, 
        text="Enter the year, the month and the day of the last match",
        font=("Verdana",  9))
    Label_end.place(x=25, y=145, width=650, height=20)
    
    Entry_year_end = tk.Entry(Sub_Frame3, bg="#9fd3e0", 
                              font=("Verdana", 9))
    Entry_year_end.place(x=550/4, y=175, width=50, height=20)

    Entry_month_end = tk.Entry(Sub_Frame3, bg="#9fd3e0", 
                               font=("Verdana", 9))
    Entry_month_end.place(x=550/2+50, y=175, width=50, height=20)
    
    Entry_day_end = tk.Entry(Sub_Frame3, bg="#9fd3e0", 
                             font=("Verdana", 9))
    Entry_day_end.place(x=825/2+100, y=175, width=50, height=20)
    
    # New sub-frame to show the predicitons
    Sub_Frame8 = tk.Frame(Bets01b, bg='#CCC')
    Sub_Frame8.place(x=0, y=200, width=width_700, height=heigth_500)
    
    Title_Bets01b = tk.Label(
        Bets01b, text="Betting predicitons", font=("Verdana", 22, "bold"))
    Title_Bets01b.place(x=0, y=0, width=width_700, height=50)
    
    Title_Bets01c = tk.Label(
        Bets01b, 
        text="Here are the predictions made for the matches !",
        font=("Verdana", 10))
    Title_Bets01c.place(x=0, y=60, width=width_700, height=30)
    Title_Bets01d = tk.Label(
        Bets01b,
        text="Bet on Away, Home or do not bet",
        font=("Verdana", 10))
    Title_Bets01d.place(x=0, y=90, width=width_700, height=30)
    Title_Bets01e = tk.Label(
        Bets01b,
        text="A CSV file was exported with the predictions !",
        font=("Verdana", 10))
    Title_Bets01e.place(x=0, y=120, width=width_700, height=90)
        
    ButtonReturn6= tk.Button(
        Sub_Frame8, text="Return", font=("Verdana", 7),
        bg="#c3c9ec", relief="ridge", borderwidth=5, 
        command=lambda:show_frame(Bets01))
    ButtonReturn6.place(x=300, y=400, width=100, height=50)

    tree_bets = ttk.Treeview(Sub_Frame8)
    tree_bets.place(x=31, y=70, width=639, height=290)
    

#%%
    show_frame(StartPage)
    window.mainloop()




