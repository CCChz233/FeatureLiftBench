"""Render paper task/validation schematics from documented design; no experiments."""
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


def construction():
    fig,ax=canvas(4.0,'From reusable capabilities to a validated benchmark',
                 'Construction defines the task; complementary checks support the frozen release.')
    ax.text(.018,.94,'CONSTRUCTION',fontsize=8.2,weight='bold',color=BLUE)
    boxes=[(.018,'Select capability','Reusable behavior\nInspectable source\nOffline execution'),
           (.265,'Source + contract','Pinned source snapshot\nAPI + behavior obligations\nScope + exclusions'),
           (.512,'Build evaluation','Protected tests\nContract mappings\nIndependent reference'),
           (.759,'Freeze release','200 tasks\n176 repositories\n182 source snapshots')]
    for x,title,body in boxes: box(ax,x,.605,.223,.285,title,body,fs=7.3,title_fs=8.1)
    for x in (.249,.496,.743): arrow(ax,(x-.002,.74),(x+.009,.74))
    ax.text(.018,.504,'VALIDATION',fontsize=8.2,weight='bold',color=GREEN)
    specs=[(.018,'Automated checks','Source / asset consistency\nAPI + behavior mappings\n200 task checks'),
           (.265,'AI-assisted audit','Contract and test review\nRepair-scope review:\n38 tasks'),
           (.512,'Author review','Task and test semantics\nTaxonomy + failure labels\nSample-based review'),
           (.759,'Reference replay','3 runs per task\n600 / 600 passing runs\n200 stable outcomes')]
    for x,title,body in specs: box(ax,x,.155,.223,.29,title,body,GREEN,'#F0F8F4',7.3,title_fs=8.1)
    ax.text(.018,.067,'Quality control combines AI-assisted review and author spot-checks; problematic candidates are excluded.',
            fontsize=7.1,color=MUTED)
    export(fig,'fig02_construction_validation')


if __name__=='__main__':
    apply_paper_style(); task(); construction()
