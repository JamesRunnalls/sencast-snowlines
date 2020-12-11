#! /usr/bin/env python
# -*- coding: utf-8 -*-

package_location = "/home/ubuntu/sencast-snowlines"
parameter_file = "snowline_run.ini"
clear_downloads = "/home/ubuntu/DIAS/input_data/OLCI_L1"

import sys
sys.path.append(package_location)

import datetime
import os
import shutil
from auxil import load_params
from main import hindcast

params, params_file = load_params(os.path.join(package_location, "parameters", parameter_file))

start_date = datetime.datetime.now()
params['General']['start'] = start_date.strftime(r"%Y-%m-%d") + "T00:00:00.000Z"
params['General']['end'] = start_date.strftime(r"%Y-%m-%d") + "T23:59:59.999Z"
with open(params_file, "w") as f:
    params.write(f)

hindcast(params_file, max_parallel_downloads=1, max_parallel_processors=1, max_parallel_adapters=1)

if os.path.exists(clear_downloads):
    print("Deleting downloads")
    shutil.rmtree(clear_downloads)