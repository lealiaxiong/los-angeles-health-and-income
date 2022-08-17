FROM continuumio/miniconda
MAINTAINER Lealia Xiong <lxiong@caltech.edu>

COPY environment.yml .
RUN \
   conda env create -f environment.yml