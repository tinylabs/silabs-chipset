#!/usr/bin/env python3
#
# Parse matrix file and generate info file for all chipsets
#
# All rights reserved.
# Tiny Labs Inc
# 2019
#
import os
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
    # Remove japanese PDF extension
    d[key] = val.replace ('-jp', '')

mapping = {
    'Part Number' : (dmap, 'NAME'),
    'Data Sheet'  : (mapds, 'DATASHEET'),
    'Kit'         : (mapds, 'REFDES'),
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
    'Package Type'  : (dmap, 'PACKAGE'),
    'Package Size (mm)'  : (dmap, 'SIZE'),
    'Cryptography' : (cryptomap, 'CRYPTO'),
    'Ethernet'  : (yesnomap, 'ETH'),
    'LESENSE'  : (ignore, None),
    'Capacitive Sense'  : (yesnomap, 'CAPSENSE'),
    None : (ignore, None),
    }

# Takes a dictionary of key/val
# Returns a new standardized dictionary
def map_row (row, dict_map):
    ret = {}
    for key,val in row.items ():
        dict_map[key][0] (ret, dict_map[key][1], val)
    return ret

family = {
    'gecko'   : {
        'manual' : 'https://www.silabs.com/documents/public/reference-manuals/EFM32G-RM.pdf',
        'pagesize' : '512',
    },
    'giant'   : {
        'manual' : 'https://www.silabs.com/documents/public/reference-manuals/EFM32GG-RM.pdf',
        'pagesize' : '512',
    },        
    'giant-s1': {
        'manual' : 'https://www.silabs.com/documents/public/reference-manuals/EFM32GG12-RM.pdf',
        'pagesize' : '512',
    },        
    'happy'   : {
        'manual' : 'https://www.silabs.com/documents/public/reference-manuals/efm32hg-rm.pdf',
        'pagesize' : '512',
    },        
    'leopard' : {
        'manual' : 'https://www.silabs.com/documents/public/reference-manuals/EFM32LG-RM.pdf',
        'pagesize' : '512',
    },        
    'pearl'   : {
        'manual' : 'https://www.silabs.com/documents/public/reference-manuals/EFM32PG1-ReferenceManual.pdf',
        'pagesize' : '512',
    },        
    'jade'    : {
        'manual' : 'https://www.silabs.com/documents/public/reference-manuals/EFM32JG1-ReferenceManual.pdf',
        'pagesize' : '512',
    },        
    'tiny'    : {
        'manual' : 'https://www.silabs.com/documents/public/reference-manuals/EFM32TG-RM.pdf',
        'pagesize' : '512',
    },        
    'tiny-s1' : {
        'manual' : 'https://www.silabs.com/documents/public/reference-manuals/efm32tg11-rm.pdf',
        'pagesize' : '512',
    },        
    'wonder'  : {
        'manual' : 'https://www.silabs.com/documents/public/reference-manuals/EFM32WG-RM.pdf',
        'pagesize' : '512',
    },        
    'zero'    : {
        'manual' : 'https://www.silabs.com/documents/public/reference-manuals/EFM32ZG-RM.pdf',
        'pagesize' : '512',
    },        
    'precision': {
        'manual' : '',
        'pagesize' : '512',
    },        
}

decoder_ring = [
    { 'match'  : r'efm32gg1',
      'family' : 'giant-s1',
      're'     : r'(efm32gg1.b(...)f\d+)(.).+',
      'val'    : ('gdb_name', 'feature', 'temp', None),
    },
    { 'match'  : r'efm32gg',
      'family' : 'giant',
      're'     : r'(efm32gg(...)f\d+).+',
      'val'    : ('gdb_name', 'feature', None),
    },
    { 'match'  : r'efm32hg',
      'family' : 'happy',
      're'     : r'(efm32hg(...)f\d+).+',
      'val'    : ('gdb_name', 'feature', None),
    },
    { 'match'  : r'efm32lg',
      'family' : 'leopard',
      're'     : r'(efm32lg(...)f\d+).+',
      'val'    : ('gdb_name', 'feature', None),
    },
    { 'match'  : r'efm32pg1',
      'family' : 'pearl',
      're'     : r'(efm32pg1.*b(...)f\d+)(.).+',
      'val'    : ('gdb_name', 'feature', 'temp', None),
    },
    { 'match'  : r'efm32jg1',
      'family' : 'jade',
      're'     : r'(efm32jg1.*b(...)f\d+)(.).+',
      'val'    : ('gdb_name', 'feature', 'temp', None),
    },
    { 'match'  : r'efm32tg11b',
      'family' : 'tiny-s1',
      're'     : r'(efm32tg11b(...)f\d+)(.).+',
      'val'    : ('gdb_name', 'feature', 'temp', None),
    },
    { 'match'  : r'efm32tg',
      'family' : 'tiny',
      're'     : r'(efm32tg(...)f\d+).*',
      'val'    : ('gdb_name', 'feature', None),
    },
    { 'match'  : r'efm32wg',
      'family' : 'wonder',
      're'     : r'(efm32wg(...)f\d+).*',
      'val'    : ('gdb_name', 'feature', None),
    },
    { 'match'  : r'efm32zg',
      'family' : 'zero',
      're'     : r'(efm32zg(...)f\d+).*',
      'val'    : ('gdb_name', 'feature', None),
    },
    { 'match'  : r'efm32g',
      'family' : 'gecko',
      're'     : r'(efm32g(...)f\d+).+',
      'val'    : ('gdb_name', 'feature', None),
    },
    { 'match'  : r'sim3',
      'family' : 'precision',
      're'     : r'(sim3.(.)..)-.-(.).*',
      'val'    : ('gdb_name', 'feature', 'temp', None),
    },
]

def decode (name, ring):
    d = {}
    for r in ring:
        if re.match (r['match'], name):
        #if name.startswith (r['match']):
            d['family'] = r['family']
            match = re.search (r['re'], name)
            for i in range (len (r['val']) - 1):
                d[r['val'][i]] = match.group (i + 1)
            break
    return d

if __name__ == '__main__':

    # Setup argument parser
    parser = argparse.ArgumentParser ()

    # Add args
    parser.add_argument ("--infile", help='Chipset matrix')

    # Parse arguments
    args = parser.parse_args ()

    if args.infile is None:
        sys.exit ('Must pass chipset matrix')
        
    # Open CSV file 
    with open (args.infile, 'r', encoding='iso-8859-1') as fin:

        # Skip two header lines
        fin.readline ()
        fin.readline ()        
        reader = csv.DictReader (fin)

        # Loop through each row
        for row in reader:

            # Map to standardized fields
            nrow = map_row (row, mapping)

            # Skip any CM0 chipsets, not supported at this time
            if nrow['CORE'] == 'm0+':
                continue
            
            # Fill in other info
            nrow['TYPE'] = 'chipset'
            name = nrow['NAME']
            #print ("=> %s" % name)
            
            # Decode name info to family
            info = decode (name, decoder_ring) 
            if 'temp' not in info:
                info['temp'] = 'g'
            if info['temp'] == 'g':
                nrow['TEMP'] = '-40,85'
            elif info['temp'] == 'i':
                nrow['TEMP'] = '-40,125'

            # Save GDB name and interface
            nrow['CMFLAGS'] = 'GDB_NAME:' + info['gdb_name']
            nrow['CMFLAGS'] += ',GDB_IF:swd'
            nrow['CMFLAGS'] += ',BOOT_PAGE_SIZE:' + family[info['family']]['pagesize']
                                                           
            # Save reference manual
            nrow['MANUAL'] = family[info['family']]['manual']
            
            # Assemble files
            path = os.path.join (info['family'], '')
            nrow['FILES'] = ','.join ([path + 'core.map',
                                       path + 'irq.map',
                                       path + 'periph.map',
                                       path + 'clock.tree',
                                       'CMakeLists.txt',
                                       os.path.join (path + info['feature'], 'driver.map'),
            ])

            # Fill in short and long descriptions
            nrow['SHORT'] = 'Silabs ' + info['family'].capitalize() + ' C' + \
                            nrow['CORE'].upper()
            nrow['LONG'] =  nrow['FLASH'] + 'kB flash/' + nrow['RAM'] +\
                            'kB RAM ' + nrow['PACKAGE'].upper()

            # Check for dependencies
            try:
                deps = []
                with open (os.path.join (info['family'], 'depends')) as fdep:
                    for line in fdep:
                        deps.append (line.strip ())
                nrow['DEPENDS'] = ','.join (deps)
            except:
                pass

            # Dump to stdout (redirect to info)
            print ("[%s]" % name)
            for key,val in nrow.items():
                if key != 'NAME':
                    print ("\t%s=%s" % (key, val))
            print ()
                
