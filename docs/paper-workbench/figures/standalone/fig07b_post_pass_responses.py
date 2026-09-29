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
      "response_n": 102
    },
    {
      "configuration": "deepseek-v4-flash",
      "short": "Flash",
      "response_n": 96
    },
    {
      "configuration": "gpt-5.6-luna",
      "short": "Luna",
      "response_n": 75
    },
    {
      "configuration": "glm-5.3-flash",
      "short": "GLM",
      "response_n": 46
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "short": "Qwen",
      "response_n": 50
    },
    {
      "configuration": "gpt-oss-120b",
      "short": "OSS",
      "response_n": 34
    }
  ],
  "response_point_data": [
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 28
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 37
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 21
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 11
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 17
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 12
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 9
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 18
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 34
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 56
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 37
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 17
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 10
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 11
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 32
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 29
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 18
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 37
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 63
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 11
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 20
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 64
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 12
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 14
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 16
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 26
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 32
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 13
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 27
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 19
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 7
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 17
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 8
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 23
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 17
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 62
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 37
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 33
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 34
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 42
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 32
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 7
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 23
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 11
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 44
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 34
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 58
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 28
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 25
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 27
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 27
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 6
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 14
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 26
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 33
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 33
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 16
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 32
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 28
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 11
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 23
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 43
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 30
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 38
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 14
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 5
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 5
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 12
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 20
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 10
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 23
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 19
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 9
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 5
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 27
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 33
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 36
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 15
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 14
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 11
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 12
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 8
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 21
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 25
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 20
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 14
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 17
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 18
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 33
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 12
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 14
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 13
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 36
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 64
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 26
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 26
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 16
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 41
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 14
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 15
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 18
    },
    {
      "configuration": "deepseek-v4-pro",
      "post_responses": 28
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 63
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 39
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 29
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 25
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 41
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 65
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 52
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 51
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 53
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 18
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 22
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 51
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 36
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 38
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 56
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 44
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 22
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 18
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 77
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 12
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 31
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 30
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 53
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 68
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 23
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 40
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 30
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 28
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 29
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 19
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 72
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 38
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 60
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 60
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 50
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 43
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 83
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 8
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 20
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 35
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 19
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 38
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 65
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 79
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 52
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 38
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 37
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 47
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 46
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 19
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 20
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 22
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 32
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 64
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 20
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 38
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 21
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 27
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 55
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 23
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 58
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 23
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 19
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 51
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 33
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 24
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 23
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 22
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 55
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 29
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 27
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 12
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 24
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 50
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 55
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 66
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 17
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 9
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 24
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 28
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 9
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 21
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 24
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 39
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 32
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 25
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 33
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 96
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 19
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 54
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 29
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 27
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 37
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 26
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 32
    },
    {
      "configuration": "deepseek-v4-flash",
      "post_responses": 37
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 9
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 9
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 47
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 78
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 16
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 27
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 13
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 20
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 65
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 8
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 11
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 8
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 24
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 17
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 6
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 5
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 11
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 5
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 51
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 27
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 27
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 8
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 11
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 6
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 46
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 14
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 10
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 15
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 13
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 4
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 13
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 9
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 44
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 14
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 6
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 10
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 15
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 10
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 9
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 14
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 56
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 20
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 6
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 6
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 8
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 14
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 35
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 1
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 6
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 7
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 4
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 10
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 10
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 6
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 16
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 15
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 5
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 82
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 10
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 8
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 11
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 10
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 11
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 9
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 15
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 10
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 10
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 19
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 11
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 13
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 4
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 29
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 13
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 16
    },
    {
      "configuration": "gpt-5.6-luna",
      "post_responses": 11
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 65
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 92
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 90
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 37
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 86
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 49
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 29
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 24
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 14
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 59
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 26
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 50
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 45
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 25
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 3
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 20
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 18
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 46
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 32
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 18
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 38
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 98
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 47
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 24
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 26
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 10
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 86
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 55
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 41
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 17
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 55
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 35
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 25
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 97
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 93
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 38
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 101
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 107
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 101
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 41
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 35
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 67
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 36
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 29
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 16
    },
    {
      "configuration": "glm-5.3-flash",
      "post_responses": 43
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 11
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 17
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 29
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 34
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 25
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 12
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 5
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 18
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 51
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 25
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 28
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 11
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 20
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 17
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 18
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 47
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 8
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 63
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 17
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 9
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 63
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 91
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 10
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 23
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 5
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 18
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 10
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 17
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 18
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 12
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 57
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 11
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 10
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 18
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 9
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 16
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 87
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 3
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 20
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 12
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 23
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 5
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 45
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 6
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 14
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 19
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 25
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 12
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 28
    },
    {
      "configuration": "qwen3.6-35b-a3b-fp8",
      "post_responses": 14
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 4
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 4
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 4
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 102
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 3
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 16
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 5
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 2
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 14
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 22
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 2
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 9
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 5
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 3
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 2
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 3
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 36
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 12
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 7
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 3
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 7
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 3
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 7
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 7
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 55
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 4
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 7
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 5
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 4
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 6
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 44
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 4
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 3
    },
    {
      "configuration": "gpt-oss-120b",
      "post_responses": 24
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
    _draw_panel(DATA, metric="post_responses", scale=1, ylabel='Subsequent responses', points_key="response_point_data", count_key="response_n", name="fig07b_post_pass_responses", ylim=(0, max(r["post_responses"] for r in DATA["response_point_data"]) * 1.08), integer_yaxis=True)

if __name__ == "__main__":
    main()
