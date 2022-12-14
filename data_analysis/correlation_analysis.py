"""
This file is implementing the correlation analysis. from the 2017 paper including:
    * Pearson's correlation coefficient
    * P-value
    * Regression analysis via linear regression     
"""
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from scipy.stats._result_classes import PearsonRResult
import pandas as pd
import numpy as np

def get_pearson(data:(dict or np.ndarray), alt:str='less', cutoff=100):
    """
    This function is calculating the Pearson's correlation coefficient which 
    "measures the linear relationship between two datasets".
    
    args:
        data_dict: dictionary of {x:y} values for the correlation analysis.
        alt: alternative hypothesis. Default is 'less' which means that the 
            correlation is negative.
        cutoff: the cutoff for the keys to include. Default is 100.
        
    return: 
        PearsonRResult: Pearson's correlation result (statistic, pvalue), 
            can also be used to specify convidence intervals.
    """
    if type(data) == dict:
        srtd = sorted(data.items())
        x = []
        y = []
        for s in srtd:
            if s[0] > cutoff: continue
            x.append(s[0])
            y.append(s[1])
    elif type(data) == np.ndarray:
        x, y = data[:,0], data[:,1]
        
    return pearsonr(x, y, alternative=alt)

def get_linear_reg(data_dict:(dict or np.ndarray)):
    """
    This function is calculating the linear regression of the data.
    
    args:
        data_dict: dictionary of {x:y} values for the correlation analysis.
        
    return: 
        tuple: (slope, intercept, r_value, p_value, std_err)
    """
    if type(data_dict) == dict:
        x, y = zip(*sorted(data_dict.items()))
    elif type(data_dict) == np.ndarray:
        x, y = data_dict[:,0], data_dict[:,1]
    return np.polyfit(x, y, 1)