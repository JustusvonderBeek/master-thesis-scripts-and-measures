# This file is meant to be shared across multiple projects
# making use of large logfiles.
# It allows filtering logfiles for specifc sources, both
# positiv and negative

import os

def filter_logfile_positiv(file, contains, outfile=None):
    """Filtering the given file for lines that are contained
    in the contains list of strings. The final file is written to *filtered*_file
    or if outfile is given to that path.
    """
    
    if outfile is None:
        filename = os.path.basename(file)
        path = os.path.dirname(file)
        outfile = os.path.join(path, f"pos_filtered_{filename}")
        
    with open(outfile, "w") as wfile:
        with open(file, "r") as infile:
            for line in infile:
                # print(f"Line: {line}")
                lower = line.lower()
                for contain_filter in contains:
                    if contain_filter not in lower:
                        continue
                    wfile.write(line)
                    break

    print(f"Filtered logfile and wrote to: '{outfile}'")

def filter_logfile_negative(file, contains, outfile=None):
    """Filtering the given file for lines that are contained
    in the contains list of strings. The final file is written to *filtered*_file
    or if outfile is given to that path.
    """
    
    if outfile is None:
        filename = os.path.basename(file)
        path = os.path.dirname(file)
        outfile = os.path.join(path, f"neg_filtered_{filename}")
        
    with open(outfile, "w") as wfile:
        with open(file, "r") as infile:
            for line in infile:
                # print(f"Line: {line}")
                lower = line.lower()
                for contain_filter in contains:
                    if contain_filter in lower:
                        continue
                    wfile.write(line)
                    break
                
    print(f"Filtered logfile and wrote to: '{outfile}'")
    