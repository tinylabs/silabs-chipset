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
    if val is not '':
        d[key] = ','.join (val.split (' ')).lower () + ','

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

def mapble (d, key, val):
    if val.lower() == 'yes':
        if key in d.keys():
            d[key] += 'ble,'
        else:
            d[key] = 'ble,'
def mapble5 (d, key, val):
    if val.lower() == 'yes':
        if key in d.keys():
            d[key] += 'ble5,'
        else:
            d[key] = 'ble5,'
def map2M (d, key, val):
    if val.lower() == 'yes':
        if key in d.keys():
            d[key] += '2M phy,'
        else:
            d[key] = '2M phy,'
def mapLR (d, key, val):
    if val.lower() == 'yes':
        if key in d.keys():
            d[key] += 'lr,'
        else:
            d[key] = 'lr,'
def mapzigbee (d, key, val):
    if val.lower() == 'yes':
        if key in d.keys():
            d[key] += 'zigbee,'
        else:
            d[key] = 'zigbee,'
def mapthread (d, key, val):
    if val.lower() == 'yes':
        if key in d.keys():
            d[key] += 'thread,'
        else:
            d[key] = 'thread,'
def mapP2G (d, key, val):
    if val.lower() == 'yes':
        if key in d.keys():
            d[key] += 'prop-2G,'
        else:
            d[key] = 'prop-2G,'
def mapPSub (d, key, val):
    if val.lower() == 'yes':
        if key in d.keys():
            d[key] += 'prop-SubG,'
        else:
            d[key] = 'prop-SubG,'

def rxCurr (d, key, val):
    d[key] = val + 'mA'
    
def mapOutputPwr (d, key, val):
    rmhtml = re.compile ('<.*?>')
    val = re.sub (rmhtml, '', val)
    val = val.replace ('"', '')
    val = val.strip ()
    d[key] = ','.join (val.split (' ')).lower () + 'dBm'

def mapFreq (d, key, val):
    rmhtml = re.compile ('<.*?>')
    val = re.sub (rmhtml, '', val)
    val = val.replace ('"', '')
    val = val.strip ()
    if val != 'null':
        d[key] = ','.join (val.split (' ')).lower () + 'MHz'

def mapAES128 (d, key, val):
    if val.lower() == 'yes':
        if key in d.keys ():
            d[key] += 'aes128,'
        else:
            d[key] = 'aes128,'

def mapAES256 (d, key, val):
    if val.lower() == 'yes':
        if key in d.keys ():
            d[key] += 'aes256,'
        else:
            d[key] = 'aes256,'

def mapECC (d, key, val):
    if val.lower() == 'yes':
        if key in d.keys ():
            d[key] += 'ecc,'
        else:
            d[key] = 'ecc,'

def mapSHA1 (d, key, val):
    if val.lower() == 'yes':
        if key in d.keys ():
            d[key] += 'sha1,'
        else:
            d[key] = 'sha1,'

def mapSHA2 (d, key, val):
    if val.lower() == 'yes':
        if key in d.keys ():
            d[key] += 'sha2,'
        else:
            d[key] = 'sha2,'

mapping = {
    # Common
    'Part Number' : (dmap, 'NAME'),
    'Data Sheet'  : (mapds, 'DATASHEET'),
    'Package Type'  : (dmap, 'PACKAGE'),
    'USB'         : (yesnomap, 'USB'),
    'Timers (16-bit)'  : (dmap, 'TIMER'),
    'ADC 1'       : (analogmap, 'ADC'),
    'DAC'         : (analogmap, 'DAC'),
    'Comparators' : (dmap, 'COMPARATOR'),
    # EFM32
    'Kit'         : (mapds, 'REFDES'),
    'MCU Core'    : (coremap, 'CORE'),
    'Core Frequency' : (dmap, 'FREQ'),
    'Flash (kB)'  : (dmap, 'FLASH'),
    'RAM (kB)'    : (dmap, 'RAM'),
    'Dig I/O'     : (dmap, 'IO'),
    'Communications'  : (commap, None),
    'EMIF'        : (dmap, 'EBI'),
    'CAN'         : (dmap, 'CAN'),
    'PCA Channels'  : (ignore, None),
    'Internal Oscillator'  : (oscmap, 'OSC_PREC'),
    'LIN'         : (ignore, None),
    'ADC 2'       : (analogmap, 'ADC'),
    'Package Size (mm)'  : (dmap, 'SIZE'),
    'Cryptography' : (cryptomap, 'CRYPTO'),
    'Ethernet'  : (yesnomap, 'ETH'),
    'LESENSE'  : (ignore, None),
    'Capacitive Sense'  : (yesnomap, 'CAPSENSE'),
    # EFR32
    'MCU'         : (coremap, 'CORE'),
    'MCU Frequency (MHz)' : (dmap, 'FREQ'),
    'Flash'       : (dmap, 'FLASH'),
    'RAM'         : (dmap, 'RAM'),
    'I²C'         : (dmap, 'I2C'),
    'I²S'         : (dmap, 'I2S'),
    'SPI'         : (dmap, 'SPI'),
    'UART'        : (dmap, 'UART'),
    'USART'       : (dmap, 'USART'),
    'Bluetooth Low Energy' : (mapble, 'RADIO'),
    'Bluetooth 5' : (mapble5, 'RADIO'),
    'Bluetooth 5 2M PHY' : (map2M, 'RADIO'),
    'Bluetooth 5 LE Long Range' : (mapLR, 'RADIO'),
    'zigbee' : (mapzigbee, 'RADIO'),
    'Thread' : (mapthread, 'RADIO'),
    'Proprietary Sub-GHz' : (mapP2G, 'RADIO'),
    'Proprietary 2.4 GHz' : (mapPSub, 'RADIO'),
    'Output Power (dBm)' : (mapOutputPwr, 'RADIO_TXP'),
    'Frequency Range' : (mapFreq, 'RADIO_FREQ'),
    'RX Current (mA)' : (rxCurr, 'RADIO_RXI'),
    'AES-128' : (mapAES128, 'CRYPTO'),
    'AES-256' : (mapAES256, 'CRYPTO'),
    'ECC' : (mapECC, 'CRYPTO'),
    'SHA-1' : (mapSHA1, 'CRYPTO'),
    'SHA-2' : (mapSHA2, 'CRYPTO'),
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
    # EFM32 microcontrollers
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
    # EFR32 microcontrollers
    'blue' : {
        'manual' : 'https://www.silabs.com/documents/public/reference-manuals/efr32xg1-rm.pdf',
        'pagesize' : '2048',
    },
    'flex' : {
        'manual' : 'https://www.silabs.com/documents/public/reference-manuals/efr32xg1-rm.pdf',
        'pagesize' : '2048',
    },
    'mighty' : {
        'manual' : 'https://www.silabs.com/documents/public/reference-manuals/efr32xg1-rm.pdf',
        'pagesize' : '2048',
    },
}

decoder_ring = [
    # EFM32 microcontroller products
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
    # EFR32 microcontroller w/ radio
    { 'match'  : r'efr32bg1',
      'family' : 'blue',
      're'     : r'(efr32bg(\d+)([p|b|v]))(\d{3})(f\d+)([g|i]).+',
      'val'    : ('gdb_start', 'series', 'perf', 'feature', 'gdb_end', 'temp', None),
    },
    { 'match'  : r'efr32fg1',
      'family' : 'flex',
      're'     : r'(efr32fg(\d+)([p|b|v]))(\d{3})(f\d+)([g|i]).+',
      'val'    : ('gdb_start', 'series', 'perf', 'feature', 'gdb_end', 'temp', None),
    },
    { 'match'  : r'efr32mg1',
      'family' : 'mighty',
      're'     : r'(efr32mg(\d+)([p|b|v]))(\d{3})(f\d+)([g|i]).+',
      'val'    : ('gdb_start', 'series', 'perf', 'feature', 'gdb_end', 'temp', None),
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

            # Trim commas
            if 'RADIO' in nrow.keys ():
                nrow['RADIO'] = nrow['RADIO'][:-1]
            if 'CRYPTO' in nrow.keys ():
                nrow['CRYPTO'] = nrow['CRYPTO'][:-1]

            # Decode name info to family
            info = decode (name, decoder_ring) 
            if 'temp' not in info:
                info['temp'] = 'g'
            if info['temp'] == 'g':
                nrow['TEMP'] = '-40,85'
            elif info['temp'] == 'i':
                nrow['TEMP'] = '-40,125'

            # Fix gdbname for EFR
            if 'gdb_name' not in info.keys():
                info['gdb_name'] = info['gdb_start'] + 'xxx' + info['gdb_end']
                
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
                
