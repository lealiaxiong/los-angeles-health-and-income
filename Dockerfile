FROM continuumio/miniconda
MAINTAINER Lealia Xiong <lxiong@caltech.edu>

COPY environment.yml .

RUN conda env create -f environment.yml

RUN echo "conda activate myenv" >> ~/.bashrc

SHELL ["/bin/bash", "--login", "-c"]