#!/bin/bash

conda env create -f environment.yml

conda activate dg

pip install -r requirements.txt