#!/bin/bash
mkdir -p /prj/datalakes/log
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate sentinel-hindcast-37
python /prj/datalakes/datalakes.py
