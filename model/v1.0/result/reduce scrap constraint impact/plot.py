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
plt.rcParams['xtick.labelsize'] = 11
plt.rcParams['ytick.labelsize'] = 11

data = pd.read_excel('values.xlsx')

fig, ax = plt.subplots()

dict_values = dict()

_color_sce = {
    
    }


for index, row in data.iterrows():
    dict_values[(row.Scenario, row['Circular constraint (2035)'], row['Scrap costs'])] = [row['Share of recycled-based'], row['Total costs']]

for key in dict_values.keys():
    pass
    
    





# _x = data['Subsidization [EUR/MW]']
# _y = data['Recycling-based additions']

# ax.plot(_x, _y, color='#7F9F80', linewidth=2.0, linestyle='dashed', marker='o', markersize=0, label='Exact progression')

# x_points = [_x[0], _x[4], _x[11], _x[17], _x[20]]
# y_points = [_y[0], _y[4], _y[11], _y[17], _y[20]]
# linear_interp = interp1d(x_points, y_points, kind='linear')

# y_interp = linear_interp(_x)
# indices_to_mark = [0, 4, 11, 17, 20]
# ax.plot(_x, y_interp, color='#1A3636', linewidth=2.5, linestyle='solid', label='Piecewise approx.', marker='o', markevery=indices_to_mark)

ax.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
ax.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)

ax.xaxis.set_major_formatter(ticker.PercentFormatter())
ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))
ax.set_ylabel("Total costs [MEUR]", fontsize=12)
ax.set_xlabel("Share of recycled-based additions in the total", fontsize=12)

       
# _legend = ax.legend(loc='upper left', facecolor='white', fontsize=12,
#                     handlelength=1.5,
#                     handletextpad=0.5, ncol=1, borderpad=0.5, columnspacing=1, edgecolor="black", frameon=True,
#                     bbox_to_anchor=(0.005, 1-0.005),
#                     shadow=False,
#                     framealpha=1
#                     )

# _legend.get_frame().set_linewidth(0.5) 

plt.tight_layout()
fig.savefig("reduce scrap constraints scatter.pdf", dpi=1000)

