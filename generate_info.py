#!/usr/bin/env python3
#
# Parse matrix file and generate info file for all chipsets
#
# All rights reserved.
# Tiny Labs Inc
# 2019
#
import re
import sys
import csv
import argparse
from collections import OrderedDict


def ignore (d, key, val):
    pass

def dmap (d, key, val):
    d[key] = val.lower ()

def yesnomap (d, key, val):
    if val.lower() == 'yes':
        d[key] = '1'
    else:
        d[key] = '0'

def coremap (d, key, val):
    d[key] = val.replace ('ARM Cortex-', '').lower()

def oscmap (d, key, val):
    d[key] = val[1:]

def analogmap (d, key, val):
    if val != '%u2014':
        val = val.replace (' ', '')
        val = val.replace ('.', '')
        if key in d.keys ():
            if d[key] == val:
                d[key] = '2x' + val
            else:
                d[key] = d[key] + '/' + val
        else:
            d[key] = val

def cryptomap (d, key, val):
    rmhtml = re.compile ('<.*?>')
    val = re.sub (rmhtml, '', val)
    val = val.replace ('"', '')
    val = val.replace ('-', '')    
    d[key] = ','.join (val.split (' ')).lower ()

def commap (d, key, val):
    rmhtml = re.compile ('<.*?>')
    val = re.sub (rmhtml, '', val)
    val = val.replace ('"', '')
    # Replace superscript 2
    val = val.replace (u'\u00b2', '2')
    val = val.replace (' x ', '-')
    periphs = val.split (' ')
    for p in periphs:
        (cnt, name) = p.split ('-')
        d[name.upper ()] = cnt

def mapds (d, key, val):
    # Remove japan extension
    d[key] = val.replace ('-jp', '')

def packagemap (d, key, val):
    d[key] = val.lower ()
    # If name ends with package then remove from name
    if d['NAME'].endswith ('-' + val.lower ()):
        d['NAME'] = d['NAME'].replace ('-' + val.lower (), '')
    
mapping = {
    'Part Number' : (dmap, 'NAME'),
    'Data Sheet'  : (mapds, 'DATASHEET'),
    'Kit'         : (ignore, None),
    'MCU Core'    : (coremap, 'CORE'),
    'Core Frequency' : (dmap, 'FREQ'),
    'Flash (kB)'  : (dmap, 'FLASH'),
    'RAM (kB)'    : (dmap, 'RAM'),
    'Dig I/O'     : (dmap, 'IO'),
    'Communications'  : (commap, None),
    'USB'         : (yesnomap, 'USB'),
    'EMIF'        : (dmap, 'EBI'),
    'CAN'         : (dmap, 'CAN'),
    'Timers (16-bit)'  : (dmap, 'TIMER'),
    'PCA Channels'  : (ignore, None),
    'Internal Oscillator'  : (oscmap, 'OSC_PREC'),
    'Comparators' : (dmap, 'COMPARATOR'),
    'LIN'         : (ignore, None),
    'ADC 1'       : (analogmap, 'ADC'),
    'ADC 2'       : (analogmap, 'ADC'),
    'DAC'         : (analogmap, 'DAC'),
    'Package Type'  : (packagemap, 'PACKAGE'),
    'Package Size (mm)'  : (dmap, 'SIZE'),
    'Cryptography' : (cryptomap, 'CRYPTO'),
    'Ethernet'  : (yesnomap, 'ETH'),
    'LESENSE'  : (ignore, None),
    'Capacitive Sense'  : (yesnomap, 'CAPSENSE'),
    None : (ignore, None),
    }

# Takes a dictionary of key/val
# Returns a new dictionary
def map_row (row, dict_map):
    ret = {}
    for key,val in row.items ():
        dict_map[key][0] (ret, dict_map[key][1], val)
    return ret

if __name__ == '__main__':

    # Setup argument parser
    parser = argparse.ArgumentParser ()

    # Add args
    parser.add_argument ("--infile", help='Chipset matrix')

    # Parse arguments
    args = parser.parse_args ()

    if args.infile is None:
        sys.exit ('Must pass input matrix')
        
    # Open CSV file 
    with open (args.infile, 'r', encoding='iso-8859-1') as file:
        # Skip two lines
        file.readline ()
        file.readline ()        
        reader = csv.DictReader (file)

        # Loop through each row
        for row in reader:
            nrow = map_row (row, mapping)
            # Fill in other info
            nrow['TYPE'] = 'chipset'
            for key,val in nrow.items():
                print ("%s=%s" % (key, val))
            print ()
                #print ("'%s'  : (ignore, None)," % (key))
                
            #break

        
