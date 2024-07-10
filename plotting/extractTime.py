import pandas as pd
from argparse import ArgumentParser

def extractAvgTime(args):
    
    df = pd.read_csv(args.input[0])
    
    avg_per_row = df.iloc[:, 1] - df.iloc[:, 0]
    
    sum = avg_per_row.sum()
    avg = avg_per_row.mean(axis=0)
    print(f"Sum: {sum}")
    print(f"Avg: {avg}")
        

if __name__ == '__main__':
    parser = ArgumentParser(description='Generate charts for pps values from .pcap csv files')
    parser.add_argument('--input', action="append", default=[], required=True)
    
    args = parser.parse_args()

    extractAvgTime(args)