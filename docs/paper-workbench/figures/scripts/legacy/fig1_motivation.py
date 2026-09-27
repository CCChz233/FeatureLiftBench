"""Historical Fig. 1 schematic; does not reproduce the AI-edited fig1.png.

Preserves original drawing code and historical text. Not used by paper.py figures.
"""
from schematic_helpers import box, arrow, canvas, export, apply_paper_style, INK, GREEN, GOLD, MUTED


def task():
    fig,ax=canvas(3.8,'Feature lifting: preserve behavior across a new package boundary',
                 'The source is implementation evidence; the new package is the evaluation target.')
    box(ax,.018,.39,.275,.48,'1  Complete source',
        'Pinned Blinker repository\nCode, tests, docs, resources\n\nPublic output contract\nAgent locates supporting code')
    box(ax,.363,.39,.275,.48,'2  New package',
        'Agent extracts, adapts,\nor reimplements the capability\n\nfeaturelifted API\nOwn runtime dependencies',GREEN,'#F0F8F4')
    box(ax,.708,.39,.275,.48,'3  Source-free evaluator',
        'Only the submission enters\nSource repository unavailable\n\nBuild + Public + Hidden\n+ Isolation',GOLD,'#FCF7EA')
    arrow(ax,(.301,.65),(.354,.65)); arrow(ax,(.647,.65),(.699,.65))
    ax.text(.328,.96,'PACKAGE\nBOUNDARY',ha='center',va='top',fontsize=6.5,color=MUTED)
    ax.plot([.328,.328],[.41,.73],color=MUTED,linestyle=(0,(3,3)),linewidth=.8)
    ax.text(.5,.298,'Preserved obligations: dispatch  •  weak-receiver lifetime  •  namespace identity',
            ha='center',fontsize=8,color=INK)
    ax.plot([.025,.98],[.23,.23],color='#CAD5DC',linewidth=.7)
    ax.text(.025,.162,'Repository editing',fontsize=8.1,weight='bold',color=MUTED)
    ax.text(.32,.162,'Existing project  →  patch  →  evaluation in that project',fontsize=8.1,color=MUTED)
    ax.text(.025,.075,'Feature lifting',fontsize=8.1,weight='bold',color=GREEN)
    ax.text(.32,.075,'Source evidence  →  new package  →  source-free evaluation',fontsize=8.1,color=INK)
    export(fig,'fig01_feature_lifting')

if __name__ == "__main__":
    apply_paper_style()
    task()
