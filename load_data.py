"""
Load geospatial and health.
"""
import pandas as pd
import geopandas as gpd

def load_census_tracts(census_tracts_shapefile, county_name='Los Angeles County'):
    """Load US Census tracts shapefile and return GeoDataFrame."""
    
    gdf = gpd.read_file(census_tracts_shapefile)
    gdf = gdf.loc[gdf['NAMELSADCO'] == county_name]
    
    return gdf

def load_health_data(health_data_file, county_name='Los Angeles County'):
    """Load City Health Dashboard data and return DataFrame."""
    
    health_data = pd.read_csv(
        health_data_file, 
        sep=' '
    ).dropna(
        subset='est'
    )
    
    # Select county data
    health_data = health_data.loc[
        health_data['county_name'] == county_name
    ]
    
    health_data = health_data.pivot_table(
        index=[
            'stcotr_fips', 
            'county_name', 
            'city_name'
        ],
        columns='metric_name',
        values='est',
        aggfunc='mean'
    ).reset_index(
    )
    
    # Add key for joining with census tracts shapefile
    health_data['TRACTCE'] = health_data['stcotr_fips'].astype(str).str[-6:]
    
    return health_data
    
def load_holc_data(holc_shapefile):
    """Load historical HOLC grades shapefile and return GeoDataFrame."""
    
    gdf_holc = gpd.read_file(holc_shapefile)
    
    return gdf_holc

def make_health_metric_gdf(
    health_metric,
    census_tracts_gdf, 
    health_data, 
    county_name='Los Angeles County'
):
    """Make GeoDataFrame for health metric."""
    
    return pd.merge(
        census_tracts_gdf, 
        health_data[['TRACTCE', health_metric, 'city_name']]
    ).drop_duplicates(
        subset=['TRACTCE']
    )