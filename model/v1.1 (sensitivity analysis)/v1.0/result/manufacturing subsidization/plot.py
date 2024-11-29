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

data = pd.read_excel('results.xlsx')

fig, ax = plt.subplots()
_x = data['Subsidization [EUR/MW]']
_y = data['Recycling-based additions']

ax.plot(_x, _y, color='#7F9F80', linewidth=2.0, linestyle='dashed', marker='o', markersize=0, label='Exact progression')

x_points = [_x[0], _x[4], _x[11], _x[17], _x[20]]
y_points = [_y[0], _y[4], _y[11], _y[17], _y[20]]
linear_interp = interp1d(x_points, y_points, kind='linear')

y_interp = linear_interp(_x)
indices_to_mark = [0, 4, 11, 17, 20]
ax.plot(_x, y_interp, color='#1A3636', linewidth=2.5, linestyle='solid', label='Piecewise approx.', marker='o', markevery=indices_to_mark)

ax.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
ax.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)

ax.yaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))
ax.xaxis.set_major_formatter(FuncFormatter(format_thousands))
ax.set_xlabel("Incentives for recycled-based mfg. [EUR/MW]", fontsize=16)
ax.set_ylabel("Share of recycled-based additions", fontsize=16)

       
_legend = ax.legend(loc='upper left', facecolor='white', fontsize=14,
                    handlelength=1.5,
                    handletextpad=0.5, ncol=1, borderpad=0.5, columnspacing=1, edgecolor="black", frameon=True,
                    bbox_to_anchor=(0.005, 1-0.005),
                    shadow=False,
                    framealpha=1
                    )

_legend.get_frame().set_linewidth(0.5) 

_col = '#B43F3F'
_x_cord = _x[11] + 0.5*(_x[17] - _x[11])
ax.annotate(f'({_y[11]:.1f}%)',
            xy=(_x[11], _y[11]), xycoords='data',
            xytext=(_x_cord, _y[11]*0.6), textcoords='data',
            arrowprops=dict(arrowstyle="-", 
                connectionstyle='angle,angleA=180,angleB=90,rad=0', color=_col),
            fontsize=16, color=_col, horizontalalignment='center',zorder=0, verticalalignment='center',
            bbox=dict(boxstyle="square,pad=0.3",
                  fc="white", ec=_col, lw=0, alpha=1))

_index = 17

ax.annotate(f'({_y[_index]:.1f}%)',
            xy=(_x[_index], _y[_index]), xycoords='data',
            xytext=(_x_cord*0.95, _y[_index]-0.4*_y[11]), textcoords='data',
            arrowprops=dict(arrowstyle="-", 
                connectionstyle='angle,angleA=90,angleB=0,rad=0', color=_col),
            fontsize=16, color=_col, horizontalalignment='center',zorder=0, verticalalignment='center',
            bbox=dict(boxstyle="square,pad=0.3",
                  fc="white", ec=_col, lw=0, alpha=1))

# ax.annotate(bbox=dict(boxstyle="square,pad=0.3", fc="white", ec=_col, lw=1, alpha=1))

_y0 = ax.get_ylim()[0]
# ax.set_ylim([_y0, 55])
# ax.set_title('Solar modules (EU-27)', fontsize=16)
plt.tight_layout()
fig.savefig("subsidization_manufacturing.pdf", dpi=1000)


###############################################################################
fig, ax = plt.subplots()
_x2_star = 19.7 * 0.92 * 10000
ax.plot(_x[11:18], y_interp[11:18], color='#1A3636', linewidth=2.0, linestyle='solid', label='Recycling-based', marker='o', markevery=[0, 6], zorder=3)
# ax.plot([_x[-1], _x2_star], [y_interp[-1], y_interp[-1]], color='#1A3636', linewidth=2.0, linestyle='solid', zorder=3)
ax.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
ax.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)
ax.yaxis.set_major_formatter(ticker.PercentFormatter())
ax.xaxis.set_major_formatter(FuncFormatter(format_thousands))
ax.set_xlabel("Incentives for EU mfg. [EUR/MW]", fontsize=16)
ax.set_ylabel("Share of EU-based additions", fontsize=16)
_x1 = 12.7 * 0.92 * 10000
_x2 = ax.get_xlim()
ax.axvspan(_x1, _x2_star, color='#508C9B', alpha=0.35, label='IRA incentives', zorder=1)
ax.set_xlim(60000, 190000)
ax.set_ylim(0, 55)

_delta_x = _x[17] - _x[16]
_delta_y = y_interp[17] - y_interp[16]
x_00 = _x[17]
y_00 = y_interp[17]

ax.plot([x_00, _x2_star], [y_00, y_00+_delta_y/_delta_x*(_x2_star - x_00)], 
        linestyle='dashed', color='#DC5F00', 
        linewidth=1., label='Mining-based')

# _patches = []
# for _lab, _col in [['Recycled-based', '#1A3636'], ['Mining-based', '#DC5F00']]:
#     _patches.append(mpatches.Patch(color=_col, label=_lab))
   
_legend = ax.legend(loc='upper left', facecolor='white', fontsize=14,
                    handlelength=1,
                    handletextpad=0.5, ncol=1, borderpad=0.5, columnspacing=1, edgecolor="black", frameon=True,
                    bbox_to_anchor=(0.005, 1-0.005),
                    shadow=False,
                    framealpha=1
                    )

_legend.get_frame().set_linewidth(0.5) 


# Zeichne die Linie mit Pfeilen an beiden Enden
plt.annotate('', xy=(_x2_star, 5.5), xytext=(_x1, 5.5),
             arrowprops=dict(arrowstyle='<->', color='#134B70', lw=1.25))

# Füge Text zur Markierung hinzu
plt.text((_x1 + _x2_star) / 2, 5.5 + 0.25, 'IRA incentives', 
         ha='center', va='bottom', color='#134B70', fontsize=14)

_col = '#B43F3F'
ax.annotate(f'({_y[11]:.1f}%)',
            xy=(_x[11], _y[11]), xycoords='data',
            xytext=(_x[11]*0.7, _y[11]*0.75), textcoords='data',
            arrowprops=dict(arrowstyle="-", 
                connectionstyle='angle,angleA=180,angleB=90,rad=0', color=_col),
            fontsize=16, color=_col, horizontalalignment='left',zorder=0, verticalalignment='center',
            bbox=dict(boxstyle="square,pad=0.3",
                  fc="white", ec=_col, lw=0, alpha=1))

ax.annotate(f'({_y[_index]:.1f}%)',
            xy=(_x[_index], _y[_index]), xycoords='data',
            xytext=(_x_cord*1.135, _y[_index]+0.7*_y[11]), textcoords='data',
            arrowprops=dict(arrowstyle="-", 
                connectionstyle='angle,angleA=90,angleB=0,rad=0', color=_col),
            fontsize=16, color=_col, horizontalalignment='center',zorder=0, verticalalignment='center',
            bbox=dict(boxstyle="square,pad=0.3",
                  fc="white", ec=_col, lw=0, alpha=1))

ax.set_xticks([40000, 60000, 90000, 120000, 150000, 180000])
plt.setp(ax.get_xticklabels()[0], visible=False)
# ax.set_title('Solar modules (EU-27)', fontsize=16)

plt.tight_layout()
fig.savefig("subsidization_IRA.pdf", dpi=1000)
