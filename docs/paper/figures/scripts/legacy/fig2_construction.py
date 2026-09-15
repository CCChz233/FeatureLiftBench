"""Historical Fig. 2 schematic; contains old 200-task scope, not the current fig2.png.

Preserves original drawing code and historical text. Not used by paper.py figures.
"""
from schematic_helpers import box, arrow, canvas, export, apply_paper_style, BLUE, GREEN, MUTED


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

if __name__ == "__main__":
    apply_paper_style()
    construction()
