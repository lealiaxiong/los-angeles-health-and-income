FROM continuumio/miniconda
MAINTAINER Lealia Xiong <lxiong@caltech.edu>

COPY environment.yml .

RUN conda env create -f environment.yml

RUN echo "conda activate gis" >> ~/.bashrc

SHELL ["/bin/bash", "--login", "-c"]

COPY . .

CMD panel serve --address="0.0.0.0" --port=$PORT plot_health_data_choropleths_with_holc.py --allow-websocket-origin=lx-health-holc-map.herokuapp.com