#!/usr/bin/python

import sys
import argparse
import os.path
import json
import csv

arg_parser = argparse.ArgumentParser(description='Parse New Jersey Count data.')
arg_parser.add_argument('configfile', type=str, nargs=1)
args = arg_parser.parse_args()

def validateArgs( p_args ):
    if os.path.isfile(args.configfile[0]) != True:
        sys.exit('ERROR: Config File ' + args.configfile[0] + ' does not exist')
    else:
        print ' Using config file ' + args.configfile[0]
    return

def readJsonConfig ( p_args ):
    with open(p_args.configfile[0]) as config_file:
        config_data = json.load(config_file)
    return config_data

def openOutputFile( p_config ):
    full_output_file = os.path.join(p_config['output_directory'], p_config['output_file'])
    try:
        f = open( full_output_file, 'w') 
        writer = csv.writer(f, quoting=csv.QUOTE_NONE)
    except:
        sys.exit('ERROR: Could not open output file: ' + full_output_file)
    return writer

def print_header( p_outfile):
    p_outfile.writerow( ('county','office','district','party','candidate','votes') )
    return

def doesJsonKeyExist( p_config, p_key ):
    key_exists = True
    if p_key not in p_config:
        key_exists = False
    return key_exists

def get_county_name(p_infile):
    return

def clean_text_values(p_text):
    clean_text = p_text.replace(',', '')
    return clean_text

def populate_candidate_party_lists( p_candidateList, p_partyList, p_header):
    counter = 0
    value0 = ""
    value1 = ""
    for value in p_header.split('\r'):
        if counter == 0:
            value0 = value
        elif counter == 1:
            value1 = value
        counter = counter + 1
    if counter > 1:
        p_candidateList.append(value0)
        p_partyList.append(value1)
    return

def print_county_totals( p_candidateList, p_partyList, p_line, p_outfile, p_config):
    for i in range(len(p_line)):
        if i > 0:
            p_outfile.writerow((p_config['county'], 
                                p_config['office'],
                                p_config['district'],
                                p_partyList[i-1], 
                                p_candidateList[i-1], 
                                clean_text_values(p_line[i]) 
                               ))
    return

def process_header_line( p_candidateList, p_partyList, p_line):
    for header in p_line:
        populate_candidate_party_lists(p_candidateList, p_partyList, header)
    return

def process_data_line( p_candidateList, p_partyList, p_line, p_outfile, p_config):
    if "TOTAL" in p_line[0].upper():
        print_county_totals(p_candidateList, p_partyList, p_line, p_outfile, p_config)
    return

def process_single_file(p_config, p_outfile, p_infile):
    counter = 0
    candidateList = []
    partyList = []
    if os.path.isfile(p_infile) != True:
        print 'ERROR: Input File ' + p_infile + ' does not exist'
    else:
        with open(p_infile, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for line in csvreader:
                counter = counter + 1
                if counter == 1:
                    process_header_line(candidateList, partyList, line)
                else:
                    process_data_line(candidateList, partyList, line, p_outfile, p_config)
    return

def process_input_files(p_config, p_outfile, p_config_key):
    input_path = p_config[p_config_key]['input_directory']
    race_data = p_config[p_config_key]
    for input_file in race_data['input_files']:
        full_input_file = os.path.join(input_path, input_file["file"])
        process_single_file(input_file, p_outfile, full_input_file)
    return

def process_single_race( p_config, p_outfile, p_config_key):
    if doesJsonKeyExist(p_config, p_config_key):
        print ' Found data for ' + p_config_key + '. Processing this race.'
        process_input_files(p_config, p_outfile, p_config_key)
    else:
        print ' Config file doesn\'t contain data for ' + p_config_key + '. Skipping this race.'
    return

def process_config_data(p_config, p_outfile):
    print_header(p_outfile)
    process_single_race(p_config, p_outfile, 'president')
    process_single_race(p_config, p_outfile, 'us_house')
    return

validateArgs( args )
config = readJsonConfig( args )
out_file = openOutputFile(config)
try:
    process_config_data(config, out_file)
except:
    print sys.exc_info()[0]

