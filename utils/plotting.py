from data_analysis.monte_carlo import ReviewProb
from data_analysis.rating_analysis import RatingAnalysisFriends, RatingAnalysisGeneral
from common.config_paths import (
            YELP_REVIEWS_PATH, YELP_USER_PATH, 
            MC_RESULTS_PATH, RESULTS, RATINGS_CORR_PATH)
from common.constants import restaurant_categories
from utils.query_raw_yelp import QueryYelp as qy
from data_analysis.correlation_analysis import get_pearson, get_linear_reg
from scipy.stats import pearsonr
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pickle
import math

def get_pkl_path(dir_path, time_period):
    t_s = f"{time_period[0].strftime('%Y-%m-%d')}_{time_period[1].strftime('%Y-%m-%d')}"
    path = lambda x: f"{dir_path}{t_s}{x}.pkl"
    return path, t_s

def get_mc_pkl_path(dir_path, time_period):
    # path -> {dir_path}/{t_s}_prob_0.pkl
    path = lambda x: get_pkl_path(dir_path, time_period)(f"_prob_{x}")
    
    data_0 = pickle.load(open(path(0), "rb"))
    data_1 = pickle.load(open(path(1), "rb"))
    
    return data_0, data_1
    
def bin_data(data, bins=[x for x in range(0,51,5)], ignore_exact=[0,1]):
    """
    This function is binning the data into bins number of bins.
    """
    binned_d = {k: 0 for k in bins}
    for i in range(len(bins)):
        l = bins[i]
        r = bins[i+1] if i < len(bins)-1 else math.inf # last bin is open ended
        for k,v in data.items():
            if ignore_exact and k in ignore_exact: continue
            if l <= k and k <= r:
                binned_d[l] += v
    return binned_d

def plot_bins(binned_d0, binned_d1=None):
    """_summary_

    Args:
        binned_d0 (dict): {bin: count}
        binned_d1 (_type_, optional): _description_. Defaults to None.
    """
    if binned_d1 is None:
        data = np.array([[x,y] for x,y in binned_d0.items()])
        plt.bar(data[:,0], data[:,1], width=5, align='edge')
    else: # grouped bar chart
        data_0 = np.array([[x,y] for x,y in binned_d0.items()])
        data_1 = np.array([[x,y] for x,y in binned_d1.items()])
        
        h0 = plt.bar(data_0[:,0], data_0[:,1], width=2.5, align='edge')
        h1 = plt.bar(data_1[:,0]+2.5, data_1[:,1], width=2.5, align='edge')
        
        plt.legend((h0[0], h1[0]), ('P(0|i)', 'P(1|i)'))

def plot_mc_prob(time_periods):
    MC_PATH_PKL = "results/monte_carlo_prob0/"
    MC_PATH_MEDIA = "media/monte_carlo_prob01_binned/"
    bins = [x for x in range(0,51,5)]
    ignore_exact = [0,1]
    for t in time_periods[:5]:
        path, t_s = get_pkl_path(MC_PATH_PKL, t)
        
        data_0 = pickle.load(open(path("_prob_0"), "rb"))
        data_1 = pickle.load(open(path("_prob_1"), "rb"))
        
        bd_0 = bin_data(data_0, bins, ignore_exact)
        bd_1 = bin_data(data_1, bins, ignore_exact)
        
        plot_bins(bd_1, bd_0)
        
        plt.xlabel("Number of i friends who reviewed same business")
        plt.ylabel("Monte Carlo probability")
        plt.title(f"{t_s}: Ignoring i={ignore_exact}")
        
        i_str = "".join([str(x) for x in ignore_exact])
        plt.savefig(f"{MC_PATH_MEDIA}{t_s}_prob_01_i{i_str}.png")
        plt.show()
        plt.clf()

def plot_over_time(data, time_periods, idx=0): # idx picks the elemnt of the tuple in data
    """_summary_

    Args:
        data (list of pears): must be of shape (t,2,2) where t = len(time_periods)
            * for one time period data is of shape (2,2)
                * rows are for P(0|i) and P(1|i)
        time_periods (_type_): _description_
    """
    idx = 0
    w = 0.4
    data = np.array(data)
    y_pos = list(range(len(data)))
    d_0 = data[:, 0, idx]
    d_1 = data[:, 1, idx]
    fig, ax = plt.subplots()
    h0 = ax.bar([y-w/2 for y in y_pos], d_0[::-1], width=w, align='center')
    h1 = ax.bar([y+w/2 for y in y_pos], d_1[::-1], width=w, align='center')
    plt.legend((h0[0], h1[0]), ('P(0|i)', 'P(1|i)'), loc='upper left')
    _=ax.set_xticks(y_pos,
        labels=[f"{p[0].strftime('%Y')}-{p[1].strftime('%Y')}" for p in time_periods][::-1])

def plot_mc_prob_compare(time_periods, ignore_exact=[0,1], 
                         bins=[x for x in range(0,51,5)], save_path=None):
    MC_PATH_PKL = "results/monte_carlo_prob0/"
    MC_PATH_MEDIA = "media/monte_carlo_prob01_binned/"
    pears = []
    lines = []
    print("{:25}|{:^10}|{:^10}|{:^10}|{:^10}".format(
            "period", "coeff", "p-value", "slope","intercept"))
    print("-"*55)
    for t in time_periods:
        path, t_s = get_pkl_path(MC_PATH_PKL, t)
        data_0 = pickle.load(open(path("_prob_0"), "rb"))
        data_1 = pickle.load(open(path("_prob_1"), "rb"))
        bd_0 = bin_data(data_0, bins, ignore_exact)
        bd_1 = bin_data(data_1, bins, ignore_exact)
        
        # calculating pearson correlation and linear regression
        pear_0 = get_pearson(bd_0, alt="two-sided")
        line_0 = get_linear_reg(bd_0)
        
        pear_1 = get_pearson(bd_1, alt="two-sided")
        line_1 = get_linear_reg(bd_1)
        
        pear = [pear_0, pear_1]
        line = [line_0, line_1]
        
        pears.append(pear)
        lines.append(line)
        
        print("{:25}|{:^10.3}|{:^10.3}|{:^10.3}|{:^10.3}".format(
            t_s,pear[0][0]-pear[1][0], # coeff diff
                pear[0][1]-pear[1][1], # p-value diff
                line[0][0]-line[1][0], # slope diff
                line[0][1]-line[1][1], )) # intercept diff
    
    plot_over_time(pears, time_periods)
    plt.title("Monte Carlo Probability Correlation")
    plt.xlabel("Time Period")
    plt.ylabel("Pearson Correlation Coefficient")
    
    if save_path:
        plt.savefig(save_path+"/all_corr.png")
    plt.clf()
    
    plot_over_time(lines, time_periods)
    plt.title("Monte Carlo Probability Regression")
    plt.xlabel("Time Period")
    plt.ylabel("Line Slope")

    if save_path:
        plt.savefig(save_path+"/all_lin.png")
    plt.clf()
        
    return pears, lines
   