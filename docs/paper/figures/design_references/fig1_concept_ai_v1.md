# Fig. 1 conceptual AI reference

Generated using the built-in image_gen tool. Image: fig1_concept_ai_v1.png. Existing manuscript figures are unchanged.

Visual inspection: complete legible labels; four teal regions dispersed across source modules and regrouped into a separate package; behavior preservation represented as a requirement; no runtime dependency back to source. This is a conceptual schematic, not measured artifact size or a prescribed module architecture.

## Exact prompt

Create a conceptual Figure 1 for the software engineering research paper FeatureLiftBench. English text only. A clean, elegant, publication-style flat scientific diagram on pure white, wide landscape about 1.9:1. One unified structural illustration, not a three-column workflow. No robots, no stage numbers, no cards, no 3D, no gradients, no shadows, no decorative icons. Do not include a giant figure title.

The visual story must be understandable immediately: a useful capability is distributed across the modules of an existing repository; a code agent must reconstruct this capability within an independent package, preserving specified behavior without runtime access to the original repository. Visualize relationships and containment, not a sequence of procedural steps.

LEFT HALF: a large thin dark-gray rectangular boundary labeled "Source repository". Inside arrange six light-gray module rectangles in an orderly but varied tiled arrangement, not a folder tree. Label these quietly "Module A" through "Module F". Within FOUR of these module regions, show small muted-teal blocks, each taking up only part of its surrounding module. These teal regions represent parts of one target capability. Include a handful of gray internal code-like strokes and gray supporting blocks. Connect the teal functional regions to one another and to a few nearby supporting gray blocks with carefully routed thin lines. The module borders must remain clearly visible: the feature spans several module boundaries. Use a small key underneath the repository: teal square "Target capability", light-gray square "Surrounding implementation". A short understated annotation below the graph reads "Behavior spans module boundaries". Do not clutter with API names, code, or real library names.

RIGHT HALF: a smaller, self-contained thin teal outlined rectangle labeled "Independent package". Inside show four muted-teal functional regions, visually corresponding to the left side but in a DIFFERENT, coherent arrangement, with a few thin internal connections and supporting neutral elements. All required internal connections terminate INSIDE this new package. Do not draw any runtime dependency link back to the source repository. The smaller drawing denotes a bounded capability, not a measured size reduction or optimal minimum.

BETWEEN: one restrained transformation arrow from the left source boundary to the new package, labeled "Feature lifting". This arrow means reconstruction, not runtime access. No intermediate agent box, no evaluator box. A small caption under the arrow reads "Reconstruct across a new boundary". Preserve spaciousness and make the target capability visibly continuous through matching teal encoding.

BEHAVIOR REQUIREMENT: below each repository/package drawing, place the same slim text marker "Specified behavior", with a subtle connector to its corresponding implementation. Connect these markers beneath the transformation with a delicate horizontal relationship labeled "Required to be preserved". Avoid pass/fail icons because this is a requirement, not a measured successful outcome.

Below the independent package, separated cleanly from the behavior marker, place the short condition "Evaluated without access to the source repository". This should be readable, not tiny, at most two lines.

Visual hierarchy: source modules and distributed teal feature, then reconstructed teal package, then the behavior-preservation relationship. Use gray for ambient implementation, muted teal for target capability, charcoal for text. Crisp consistent line weights. Academic sans-serif typography with slightly heavier region labels. Do not add extra explanatory prose or metrics. This should feel like a carefully composed paper diagram, not a corporate process infographic. Ensure all text is complete, correct, and free of overlaps. Generate the image only.

