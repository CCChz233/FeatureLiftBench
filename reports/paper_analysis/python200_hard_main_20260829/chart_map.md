# Chart map

| Segment | Question | Family | Dataset and fields | Supported claim |
| --- | --- | --- | --- | --- |
| Failure composition | Where do the 200 tasks first stop? | Horizontal bar | `failure_stages`: `stage`, `count`; audit fields include `share`, split counts, and rank | The run has 132 passes; the 68 non-passes are concentrated in missing submission, build, and public stages rather than isolation. |

The chart uses one neutral series, a count axis starting at zero, direct category
labels, no legend, and deterministic descending order. Pass is retained in the
chart to keep the denominator visible. Failure-stage claims use mutually
exclusive first outcomes in the order missing submission → build → public →
hidden → isolation.
