import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import FuncFormatter
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.patches as mpatches


def format_thousands(x, pos):
    """
    Format the tick labels with a space between thousands.
    """
    return '{:,.0f}'.format(x).replace(',', ' ')

plt.style.use("default")
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16

data = pd.read_excel('values.xlsx')


# RECYCLED-BASED ADDITIONS
fig, ax = plt.subplots()
ax.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
ax.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)
ax.xaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))
ax.yaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))
ax.set_xlabel("Limit on EU's import share [%]", fontsize=16)
ax.set_ylabel("Share of recycled-based additions", fontsize=16)

_filter_2 = data.loc[data['Overcapacity constraint relaxed'] == 'Yes']['Share of recycled-based [%]']
_x = data.loc[data['Overcapacity constraint relaxed'] == 'Yes']['Max import share per year [%]']
ax.plot(_x, _filter_2, label='Relaxed exp. plan', color='#211951', linewidth=2)

_filter_1 = data.loc[data['Overcapacity constraint relaxed'] == 'No']['Share of recycled-based [%]']
_x = data.loc[data['Overcapacity constraint relaxed'] == 'No']['Max import share per year [%]']
ax.plot(_x, _filter_1, label='Strict exp. plan', color='#836FFF', linewidth=2)



_legend = ax.legend(loc='center', facecolor='white', fontsize=14,
                    handlelength=1.5,
                    handletextpad=0.5, ncol=2, borderpad=0.5, columnspacing=1, edgecolor="black", frameon=True,
                    bbox_to_anchor=(0.5, 1.025),
                    shadow=False,
                    framealpha=1
                    )
ax.set_xlim([-2.5, 55])
ax.set_ylim([-2.5, 32.5])
_legend.get_frame().set_linewidth(0.5) 
plt.tight_layout()
fig.savefig("recycled-based additions.pdf", dpi=1000)  


# TOTAL COSTS
fig, ax = plt.subplots()
ax.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
ax.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)
ax.xaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))
ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))
ax.set_xlabel("Limit on EU's import share [%]", fontsize=16)
ax.set_ylabel("Total costs [MEUR]", fontsize=16)

_filter_2 = data.loc[data['Overcapacity constraint relaxed'] == 'Yes']['Total costs [MEUR]']
_x = data.loc[data['Overcapacity constraint relaxed'] == 'Yes']['Max import share per year [%]']
ax.plot(_x, _filter_2, label='Relaxed exp. plan', color='#211951', linewidth=2)

_filter_1 = data.loc[data['Overcapacity constraint relaxed'] == 'No']['Total costs [MEUR]']
_x = data.loc[data['Overcapacity constraint relaxed'] == 'No']['Max import share per year [%]']
ax.plot(_x, _filter_1, label='Strict exp. plan', color='#836FFF', linewidth=2)



_legend = ax.legend(loc='center', facecolor='white', fontsize=14,
                    handlelength=1.5,
                    handletextpad=0.5, ncol=2, borderpad=0.5, columnspacing=1, edgecolor="black", frameon=True,
                    bbox_to_anchor=(0.5, 1.025),
                    shadow=False,
                    framealpha=1
                    )
ax.set_xlim([-2.5, 55])
ax.set_ylim([600000, 760000])
ax.set_yticks([600000, 625000, 650000, 675000, 700000, 725000, 750000])
_legend.get_frame().set_linewidth(0.5) 
plt.tight_layout()
fig.savefig("total costs.pdf", dpi=1000)  


# TOTAL SCRAP
fig, ax = plt.subplots()
ax.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
ax.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)
ax.xaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))
ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))
ax.set_xlabel("Limit on EU's import share [%]", fontsize=16)
ax.set_ylabel("Total scrap [kt]", fontsize=16)



_filter_2 = data.loc[data['Overcapacity constraint relaxed'] == 'Yes']['Total scrap [Mt]']
_x = data.loc[data['Overcapacity constraint relaxed'] == 'Yes']['Max import share per year [%]']
ax.plot(_x, _filter_2, label='Relaxed exp. plan', color='#211951', linewidth=2)

_filter_1 = data.loc[data['Overcapacity constraint relaxed'] == 'No']['Total scrap [Mt]']
_x = data.loc[data['Overcapacity constraint relaxed'] == 'No']['Max import share per year [%]']
ax.plot(_x, _filter_1, label='Strict exp. plan', color='#836FFF', linewidth=2)

_legend = ax.legend(loc='center', facecolor='white', fontsize=14,
                    handlelength=1.5,
                    handletextpad=0.5, ncol=2, borderpad=0.5, columnspacing=1, edgecolor="black", frameon=True,
                    bbox_to_anchor=(0.5, 1.025),
                    shadow=False,
                    framealpha=1
                    )

_legend.get_frame().set_linewidth(0.5) 
ax.set_xlim([-2.5, 55])
ax.set_ylim([0, 80000])
plt.tight_layout()
fig.savefig("total scrap.pdf", dpi=1000)  
  



       




