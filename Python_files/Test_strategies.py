# %%
import time
import pandas as pd
import numpy as np
from Test_functions import simulate_money, simulate_accuracy
import multiprocessing as mp
import matplotlib.pyplot as plt

def graphics_money_ranks(dfs, Long, Short):
    """
    Plot graphics to see the imapct of each of the combinaisons
    """
    # Group the dataframes into sets of year
    Size = int(len(dfs) / (len(Long) * len(Short)))
    
    grouped_dfs = [dfs[i::Size] for i in range(Size)]
    list_names = []
    for i in range(len(grouped_dfs)):
        for j in range(len(grouped_dfs[i])):
            fuse = grouped_dfs[i][j][["Year", "Long", "Short"]].iloc[0].values
            fused = ' '.join(fuse.astype(str))
            list_names.append(fused)
    
    # Find the counts of rank of each df
    rank_dfs = []
    k = 0
    for group in grouped_dfs:
        rank_df = pd.DataFrame(columns=list_names[k:k + len(group)])
        k += len(Long) * len(Short)
        for row_index in range(len(group[0])):
            ranks = [df['Money'].iloc[row_index] for df in group]
            # Check if duplicate
            if len(set(ranks)) != len(ranks):
                # Skip this row if duplicates
                ranks = pd.Series(len(Long) * len(Short) * [len(Long) * len(Short) + 1])
                rank_df.loc[row_index] = ranks.values
            else:
                ranks = pd.Series(ranks).rank(ascending=False, method='min')
                rank_df.loc[row_index] = ranks.values
    
        rank_dfs.append(rank_df)
    
    # Find the % of counts relative to the total simulations
    result_dfs = []  # List to store the result DataFrames
    
    for rank_df in rank_dfs:
        counts = rank_df.apply(pd.Series.value_counts)
        columns_sums = counts.sum()
        percentage = counts / columns_sums
        percentage = percentage.fillna(0)
        result_dfs.append(percentage.T)
    
    for result_df in result_dfs:
        result_df.columns = [f"Rank {i + 1}" for i in range(len(result_df.columns))]
    
    # Iterate over each result DataFrame and plot a separate graph for each
    for i, result_df in enumerate(result_dfs):
        # Create a new figure and axes
        fig, ax = plt.subplots(figsize=(10, 6))
        # Get the names of the dataframes
        df_names = result_df.T.columns
        # Get the data for each rank
        data = result_df.values.T * 100
        # Plot the stacked histogram
        ax.bar(df_names, data[0], label="Rank 1", alpha=0.7)
        bottom = data[0]
        bottom = np.nan_to_num(bottom, nan=0)
        labels = ["Rank 1", "Rank 2", "Rank 3", "Rank 4", "Rank 5", "Rank 6", "Same rank"]
        for j in range(1, len(data)):
            ax.bar(df_names, data[j], bottom=bottom, label=labels[j], alpha=0.7)
            bottom += data[j]
        # Set the y-axis limit to (0, 100)
        ax.set_ylim(0, 100)
        # Set the title and labels
        ax.set_title("Stacked Histogram - 2023 being predicted by " + str(2020 + i))
        ax.set_xlabel("Models")
        ax.set_ylabel("Percentage")
        # Add a legend
        ax.legend()
    
    # Create a figure and axis for box plots
    fig, ax = plt.subplots(figsize=(10, 6))
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    # Set the plot title and axis labels
    ax.set_title("Box Plot of 'Money' Column")
    ax.set_xlabel("Models")
    ax.set_ylabel("Money")
    ax2.set_title("Box Plot of 'Accuracy' Column")
    ax2.set_xlabel("Models")
    ax2.set_ylabel("Accuracy")
    
    # List to store the box plot labels
    labels = []
    
    # Iterate over the DataFrames
    for i, df in enumerate(money_results):
        # Extract the "Money" and "Accuracy" columns
        df["Total"] = df["Won"] + df["Lost"]
        df = df[df["Total"] > 30]
        money_data = df["Money"]
        accuracy_data = df["%wl"]
    
        # Create the box plots
        ax.boxplot(money_data, positions=[i])
        ax2.boxplot(accuracy_data, positions=[i])
    
        # Labels
        Year = str(df["Year"].iloc[0])
        Long = str(df["Long"].iloc[0])
        Short = str(df["Short"].iloc[0])
        # Add label to the list
        labels.append(Year + "_" + Long + "_" + Short)
    
        if i == 0:
            ax.axhline(y=0, color='red', linestyle='--')
    
    # Set the x-axis tick labels
    ax.set_xticklabels(labels, rotation="vertical")
    ax2.set_xticklabels(labels, rotation="vertical")
    plt.show()
    # Create a figure and axis for scatter plot
    fig, ax3 = plt.subplots(3, 6, figsize=(15, 10))
    fig.suptitle("Scatter Plots")
    
    
    
    # list of money to find min and max
    money_list = []
    # Iterate over the DataFrames
    for i, df in enumerate(money_results):
        # Extract the "Money" column
        df["Total"] = df["Won"] + df["Lost"]
        df = df[df["Total"] > 30]
        df = df[df["Money"] > 0]
        money = df["Money"]
        # used to find min and max of cmap
        money_list.append(money)
    # Flatten the list of money values
    money_data = pd.DataFrame(money_list)

    # Get the minimum and maximum values of money
    money_min = min(money_data.min())
    money_max = max(money_data.max())
  
    
    for i, df in enumerate(money_results):
        df["Total"] = df["Won"] + df["Lost"]
        df = df[df["Total"] > 30]
        df = df[df["Money"] > 0]
        x = df["Upper"]
        y = df["Lower"]
        money = df["Money"]
        # Subplot position
        row = i//6
        col = i % 6
        
        # plot
        ax = ax3[row, col]
        sc = ax.scatter(x, y, c=money, cmap="plasma", s=20, edgecolors="black", 
                   vmin=money_min, vmax=money_max)
        ax.set_xlim([0.5, 1])
        ax.set_ylim([0, 0.5])
        ax.set_title(labels[i])
        
        
    # Remove empty subplots if there are fewer than 18 plots
    if len(money_results) < 18:
        for i in range(len(money_results), 18):
            row = i // 6
            col = i % 6
            fig.delaxes(ax3[row, col])
    # Create the colorbar
    cbar_ax = fig.add_axes([0.95, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(sc, cax=cbar_ax)
    cbar.set_label("Money")
    # Space between graph
    fig.subplots_adjust(left=0.05, right=0.88, bottom=0.08, top=0.9, wspace=0.25, hspace=0.4)

    # Show the plot
    plt.show()
    
    
def Money_parallel(Year_predicted, Long, Short, seed=None):
    """
    Allow to run mulitple simulations in case we want to see how the models
    behave under random upper and lower bounds. It allows to test the models
    under differetn random numbers and to see their performance VS each others.
    """

    # Number of simulation
    num_sims = 10
    Money_df_list = []
    # Multiprocessing as it's MonteCarlo
    with mp.Pool() as pool:
        results = pool.starmap(
            simulate_money, [
                (Year_predicted, long_val, short_val, num_sims, seed
                 ) for long_val in Long for short_val in Short])

    for result in results:
        Results, long_val, short_val = result
        Money_df_list.extend(Results)

    return Money_df_list

def Accuracy_parallel(Year_predicted, Long, Short):
    """
    Allow to run mulitple simulations in case we want to see how the models
    perform with the different parameters
    """
    with mp.Pool() as pool:
        results = pool.starmap(
            simulate_accuracy, [
                (Year_predicted, long, short
                 ) for long in Long for short in Short])
    
    # Concatenate the results
    counts_df, df_params = zip(*results)
    counts_df = pd.concat(counts_df)
    df_params = pd.concat(df_params, axis=1)
    counts_df = counts_df.sort_values("Accurancy")
    
    # Graphic
    plt.plot(counts_df.index, counts_df["Accurancy"]*100)
    plt.xticks(counts_df.index, rotation="vertical")
    plt.title(str(Year_predicted) + ": Models VS Accurancy")
    plt.ylabel("Accurancy in %")
    plt.show()
    return counts_df, df_params

if __name__ == "__main__":
    """
    Run the code to create the graphics and the different tests
    """
    start = time.time()
    # Parameters
    predicted_year = 2023
    long_values = [10, 20, 30]
    short_values = [3, 5]
    random_seed = 0
    
    # How the models behave with the odds
    money_results = Money_parallel(predicted_year, long_values, 
                                   short_values, random_seed) 
    graphics_money_ranks(money_results, long_values, short_values)
    
    # Not taking into account the odds but only the predictions %
    accurancy_df = Accuracy_parallel(predicted_year, long_values, short_values)
    time.sleep(1)
    print("Run time: ", time.time()-start)
    

