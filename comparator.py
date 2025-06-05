#!/usr/bin/env python3

import json
import yaml
import csv
import argparse

def intake(file):
    with open(file) as csvfile:
        exportable = []
        contents = csv.DictReader(csvfile)
        for row in contents:
            exportable.append(row)
        return exportable
    
def lodtolist(lod, key):
    exportlist = []
    for row in lod:
        exportlist.append(row[key])

    return exportlist

def checker(inputlist, lod, key):
    matchlist = []
    nonmatchlist = []
    for row in lod:
        if row[key] != '':
            if row[key] not in inputlist:
                matchlist.append(row)
            else:
                nonmatchlist.append(row)
    return matchlist, nonmatchlist

def main():
    data1 = intake('/home/sneed/Downloads/data1.csv')
    data2 = intake('/home/sneed/Downloads/data2.csv')
    d1ips = lodtolist(data1, 'IP Address')
    d2ips = lodtolist(data2, "IPv4")
    
    print(checker(d2ips, data1, 'IP Address'))
    print(checker(d1ips, data2, 'IPv4'))

main()