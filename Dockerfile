FROM continuumio/miniconda
MAINTAINER Lealia Xiong <lxiong@caltech.edu>


FROM continuumio/miniconda3

RUN conda install -c pyviz holoviz
RUN conda install -c pyviz geoviews-core
RUN conda install geopandas

COPY . .
CMD panel serve --address="0.0.0.0" --port=$PORT main.py --allow-websocket-origin=worldbank-climate-dashboard.herokuapp.com

COPY . .

CMD panel serve --address="0.0.0.0" --port=$PORT plot_health_data_choropleths_with_holc.py --allow-websocket-origin=lx-health-holc-map.herokuapp.com