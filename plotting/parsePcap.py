from argparse import ArgumentParser
import pandas as pd
import os
import subprocess


def concat(strings):
    """Concats list of strings into single string"""
    string = ""
    for x in strings:
        string += x
    return string

def convertTSharkCsvToDataFrame(inputFile, interfaces=None):
    """
    Reading a tshark stat file and converting to dataframe
    """
    # Reading input and removing first and last row
    with open(inputFile, "r") as f:
        rows = f.readlines()[6:]
        table_start = 0
        for row in rows:
            if "-----" in row:
                title_row = rows[table_start+2]
                table_start += 4
                break
            table_start += 1
        rows = rows[table_start:]
        rows = rows[:len(rows)-1]

    # print(rows)
    # print(title_row)
    stats = concat(rows)
    stats = title_row + "\n" + stats
    # print(stats)
    with open("tmp.txt", "w") as f:
        f.write(stats)
        f.close()

    data = pd.read_fwf("tmp.txt", delimiter=' |')
    os.remove("tmp.txt")

    # Fixing this strange <> stuff
    sep = '<'
    data["Interval"] = data["Interval"].apply(lambda x : x.split(sep, 1)[0])

    # Rename the columns in case names are given
    column_index = 3 # Starting with 3 because 0 is interval, 1 is frames, 2 is bytes
    old_columns = data.columns.to_list()
    if interfaces is None:
        return data
    
    for iface in interfaces:
        old_columns[column_index] = f"{iface} Frames"
        column_index += 1
        old_columns[column_index] = f"{iface} Bytes"
        column_index += 1
            
    data.columns = old_columns

    # data.to_csv(outputFile)
    # print(f"Wrote csv to {outputFile}")
    return data
    # print(data)

def extractStatsFromPcap(inputFile, outputFile, interfaces=None):
    """Parsing the given input file in pcap format and exporting 
    the data in an easy to parse pandas format."""
    
    interfaceList = ""
    if interfaces is not None:
        for interface in interfaces:
            interfaceList += f",frame.interface_name=={interface}"
    
    filter=f"FRAMES,BYTES{interfaceList}"
    tsharkCmd = f"tshark -r {inputFile} -z io,stat,1,{filter} -Q > {outputFile}"
    subprocess.run(tsharkCmd, shell=True)
        
def parsePcap(inputFile, interfaces=None):
    """
    Extracting pps and tp stats from the pcap file.
    Returning the data in a pandas dataframe
    """
        
    extractStatsFromPcap(inputFile, "tmp.csv", interfaces)
    data = convertTSharkCsvToDataFrame("tmp.csv", interfaces)
    
    # os.remove("tmp.csv")
    
    # print(data)
    
    return data