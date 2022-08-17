FROM continuumio/miniconda
MAINTAINER Lealia Xiong <lxiong@caltech.edu>


FROM continuumio/miniconda3

RUN conda update conda
RUN pip install fiona
RUN pip install pyproj shapely
RUN pip install geopandas
RUN conda install -c pyviz holoviz
RUN conda install -c pyviz geoviews-core

COPY . .

CMD panel serve --address="0.0.0.0" --port=$PORT plot_health_data_choropleths_with_holc.py --allow-websocket-origin=lx-health-holc-map.herokuapp.com