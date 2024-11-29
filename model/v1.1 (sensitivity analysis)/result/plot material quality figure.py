# import pyam as py
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd

plt.rcParams["figure.figsize"] = [8, 4]
plt.rcParams["xtick.labelsize"] = 12
plt.rcParams["ytick.labelsize"] = 12

def format_thousands(x, pos):
    """
    Format the tick labels with a space between thousands.
    """
    return "{:,.0f}".format(x).replace(",", " ")

_data = pd.read_excel('recycled-based additions as a function of the quality of the recycled material (pessimistic).xlsx')

fig, ax = plt.subplots()
_x = _data['Recycling material efficiency']
_y = _data['Recycling-based additions [in GW]']/1000
_y_50 = _data['Recycling-based additions [in GW, -50% scrap costs]']/1000
_y_25 = _data['Recycling-based additions [in GW, -75% scrap costs]']/1000

ax.plot(_x, _y_25, lw=1.5, linestyle="dotted", color='#698474', marker="o", markersize=4, label='$250~EUR/t$', markevery=2)
ax.plot(_x, _y_50, lw=1.5, linestyle="dashed", color='#698474', marker="s", markersize=0, label='$500~EUR/t$', markevery=2)
ax.plot(_x, _y, lw=1.5, linestyle="solid", color='#698474', marker="s", markersize=4, label='$1000~EUR/t$', markevery=2)

ax.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
ax.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)
ax.set_ylabel("Recycling-based additions [GW]", fontsize=12)
ax.set_xlabel("Reutilization rate of recycled materials [%]", fontsize=12)
ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))
ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_xticklabels(
    ["0%", "20%", "40%", "60%", "80%", "100%"]
)

_c = '#D91656'
ax.plot([0.85, 0.85], [236, 236], linewidth=0, marker='x', markersize=8, color=_c, label='$236~GW~(85\%)$')

_legend = ax.legend(
    loc="upper left",
    facecolor="white",
    handlelength=2.5,
    handletextpad=0.5,
    ncol=1,
    borderpad=0.5,
    columnspacing=1,
    edgecolor="black",
    frameon=True,
    bbox_to_anchor=(0.005, 1 - 0.005),
    shadow=False,
    framealpha=1,
    title='Scrap cost'
)

ax.fill_between(_x, _y, _y_25, color='#D6EFD8')

plt.tight_layout()
fig.savefig('recycling_quality.pdf')
fig.savefig('recycling_quality.png', dpi=2000)
