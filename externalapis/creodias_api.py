#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Sencast uses the CREODIAS API to query the image database in order to identify suitable images and also to download images.

Documentation for CREODIAS API can be found `here. <https://creodias.eu/eo-data-finder-api-manual>`_
"""

import os
import requests
from shutil import copytree, copyfile
from requests.status_codes import codes
from tqdm import tqdm
from zipfile import ZipFile
from pathlib import Path

# Documentation for CREODIAS API can be found here:
# https://creodias.eu/eo-data-finder-api-manual

# search address
search_address = "https://finder.creodias.eu/resto/api/collections/{}/search.json?{}"  #Sentinel3

# download address
download_address = "https://zipper.creodias.eu/download/{}?token={}"

# token address
token_address = 'https://auth.creodias.eu/auth/realms/DIAS/protocol/openid-connect/token'


def get_download_requests(auth, startDate, completionDate, sensor, resolution, wkt):
    query = "maxRecords={}&startDate={}&completionDate={}&instrument={}&geometry={}&productType={}&processingLevel={}"
    maxRecords = 1000
    geometry = wkt.replace(" ", "", 1).replace(" ", "+")
    satellite, instrument, productType, processingLevel = get_dataset_id(sensor, resolution)
    query = query.format(maxRecords, startDate, completionDate, instrument, geometry, productType, processingLevel)
    uuids, product_names, timelinesss, beginpositions, endpositions = search(satellite, query)
    uuids, product_names = timeliness_filter(uuids, product_names, timelinesss, beginpositions, endpositions)
    return [{'uuid': uuid} for uuid in uuids], product_names

def get_updated_files(auth, startDate, completionDate, sensor, resolution, wkt, publishedAfter):
    query = "maxRecords={}&startDate={}&completionDate={}&instrument={}&geometry={}&productType={}&processingLevel={}&publishedAfter={}"
    maxRecords = 1000
    geometry = wkt.replace(" ", "", 1).replace(" ", "+")
    satellite, instrument, productType, processingLevel = get_dataset_id(sensor, resolution)
    query = query.format(maxRecords, startDate, completionDate, instrument, geometry, productType, processingLevel, publishedAfter)
    uuids, product_names, timelinesss, beginpositions, endpositions = search(satellite, query)
    uuids, product_names = timeliness_filter(uuids, product_names, timelinesss, beginpositions, endpositions)
    return [{'uuid': uuid} for uuid in uuids], product_names

def timeliness_filter(uuids, product_names, timelinesss, beginpositions, endpositions):
    num_products = len(uuids)
    uuids_filtered, product_names_filtered, positions, timelinesss_filtered = [], [], [], []
    for i in range(num_products):
        curr_pos = (beginpositions[i], endpositions[i])
        if curr_pos in positions:
            curr_proj_idx = positions.index(curr_pos)
            if timelinesss[i] == 'Non Time Critical' and timelinesss_filtered[curr_proj_idx] == 'Near Real Time':
                timelinesss_filtered[curr_proj_idx] = timelinesss[i]
                uuids_filtered[curr_proj_idx] = uuids[i]
                product_names_filtered[curr_proj_idx] = product_names[i]
                positions[curr_proj_idx] = (beginpositions[i], endpositions[i])
            elif timelinesss[i] == 'Near Real Time' and timelinesss_filtered[curr_proj_idx] == 'Non Time Critical':
                continue
            else:
                timelinesss_filtered.append(timelinesss[i])
                uuids_filtered.append(uuids[i])
                product_names_filtered.append(product_names[i])
                positions.append((beginpositions[i], endpositions[i]))
        else:
            timelinesss_filtered.append(timelinesss[i])
            uuids_filtered.append(uuids[i])
            product_names_filtered.append(product_names[i])
            positions.append((beginpositions[i], endpositions[i]))
    return uuids_filtered, product_names_filtered


def do_download(auth, download_request, product_path, server):
    if server is not False:
        try:
            if local_download(product_path, server) is False:
                print("Failed to locate file on server, downloading file from API.")
                download(auth, download_request['uuid'], product_path)
        except Exception as e:
            print(e)
            print("Failed to copy file from server, downloading file from API.")
            download(auth, download_request['uuid'], product_path)
    else:
        download(auth, download_request['uuid'], product_path)



def get_dataset_id(sensor, resolution):
    if sensor == 'OLCI' and int(resolution) < 1000:
        return 'Sentinel3', 'OL', 'EFR', ''
    elif sensor == 'OLCI' and int(resolution) >= 1000:
        return 'Sentinel3', 'OL', 'ERR', ''
    elif sensor == 'MSI':
        return 'Sentinel2', 'MSI', '', 'LEVEL1C'
    else:
        raise RuntimeError("CREODIAS API is not yet implemented for sensor: {}".format(sensor))


def search(satellite, query):
    print("Search for products: {}".format(query))
    uuids, filenames = [], []
    timelinesss, beginpositions, endpositions = [], [], []
    while True:
        response = requests.get(search_address.format(satellite, query))
        if response.status_code == codes.OK:
            root = response.json()
            for feature in root['features']:
                uuids.append(feature['id'])
                filenames.append(feature['properties']['title'])
                timelinesss.append(feature['properties']['timeliness'])
                beginpositions.append(feature['properties']['startDate'])
                endpositions.append(feature['properties']['completionDate'])
            return uuids, filenames, timelinesss, beginpositions, endpositions
        else:
            raise RuntimeError("Unexpected response: {}".format(response.text))


def download(auth, uuid, filename):
    username = auth[0]
    password = auth[1]
    token = get_token(username, password)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    url = download_address.format(uuid, token)
    file_temp = "{}.incomplete".format(filename)
    try:
        downloaded_bytes = 0
        with requests.get(url, stream=True, timeout=100) as req:
            with tqdm(unit='B', unit_scale=True, disable=not True) as progress:
                chunk_size = 2 ** 20  # download in 1 MB chunks
                with open(file_temp, 'wb') as fout:
                    for chunk in req.iter_content(chunk_size=chunk_size):
                        if chunk:  # filter out keep-alive new chunks
                            fout.write(chunk)
                            progress.update(len(chunk))
                            downloaded_bytes += len(chunk)
        with ZipFile(file_temp, 'r') as zip_file:
            zip_file.extractall(os.path.dirname(filename))
    finally:
        try:
            Path(file_temp).unlink()
        except OSError:
            pass


def local_download(filepath, server):
    filename = os.path.basename(filepath)
    if parse_filename(filename) is False:
        return False
    satellite, sensor, product, year, month, day = parse_filename(filename)
    server_path = os.path.join(server,satellite,sensor,product, year, month, day, filename)
    if os.path.isfile(server_path):
        copyfile(server_path, filepath)
        return True
    elif os.path.isdir(server_path):
        copytree(server_path, filepath)
        return True
    else:
        return False


def parse_filename(filename):
    if "S3" in filename:
        satellite = "Sentinel-3"
        sensor = "OLCI"
        product = filename.split("____")[0].split("S3A_")[1]
        year, month, day = parse_date(filename.split("_")[7])
    elif "S2" in filename:
        satellite = "Sentinel-2"
        sensor = "MSI"
        product = "L1C"
        year, month, day = parse_date(filename.split("_")[2])
    else:
        return False
    return satellite, sensor, product, year, month, day


def parse_date(date):
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]
    return year, month, day

def get_token(username, password):
    token_data = {
        'client_id': 'CLOUDFERRO_PUBLIC',
        'username': username,
        'password': password,
        'grant_type': 'password'
    }
    response = requests.post(token_address, data=token_data).json()
    try:
        return response['access_token']
    except KeyError:
        raise RuntimeError(f'Unable to get token. Response was {response}')