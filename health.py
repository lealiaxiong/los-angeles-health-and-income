"""
Functions for health, median income analysis by census tract.
"""

import numpy as np
import pandas as pd

import holoviews as hv
import colorcet as cc

def load_health_data(health_file):
    """
    Load health data at tract resolution downloaded from 
    City Health Dashboard (https://www.cityhealthdashboard.com/).
    Returns DataFrame.
    """
    
    health_data = pd.read_csv(health_file, sep=' ', low_memory=False)
    health_data_tidy = health_data.pivot_table(
        index='stcotr_fips',
        columns='metric_name',
        values='est',
        aggfunc='mean'
    ).reset_index(
    )
    
    return health_data_tidy

def load_hinc_data(income_data_file):
    """
    Load 2018 median household income data (in 2020 inflation-adjusted dollars) 
    downloaded from the American Community Survey 
    (B19013 - https://data.census.gov/cedsci/table?q=B19013&t=Income%20%28Households,%20Families,%20Individuals%29).
    Truncates data - i.e. '2,500-' is converted to 2500; 
    '250,000+' is converted to 250000.
    Adds `stcotr_fips` column corresponding to 
    concatenation of State, County, Tract FIPS codes.
    Returns DataFrame.
    """
    income_data = pd.read_csv(
        income_data_file, header=[0,1]
    ).droplevel(
        level=1, axis=1
    ).rename(
        columns={
            'B19013_001E': 'median income', 
            'B19013_001M': 'margin of error'
        }
    )
    
    income_data['median income'] = income_data['median income'].replace("2,500-", 2500)
    income_data['median income'] = income_data['median income'].replace("-", np.nan)
    income_data['median income'] = income_data['median income'].replace("250,000+", 250000)
    income_data['median income'] = income_data['median income'].astype(float)
    income_data['stcotr_fips'] = income_data['GEO_ID'].str[-11:].astype(int)
    
    return income_data

def _plot_equal_line(y):
    """
    Plot line with slope 1 from min(y) to max(y):
    """
    return hv.Curve(
        [(np.min(y), np.min(y)), (np.max(y), np.max(y))],
        label='equal'
    ).opts(
        color='gray',
        line_dash='dashed',
    )

def plot_prediction_vs_actual(y_pred, y, label, log10=True):
    """
    Plot predicted value `y_pred` vs. actual value `y`.
    If `log10`, plot log10(predicted) vs. log10(actual) and predicted vs. actual.
    Marginal plots contain kernel density estimated distribution.
    """
    equal_line = _plot_equal_line(y)
    if log10:
        points = hv.Points(
            np.concatenate([y, y_pred], axis=1), 
            kdims=[f'actual log10({label})', f'predicted log10({label})']
        )
        xdist, ydist = (
            hv.Distribution(points, kdims=[dim]) 
            for dim in [f'actual log10({label})', f'predicted log10({label})']
        )
        equal_line2 = _plot_equal_line(10**y)
        points2 = hv.Points(
            np.concatenate([10**y, 10**y_pred], axis=1), 
            kdims=[f'actual {label}', f'predicted {label}']
        )
        xdist2, ydist2 = (
            hv.Distribution(points2, kdims=[dim]) 
            for dim in [f'actual {label}', f'predicted {label}']
        )

        plot = (
            (
                (points * equal_line).opts(legend_position='bottom_right') << 
                ydist << xdist
            ) + (
                (points2 * equal_line2).opts(legend_position='bottom_right') <<
                ydist2 << xdist2
            ).opts(
                hv.opts.Curve(axiswise=True)
            )
        )
    
    else:
        points = hv.Points(
            np.concatenate([y, y_pred], axis=1), 
            kdims=[f'actual {label}', f'predicted {label}']
        )
        xdist, ydist = (
            hv.Distribution(points, kdims=[dim]) 
            for dim in [f'actual {label}', f'predicted {label}']
        )

        plot = (
            (points * equal_line).opts(legend_position='bottom_right') << 
            ydist << xdist
        )
        
    return plot