"""
Plot choropleths of recent health data and 1939 HOLC grades in Los Angeles.
"""
import os 
import json

import numpy as np
import pandas as pd

import geopandas as gpd
import geoviews as gv
import geoviews.tile_sources as gts
gv.extension('bokeh')

import panel as pn

from load_data import *
    
def plot_interactive_health_choropleth(
    census_tracts_gdf, 
    health_data, 
    gdf_holc, 
    xlim_webmerc,
    ylim_webmerc, 
    county_name='Los Angeles County'
):
    """
    Plot interactive choropleth of health data with 
    dropdown for selecting health metric and toggle for 
    historical HOLC grade overlay as Panel layout.
    """
    
    # Get list of metrics sorted by weight in regression
    try:
        with open('metrics_sorted_by_weight.json', 'r') as f:
            metrics_json = json.load(f)
            metrics = json.loads(metrics_json)
    except:
        metrics = list(health_data.columns)
        for entry in ['stcotr_fips', 'county_name', 'city_name', 'TRACTCE']:
            metrics.remove(entry)
        
    gdf_metric_dict = {
        health_metric: make_health_metric_gdf(
            health_metric,
            census_tracts_gdf, 
            health_data, 
            county_name='Los Angeles County'
        ) for health_metric in metrics
    }
    
    # Make panel widgets
    metric_select = pn.widgets.Select(
        name='', 
        options=list(metrics)
    )

    holc_toggle = pn.widgets.Toggle(name='Overlay historical HOLC ratings', button_type='primary')

    widgets = pn.Row(
        pn.Spacer(width=15),
        metric_select,
        pn.Spacer(width=15),
        holc_toggle,
        align='center'
    )
    
    # Make plot
    @pn.depends(metric_select.param.value, holc_toggle.param.value)
    def plot_health_choropleth(
        health_metric='Air pollution - particulate matter', 
        overlay_holc=False
    ):

        gdf_metric = gdf_metric_dict[health_metric]
        metric_shapes = gv.Polygons(gdf_metric, vdims=[health_metric, 'city_name'], group='metric')

        tile = gts.StamenToner()

        frame_width=800
        aspect = abs((ylim_webmerc[1] - ylim_webmerc[0]) / (xlim_webmerc[1] - xlim_webmerc[0]))
        frame_height = int(frame_width * aspect)

        poly_opts = dict(alpha=0.4, tools=['hover'])
        WMTS_opts = dict(xlim=xlim_webmerc, ylim=ylim_webmerc, frame_width=frame_width, frame_height=frame_height)

        metric_choropleth = (tile * metric_shapes).opts(
            gv.opts.Polygons(**poly_opts),
            gv.opts.Polygons('metric', title=f"{health_metric} in {county_name}", cmap='cividis', colorbar=True),
            gv.opts.WMTS(**WMTS_opts)
        )

        def click_policy(plot, element):
            plot.state.legend.click_policy = 'hide'

        if overlay_holc:
            gv.Store.add_style_opts(
                gv.Polygons, 
                [
                    'hatch_pattern', 
                    'hatch_color', 
                    'hatch_alpha', 
                    'hatch_scale'
                ], 
                'bokeh'
            )
            hatches = ['-', '/', '\\', 'x']
            gdf_holc['hatch'] = gdf_holc['holc_grade'].map(
                {
                    'A': hatches[0], 
                    'B': hatches[1], 
                    'C': hatches[2], 
                    'D': hatches[3]
                }
            )
            gdf_holc['hatch_scale'] = gdf_holc['hatch'].map(
                {
                    '-': 5, '/': 10, '\\': 10, 'x': 5
                }
            )
            holc_overlay = gv.Polygons(
                gdf_holc, vdims=['holc_grade', 'hatch', 'hatch_scale'], group='holc'
            )

            return (metric_choropleth * holc_overlay).opts(
                gv.opts.Polygons(
                    'holc', 
                    hatch_pattern='hatch', 
                    hatch_color='gray', 
                    hatch_scale='hatch_scale',
                    alpha=0.01, 
                    hatch_alpha=0.5,
                    show_legend=True,
                    legend_position='bottom_left',
                ),
                gv.opts.Overlay(
                    hooks=[click_policy]
                )
            )

        return metric_choropleth
    
    return pn.Column(plot_health_choropleth, pn.Spacer(height=15), widgets)

# Make panel layout
    
county_name = 'Los Angeles County'

# Filenames
census_tracts_shapefile = os.path.join('CA_2021_census_tracts_500k', 'CA_2021_census_tracts_500k.shp')
health_data_file = 'CA_health_data_by_census_tract.txt'
holc_shapefile = os.path.join('CA_Los_Angeles_HOLC', 'CA_Los_Angeles_HOLC.shp')

# Load data
census_tracts_gdf = load_census_tracts(census_tracts_shapefile, county_name=county_name)
health_data = load_health_data(health_data_file, county_name=county_name)
gdf_holc = load_holc_data(holc_shapefile)

# Bounding box
with open('lims_webmerc.json', 'r') as f:
            lims_json = json.load(f)
            lims_webmerc = json.loads(lims_json)
            
xlim_webmerc = (lims_webmerc[0], lims_webmerc[1])
ylim_webmerc = (lims_webmerc[2], lims_webmerc[3])

layout = plot_interactive_health_choropleth(
    census_tracts_gdf, 
    health_data, 
    gdf_holc, 
    xlim_webmerc,
    ylim_webmerc,
    county_name=county_name
)

layout.servable()