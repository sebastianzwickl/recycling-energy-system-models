# import pyam as py
import matplotlib.pyplot as plt
import os
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import numpy as np
from matplotlib.ticker import FuncFormatter
import pandas as pd


_string_ex = "Existing"
_string_primary = "Mining-based additions"
_string_secondary = "Recycling-based additions"

_colors = {
    _string_primary: "#FBA834",
    _string_ex: "#124076",
    _string_secondary: "#7F9F80",
}

_font = 16


def format_thousands(x, pos):
    """
    Format the tick labels with a space between thousands.
    """
    return "{:,.0f}".format(x).replace(",", " ")


def run(model, dataframe, folder):
    plt.style.use("default")
    plt.rcParams["xtick.labelsize"] = 16
    plt.rcParams["ytick.labelsize"] = 16

    # (1) CAPACITY
    fig, ax = plt.subplots()
    _x = dataframe.Year
    _current = dataframe["Current capacity [MW]"] / 1000
    _newly_prim = dataframe["Newly|Primary [MW]"] / 1000
    _newly_sec = dataframe["Newly|Secondary [MW]"] / 1000

    _labels = [_string_ex, _string_primary, _string_secondary]
    _bottom = np.zeros(len(_x))
    _width = 0.5

    for _val, _lab in [
        [_current, _labels[0]],
        [_newly_prim, _labels[1]],
        [_newly_sec, _labels[2]],
    ]:
        ax.bar(
            _x,
            _val,
            _width,
            label=_lab,
            bottom=_bottom,
            color=_colors.get(_lab, "black"),
            zorder=2,
            linewidth=0.2,
            edgecolor="black",
        )
        _bottom = np.add(_bottom, _val)

    ax.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
    ax.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)

    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((-3, 4))

    ax.yaxis.set_major_formatter(formatter)
    plt.ylim(0, 2500)
    ax.set_xlabel("Year", fontsize=_font)
    ax.set_ylabel("Cummulative capacity [GW]", fontsize=_font)
    # if model.scenario == 'Solar Modules':
    #     ax.set_title('Solar modules (EU-27)', fontsize=_font)
    # else:
    #     ax.set_title('Wind turbines (EU-27)', fontsize=_font)

    _patches = []
    if sum(_newly_sec) == 0:
        for _reg in _labels[0:2]:
            _patches.append(
                mpatches.Patch(color=_colors.get(_reg, "black"), label=_reg)
            )
    else:
        for _reg in _labels:
            _patches.append(
                mpatches.Patch(color=_colors.get(_reg, "black"), label=_reg)
            )

    _legend = ax.legend(
        handles=_patches,
        loc="upper left",
        facecolor="white",
        fontsize=_font * 0.9,
        handlelength=1,
        handletextpad=0.5,
        ncol=1,
        borderpad=0.5,
        columnspacing=1,
        edgecolor="black",
        frameon=True,
        bbox_to_anchor=(0.005, 1 - 0.005),
        shadow=False,
        framealpha=1,
    )

    _legend.get_frame().set_linewidth(0.5)

    plt.tight_layout()
    fig.savefig(
        os.path.join(folder, model.scenario + "_cumulative_capacity.pdf"), dpi=1000
    )

    # (2) IMPORT SHARE
    fig, ax = plt.subplots()
    _x = dataframe.Year
    _current = dataframe["Import share global production [%]"]
    ax.plot(
        _x,
        _current,
        lw=1,
        color=_colors.get(_string_primary, "red"),
        linestyle="dashed",
        label="Annual",
    )

    dataframe["Interval"] = (dataframe["Year"] - 2020) // 5
    interval_averages = (
        dataframe.groupby("Interval")["Import share global production [%]"]
        .mean()
        .reset_index()
    )
    interval_averages["Interval"] = interval_averages["Interval"] * 5 + 2020
    _aver = []
    for _index in range(0, 6, 1):
        _aver += 5 * [interval_averages["Import share global production [%]"][_index]]
    _aver += [interval_averages["Import share global production [%]"][6]]
    indices_to_mark = [i for i in range(len(_aver)) if i % 5 == 0 or i % 5 == 4]
    ax.plot(
        _x,
        _aver,
        lw=2,
        marker="d",
        markevery=indices_to_mark,
        label="5-year average",
        color=_colors.get(_string_primary, "red"),
    )

    ax.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
    ax.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)
    plt.ylim(0, 52.5)

    _legend = ax.legend(
        loc="lower right",
        facecolor="white",
        fontsize=_font * 0.9,
        handlelength=1,
        handletextpad=0.5,
        ncol=1,
        borderpad=0.5,
        columnspacing=1,
        edgecolor="black",
        frameon=True,
        bbox_to_anchor=(0.995, 0.005),
        shadow=False,
        framealpha=1,
    )
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    _legend.get_frame().set_linewidth(0.5)

    ax.set_ylabel("Import share in global production", fontsize=_font)
    # if model.scenario == 'Solar Modules':
    #     ax.set_title('Solar modules (EU-27)', fontsize=_font)
    # else:
    #     ax.set_title('Wind turbines (EU-27)', fontsize=_font)
    ax.set_xlabel("Year", fontsize=_font)
    plt.tight_layout()
    fig.savefig(os.path.join(folder, model.scenario + "_import_share.pdf"), dpi=1000)

    # (3) DECOMMISSIONED
    fig, ax = plt.subplots()
    _x = dataframe.Year
    _dec = dataframe["Decommissioned [MW]"] / 1000
    ax.bar(
        _x,
        _dec,
        _width,
        label="Decommissioned",
        color="#C8ACD6",
        zorder=2,
        edgecolor="black",
        linewidth=0.2,
    )
    ax.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
    ax.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)
    ax.set_ylabel("Decommissioned capacity [GW]", fontsize=_font)
    # if model.scenario == 'Solar Modules':
    #     ax.set_title('Solar modules (EU-27)', fontsize=_font)
    # else:
    #     ax.set_title('Wind turbines (EU-27)', fontsize=_font)
    ax.set_xlabel("Year", fontsize=_font)
    # plt.ylim(0, 80000)
    plt.tight_layout()
    fig.savefig(os.path.join(folder, model.scenario + "_decommissioned.pdf"), dpi=1000)

    # (4) SCRAP
    fig, ax = plt.subplots()
    _x = dataframe.Year
    _scrap = dataframe["Total scrap [tons]"] / 1000
    ax.plot(_x, _scrap, lw=2, color="#373A40", linestyle="solid", label="Scrap")
    ax.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
    ax.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)
    ax.set_ylabel("Total scrap [kt]", fontsize=_font)
    ax.set_xlabel("Year", fontsize=_font)
    plt.ylim(0, 80000)
    ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))
    
    if model.choice == 1:
        # get the waste amount from before
        folder_new = folder.replace("pessimistic", "optimistic")
        value = list(pd.read_excel(folder_new + '\solution.xlsx')['Total scrap [tons]'])[-1]/1000
        _col = '#B43F3F'
        # ax.annotate(f' Optimistic market ({value:,.0f})'.replace(',', ' '),
        #             xy=(2050, value), xycoords='data',
        #             xytext=(2045, value*1.0), textcoords='data',
        #             arrowprops=dict(arrowstyle="-", 
        #                 connectionstyle='angle,angleA=180,angleB=90,rad=0', color=_col),
        #             fontsize=14, color=_col, horizontalalignment='right',zorder=2, verticalalignment='center',
        #             bbox=dict(boxstyle="square,pad=0.3",
        #                   fc="white", ec=_col, lw=0, alpha=1))
        # ax.plot(2050, value, marker='o', color=_col)
        
    value =  list(_scrap)[-1]
    print(value)
    ax.annotate(f'({value:,.0f})'.replace(',', ' '),
                xy=(2050, value), xycoords='data',
                xytext=(2045, value*1.0), textcoords='data',
                arrowprops=dict(arrowstyle="-", 
                    connectionstyle='angle,angleA=180,angleB=90,rad=0', color='#373A40'),
                fontsize=14, color='#373A40', horizontalalignment='right',zorder=2, verticalalignment='center',
                bbox=dict(boxstyle="square,pad=0.3",
                      fc="white", ec='#373A40', lw=0, alpha=1))
    ax.plot(2050, value, marker='o', color='#373A40')
    
    plt.tight_layout()
    fig.savefig(os.path.join(folder, model.scenario + "_total_scrap.pdf"), dpi=1000)

    # (5) ADDITIONS (ONLY)
    fig, ax = plt.subplots()
    _x = dataframe.Year

    dataframe["5yr_group"] = (dataframe["Year"] // 10) * 10
    grouped = dataframe.groupby("5yr_group")["Newly|Primary [MW]"].sum().reset_index()
    grouped.columns = ["5yr_group", "Sum_Newly_prim_MW"]
    grouped2 = (
        dataframe.groupby("5yr_group")["Newly|Secondary [MW]"].sum().reset_index()
    )
    grouped2.columns = ["5yr_group", "Sum_Newly_sec_MW"]

    _labels = [_string_primary, _string_secondary]
    _bottom = np.zeros(3)
    _width = 2.5

    for _val, _lab in [
        [grouped["Sum_Newly_prim_MW"].values, _labels[0]],
        [grouped2["Sum_Newly_sec_MW"].values, _labels[1]],
    ]:
        _val[2] += _val[3]
        _val= _val[:-1] / 1000
        
        ax.bar(
            [2020, 2030, 2040],
            _val,
            _width,
            label=_lab,
            bottom=_bottom,
            color=_colors.get(_lab, "black"),
            zorder=2,
            linewidth=0.2,
            edgecolor="black",
        )
        
        
        print('Bottom: {}'.format(_bottom))
        _x = [2020, 2030, 2040]
    
        for _index in [0, 1, 2]:
            if _val[_index] > 0:
                ax.text(_x[_index], _val[_index] * 0.5 + _bottom[_index], str(int(_val[_index])), ha='center', color='#11235A', fontsize=14, va='center')
        _bottom = np.add(_bottom, _val)

    ax.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
    ax.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)

    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((-3, 4))

    ax.yaxis.set_major_formatter(formatter)
    plt.ylim(0, 1600)
    ax.set_xlabel("Period", fontsize=_font)
    ax.set_ylabel("Capacity additions [GW]", fontsize=_font)
        
    
    
    # if model.scenario == 'Solar Modules':
    #     ax.set_title('Solar modules (EU-27)', fontsize=_font)
    # else:
    #     ax.set_title('Wind turbines (EU-27)', fontsize=_font)

    _patches = []
    for _reg in _labels:
        if _reg == "Mining-based additions":
            _lab1 = "Mining-based"
        else:
            _lab1 = "Recycling-based"
        _patches.append(mpatches.Patch(color=_colors.get(_reg, "black"), label=_lab1))

    _legend = ax.legend(
        handles=_patches,
        loc="upper left",
        facecolor="white",
        fontsize=14,
        handlelength=0.75,
        handletextpad=0.25,
        ncol=1,
        borderpad=0.4,
        columnspacing=1,
        edgecolor="black",
        frameon=True,
        bbox_to_anchor=(0.0, 1),
        shadow=False,
        framealpha=1,
    )

    _legend.get_frame().set_linewidth(0.5)
    ax.set_xticks([2020, 2030, 2040])
    ax.set_xticklabels(labels=["2020s", "2030s", "2040s"])

    plt.tight_layout()
    fig.savefig(
        os.path.join(folder, model.scenario + "_additions_capacity.pdf"), dpi=1000
    )
