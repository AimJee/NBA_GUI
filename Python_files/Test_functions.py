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
    
    The function uses the odds to simulate how much money the player would
    have won following the different configurations. The odds are extracted
    from a CSV. It was created using the function "Load_odds.py"
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
        
    
    # Find the 2023 odds and merge it with the data_to_use1
    # We end up with the odds with the right index
    odds = pd.read_csv(current_directory + "/CSV_files/odds.csv")
    odds["Team_name"].unique()
    odds[["match_num", "team_name"]] = odds[["Match_num", "Team_name"]]
    odds = odds.drop(["Match_num", "Team_name"], axis=1)
    odds = odds[["match_num", "team_name", 
                     "Money Line", "Location"]].set_index(
                         ["team_name", "match_num"])
    odds = odds.replace(["Home", "Away"], value=[1, 0])
    odds_df = odds.merge(data_to_use1, left_index=True, 
                             right_index=True, how='right')
    odds_df = odds_df.set_index(["index"]).sort_index()
    temp = odds_df[odds_df["Location"]==1].drop("Location", axis=1)
    temp2 = odds_df[odds_df["Location"]==0].drop("Location", axis=1)
    temp.columns = ["Money Line Home"]
    temp2.columns = ["Money Line Away"]
    odds_df = pd.concat([temp, temp2], axis=1)
    Money_df_list = []

    # Find parameters of last 3 years individually
    for i in range(int(Year_predicted)-3, int(Year_predicted), 1):
        Money = []
        # Data to get and regress
        x, y, data = get_year_data(i, Long, Short)
        Regr_result = sm.Logit(y, x).fit("HC3")
        Predicts_clean = Regr_result.predict(Matches[0])
        Cols_name.append(i)
        # Each year are comparable
        np.random.seed(seed) 
        for s in range(num_sims):
            # Limits
            Upper = np.random.uniform(0.5, 1)
            Lower = np.random.uniform(0, 0.5)
            Predicts = Predicts_clean.copy()    
            # go to closest integer
            Predicts[(Predicts<Lower)] = 0
            Predicts[(Predicts>Upper)] = 1
            Predicts[((Predicts<=Upper) & (Predicts>=Lower))] = np.nan
            
            new_col = []
            Ind_pre = Predicts.index
            for index, value in enumerate(Predicts):
                try:
                    # If we didnt bet then we get 0
                    if np.isnan(value):
                        new_col.append(0)
                    # If the bet is won then we get the odds minus 1
                    elif value == Matches[1].loc[Ind_pre[index]]:
                        if value == 1:
                            new_col.append(
                                odds_df.loc[Ind_pre[index]]["Money Line Home"]-1)
                        else:
                            new_col.append(
                                odds_df.loc[Ind_pre[index]]["Money Line Away"]-1)
                    # If we only want the result and not the quote
                    # elif val == y_result[k]:
                        # new_col.append(1)
                    # If the result is not available then we get 0
                    elif np.isnan(Matches[1].loc[Ind_pre[index]]) == np.nan:
                        new_col.append(0)
                    # If we lose then we lose our bet
                    else:
                        new_col.append(-1)
                except:
                    print(Ind_pre[index])
                    
            
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
    Cols_name = []
    Predictions = []
    Parameters = []
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))
    for k in range(int(Year_predicted)-3, int(Year_predicted), 1):
        # Data of predicted year
        _, _, Matches = get_year_data(Year_predicted, Long, Short)    
        # Data to get and regress
        x, y, data = get_year_data(k, Long, Short)
        Regr_result = sm.Logit(y, x).fit("HC3")
        # Perform White's test for heteroscedasticity
        # white_test = het_white(Regr_result.resid_dev, Regr_result.model.exog)
        Parameters.append(Regr_result.params)
        Names = Matches[0].columns.tolist()
        # Save result
        with open(current_directory + '/Tests/regression_summary_' + str(k) + "_" + \
                  str(Long) + "_" + str(Short) + ".txt", 'w') as f:
            f.write(Regr_result.summary(
                xname=Names).as_text())
        with open(current_directory + '/Tests/het_white_result_' + str(k) + \
                  '_' + str(Long) + '_' + str(Short) + '.txt', 'w') as f:
            f.write("HetWhite Test Result\n")
            #f.write("LM Statistic: {}\n".format(white_test[0]))
            #f.write("LM-Test p-value: {}\n".format(white_test[1]))
            #f.write("F-Statistic: {}\n".format(white_test[2]))
            #f.write("F-Test p-value: {}\n".format(white_test[3]))     
        
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

