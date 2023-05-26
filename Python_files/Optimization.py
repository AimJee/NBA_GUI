import pandas as pd
import matplotlib.pyplot as plt
import multiprocessing as mp
from tqdm import tqdm 
from Test_functions import simulate_accuracy
import matplotlib.colors as mcolors
import numpy as np

def simulate_accuracy_wrapper(args):
# Wrapper as pool.imap takes one arg for inputs
    year, long_val, short_val = args
    return simulate_accuracy(year, long_val, short_val)

if __name__ == "__main__":
    # inputs
    inputs = [
        (2023, long_val, short_val) for long_val in range(
            60, 2, -1) for short_val in range(long_val-1, 1, -1)]
    # empty list
    results = []
    # Mulitprocessing
    with mp.Pool() as pool:
        # Add a progress bar 
        progress_bar = tqdm(total=(len(inputs)))
        for result in list(tqdm(pool.imap(
                simulate_accuracy_wrapper, inputs), total=len(inputs))):
            results.append(result)
            progress_bar.update(1)
    # Zip results
    counts_df, df_params, money_df = zip(*results)
    money_df = pd.concat(money_df)

    index_list = money_df.index.tolist()
    # Strnig operations
    new_index = [string[5:] for string in index_list]
    new_index = pd.DataFrame(new_index)
    new_index = new_index[0].unique()
    # Still string operations
    long_param = []
    short_param = []
    for string in new_index:
        split_values = string.split("_")
        long_param.append(int(split_values[0]))
        short_param.append(int(split_values[1]))
    # Data organization and Plot
    range_size = 3
    df = money_df.copy()
    df = df.reset_index()
    df = df.drop("index", axis=1)
    df["group"] = df.index // range_size
    mean_values = df.groupby('group')[0].mean()
    final_df = pd.concat([mean_values, pd.DataFrame(long_param), pd.DataFrame(short_param)], axis=1)
    final_df.columns = ["Mean", "Long", "Short"]
    final_df.index = new_index
    final_df = final_df.sort_values(["Long", "Short"])
    
    x = final_df["Long"]
    y = final_df["Short"]
    color = final_df["Mean"]
    
    # Set the color limit
    vmin = np.min(color)
    vmax = np.max(color)
    
    # Define the colors for the values
    cmap_colors = ["purple", "blue","red", "orange", "yellow"]
    
    # Create a custom colormap
    cmap = mcolors.ListedColormap(cmap_colors)
    
    # Create a figure and axes
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Create a scatter plot with color intensity as a colormap
    heatmap = ax.scatter(x, y, c=color, cmap=cmap, s=30, vmin=vmin, vmax=vmax)
    
    # Set labels and title
    ax.set_xlabel("Long")
    ax.set_ylabel("Short")
    ax.set_title("Heatmap of all combinations")
    
    # Add a colorbar
    cbar = plt.colorbar(heatmap)
    cbar.set_label("Mean of Money through the 3 years")
    
    # Show the plot
    plt.show()