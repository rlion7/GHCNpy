# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Weather Data from Global Historical Climate Norms Daily
#
# Original code from: https://github.com/jjrennie/GHCNpy
# Modified by: Robert Lion
#
# ## Modifications: 
# * Ported to Python 3
# * Added Pandas DataFrame output
#
# ## Future Improvements:
# * Add averaging / combination feature to pool data from multiple stations
# * Lots and lots of cleanup to smooth out the original functions
# * In particular, some calls will just re-download files that you may already have, so this could be improved to prevent downloading (with option to download new file, as they're updated daily at the source location.
# * Update functions to allow batch outputs of multiple stations

import ghcnpy as gp
import pandas as pd
import numpy as np
import datetime

# ## Input the latitude and longitude of your target location.
# Google maps is a nice convenient source.

# +
# lat and lon in decimal format
lat = -18.831751
lon = 48.308693

# distance threshold (km from target)
dist = 200

# print a list of stations within range
gp.find_station(lat, lon, dist)

# future feature, maybe, put station names into DataFrame
# stn_cols = ['GHCN_ID','LAT','LON','ELEV','ST','STATION_NAME']
# stn_df = pd.DataFrame(gp.find_station(lat, lon, dist), columns=stn_cols)
# -

# ## Create raw CSV file
# Select the station ID (GHCND ID) from the list above and paste it into the output function below. 
# The output CSV file is generated from the source file (a fixed-width text file).
# Limited cleanup is done as follows:
# * Original data is one line per measurement with 31 value fields (i.e. one line for TMAX for January, one line for TMIN for January, etc.)
# * The data is reshaped so each line contains one day with all possible measurements.
# * A huge number of missing values are generated as each weather station may not report all possible measurements. These are left in this raw CSV file and removed later.

station_id = "MA000067095"
gp.output_to_csv(station_id)

# ## Convert the csv to a Pandas DataFrame
# Initial data cleanup is automated as follows:
# * Missing values (-9999.9) are replaced with NaN
# * Columns with no real values are dropped (i.e. station doesn't track that data)
# * Date column is created from YYYY MM DD parts, non-real dates are dropped (e.g. Feb 30)
# * Dates in the future are dropped

df = gp.csv_to_dataframe(station_id)

# ## Output Sample
# Output below shows end of DataFrame for review.

df.tail(50)

# ## Write Cleaned CSV
# The clean DataFrame object is written out as a CSV.

last_date_str = str(df.iloc[-1,0]) + str(df.iloc[-1,1]) + str(df.iloc[-1,2])
out_path = station_id + "_cln_" + last_date_str + ".csv"
df.to_csv(out_path)

# ## END
