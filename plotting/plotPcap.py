from cProfile import label
import sys
import os
import math
import numpy as np
import matplotlib.ticker as plticker
from argparse import ArgumentParser
from parsePcap import parsePcap
from matplotlib.ticker import ScalarFormatter

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

    interfaces=[
        "h1-wifi", 
        "h1-eth", 
        "h1-cellular",
    ]
    filterRules=[
        "udp&&!stun&&!mdns&&!icmp",
        "udp&&!stun&&!mdns&&!icmp",
        "udp&&!stun&&!mdns&&!icmp",
        # "stun&&!icmp&&ip.addr==1.20.50.100", 
        # "stun&&!icmp&&ip.dst==1.20.50.20", 
        # "stun&&!icmp&&ip.src==1.20.50.10&&ip.dst==2.40.60.3", 
        # "!stun&&udp&&!mdns&&ip.dst==1.20.50.20"
    ]
    columns=[
        "H1 Wi-Fi", 
        "H1 Ethernet",
        "H1 Cellular",
    ]
    resolution="0,05"
    # interfaces=[
    #     "h1-cellular", 
    #     "h1-cellular", 
    #     "h2-cellular", 
    #     "h1-cellular"
    # ]
    # filterRules=[
    #     "stun&&!icmp&&ip.addr==1.20.50.100", 
    #     "stun&&!icmp&&ip.dst==1.20.50.20", 
    #     "stun&&!icmp&&ip.src==1.20.50.10&&ip.dst==2.40.60.3", 
    #     "!stun&&udp&&!mdns&&ip.dst==1.20.50.20"
    # ]
    # columns=[
    #     "H1 STUN Address Resolution", 
    #     "H1 -> H2 STUN Probes (out)",
    #     "H1 -> H2 STUN Probes (in)", 
    #     "H1 -> H2 Cellular (QUIC)"
    # ]
    # resolution="0,005"
    # interfaces=[
    #     # "h1-wifi", 
    #     "h1-eth", 
    #     "h1-cellular",
    #     "h1-eth", 
    #     # "h1-cellular", 
    #     # "h2-eth",
    #     # "h2-cellular"
    # ]
    # filterRules=[
    #     # "!stun&&!mdns&&udp&&ip.dst==192.168.1.3", 
    #     "!stun&&!mdns&&udp&&(quic.path_challenge.data||quic.path_response.data)", 
    #     "!mdns&&udp&&!icmp&&!stun&&(ip.dst==1.20.50.100||ip.dst==1.20.50.20)", 
    #     "!stun&&!mdns&&udp&&!(quic.path_challenge.data||quic.path_response.data)", 
    #     # "udp&&!icmp&&!stun&&ip.dst==1.20.50.20&&!(quic.path_challenge.data||quic.path_response.data)",
    #     # "!stun&&!mdns&&udp&&ip.dst==172.16.2.20",
    #     # "!stun&&!mdns&&udp&&ip.dst==2.40.60.3",
    # ]
    # columns=[
    #     # "H1 Wi-Fi", 
    #     "H1 Ethernet (QUIC Probes)",
    #     "H1 Cellular (QUIC Probes)",
    #     "H1 Ethernet (Data)",
    #     # "H1 Cellular (Data)",
    #     # "H2 Cellular (in)"
    # ]
    # resolution="0,005"
    data = parsePcap(args.input[0], resolution, interfaces, filterRules, columns)

    # --------------------
    # Plotting the pps
    # --------------------

    # Define custom colors
    color_dict = {
        "H1 Wi-Fi": "#61bf2a", 
        "H1 Ethernet (QUIC Probes)" : "orange",
        "H1 Cellular (QUIC Probes)" : "red",
        "H1 Ethernet (Data)" : "#159bedA0",
        "H2 Ethernet (in)" : "#fcbd03",
        # "H2 Cellular (in)" : "purple"
    }
    # dash_dict = {
    #     'H1 Wi-Fi': "--", 
    #     'H1 Ethernet (QUIC Probes)' : "--",
    #     'H1 Cellular (QUIC Probes)' : "-",
    #     'H1 Ethernet (Data)' : "--",
    #     'H2 Ethernet (in)' : "--",
    #     # 'H2 Cellular (in)' : "-"
    # }

    # print(data)
    fig, axes = plt.subplots()

    # filtered_data = data.filter(items=["Interval", "h1-wifi", "h1-eth", "h1-cellular", "h2-wifi", "h2-eth", "h2-cellular"])
    filtered_data = data.filter(items=["Interval"] + columns)
    conv_data = filtered_data.melt(id_vars="Interval")
    # print(conv_data)
    plot = sns.lineplot(data=conv_data, y="value", x="Interval", hue="variable", linewidth=1, palette="tab10")

    # axes.lines[2].set_linestyle("dashed")
    # axes.lines[2].set_linestyle("--")

    xmax = data["Interval"][len(data["Interval"])-1]
    # print(xmax)
    # axes.set_xlim(xmin=4.153, xmax=5.65)
    axes.set_xlim(xmin=0, xmax=15.4)
    # axes.set_xlim(xmin=0.7, xmax=1.3)
    # # axes.set_xlim(xmin=0, xmax=xmax)
    
    # Scale the ticks in case we have too many (aka more than 20)
    # print(len(data["Interval"]))
    # if len(data["Interval"]) > 20:
    #     tick_scale = len(data["Interval"]) / 20
    #     print(tick_scale)
    #     # tick_scale = math.floor(tick_scale)
    #     loc = plticker.MultipleLocator(base=1)
    #     axes.xaxis.set_major_locator(loc)
    #     plt.xticks(rotation=90)
    # else:
    #     loc = plticker.MultipleLocator(base=1)
    #     axes.xaxis.set_major_locator(loc)
    #     plt.xticks(rotation=0)


    # print(max_index)
    # axes.xaxis.set_ticks(np.arange(0, max_index, 5))
    # Plot log to see the traffic for the two idle interfaces
    logscale=False
    for column in columns:
        if max(data[column]) > 30:
            logscale=True
            break
    
    if logscale:
        axes.set_yscale('log',base=10)
        axes.set_ylim(ymin=10e-1)
    else:
        axes.set_ylim(ymin=0)
        # axes.set_ylim(ymin=0, ymax=4)
    
    axes.yaxis.set_major_formatter(ScalarFormatter())
    axes.set(xlabel="Time in seconds")
    axes.set(ylabel="Packets per second")

    loc = plticker.MultipleLocator(base=1)
    # loc = plticker.MultipleLocator(base=0.1)
    # loc = plticker.MultipleLocator(base=0.1)
    minor_loc = plticker.MultipleLocator(base=0.2)
    # minor_loc = plticker.MultipleLocator(base=0.02)
    # minor_loc = plticker.MultipleLocator(base=0.01)
    # minor_loc = plticker.MultipleLocator(base=1)
    axes.xaxis.set_major_locator(loc)
    axes.xaxis.set_minor_locator(minor_loc)
    # axes.yaxis.set_minor_locator(minor_loc)

    axes.grid(which="minor", linestyle="dotted", linewidth='0.5', color="gray")
    plt.grid(True, axis="x")
    # plt.xticks(rotation=90)

    # axes.legend(loc="upper right", title="Interface", fancybox=True, framealpha=0.9)
    axes.legend(loc="best", title="Interfaces", fancybox=True, framealpha=0.9)
    # axes.legend(loc=(0.6,0.78), title="Interfaces", fancybox=True, framealpha=0.9)
    plt.title("Prototype Path Discovery")
    # plt.title("Cellular Path Building in Detail")
    # plt.title("QUIC Path Probing")


    # # Adding some figure custom annotations for Pathfinding Test 1
    plt.axvline(x=1.29, color=(1, 0, 0, 1), linestyle="--")
    plt.axvline(x=5.54, color=(1, 0, 0, 1), linestyle="--")
    
    # add arrow
    plt.annotate("1. Ethernet path\nadded to QUIC", xy=(1.29, 6.0), xytext=(2.1, 6.2), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))
    plt.annotate("3. Cellular path\nadded to QUIC", xy=(5.54, 4.0), xytext=(6.5, 4.2), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))
    # Annotate the path probings (or keep aplives)
    plt.annotate("4. QUIC keep-alives\nevery ~1s on idle\n paths", xy=(9.7, 3), xytext=(10.2, 4.2), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))
    # Annotate the decision to use the shorter path RTT
    plt.annotate("2. QUIC choosing\nEthernet path\nfor sending due\nto shorter RTT", xy=(1.29, 3), xytext=(2.1, 3.1), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))
    
    plt.axvspan(0, 1.29, facecolor="gray", alpha=0.3)
    plt.axvspan(4.15, 5.54, facecolor="gray", alpha=0.3)
    plt.axvspan(11.34, 16, facecolor="gray", alpha=0.3)
    
    
    # Adding the cellular path finding annotation Test 1
    # plt.axvline(x=4.37, color=(1, 0, 0, 1), linestyle="--")
    # plt.axvline(x=4.87, color=(1, 0, 0, 1), linestyle="--")
    # plt.axvline(x=5.27, color=(1, 0, 0, 1), linestyle="--")
    
    # plt.annotate("1. Finished resolving peer-\nreflexive address via TURN\nserver", xy=(4.37, 3.12), xytext=(4.41, 3.45), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5", alpha=0.8))
    
    # plt.annotate("2. Both peers\nstart probing,\nrepeating every\n~200ms", xy=(4.45, 2), xytext=(4.5, 2.5), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))

    # plt.annotate("3. First probe\narrives at H2\n~36ms after\nsending (only\nreflexive probe\nreaches H2)", xy=(4.49, 1), xytext=(4.57, 0.5), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5", alpha=0.8))

    # plt.annotate("4. Full STUN\nHandshake\ncompleted,\nfirst\nUSE_CANDIDATE\nsent", xy=(4.86, 3), xytext=(4.925, 2.13), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.4", alpha=0.8))

    # plt.annotate("5. Candidate\nnominated", xy=(5.27, 2), xytext=(5.32, 2.5), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))

    # # Difference: 5,557687136−5,271353439 = 0,286333697
    # plt.annotate("6. Path added to\nQUIC and used\n~286ms after\nNomination", xy=(5.56, 1), xytext=(5.33, 1.31), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))


    # # Annotations for migration Test 2
    # plt.axvline(x=7, color=(1, 0, 0, 1), linestyle="--")
    # plt.axvline(x=12, color=(1, 0, 0, 1), linestyle="--")
    
    # plt.axvline(x=31, color=(1, 0, 0, 1), linestyle="--")
    # plt.axvline(x=45, color=(1, 0, 0, 1), linestyle="--")
    
    # plt.annotate("1. Ethernet path\n100% loss and\nmigration to Wi-Fi", xy=(7, 80), xytext=(13.5, 80), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))
    
    # plt.annotate("2. Wi-Fi path\n100% loss and\nmigration to\nCellular", xy=(12, 20), xytext=(15.5, 20), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))
    
    # plt.annotate("3. QUIC packets\nare still sent but\ndo not arrive", xy=(15, 3), xytext=(15, 6), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))
    
    # plt.annotate("4. Ethernet path\nre-enabled", xy=(31, 45), xytext=(35.5, 25), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))
    
    # plt.annotate("5. Migration back\nto Ethernet path", xy=(32, 100), xytext=(35.5, 63), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))
    
    # plt.annotate("6. Wi-Fi path\nand interface\nre-enabled", xy=(45, 2), xytext=(48.5, 1.5), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))

    # plt.annotate("7. It takes until\nthe next iteration\nto consider the\nWi-Fi path for\nprobing again", xy=(63, 3), xytext=(49.5, 5.5), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))

    # # Color the ICE probings
    # plt.axvspan(0, 1, facecolor="gray", alpha=0.3)
    # plt.axvspan(4, 5, facecolor="gray", alpha=0.3)
    # plt.axvspan(11, 21, facecolor="gray", alpha=0.3)
    # plt.axvspan(30, 32, facecolor="gray", alpha=0.3)
    # plt.axvspan(42, 52, facecolor="gray", alpha=0.3)
    # plt.axvspan(62, 63, facecolor="gray", alpha=0.3)
    # plt.axvspan(73, 75, facecolor="gray", alpha=0.3)

    # Annotations for QUIC Probing Test 3
    # plt.axvline(x=0.71, color=(1, 0, 0, 1), linestyle="--")
    # plt.axvline(x=1.243, color=(1, 0, 0, 1), linestyle="--")

    # plt.axvspan(0.71, 0.81, facecolor="gray", alpha=0.3)

    # plt.annotate("1. QUIC Path\nChallenge and\nResponses\n(ingress,egress)", xy=(0.791, 1), xytext=(0.73, 2.2), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))

    # plt.annotate("2. QUIC Probing\non Cellular every\n~1s", xy=(1.02, 1), xytext=(0.9, 3.2), arrowprops=dict(arrowstyle="->", color="black"), bbox=dict(facecolor="white", boxstyle="round,pad=0.5"))

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