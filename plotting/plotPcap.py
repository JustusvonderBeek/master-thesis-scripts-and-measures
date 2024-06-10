from cProfile import label
import sys
import os
from argparse import ArgumentParser
from parsePcap import parsePcap

try:
    import seaborn as sns
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FixedLocator, MaxNLocator
    import pandas as pd
except ImportError:
    print('Failed to load dependencies. Please ensure that seaborn, matplotlib, and pandas can be loaded.', file=sys.stderr)
    exit(-1)

def exportToPdf(fig, filename):
    """
    Exports the current plot to file. Both in the 10:6 and 8:6 format (for thesis and slides.
    """

    # Saving to 8:6 format (no name change)
    fig.set_figwidth(8)
    fig.set_figheight(6)

    fig.savefig(filename, bbox_inches='tight', format='pdf')
    print(f"Wrote output to {filename}")


    # Saving plot to slide format 10:6 (with changed name to sld_)
    fig.set_figwidth(10)
    fig.set_figheight(6)
    
    path, file = os.path.split(filename)
    file = "sld_" + file
    filename = os.path.join(path, file)
    fig.savefig(filename, bbox_inches='tight', format='pdf')
    print(f"Wrote output to {filename}")

def plotThroughput(args):
    """
    Gets the parsed command line and outputs the final throughput graph.
    """

    interfaces=["h1-wifi", "h1-eth", "h1-cellular"]
    data = parsePcap(args.input[0], interfaces)

    # yvalues = "Packets"
    # if args.plotting is not None:
    #     yvalues = args.plotting

    # min_xlength = 20
    # throughput = None
    # for index, file in enumerate(args.input):
    #     ingress = pd.read_csv(file, index_col=0)
    #     egress = None
    #     enclave = None
    #     if result.input_outgoing is not None and len(result.input_outgoing) > index:
    #         egress = pd.read_csv(result.input_outgoing[index])
    #     if result.input_e is not None and len(result.input_e) > index:
    #         enclave = pd.read_csv(result.input_e[index])

    #     # print(ingress)
    #     # if egress is not None:
    #     #     print(egress)
            
    #     # Post processing

    #     # Convert values to Mbps
    #     ingress["Direction"] = "ingress"
    #     ingress["Mode"] = "Baseline"
    #     if egress is not None:
    #         # Adding the second column
    #         egress["Direction"] = "egress"
    #         ingress = pd.concat([ingress, egress], ignore_index=True)
    #     if enclave is not None:
    #         enclave["Mode"] = "Enclave"
    #         ingress = pd.concat([ingress, enclave], ignore_index=True)

    #     ingress[yvalues] /= 1e6 / 8

    #     size = re.findall("_b(\d+)", file)
    #     if len(size) > 0:
    #         size = size[0]
    #         ingress["Size"] = size
    #     print(ingress)

    #     if throughput is None:
    #         throughput = pd.DataFrame(ingress)
    #     else:
    #         throughput = pd.concat([throughput, ingress], ignore_index=True)

    #     if min_xlength > len(ingress):
    #         min_xlength = len(ingress)

    # data = pd.DataFrame(throughput)
    # data = throughput
    # print(data)

    # # Plotting
    # fig, axes = plt.subplots()

    # baseline = data[data["Mode"] == "Baseline"]
    # enclave = data[data["Mode"] == "Enclave"]
    # sns.lineplot(data=enclave, y=yvalues, x="Interval", hue="Size", marker="o")
    # if len(enclave) > 0:
    #     custom_pal = {"100":"blue", "200":"orange", "500":"green", "1000":"red", "1420":"purple"}
    #     sizes = [100, 200, 500, 1000, 1420]
    #     for i in range(5):
    #         sns.lineplot(data=baseline[baseline["Size"] == f"{sizes[i]}"], y=yvalues, x="Interval", marker="s", linestyle="--", hue="Size", palette=custom_pal, label=f"{sizes[i]} Baseline", legend=None)

    # if result.xaxis is not None:
    #     axes.set(xlabel=result.xaxis)
    # else:
    #     axes.set(xlabel="Time in seconds")
    # if result.yaxis is not None:
    #     axes.set(ylabel=result.yaxis)
    # else:
    #     axes.set(ylabel="MBit/s")
    # if result.title is not None:
    #     plt.title(result.title)
    # else:
    #     plt.title("Throughput")

    # plt.legend(title="PDU size")
    # axes.set_xlim(xmin=0, xmax=6)
    # axes.set_ylim(ymin=0)
    # plt.grid()
    # plt.tight_layout()

    # Saving the plot
    # exportToPdf(fig, result.output)
    # return
    
    # --------------------
    # Plotting the pps
    # --------------------

    # print(data)
    fig, axes = plt.subplots()

    filtered_data = data.filter(items=["Interval", "h1-wifi Frames", "h1-eth Frames", "h1-cellular Frames"])
    conv_data = filtered_data.melt(id_vars="Interval")
    # print(conv_data)
    sns.lineplot(data=conv_data, y="value", x="Interval", hue="variable")

    axes.set_xlim(xmin=0)
    axes.set_ylim(ymin=0)

    axes.set(xlabel="Time in seconds")
    axes.set(ylabel="Packets per second")
    plt.legend(title="Interface")
    plt.title("Packets per second")
    plt.grid()

    exportToPdf(fig, args.output)


if __name__ == '__main__':

    parser = ArgumentParser(description='Generate charts for pps values from .pcap csv files')
    parser.add_argument('--input', action="append", default=[], required=True)
    parser.add_argument('--input-e', action="append", default=[], required=False)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--input-outgoing', type=str, required=False)
    parser.add_argument('--plotting', type=str, required=False)
    parser.add_argument('--xaxis', type=str, required=False)
    parser.add_argument('--yaxis', type=str, required=False)
    parser.add_argument('--title', type=str, required=False)

    args = parser.parse_args()

    plotThroughput(args)