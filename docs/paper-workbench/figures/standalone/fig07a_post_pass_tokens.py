#!/usr/bin/env python3
"""Standalone renderer for one current-paper figure. Run --help for output options."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt

BLUE = "#0072B2"
INK = "#202B33"
MUTED = "#56616A"
WIDTH = 7.2

matplotlib.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 9, "axes.labelsize": 9, "axes.titlesize": 9,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.8,
    "axes.axisbelow": True, "axes.grid": False,
    "lines.linewidth": 1.2, "lines.markersize": 4, "legend.frameon": False,
    "text.usetex": False, "pdf.fonttype": 42, "ps.fonttype": 42,
    "svg.fonttype": "none", "figure.facecolor": "white",
    "savefig.facecolor": "white", "savefig.transparent": False,
})

from matplotlib.ticker import MaxNLocator

DATA = {
  "summaries": [
    {
      "configuration": "deepseek-v4-pro",
      "short": "Pro",
      "checkpoint_n": 98
    },
    {
      "configuration": "deepseek-v4-flash",
      "short": "Flash",
      "checkpoint_n": 93
    },
    {
      "configuration": "gpt-5.6-luna",
      "short": "Luna",
      "checkpoint_n": 43
    },
    {
      "configuration": "glm-5.3-flash",
      "short": "GLM",
      "checkpoint_n": 27
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "short": "Qwen",
      "checkpoint_n": 25
    },
    {
      "configuration": "gpt-oss-120b",
      "short": "OSS",
      "checkpoint_n": 31
    }
  ],
  "point_data": [
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5399362152344981
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7450314618618723
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7956574237785157
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.29396019181604943
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7148290696724052
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5791124986178938
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5979934187189968
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6712812533491047
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7352927259476758
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.8285995281825622
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7780735615212808
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5305591922328298
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.4851324420694251
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.552448552283335
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.718820411887722
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6673871485727512
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6109411146787509
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6041419346556018
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5817520323809562
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6545490990768352
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.4587968312984642
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.562198117618314
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5971260988963232
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5547229672008053
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7330242778083165
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7643659275618712
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5745967287131162
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7390122902955786
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5106865149739275
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.1552162568960791
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7192434435241992
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7527866780991922
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.8817036087320053
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7614167727607851
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.8052690622467079
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7412527848036382
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.888250874970542
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5602944826829789
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7095773517606179
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7445033953830431
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.8516131048880079
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7229497235164882
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.9023830197008922
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6651224628552198
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6204829508960468
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.8527971805775474
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6665403345693146
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.3908441350561599
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6731489154300335
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.8474942185737689
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7307966341133837
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7193547431451359
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.645219917237925
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.419292236823298
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5729634608613389
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6365640971004807
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7664424386447097
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7778873822912545
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6163982363648086
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6305707438859397
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6162558622840931
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.25264912448595866
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.4778306698401904
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5484547538023474
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.748820913187153
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.631662104847008
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7241580362374961
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7307756826172173
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5122757638867929
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.1929664469446307
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.83184194391996
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6474467339980178
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.8021844407657992
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6444115013319432
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5793084685943273
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.2619114063918546
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5376461419897083
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.4510619925103354
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7126696571980726
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7436237136723751
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7256135985911264
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7146197485433916
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6145770959813565
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6943384991626572
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.9071890275675542
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.46987859187237163
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7691257050353084
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7303897944083327
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6831782137773295
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5904571197643097
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7282936086346674
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7688450881944032
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5444162983129349
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.6503708052731222
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.5771433015027155
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.747060877806311
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7613726661705783
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_fraction": 0.7934050752379097
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8418564135626811
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7653055952477521
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7750370439029516
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7073077443536698
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8138429799695479
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8182266363176542
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.9064280299993953
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8938966287286045
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6972691901113623
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6429804190434784
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6580853995855929
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6404448378954218
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.700245881531523
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6902069099411267
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8133067970269313
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7225572440184027
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6794603952741495
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8203795243141839
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.5426045521071888
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7545685927611993
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6392095647344266
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.688832492445453
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7956749451270434
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.697849537452414
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.645660525079597
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7621319960931595
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8256420495669753
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.5816574080409037
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6888516731708816
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7351516667537566
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8118555105500255
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7166623236682521
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8192672488145833
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6277756743794307
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.857064914372028
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.5437909934349405
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8235273936885557
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7500140224860271
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7888898807457441
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7480356214072938
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8651282021883989
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.9041364225471151
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8186338479884214
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7600641729325991
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.71975098945824
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8327836733446564
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8706794607235545
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7300633292797323
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.70294003852962
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6488338750653815
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7112435665975048
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.9060165566687733
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7151013032688768
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7770769177843196
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6917403119915897
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.738780010431959
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.5276039484938854
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6652432065646842
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.773699573086173
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8288769386141543
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6031974095433728
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7345790421890228
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6120929367494142
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6801170447194204
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7688656104572751
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.3957530300336525
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8278426305363229
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7052006878764052
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.5660315909091425
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.5894327509036577
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6618961016627433
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6813030747422095
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7803978383377814
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7969103578052994
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6869121015223905
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.3920095228267759
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.732277618917295
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6786393515435291
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6145874868196036
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6728708491585832
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6269497950604408
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7614017514214722
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7869743556597323
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8308612726496714
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7826544790262036
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.5967831814963437
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.6055172196981816
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7660193678377967
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.599440415272316
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.5119055178700747
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7817770552275173
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.7882260488399803
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_fraction": 0.8005081921218833
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.5092023184229774
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.6620285354251426
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.8760488144379696
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.899995519994714
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.6781283961737666
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.8485004038680748
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.6403555170018371
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.5523336208335652
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.7271866121921081
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.5061746316321919
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.49793574685462694
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.6528403774618317
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.31544731311725643
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.6571451688280636
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.6488955638627311
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.5138572979334274
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.6512407749497229
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.5122976314368657
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.48080988001635966
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.6397327868695843
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.7902683792405546
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.7275440310634786
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.7454797254180606
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.7080012763365274
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.5794369064718105
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.45875217111464933
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.5304837111443822
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.5264673619757406
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.6478034506346432
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.4803654333743449
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.5443123794995657
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.38097349277217524
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.5785390438647892
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.552028733634573
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.5289927009098444
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.5188232231189794
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.647063874790406
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.5812069026191353
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.6266057468984776
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.65489016043281
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.5109807501036423
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.11042952757659616
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_fraction": 0.6788703151780469
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.5480719679819717
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.8882716196351585
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.5186801476236708
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.36218559274058587
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.4774740315624499
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.8360011981761097
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.5220316812297566
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.7905777218210527
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.5965604807778657
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.6712368561316949
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.6177427895575087
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.649152182510772
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.7588102673359794
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.7202248171615088
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.712923571152634
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.6363180181462679
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.5461111443039514
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.7050214586141689
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.8098350219920832
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.7954342605247321
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.6104459248589605
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.6819053343839099
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.757444300216272
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.6436610215385714
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.7013251507154402
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.7803984609021258
    },
    {
      "configuration": "glm-5.3-flash",
      "post_fraction": 0.5310780103338055
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.4653246136035192
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.5597511688507215
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.6399494187696461
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.0812335037252347
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.5926229381195712
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.37911125900181986
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.4529915153404595
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.5175371207773741
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.5894890312334637
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.5368165768019341
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.22836106579024207
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.8139101894138168
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.519419551886569
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.10731979593852985
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.6648590783054298
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.7085917906637452
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.5210362755688327
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.45550440391335734
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.5744607964685035
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.08209714506643875
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.8359504085113268
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.07489735291997132
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.715410851842593
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.7117577983918191
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_fraction": 0.6627795523652786
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.6042437612676724
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.4585462111231005
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.2030790882074699
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.69496188406203
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.1899505432034761
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.3550516652566132
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.30709874439339613
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.47630731665025755
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.7190183101643706
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.03643803705684512
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.3265698889255471
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.2544913646800439
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.2623444702196246
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.17839754837753008
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.4715076626815374
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.4037257588822893
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.496221107160224
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.4327226965263775
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.28353158031162695
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.3783327441416631
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.3710879830158982
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.5227348291161735
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.5911448828129321
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.8148442955827437
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.2950713296465962
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.4254858993654779
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.33798750396891597
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.42716735801766503
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.3194620120028704
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.17398674082203178
    },
    {
      "configuration": "gpt-oss-120b",
      "post_fraction": 0.30595510367776974
    }
  ]
}

def finish(fig, name):
    for ext in ("pdf", "png"):
        path = OUTPUT_DIR / f"{name}.{ext}"
        fig.savefig(path, format=ext, dpi=300, bbox_inches=None)
        print(path)
    plt.close(fig)


def _draw_panel(data, *, metric, scale, ylabel, points_key, count_key, name,
                ylim=None, yticks=None, integer_yaxis=False):
    fig, ax = plt.subplots(figsize=(3.50, 2.55))
    fig.subplots_adjust(left=.18, right=.98, bottom=.22, top=.97)
    rng = np.random.default_rng(20260917)
    for i, summary in enumerate(data['summaries']):
        values = np.array([r[metric] * scale for r in data[points_key]
                           if r['configuration'] == summary['configuration']])
        if not len(values):
            ax.text(i, .48, '—', transform=ax.get_xaxis_transform(), ha='center',
                    va='center', fontsize=12, color='#A5ADB3')
            continue
        if len(values) >= 10:
            ax.boxplot([values], positions=[i], widths=.48, patch_artist=True,
                       showfliers=False,
                       boxprops=dict(facecolor='#DCEBF4', edgecolor=BLUE, linewidth=.8),
                       medianprops=dict(color=INK, linewidth=1.5),
                       whiskerprops=dict(color=BLUE, linewidth=.8),
                       capprops=dict(color=BLUE, linewidth=.8))
        ax.scatter(i + rng.uniform(-.17, .17, len(values)), values,
                   s=12 if len(values) < 10 else 7, color=BLUE,
                   alpha=.85 if len(values) < 10 else .37, linewidths=0, zorder=3)
        if len(values) < 10:
            ax.hlines(np.median(values), i - .23, i + .23, color=INK, linewidth=1.4, zorder=4)
    ax.set_xticks(range(6), [f"{r['short']}\n$n$={r[count_key]}" for r in data['summaries']])
    ax.tick_params(axis='x', length=0, pad=6, labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    ax.set_xlim(-.6, 5.6)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.grid(axis='y', color='#E9EDF0', linewidth=.5)
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['left', 'bottom']].set_color('#8C969F')
    if ylim is not None:
        ax.set_ylim(*ylim)
    if yticks is not None:
        ax.set_yticks(yticks)
    if integer_yaxis:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
    finish(fig, name)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "output")
    args = parser.parse_args()
    global OUTPUT_DIR
    OUTPUT_DIR = args.output_dir.expanduser().resolve()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _draw_panel(DATA, metric="post_fraction", scale=100, ylabel='Post-pass tokens (%)', points_key="point_data", count_key="checkpoint_n", name="fig07a_post_pass_tokens", ylim=(0, 100), yticks=[0, 25, 50, 75, 100])

if __name__ == "__main__":
    main()
