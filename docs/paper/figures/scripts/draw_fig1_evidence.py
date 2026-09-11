"""Editable, source-backed Fig. 1 design; no experiments or manuscript changes."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

OUT = Path(__file__).resolve().parents[1] / 'design_references'
INK, GRAY, LINE = '#202830', '#56616B', '#C4CBD0'
BLUE, ORANGE = '#225C82', '#A65324'
PALE, WARM = '#F2F6F8', '#FBF5EF'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'pdf.fonttype': 42,
                     'svg.fonttype': 'none', 'text.usetex': False})
fig = plt.figure(figsize=(12, 6.6), facecolor='white')
ax = fig.add_axes([0, 0, 1, 1])
ax.set(xlim=(0, 120), ylim=(0, 66))
ax.axis('off')

def text(x, y, s, size=12, color=INK, weight='normal', mono=False, **kw):
    return ax.text(x, y, s, fontsize=size, color=color, weight=weight,
                   fontfamily='DejaVu Sans Mono' if mono else 'DejaVu Sans',
                   va='center', **kw)

def line(x1, y1, x2, y2, color=LINE, lw=.8, **kw):
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, **kw)

def rect(x, y, w, h, fill='white', color=LINE, lw=.8):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=color, lw=lw))

def arrow(x1, y1, x2, y2, color=INK, lw=1.3):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2), arrowstyle='-|>',
                                mutation_scale=12, lw=lw, color=color,
                                shrinkA=0, shrinkB=0))

def tag(x, y, letter):
    rect(x, y-.85, 1.8, 1.7, PALE, BLUE, .7)
    text(x+.9, y, letter, 10.5, BLUE, 'bold', ha='center')

# A compact task contrast, rather than a large illustrative title.
text(2, 63.1, 'Repository editing', 12, GRAY, 'bold')
text(24, 63.1, 'Repository + issue', 12, GRAY)
arrow(48,63.1,53,63.1,GRAY,.9)
text(56,63.1,'Patch',12,GRAY)
arrow(72,63.1,77,63.1,GRAY,.9)
text(81,63.1,'Evaluate in the same repository',12,GRAY)
text(2, 59.1, 'Feature lifting', 12, BLUE, 'bold')
text(24,59.1,'Repository + contract',12,INK)
arrow(48,59.1,53,59.1,BLUE)
text(56,59.1,'New package',12,ORANGE,'bold')
arrow(72,59.1,77,59.1,BLUE)
text(81,59.1,'Evaluate without the source repository',12,BLUE,'bold')
line(2,55.8,118,55.8,INK,.8)

text(2,52.6,'(a) Intact implementation evidence',13.5,INK,'bold')
text(43,52.6,'(b) A new package boundary',13.5,INK,'bold')
text(84,52.6,'(c) Behavior must survive',13.5,INK,'bold')

# Actual source paths and symbols from the pinned task, simplified for display.
rect(2,29.5,34,19.4,PALE)
text(3.5,47.1,'blinker / src / blinker',12,BLUE,'bold',mono=True)
line(3.5,45.4,34.5,45.4)
text(3.5,43.4,'base.py',12,INK,'bold',mono=True)
text(5,40.9,'Signal.connect / send',11.3,mono=True)
text(5,38.5,'_cleanup_receiver; Namespace',11.3,mono=True)
text(3.5,35.9,'_utilities.py',12,INK,'bold',mono=True)
text(5,33.5,'reference; hashable_identity',11.3,mono=True)
text(3.5,31.1,'_saferef.py: BoundMethodWeakref',11.1,mono=True)
text(2,27.9,'Selected symbols from the intact source repository.',10.1,GRAY)

rect(2,11.9,34,13.8)
text(3.5,23.8,'Public behavioral contract',12,INK,'bold')
tag(3.5,20.7,'A'); text(6.1,20.7,'Sender-specific dispatch',11.5)
tag(3.5,17.7,'B'); text(6.1,17.7,'Weak-receiver cleanup',11.5)
tag(3.5,14.7,'C'); text(6.1,14.7,'Stable identity for each name',11.5)
text(2,10.1,'Selected clauses; async / global singleton excluded.',10.1,GRAY)

# Both inputs reach the agent; the agent is an action, not a giant decorative box.
line(36,39,39,39,BLUE,1)
line(36,19,39,19,BLUE,1)
line(39,19,39,39,BLUE,1)
arrow(39,35,43,35,BLUE)
text(39.5,42,'Agent',11,BLUE,'bold',ha='center')

rect(43,28.7,31,20.2,WARM,ORANGE,1.5)
text(44.5,46.5,'Submitted package',12,ORANGE,'bold')
line(44.5,44.6,72.5,44.6,ORANGE,.7)
text(44.5,42.5,'from featurelifted import (',11.3,mono=True)
text(44.5,39.9,'    Signal, Namespace, ANY)',11.3,mono=True)
line(44.5,37.7,72.5,37.7)
text(44.5,35.5,'Dispatch + lifetime + identity',11.8,INK,'bold')
text(44.5,32.8,'Supporting behavior must be retained.',10.5,GRAY)
text(44.5,30.7,'Internal organization is unconstrained.',10.5,GRAY)

text(43,25.8,'Permitted implementation strategies',11.5,INK,'bold')
text(43,23.2,'Extract / adapt / reimplement',11.5)
line(43,21.1,74,21.1)
text(43,18.9,'Forbidden runtime dependencies',11.5,INK,'bold')
text(46,16.2,'import blinker',11.4,mono=True)
text(46,13.4,'read source repository files',10.8)
for y in (16.2,13.4):
    line(43.4,y-.55,44.5,y+.55,ORANGE,1.4)
    line(43.4,y+.55,44.5,y-.55,ORANGE,1.4)

# The submitted artifact visibly crosses into the isolated evaluation runtime.
line(79,11.9,79,48.6,GRAY,1,linestyle=(0,(4,4)))
text(79,50.1,'Runtime boundary',10.5,GRAY,ha='center')
arrow(74,35,84,35,ORANGE,1.8)
text(79,38.0,'Package',10.5,ORANGE,'bold',ha='center',
     bbox={'facecolor':'white','edgecolor':'none','pad':1})

rect(84,11.9,34,37,fill='white',color=BLUE,lw=1)
rect(84,41.4,34,7.5,fill=PALE,color=BLUE,lw=.7)
text(85.5,46.9,'Source-free evaluator',12,BLUE,'bold')
text(85.5,44.5,'Source repository unavailable',11.2)
text(85.5,42.6,'Network off; fixed dependency environment',9.8,GRAY)
text(85.5,39.5,'Illustrative contract checks',11.3,INK,'bold')

tag(85.5,36.8,'A'); text(88.1,36.8,'Sender filtering',11.5,INK,'bold')
text(85.5,33.9,'Bound to p; event from q (q ≠ p)',10.7)
text(85.5,31.5,'Expected: receiver is not called',10.7,BLUE)
line(85.5,29.7,116.5,29.7)
tag(85.5,27.4,'B'); text(88.1,27.4,'Receiver lifetime',11.5,INK,'bold')
text(85.5,24.6,'Weak receiver is garbage-collected',10.7)
text(85.5,22.2,'Expected: receiver is removed',10.7,BLUE)
line(85.5,20.4,116.5,20.4)
tag(85.5,18.1,'C'); text(88.1,18.1,'Namespace identity',11.5,INK,'bold')
text(85.5,15.4,'ns.signal("x") is ns.signal("x")',10.3,mono=True)
text(85.5,13.4,'Expected: True',10.7,BLUE)

# One clear conjunctive gate; test scenarios above are illustrative, not outcomes.
line(2,8.0,118,8.0,INK,.8)
text(2,5.9,'Functional pass',11.5,INK,'bold')
text(21,5.9,'Build  ∧  Public tests  ∧  Hidden tests  ∧  Source isolation',12,BLUE,'bold')
text(2,2.9,'Agent-visible: source repository + contract',10.5,GRAY)
text(60,2.9,'Withheld: benchmark tests + reference implementation',10.5,GRAY)

OUT.mkdir(parents=True, exist_ok=True)
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
outside=[]
for t in ax.texts:
    b=t.get_window_extent(renderer)
    if b.x0<0 or b.y0<0 or b.x1>fig.bbox.width or b.y1>fig.bbox.height:
        outside.append(t.get_text())
if outside:
    raise ValueError(f'Text outside canvas: {outside}')
for suffix in ('svg','pdf','png'):
    p=OUT/f'fig1_evidence_v2.{suffix}'
    fig.savefig(p,dpi=220,facecolor='white')
    print(p)
(OUT/'fig1_evidence_v2_validation.json').write_text(json.dumps({
    'canvas_inches':[12,6.6], 'intended_width_inches':7.2,
    'main_body_size_at_intended_width_pt':'6.4–7.2',
    'outside_canvas_text':outside,
    'source':'benchmark/tasks/blinker__signal_registry_core__001/TASK.md',
    'checks':'Illustrative contract scenarios, not extracted test bodies or experiment outcomes',
    'manuscript_replaced':False, 'new_experiments':False
},indent=2),encoding='utf-8')
plt.close(fig)
