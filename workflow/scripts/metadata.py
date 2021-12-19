#!/usr/bin/env python3

# Usage
# ./metadata.py \
#  --db ../../results/sqlite_db/yersinia_pestis_db.sqlite \
#  --samples-csv SAMEA5054093 \
#  --world world.geo.json \
#  --output test.txt


# -----------------------------------------------------------------------------#
#                         Modules and Packages                                 #
# -----------------------------------------------------------------------------#

import argparse  # Command-line argument parsing
import sqlite3  # database queries
import os  # path manipulation
import datetime  # calculate current year
from geopy.geocoders import Nominatim  # Geocode addresses
import json


script_path = os.path.realpath(__file__)
scripts_dir = os.path.dirname(script_path)

# ------------------------------------------------------------------------------#
# Argument Parsing                                                              #
# ------------------------------------------------------------------------------#

parser = argparse.ArgumentParser(
    description=("Create a metadata tsv from pipeline data."), add_help=True,
)

# Argument groups for the program

parser.add_argument(
    "--db", help="Sqlite3 database.", action="store", dest="dbPath", required=True,
)

parser.add_argument(
    "--samples-csv",
    help="Sample names in CSV format.",
    action="store",
    dest="samplesCSV",
    required=True,
)

parser.add_argument(
    "--world",
    help="World Geo JSON.",
    action="store",
    default=os.path.join(scripts_dir, "world.geo.json"),
    dest="worldGeoJson",
    required=False,
)


parser.add_argument(
    "--output",
    help="Ouput TSV file path.",
    action="store",
    dest="outputPath",
    required=True,
)


# Retrieve user parameters
args = vars(parser.parse_args())

sqlite_db_path = args["dbPath"]
samples_csv = args["samplesCSV"]
world_geo_json_path = args["worldGeoJson"]
samples_list = samples_csv.split(",")
output_path = args["outputPath"]


# ------------------------------------------------------------------------------#
# Setup                                                                         #
# ------------------------------------------------------------------------------#


# Create a mapping of countries to continents
continent_dict = {}

with open(world_geo_json_path) as infile:
    data = json.load(infile)

for feature in data["features"]:

    country = feature["properties"]["admin"]
    continent = feature["properties"]["continent"]

    # Manual edits for Nominatim compatibility
    if country == "United Kingdom":
        country = "England"
    elif country == "Netherlands":
        country = "The Netherlands"
    continent_dict[country] = continent

# k = list(continent_dict.keys())
# k.sort()

geolocator = Nominatim(user_agent="ncov-phylogeography")

CURRENT_YEAR = datetime.datetime.utcnow().year

output_path_main = output_path
output_path_latlon = os.path.splitext(output_path_main)[0] + "_latlon.tsv"

geocode_dict = {}  # Name: [lat, lon]


# Output Headers
# 1. Nucleotide Accession
# 2. Isolate
# 3. Date
# 4. Country

output_headers_main = [
    "sample",
    "isolate",
    "collection_date",
    "country",
    "province",
    "species",
]

output_ref_vals = [
    "Reference",
    "Wuhan-Hu-1",
    "2019-12-XX",
    "China",
    "Hubei",
    "SARS-CoV-2"
]


# Nextstrain LatLon Format (no header)
# 1. Geo Level
# 2. Geo Name
# 3. Geo Lat
# 4. Geo Lon

output_delim = "\t"

conn = sqlite3.connect(sqlite_db_path)
cur = conn.cursor()

header = output_delim.join(output_headers_main)


# Write headers to file
with open(output_path_main, "w") as outfile:
    outfile.write(header + "\n")

# Write reference metadata to file
with open(output_path_main, "a") as outfile:
    # Write reference
    str_vals = [str(val) for val in output_ref_vals]
    outfile.write(output_delim.join(str_vals) + "\n")

for sample in samples_list:
    # Remove the _genomic suffix from assemblies
    assembly = False
    # Remove the assembly suffix genomic for query
    if "_genomic" in sample:
        sample = sample.replace("_genomic", "")
        assembly = True
    query = """
            SELECT
              NucleotideAccession,
              NucleotideIsolate,
              NucleotideCollectionDate,
              NucleotideCountry,
              NucleotideSpecies
            FROM
              Nucleotide
            WHERE
              NucleotideAccession LIKE '%{}%'
            """.format(
        sample, sample
    )

    result = cur.execute(query).fetchone()


    # Store the output values for the main file
    output_main_vals = [
        sample,  # sample [0]
        "NA",  # isolate [1]
        "NA",  # date [2]
        "NA",  # country [3]
        "NA",  # province [4]   
        "NA",  # species [5]                
    ]

    if result:

        # Accession
        isolate = result[1]
        if isolate:
            output_main_vals[1] = isolate

        # Collection Date
        date = result[2]
        if date:
            output_main_vals[2] = date

        # Collection Location
        location = result[3]
        if location:
            location_split = location.split(":")
            country = location_split[0]
            output_main_vals[3] = country 

            if len(location_split) > 1:
                province = location_split[1].lstrip()
                output_main_vals[4] = province

        species = result[4]
        if species:
            output_main_vals[5] = species


    # Write data to main output file
    with open(output_path_main, "a") as outfile:
        # Write samples
        str_vals = [str(val) for val in output_main_vals]
        outfile.write(output_delim.join(str_vals) + "\n")


cur = conn.cursor()
conn.close()
