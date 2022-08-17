FROM continuumio/miniconda
MAINTAINER Lealia Xiong <lxiong@caltech.edu>

COPY environment.yml .
RUN \
   conda init zsh \
   && conda env create -f environment.yml \
   && conda activate gis