"""Shared drawing primitives for historical Fig. 1/2 designs only."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figure_data import prepare_matplotlib
prepare_matplotlib()
from matplotlib import pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from paper_style import FIGURES_DIR, apply_paper_style, save_figure

INK = '#20323F'
MUTED = '#536674'
BLUE = '#0072B2'
GREEN = '#168569'
GOLD = '#AF7200'


def box(ax, x, y, w, h, title, body, color=BLUE, fill='#F2F7FA', fs=8.2, title_fs=9):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.009,rounding_size=0.012',
                               linewidth=1,edgecolor=color,facecolor=fill))
    ax.text(x+.018,y+h-.040,title,ha='left',va='top',fontsize=title_fs,weight='bold',color=color)
    ax.text(x+.018,y+h-.115,body,ha='left',va='top',fontsize=fs,linespacing=1.55,color=INK)


def arrow(ax,a,b,color=MUTED):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=11,linewidth=1.2,color=color))


def canvas(height,title,subtitle):
    fig=plt.figure(figsize=(7.2,height)); ax=fig.add_axes([.025,.035,.95,.86])
    ax.set(xlim=(0,1),ylim=(0,1)); ax.axis('off')
    fig.text(.04,.955,title,fontsize=11,weight='bold',color=INK)
    fig.text(.04,.907,subtitle,fontsize=8,color=MUTED)
    return fig,ax


def export(fig,name):
    for path in save_figure(fig,name):
        if path.suffix=='.pdf': (FIGURES_DIR/path.name).write_bytes(path.read_bytes())
        print(path)
    plt.close(fig)
