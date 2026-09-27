"""Publication vector diagram of three evidence-grounded reconstruction pairs."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


def draw():
    from figure_common import finish
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})
    fig, ax = plt.subplots(figsize=(15, 7.5))
    fig.subplots_adjust(0.006, 0.008, .994, .99)
    ax.set(xlim=(0, 15), ylim=(0, 8.3))
    ax.axis('off')
    ink, muted, blue = '#182d3e', '#536575', '#1665a1'

    def text(x, y, s, size=12, bold=False, color=ink, ha='left', **kw):
        ax.text(x, y, s, fontsize=size, fontweight='bold' if bold else 'normal',
                color=color, ha=ha, va='center', linespacing=1.4, **kw)

    def box(x, y, w, h, fill, edge='none', radius=.10):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                     boxstyle=f'round,pad=0,rounding_size={radius}',
                     facecolor=fill, edgecolor=edge, linewidth=.85))

    def arrow(start, end, color=ink, style='-|>'):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style,
                     mutation_scale=12, color=color, linewidth=1.15))

    headings = [(2.02, 'Upstream / source', 'Implementation evidence'),
                (6.17, 'Destination obligation', 'In the lifted package'),
                (9.32, 'Reconstruction', 'Paired agent artifacts'),
                (13.02, 'Observed outcome', 'Under the same contract')]
    for x, title, sub in headings:
        text(x, 8.04, title, 13, True)
        text(x, 7.73, sub, 10, color=muted)
    text(.12, 8.04, 'Case', 13, True)
    text(5.70, 8.03, 'New\npackage\nboundary', 10.5, True, blue, 'center')
    ax.plot([5.70, 5.70], [.43, 7.52], color=blue, lw=1.25, ls=(0, (5, 4)))

    rows = [
        dict(name='platformdirs', kind='ADAPTATION', desc='Platform-specific\nuser and cache\ndirectories',
             source_title='Implicit host platform', source='Host platform selects the\nimplementation; path helpers\nassume that platform.',
             source_flow='host platform → path helper',
             obligation_title='Explicit platform input', obligation='Returned paths must honor\nthe selected platform,\nindependently of the host.',
             failed_title='Host-dependent joining', failed='Windows branch still uses\nthe host’s path operations.',
             passed_title='Platform-aware helper', passed='Path operations follow\nthe selected platform.',
             bad='Selected-platform\nrequirement fails', good='Passes platform\nbehavior checks',
             relationship='Platform selection ↔ path operations'),
        dict(name='cerberus', kind='PRESERVATION', desc='Schema validation\nwith structured\ndiagnostics',
             source_title='Grouped diagnostics', source='Child validators produce\ngrouped error records for\na recursive error handler.',
             source_flow='validator → groups → handler',
             obligation_title='Structured nested errors', obligation='Nested validation must\npreserve structured diagnostics\nand child error paths.',
             failed_title='Incompatible formatter', failed='Group records exist, but\ngroup-aware handling is missing.',
             passed_title='Group-aware renderer', passed='Group production connects\nto recursive diagnostic rendering.',
             bad='Nested diagnostic\nchecks fail', good='Passes nested\ndiagnostic checks',
             relationship='Validator ↔ shared diagnostic representation ↔ formatter'),
        dict(name='importlib_\nresources', kind='ADAPTATION', desc='Access to package\nresource files',
             source_title='Filesystem-backed resources', source='Resource discovery may return\nan ordinary filesystem-backed\nresource object.',
             source_flow='package → resource → path',
             obligation_title='Destination traversal policy', obligation='Resource traversal must stay\nwithin the exposed tree:\nan added destination obligation.',
             failed_title='Unguarded traversal', failed='Resource reads delegate\nto an unrestricted resource object.',
             passed_title='Boundary wrapper', passed='Child-path resolution enforces\nthe exposed resource boundary.',
             bad='Evaluated boundary\nchecks fail', good='Passes evaluated\nboundary checks',
             relationship='Resource access ↔ traversal policy')
    ]
    for i, r in enumerate(rows):
        y = 5.39 - i * 2.47
        box(0, y+.15, 1.78, 2.01, '#edf4fa')
        text(.16, y+1.70, r['name'], 14, True)
        box(.14, y+1.04, 1.49, .30, '#d6e7f5')
        text(.885, y+1.19, r['kind'], 9.2, True, blue, 'center')
        text(.16, y+.62, r['desc'], 11)
        box(1.98, y+.15, 3.27, 2.01, '#f5f7fa', '#bdc9d3')
        text(2.16, y+1.83, r['source_title'], 11.9, True)
        text(2.16, y+1.12, r['source'], 11.6)
        box(2.12, y+.32, 2.98, .35, '#e5ecf2')
        text(3.61, y+.495, r['source_flow'], 10, color=muted, ha='center')
        arrow((5.28, y+1.15), (6.04, y+1.15))
        box(6.12, y+.15, 2.90, 2.01, '#fff7e9', '#e5cda3')
        text(6.30, y+1.77, r['obligation_title'], 11.6, True)
        text(6.30, y+.96, r['obligation'], 11.2)
        for passing in (False, True):
            by = y+.15 if passing else y+1.23
            color = '#287451' if passing else '#b3373b'
            box(9.48, by, 5.46, .93, '#edf7f0' if passing else '#fdf0ef',
                '#a8cfb7' if passing else '#e5b3b2')
            arrow((9.04, by+.465), (9.44, by+.465))
            # Shape and text redundantly encode status for grayscale printing.
            if passing:
                ax.plot([9.65,9.72,9.87],[by+.62,by+.54,by+.72], color=color, lw=2.4, solid_capstyle='round')
            else:
                ax.plot([9.66,9.84],[by+.54,by+.72],color=color,lw=2.3,solid_capstyle='round')
                ax.plot([9.66,9.84],[by+.72,by+.54],color=color,lw=2.3,solid_capstyle='round')
            text(9.98, by+.69, ('Passing: ' if passing else 'Failed: ') + r['passed_title' if passing else 'failed_title'], 11.2, True, color)
            text(9.98, by+.29, r['passed' if passing else 'failed'], 10.7)
            ax.plot([12.88,12.88],[by+.11,by+.82],color='#c2d2c9' if passing else '#e3c8c8',lw=.9)
            text(13.05, by+.465, r['good' if passing else 'bad'], 10.6, color=color)
        # The supporting relationship spans source and reconstruction, not the outcome.
        ax.plot([3.62,3.62,11.55,11.55],[y+.10,y-.045,y-.045,y+.10],color=muted,lw=.85)
        text(7.55, y-.045, r['relationship'], 11.2, ha='center',
             bbox=dict(facecolor='white', edgecolor='none', pad=4))
    finish(fig, 'fig6_qualitative_mechanisms')


if __name__ == '__main__':
    from figure_common import run_single
    run_single(draw, __doc__)
