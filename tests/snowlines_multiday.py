#! /usr/bin/env python
# -*- coding: utf-8 -*-

package_location = "/home/ubuntu/sencast-snowlines"
output_location = "/home/ubuntu/DIAS/output_data"
clear_downloads = "/home/ubuntu/DIAS/input_data/OLCI_L1"
parameter_file = "snowline_run.ini"

import sys
sys.path.append(package_location)

import datetime
import os
import shutil
from auxil import load_params
from main import hindcast

params, params_file = load_params(os.path.join(package_location, "parameters", parameter_file))

start_date = datetime.datetime(2020, 12, 18)
number_of_days = 4

for days in range(number_of_days):
    # Remove .ini file
    process_date = start_date + datetime.timedelta(days=days)
    str_time = process_date.strftime(r"%Y-%m-%d")
    folder_name = "{}_sui_{}_{}".format(parameter_file.split(".")[0], str_time, str_time)
    par_file = os.path.join(output_location, folder_name, parameter_file)
    if os.path.exists(par_file):
        os.remove(par_file)
    folders = ["L2SNOW"]
    for folder in folders:
        temp_folder = os.path.join(output_location, folder_name, folder)
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)

    params['General']['start'] = process_date.strftime(r"%Y-%m-%d") + "T00:00:00.000Z"
    params['General']['end'] = process_date.strftime(r"%Y-%m-%d") + "T23:59:59.999Z"
    with open(params_file, "w") as f:
        params.write(f)

    hindcast(params_file, max_parallel_downloads=1, max_parallel_processors=1, max_parallel_adapters=1)

    if os.path.exists(clear_downloads):
        print("Deleting downloads")
        shutil.rmtree(clear_downloads)
