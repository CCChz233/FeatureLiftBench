"""Behavioral properties in confirmed source-exposed failures; Fig. 6.

Pooled run composition, with no model ranking or property-specific failure rates.
The companion codebook table supplies operational definitions; counts appear here.
"""
import json
from pathlib import Path
import sys
from figure_common import BLUE, INK, finish, run_single
from matplotlib import pyplot as plt
import paper_style
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from behavioral_obligations import load_analysis


def build_figure():
    data=load_analysis()
    rows=data['properties']
    fig,ax=plt.subplots(figsize=(6.8,2.65))
    fig.subplots_adjust(left=.29,right=.75,bottom=.19,top=.87)
    fig.text(.01,.97,'(a) Composition of confirmed semantic violations',fontsize=9,weight='bold',va='top',color=INK)
    fig.text(.77,.885,'Runs / distinct tasks',fontsize=8,va='bottom',color=INK)
    ax.barh(range(len(rows)),[r['percent'] for r in rows],height=.57,color=BLUE,zorder=3)
    ax.set_yticks(range(len(rows)),[r['label'] for r in rows],fontsize=8)
    ax.set_ylim(len(rows)-.42,-.65)
    ax.set_xlim(0,40)
    ax.set_xticks([0,10,20,30,40])
    ax.set_xlabel('Share of confirmed behavioral violations (%)',fontsize=8)
    ax.tick_params(axis='y',length=0,pad=6)
    ax.tick_params(axis='x',labelsize=8,length=3)
    ax.grid(axis='x',color='#E8EDF1',linewidth=.6,zorder=0)
    ax.spines[['top','right','left']].set_visible(False)
    ax.spines['bottom'].set_color('#9AA5AD')
    for i,row in enumerate(rows):
        ax.text(1.04,i,f"{row['n']} runs / {row['distinct_tasks']} tasks",va='center',fontsize=8,color=INK,transform=ax.get_yaxis_transform())
    fig.canvas.draw()
    for item in fig.findobj(plt.Text):
        if item.get_visible() and item.get_text():
            box=item.get_window_extent(fig.canvas.get_renderer())
            assert box.x0>=-1 and box.y0>=-1 and box.x1<=fig.bbox.x1+1 and box.y1<=fig.bbox.y1+1,item.get_text()
    return fig,data


def draw_failure_analysis():
    fig,data=build_figure()
    output=Path(paper_style.OUTPUT_DIR);output.mkdir(parents=True,exist_ok=True)
    (output/'fig6_plot_data.json').write_text(json.dumps(data,indent=2)+'\n')
    finish(fig,'fig6_behavioral_obligations')


if __name__=='__main__':
    run_single(draw_failure_analysis,__doc__)
