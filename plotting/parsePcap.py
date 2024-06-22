from argparse import ArgumentParser
import pandas as pd
import os
import subprocess
import re


def concat(strings):
    """Concats list of strings into single string"""
    string = ""
    for x in strings:
        string += x
    return string

def convertTSharkStatsToDataFrame(inputFile, interfaces=None, removeTmpFile=False):
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
    stats = title_row + stats
    # print(stats)
    with open("tmp_cut.txt", "w") as f:
        f.write(stats)
        f.close()

    data = pd.read_csv("tmp_cut.txt", delimiter=',')
    if removeTmpFile:
        os.remove("tmp_cut.txt")

    # Fixing this strange <> stuff
    # print(data)
    # sep = '<>'
    # test = data["Interval"]
    # print(test)
    # test_split = test.split(sep)
    # print(test_split)
    # data["Interval"] = data["Interval"].apply(lambda x : x.split(sep))
    
    # print(data)

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

def compareSentAndReceivedPackets(sendPacketsFile, receivedPacketsFile, interfaces=None, filterExpression=None):
    """
    Comparing the send and received pcap file for missing packets.
    Outputs a list of packet numbers that was sent but not received.
    """
    
    workingDir = os.path.dirname(sendPacketsFile)
    # mergeCmd = f"mergecap -w {workingDir}/merged.pcap {sendPacketsFile} {receivedPacketsFile}"
    # subprocess.run(mergeCmd, shell=True)
    
    if interfaces is None or len(interfaces) < 2:
        interfaces = ["h1-eth", "h2-eth"]
    
    sentCmd = f'tshark -r {sendPacketsFile} -Y "frame.interface_name=h1-"'

def extractStatsFromPcap(inputFile, outputFile, interfaces=None):
    """Parsing the given input file in pcap format and exporting 
    the data in an easy to parse pandas format."""
    
    interfaceList = "\""
    if interfaces is not None:
        for interface in interfaces:
            interfaceList += f",!stun&&udp&&frame.interface_name=={interface}"
    interfaceList += "\""
    
    filter=f"FRAMES,BYTES{interfaceList}"
    tsharkCmd = f"tshark -r {inputFile} -z io,stat,0,05,{filter} -Q > {outputFile}"
    print(tsharkCmd)
    subprocess.run(tsharkCmd, shell=True)

def replace_match_first(match):
    first_number = match.group(1)
    return first_number

def replace_match_second(match):
    second_number = match.group(2)
    return second_number

def convertTsharkIntervalToIndex(inputFile, outputFile=None, second=False):
    """
    Replacing the Tshark Interval format x.x <> y.y with a single number.
    If second is true, y.y is selected as index, otherwise x.x
    """
    
    replace_func = replace_match_first
    if second:
        replace_func = replace_match_second
    
    # Matching the pattern 'number <>  number'
    pattern = r'(\d+(?:\.\d+)?)\s*<>\s*(\d+(?:\.\d+)?\s*|Dur\s*)'
    
    with open(inputFile, "r") as file:
        content = file.read()
    
    replaced_content = re.sub(pattern, replace_func, content)
    
    output = inputFile
    if outputFile is not None:
        output = outputFile
        
    with open(output, "w") as file:
        file.write(replaced_content)
    
def replaceSeparator(inputFile, outputFile=None, replacement=","):
    """
    Replacing the existing tshark seperator '|' with the replacement separator
    """
    
    with open(inputFile, "r") as file:
        content = file.read()

    replaced = content.replace('|', replacement)
    
    output = inputFile
    if outputFile is not None:
        output = outputFile
        
    with open(output, "w") as file:
        file.write(replaced)

def removeCommaInLine(line):
    
    comma_index = line.find(',')
    if comma_index == -1:
        return line
    
    line = line[:comma_index] + line[comma_index+1:]
    
    comma_index = line.rfind(',')
    if comma_index == -1:
        return line
    
    line = line[:comma_index] + line[comma_index+1:]
    return line

def removeSpacesInLine(line):
    line = line.replace(' ', '').replace('\t', '')
    return line

def removeFirstAndLastCommaAndSpaces(inputFile, outputFile=None):
    """
    Due to previous parsing, remove the first and last occurrence of ',' per line
    """

    with open(inputFile, "r") as file:
        lines = file.readlines()
        
    removed_commas = list()
    for line in lines:
        line = removeCommaInLine(line)
        line = removeSpacesInLine(line)
        removed_commas.append(line)
        
    output = inputFile
    if outputFile is not None:
        output = outputFile
        
    with open(output, "w") as file:
        file.writelines(removed_commas)

def parsePcap(inputFile, interfaces=None):
    """
    Extracting pps and tp stats from the pcap file.
    Returning the data in a pandas dataframe
    """
        
    extractStatsFromPcap(inputFile, "tmp.txt", interfaces)
    convertTsharkIntervalToIndex("tmp.txt")
    replaceSeparator("tmp.txt")
    removeFirstAndLastCommaAndSpaces("tmp.txt")
    data = convertTSharkStatsToDataFrame("tmp.txt", interfaces)
    
    # os.remove("tmp.csv")
    
    # print(data)
    
    return data