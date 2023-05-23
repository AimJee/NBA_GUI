import numpy as np
import pandas as pd
import statsmodels.api as sm
from GUI_data import get_year_data
import os

def simulate_money(Year_predicted, Long, Short, num_sims, seed=0):
    """
    Year_predicted = Season we want to predict the result of. We use the last
    3 seasons as regressors years
    Long = the length of the moving average for some of the parameters
    Long can be a list
    Short = the length of the moving average for some parameters
    Short can be a list
    num_sims = how many Monte Carlo simulations we run. Note that this number
    is the number of simulations by "configurations". The length of the confi-
    gurations is 3*len(long)*len(short).
    seed = the random seed. It's a constant for comparaison purposes
    
    The function uses the Quotes to simulate how much money the player would
    have won following the different configurations. The Quotes are extracted
    from a CSV. It was created using the function "Load_quotes.py"
    Here it's used for example purposes but it's not directly inplanted in the
    project.
    """
    
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))
    # Set the seed value
    np.random.seed(seed)  
    # Cols name
    Cols_name = []
    # Data of predicted year
    _, _, Matches = get_year_data(Year_predicted, Long, Short)
    # Find the Matches list of the year 
    data_to_use1 = Matches[4].sort_values(
        by=["team_name", "match_num"]).drop(["game_date", "home_team", "game_id"], 
                                            axis=1)
    data_to_use1 = data_to_use1.reset_index()
    data_to_use1 = data_to_use1.set_index(["team_name", "match_num"])    
        
    # Find the 2023 quotes and merge it with the data_to_use1
    # We end up with the quotes with the right index
    quotes = pd.read_csv(current_directory + "/CSV_files/Quotes.csv")
    quotes[["match_num", "team_name"]] = quotes[["Match_num", "Team_name"]]
    quotes = quotes.replace("Los Angeles Clippers", value="LA Clippers")
    quotes = quotes.drop(["Match_num", "Team_name"], axis=1)
    quotes = quotes[["match_num", "team_name", 
                     "Money Line", "Location"]].set_index(
                         ["team_name", "match_num"])
    quotes = quotes.replace(["Home", "Away"], value=[1, 0])
    quotes_df = quotes.merge(data_to_use1, left_index=True, 
                             right_index=True, how="left")
    quotes_df = quotes_df.set_index(["index"]).sort_index()
    Money_df_list = []
    # Find parameters of last 3 years individually
    for i in range(int(Year_predicted)-3, int(Year_predicted), 1):
        Money = []
        # Data to get and regress
        x, y, data = get_year_data(i, Long, Short)
        Regr_result = sm.Logit(y, x).fit(cov_type="HC3")
        Predicts_clean = Regr_result.predict(Matches[0])
        Cols_name.append(i)
        # Each year are comparable
        np.random.seed(seed) 
        for s in range(num_sims):
            # Limits
            Upper = np.random.uniform(0.5, 1)
            Lower = np.random.uniform(0, 0.5)
            Upper = 0.5
            Lower = 0.5
            Predicts = Predicts_clean.copy()    
            # go to closest integer
            Predicts[(Predicts<Lower)] = 0
            Predicts[(Predicts>Upper)] = 1
            Predicts[((Predicts<=Upper) & (Predicts>=Lower))] = np.nan
            
            new_col = []
            
            for k, val in enumerate(Predicts):
                try:
                    # If we didnt bet then we get 0
                    if np.isnan(val):
                        new_col.append(0)
                    # If the bet is won then we get the quotes minus 1
                    elif val == Matches[1].iloc[k]:
                        new_col.append(quotes_df[
                            quotes_df["Location"]==val].loc[
                                Predicts.index[k]]["Money Line"]-1)
                    # If we only want the result and not the quote
                    # elif val == y_result[k]:
                        # new_col.append(1)
                    # If the result is not available then we get 0
                    elif np.isnan(Matches[1].iloc[k]) == np.nan:
                        new_col.append(0)
                    # If we lose then we lose our bet
                    else:
                        new_col.append(-1)
                except:
                    print(Predicts.index[k])
            
            # Count the bet won/lost
            won = np.sum(np.array(new_col)>0)
            lost = np.sum(np.array(new_col)<0)
            # percentage of bet won
            if (won + lost) == 0:
                Perc = 0
            else:
                Perc = won/(won + lost)
            # into the list
            Money.append((str(i), Long, Short, Lower, Upper, 
                          sum(new_col), won, lost, Perc))
        # into a list of df
        Money_df_list.append(pd.DataFrame(
            Money, columns=[
                "Year", "Long", "Short", "Lower", "Upper", 
                "Money", "Won", "Lost", "%wl"]))
    return Money_df_list, Long, Short

def simulate_accuracy(Year_predicted, Long, Short):
    """
    Test the accuracy of the 18 models 
    """
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))
    # Cols name
    Cols_name = []
    Predictions = []
    Parameters = []
    
    for k in range(int(Year_predicted)-3, int(Year_predicted), 1):
        # Data of predicted year
        _, _, Matches = get_year_data(Year_predicted, Long, Short)    
        # Data to get and regress
        x, y, data = get_year_data(k, Long, Short)
        Regr_result = sm.Logit(y, x).fit(cov_type="HC3")
        Parameters.append(Regr_result.params)
        Names = Matches[0].columns.tolist()
        
        with open(current_directory + '/Tests/regression_summary_' + str(k) + "_" + \
                  str(Long) + "_" + str(Short) + ".txt", 'w') as f:
            f.write(Regr_result.summary(
                xname=Names).as_text())
        
        # Only predicts if data is not nan
        Predicts = Regr_result.predict(Matches[0])
        Cols_name.append(str(k)+"_"+str(Long)+"_"+str(Short))
        # Limits
        Upper = 0.5
        Lower = 0.5
        # Round based on the Bounds
        Predicts[(Predicts<Lower)] = 0
        Predicts[(Predicts>Upper)] = 1
        # Keep all the data with same index to compare easily
        non_nan_mask = ~np.isnan(Predicts) & ~np.isnan(Matches[1])
        # Empty
        result = np.full_like(Predicts, np.nan)
        # Enter the data only on the non-nan cell
        result[non_nan_mask] = ((
            Predicts[non_nan_mask] == 1) & (Matches[1][non_nan_mask] == 1)) | \
            ((Predicts[non_nan_mask] == 0) & (Matches[1][non_nan_mask] == 0))
        # add to the list
        Predictions.append(result)
        
    # into a df
    df = pd.DataFrame(Predictions).T
    df_params = pd.DataFrame(Parameters).T
    df_params.columns = Cols_name
    df_params.index = Matches[0].columns
    df.columns = Cols_name
    # counts the bets won and lost
    ones_counts = df.fillna(0).astype(int).sum()
    zeros_counts = df.fillna(1).astype(int).eq(0).sum()
    counts_df = pd.concat([ones_counts, zeros_counts], 
                          axis=1, keys=["Ones", "Zeros"])
    # total bet 
    counts_df["Sum"] = counts_df["Ones"] + counts_df["Zeros"]
    # Accurancy of betting
    counts_df["Accurancy"] = counts_df["Ones"]/counts_df["Sum"]
    return counts_df, df_params

