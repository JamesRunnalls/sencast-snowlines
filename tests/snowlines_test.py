#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Import libs, some of them might be unused here, but something magical happens when they are imported
# which causes geos_c.dll and objectify.pyx errors to disappear in windows.
import cartopy.crs
import netCDF4

import sys
sys.path.append("/media/jamesrunnalls/JamesSSD/Snowline/sencast-snowlines")

from main import hindcast

hindcast("/media/jamesrunnalls/JamesSSD/Snowline/sencast-snowlines/parameters/snowline_run_s2.ini")
