# %%
import time
import pandas as pd
import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt
import os 

def graphics_money_ranks(dfs, Long, Short):
    """
    Plot graphics to see the imapct of each of the combinaisons
    """
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))
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
                ranks = pd.Series(len(group)*[len(Long)*len(Short)+1])
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
        result_df.columns = [f"Rank {i}" for i in range(len(result_df.columns))]
    
    # Define the color map
    colors = plt.colormaps["plasma"].reversed()
    # Iterate over each result DataFrame and plot a separate graph for each
    for i, result_df in enumerate(result_dfs):
        # Create a new figure and axes
        fig, ax = plt.subplots(figsize=(10, 6))
        # Get the names of the dataframes
        df_names = result_df.T.columns
        # Get the data for each rank
        data = result_df.values.T * 100
        # Plot the horizontal bar chart
        y_pos = np.arange(len(df_names))
        bars = []
        labels = [f"Rank {i}" for i in range(1, len(result_df) + 1)]
        labels.append("Same rank")
        for j in range(len(data)):
            bar = ax.barh(y_pos, data[j], align='center', left=np.sum(data[:j], axis=0), color=colors((j + 1) / (len(data) + 1)), alpha=0.7)
            bars.append(bar)
        # Set the y-axis tick positions and labels
        ax.set_yticks(y_pos)
        ax.set_yticklabels(df_names)
        # Set the x-axis limit to (0, 100)
        ax.set_xlim(0, 100)
        # Set the title and labels
        ax.set_title("Rank Distribution - 2023 being predicted by " + str(2020 + i))
        ax.set_xlabel("Percentage")
        ax.set_ylabel("Models")
        # Create a legend on the right side
        ax.legend(bars, labels, loc='center left', bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
        plt.savefig(
            current_directory + "/Tests/Graphs_Rank_Distribution_" + str(2020 + i) + ".png",
            dpi=300)
    # Create a figure and axis for box plots
    fig, ax = plt.subplots(figsize=(20, 12))
    fig2, ax2 = plt.subplots(figsize=(20, 12))
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
    for i, df in enumerate(dfs):
        # Extract the "Money" and "Accuracy" columns
        df["Total"] = df["Won"] + df["Lost"]
        # Dont take into account if not played enough
        df = df[df["Total"] > 30]
        money_data = df["Money"]
        accuracy_data = df["%wl"]
        # Create the box plots
        ax.boxplot(money_data, positions=[i])
        ax2.boxplot(accuracy_data, positions=[i])
        # Labels
        Year = str(df["Year"].iloc[0])
        Long_val = str(df["Long"].iloc[0])
        Short_val = str(df["Short"].iloc[0])
        # Add label to the list
        labels.append(Year + "_" + Long_val + "_" + Short_val)
        if i == 0:
            ax.axhline(y=0, color='red', linestyle='--')
    # Set the x-axis tick labels
    ax.set_xticklabels(labels, rotation="vertical")
    ax2.set_xticklabels(labels, rotation="vertical")
    plt.savefig(current_directory + "/Tests/Graphs_box_plot_accuracy.png", dpi=300)
    plt.show()
    plt.close(fig2)
    plt.savefig(current_directory + "/Tests/Graphs_box_plot_money.png", dpi=300)
    plt.show()
    # list of money to find min and max
    money_list = []
    # Iterate over the DataFrames
    for i, df in enumerate(dfs):
        # Extract the "Money" column
        df["Total"] = df["Won"] + df["Lost"]
        # 5 games as we look for money
        df = df[df["Total"] > 5]
        df = df[df["Money"] > 0]
        money = df["Money"]
        # used to find min and max of cmap
        money_list.append(money)
    # Flatten the list of money values
    money_data = pd.DataFrame(money_list)
    # Get the minimum and maximum values of money
    money_min = min(money_data.min())
    money_max = max(money_data.max())
    for i in range(Size):
        fig3, ax3 = plt.subplots(len(Long), len(Short), figsize=(15, 20 ))
        fig3.suptitle("Scatter Plots " + str(dfs[i]["Year"].loc[0]), fontsize=25)
        for j in range(len(Short)*len(Long)):
            df = dfs[(i + Size*j)]
            # Create a figure and axis for scatter plot
            df["Total"] = df["Won"] + df["Lost"]
            df = df[df["Total"] > 5]
            df = df[df["Money"] > 0]
            x = df["Upper"]
            y = df["Lower"]
            money = df["Money"]
            # Subplot position
            col = j % len(Short)
            row = j // (len(Short))
            # plot
            ax = ax3[row, col]
            sc = ax.scatter(x, y, c=money, cmap="plasma", s=25, 
                       vmin=money_min, vmax=money_max)
            ax.set_xlim([0.5, 1])
            ax.set_ylim([0, 0.5])
            ax.set_title(labels[(i+Size*j)], fontsize=16)
        # Create the colorbar
        cbar_ax = fig3.add_axes([0.95, 0.15, 0.02, 0.7])
        cbar = fig3.colorbar(sc, cax=cbar_ax)
        cbar.set_label("Money")
        # Space between graph
        fig3.subplots_adjust(left=0.125, right=0.9, bottom=0.1, top=0.9, 
                             wspace=0.25, hspace=0.2)
        plt.savefig(current_directory + "/Tests/Graphs_scatter_plots" + \
                    str(i+1) + ".png", dpi=300)
        # Show the plot
        plt.show()
        plt.close(fig3)
        
def Money_parallel(Year_predicted, Long, Short, num_sims, seed=None):
    """
    Allow to run mulitple simulations in case we want to see how the models
    behave under random upper and lower bounds. It allows to test the models
    under differetn random numbers and to see their performance VS each others.
    """
    from Test_functions import simulate_money
    # Number of simulation
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
    from Test_functions import simulate_accuracy
    
    results = []
        
    with mp.Pool() as pool:
        results = pool.starmap(
            simulate_accuracy, [
                (Year_predicted, long_val, short_val
                 ) for long_val in Long for short_val in Short])
    
    # Concatenate the results
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))
    counts_df, df_params, money_df = zip(*results)
    counts_df = pd.concat(counts_df)
    df_params = pd.concat(df_params, axis=1)
    counts_df_ord = counts_df.sort_values("Accuracy")
    money_df = pd.concat(money_df)
    
    # Graphic
    plt.figure(figsize=(15, 10))
    plt.plot(counts_df_ord.index, counts_df_ord["Accuracy"]*100)
    plt.xticks(counts_df_ord.index, rotation="vertical")
    plt.title(str(Year_predicted) + ": Models VS Accuracy")
    plt.ylabel("Accuracy in %")
    plt.savefig(current_directory + "/Tests/Graphs_accuracy.png", dpi=300)
    plt.show()
    # Graphic
    plt.figure(figsize=(15, 10))
    plt.scatter(money_df.index, money_df)
    plt.xticks(money_df.index, rotation="vertical")
    plt.title(str(Year_predicted) + ": Models VS Money")
    plt.ylabel("Money")
    plt.savefig(current_directory + "/Tests/Graphs_money.png", dpi=300)
    plt.show()
    # Graphic
    plt.figure(figsize=(15,10))
    plt.scatter(counts_df["Accuracy"]*100, money_df)
    plt.title(str(Year_predicted) + ": Accuracy VS Money")
    plt.ylabel("Money")
    plt.xlabel("Accuracy")
    plt.savefig(current_directory + "/Tests/Graphs_relation_money_accuracy.png", dpi=300)
    plt.show()
    return counts_df, df_params

if __name__ == "__main__":
    """
    Run the code to create the graphics and the different tests
    """
    start = time.time()
    # Parameters
    predicted_year = 2023
    long_values = [20, 30, 40, 50]
    short_values = [5, 10, 20]
    random_seed = 0
    num_sims = 10000
    # How the models behave with the odds
    money_results = Money_parallel(predicted_year, long_values, 
                                   short_values, num_sims, random_seed) 
    graphics_money_ranks(money_results, long_values, short_values)
    
    # Not taking into account the odds but only the predictions %
    Accuracy_df = Accuracy_parallel(predicted_year, long_values, short_values)
    print("Run time: ", time.time()-start)
    

