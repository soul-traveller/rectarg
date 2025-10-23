#!/usr/bin/env python3

"""
---
v1.1
---
# Reference and Usage Guide

**Author:** Knut Larsson  
**Purpose:** Generate a calibration target image from ArgyllCMS `.cht` and `.cie` pairs, preserving colorimetric values and physical dimensions for printing or soft-proofing.

---

## Table of Contents

1. [Overview](#overview)
2. [Supported Targets](#supported-targets)
3. [Installation](#installation)
4. [Command-Line Usage](#command-line-usage)
5. [Arguments](#arguments)
6. [Examples](#examples)
7. [Use Cases](#use-cases)
8. [ICC Profile Management](#icc-profile-management)
9. [Features](#features)
10. [Provided CHT Files](#provided-cht-files)
11. [Trouble Shooting](#trouble-shooting)
12. [Technical Reference](#technical-reference)
    - [Scaling Model](#scaling-model)
    - [Fiducial Marks](#fiducial-marks)
    - [Chart Definition](#chart-definition)
    - [Patch Area Definitions](#patch-area-definitions)
    - [Color Conversion](#color-conversion)
    - [Labels and Text](#labels-and-text)
    - [Output](#output)
    - [Diagnostics](#diagnostics)
13. [Notes](#notes)

---

## Overview

`rectarg.py` recreates calibration target images from `.cht` (chart layout) and `.cie` (reference data) files compatible with **ArgyllCMS**. It performs full color conversions (LAB → XYZ (D50) → sRGB (D65 via Bradford)), preserves physical dimensions, and adds fiducials, labels, and geometry for accurate reproduction.

Calibration targets ensure scanners, printers, and displays show colors consistently. Vendors often withhold digital originals; this tool reconstructs them faithfully for visual or colorimetric comparison.

### Applications

- **Display calibration:** Compare a display’s color calibration to the physical target.
- **Printer calibration:** Print a clean target image for visual or colorimetric comparison.
- **Scanner profiling:** Compare a scanned target against a reference image.

For example targets, see:
- [Wolf Faust IT8 targets (12641-1)](http://www.targets.coloraid.de)
- [LaserSoft Advanced IT8 target (12641-2)](https://www.silverfast.com/products-overview-products-company-lasersoft-imaging/it8-targets-for-scanner-calibration-profiling-for-predictable-brilliant-colors/)

ArgyllCMS (http://argyllcms.com) is a professional open-source color management system widely used for calibration workflows.

---

## Supported Targets

Tested successfully with:

- Wolf Faust IT8.7/2 Targets (12641-1)
- LaserSoft Advanced Color Calibration Target IT8 (12641-2)
- CMP Digital Target-4
- Hutchcolor HCT
- LaserSoft DCPro Studio Target
- QPcard_202 Target
- SpyderChecker & SpyderChecker24 Targets

> **Note:** There is a good chance rectarg may be used successfully on other cht-cie file pairs, but ColorChecker Passport is not supported due to unsupported `.cht` parameters.

---

## Installation

**Dependencies:**

```
pip install numpy Pillow tifffile argparse scipy
```

Required: `numpy`, `Pillow (PIL)`, `tifffile`, `argparse`  
Optional: `scipy`

---

## Command-Line Usage

```bash
python3 rectarg.py <chart.cht> <data.cie> <output.tif> [options]
```

### Example
```bash
python3 rectarg.py R230122W.cht R230122W.txt output.tif   --target_dpi 300 --background GS10 --intent display --label_axis_visible X=B
```

---

## Arguments

| Type | Argument | Description |
|------|-----------|-------------|
| Positional | `<chart.cht>` | Chart definition file (ArgyllCMS .cht) |
| Positional | `<data.cie>` | Reference or measurement data (.cie, .txt, or IT8) |
| Positional | `<output.tif>` | Output filename (16-bit TIFF) |
| Optional | `--target_dpi [DPI]` | Output resolution (default: A4-fit scaled to 300 DPI) |
| Optional | `--background-color [PATCH_ID]` | Use specified patch color as background |
| Optional | `--intent [absolute;display]` | Color conversion intent. <br>`absolute` : Calibration reference / technical validation Keeps exact colorimetric data. Linear sRGB, 16-bit TIFF. D50→D65 adaptation only (no gamma), no perceptual modification.<br>`display` (default): Screen visualization / preview image added gamma 2.2 encoding (nonlinear tone mapping), 16-bit TIFF with gamma. |
| Optional | `--color_space [lab;xyz]` | Input color space (default: lab) |
| Optional | `--label_axis_visible [AREA_NAME]=[L;T;R;B;ALL;NONE]` | Manually toggle label sides. Left, Top, Right, Bottom, ALL (default), NONE. Can be speficified multiple times. <br>Example: `--label_axis_visible X=B --label_axis_visible Y=RT` Forces only bottom label for area X, as well as right and top labels for area Y. |
| Optional | `--margin [MM]` | Page margin in millimeters (default: 15) |
| Optional | `--font [PATH]` | TrueType font path. If not found, the script searches common system font paths (Palatino, Helvetica, Times, Arial, DejaVuSans) |
| Optional | `--font_mm [LABEL_MM] [FOOTER_MM]` | Physical text heights (default: 2 mm) |
| Optional | `--png` | Save PNG preview |
| Optional | `--debug` | Enable diagnostic output |

---

## Examples

For simplicity: Go to a folder in terminal. Place this script as well as `.cht` and `.cie` file in folder. Run command as shown below.

```bash
# Wolf Faust IT8.7/2 target for display
python3 rectarg.py R230122W.cht R230122W.txt output.tif --target_dpi 300 --background GS10 --label_axis_visible X=B

# Wolf Faust IT8.7/2 target with custom font and text size (in mm)
python3 rectarg.py R230122W.cht R230122W.txt output_font.tif --font /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf --font_mm 3.0 2.0

# LaserSoft IT8 target, Absolute Colorimetric
python3 rectarg.py ISO12641_2_1.cht R250715.cie output.tif --intent absolute --background-color N33 --target_dpi 200

# Hutchcolor HCT (XYZ data) for display
python3 rectarg.py Hutchcolor.cht 0579.txt Hutchcolor.tif --target_dpi 200 --color_space xyz

# CMP Digital Target-4 for display
python3 rectarg.py CMP_Digital_Target-4.cht CMP_Digital_Target-4.cie output.tif --target_dpi 200 --color_space xyz --label_axis_visible Y=TLB --label_axis_visible X=TRB --font_mm 1.5 1.5

# LaserSoft DCPro Studio Target for display
python3 rectarg.py LaserSoftDCPro.cht D120104.txt LaserSoftDCPro-200dpi.tif --target_dpi 200 --intent absolute --font_mm 1 1 --margin 7
 
# QPcard_202 Target, Absolute Colorimetric
python3 rectarg.py QPcard_202.cht QPcard_202.cie output.tif --intent absolute --target_dpi 200 --font_mm 2.5 2.5

# SpyderChecker Target, Absolute Colorimetric
python3 rectarg.py SpyderChecker.cht SpyderChecker.cie SpyderChecker-200dpi.tif --intent absolute --target_dpi 200 --color_space xyz

# SpyderChecker24 for display
python3 rectarg.py SpyderChecker24.cht SpyderChecker24.cie SpyderChecker24-200dpi.tif --target_dpi 200 --color_space xyz
```

---

## Use Cases
### General
* Use absolute intent image is colorimetric truth for numerical or colorimetric comparison only, like when measuring Lab values etc. Image is too dark for printing or comparison against physical reference target.
* Use display intent image is visually faithful representation → for visual side-by-side comparison with the physical target or softproofing.

### Example Use Cases
1. If you want to produce a printable target that looks like the physical chart (for visual comparison) you can do the following:

   - Option 1: Use rectarg display intent image directly. Print it with color management ON (normal sRGB → printer conversion through your calibrated printer profile). That should yield a print that perceptually matches the physical target, for comparison against original physical reference target.

   - Option 2: Comparison of Printed Image against Soft-Proofing Image Create a soft-proofing image for on-screen comparison against a printed target. Use display-intent image from rectarg and apply a printer's ICC profile via an application to create the soft-proofing image.

2. If you want to compare a scanned image of the reference target on-screen against created image from rectarg: Use rectarg display intent image directly. Compare against scanned image on-screen, assuming scanner uses calibrated icc/icm profile. If scanner output is raw, without any profile, then apply a scanner profile onto scanned image before comparing against rectarg display intent image.

3. If you want to compare a calibrated display against physical reference target: Use rectarg display intent image directly on the display that has color management ON (using its icc/icm profile). Then compare against physical target.

4. If you want to profile printer: Use rectarg display intent image and print without color management. Then scan/measure printed image and create icc-profile. If hand scanner is used, scale the image to maximise chart size when printing, if possible.


### Overview of Use Cases

| Use Case | Image Intent | Tagged As | ICC Conversion | Color Management | Purpose |
|-----------|---------------|------------|----------------|------------------|----------|
| Display measurement | absolute | linear sRGB | No | ON (monitor ICC) | Numeric accuracy |
| Display visual check | display | sRGB (γ2.2) | No | ON | Visual comparison |
| Printer visual comparison | display | sRGB (γ2.2) | Yes <br>(soft-proofing) | ON | Match physical chart visually |
| Printer profiling | display | sRGB (γ2.2) | — | OFF | Build printer profile |
| Scanner profiling | — | — | — | OFF | Build/verify scanner profile |
| Scanner visual comparison | display | sRGB (γ2.2) | No | ON | Visual compare scan vs target |
| Scanner numeric comparison | absolute | linear sRGB | No | ON | Compare measured Lab vs reference |

### Intent Notes

- **Absolute intent:** Colorimetric truth for numerical analysis. Too dark for printing.
- **Display intent:** Visually faithful representation for on-screen comparison.

---

## ICC Profile Management

Assigning or converting ICC profiles can, for example, be done using:
- ArgyllCMS
- ImageMagick
- Photoshop
- GIMP
- macOS ColorSync Utility

### Example Commands

**ImageMagick:**
```bash
magick rectarg_image_display.tif -profile printer.icc rectarg_image_printproof.tif
```

**ArgyllCMS:**
```bash
cctiff -i p -v printer.icm rectarg_image_display.tif rectarg_image_printproof.tif
```

---

## Features

- Parses `.cht` layout definitions (fiducials, patch areas)
- Reads `.cie`, `.txt`, or IT8 reference data
- LAB → XYZ (D50) → sRGB (D65 via Bradford) color conversion
- 16-bit RGB TIFF output
- Automatic patch ID generation and labeling
- DPI-scaled fiducials and text
- Optional PNG preview
- Margin and font customization

---

## Provided CHT Files

Most targets tested with this script were provided with the ArgyllCMS software, and many of those have probably been made manually, as several had odd configurations and dummy data, which caused bad images by rectarg. 

For the purpose of generating nice looking images I have edited the definition part of several of the .cht files. Those that want to experiment with getting exact match of fiducials to original target may modify the cht file, or use those provided for a nice printout. 

Details on how to interpret the specification inside the cht file is provided below.

---

## Trouble Shooting

* If individual gray patches appear instead of colors: Related Patch ID cannot be cannot be found in `.cie` file. 
* If all patches come out as gray: 
 - `Patch Area` line (ex. `Y`) in `.cht` layout definitions has label definitions that cannot be found in `.cie` file.
 - Patch Labels cannot be found in `.cie` file.
* If fiducial marks are positioned wrong:
 - `F` line in `.cht` layout definitions has wrong coordinate numbers. 

---

## Technical Reference

### Scaling Model

- `.cht` coordinates used directly; rescaled to chosen DPI.
- Physical proportions preserved for A4-fit DPIs (72, 100, 200, 300, 600, 1200).

Example:

	If 100dpi is detected, scaling factor is calulated in reference to 300 DPI:
	  - scale_x ≈ 2.9988 px/unit
	  - scale_y ≈ 3.0009 px/unit
	  - Each 25.625 unit patch (at 100dpi) becomes ≈ 77×77 px (≈ 6.52 mm per side)

### Fiducial Marks

- Defined by `F` lines in `.cht`.
- L-shaped corners; DPI-scaled size and thickness (≈ 5 px at 300 DPI).

### Chart Definition

- Defined by `D` line in `.cht`.
- `D` line defines overall chart dimensions.
- If two first (x,y) coordinates are not specified correclty, chart may not generate properly. 

Example:
```
D ALL ALL _ _ 613 433 49.0 33.0 0 0
```

### Patch Area Definitions

- Defined by `Y` and `X` lines in `.cht`.
- `Y` defines main color patch grid.
- `X` defines secondary grid area.
- Nameing should be unique per patch area.

Example (Wolf Faust Target):
```
Y 01 22 A L 25.625 25.625 26.625 26.625 25.625 25.625
X GS00 GS23 _ _ 25.625 51.25 1.0 360.5 25.625 0
```

Interpreted as:
[xstart, xend, ystart, yend, tile_x, tile_y, pre_x, pre_y, post_x, post_y]

- Labels:
      - Numeric [xstart, xend]: 01–22 → “01”…“22”
      - Alphabetic [ystart, yend]: A–L → “A”…“L”
      - Prefixed [xstart, xend]: GS00–GS23 → “GS00”…“GS23”
      - “_” disables labels for that axis
      - Each patch ID (e.g. A01) is matched to corresponding data in `.cie`. 
      - Supports recognition of label differences, such as A1 vs A01, or with or without quotes (A1 vs "A1"), or special labels with preceding number, like "2A1".
      - Supports two letter running alphabetical labels, like A-AX → “A”…“AX”.

- Grid defining coordinates:
      - [tile_x, tile_y]: Pixel units (at a given dpi defined by originator) for color patch.
      - [pre_x, pre_y]: Chart area padding. Pixcel units from reference (0,0) where first patch is placed.
      - [post_x, post_y]: Chart area padding. Pixel units added in x direction after last column for the specifed patch grid area, and added in y direction after last row placement.


### Color Conversion

- Default data columns from cie file: LAB
- Alterntively, data columns can be selected to use XYZ columns. 
- Conversion chain: LAB (D50) → XYZ (D50) → XYZ (D65 via Bradford) → sRGB (IEC 61966-2-1)
- Resulting RGB values are not clipped or manipulated to preserve true reference colors.

### Labels and Text

- Footer includes: creation date, originator, descriptor, and manufacturer.
- Patch IDs automatically generated from label start/end tokens
- Top and left patch labels, plus mirrored labels on bottom and right sides
- Physical sizing in mm maintained via pixel scaling. Example: 2.0 mm → 24 px at 300 DPI.
- Hides labels if two patch areas are too close to each other.
- Required clearance between defined patch areas is calculated dynamically, based on the maximum label size plus 2 mm buffer. That way: 
    - Column labels appear only if there’s at least (font height + 2 mm) vertical gap. If column labels are rotated, rotated label’s longest dimension is used instead of font height.
    - Row labels appear only if there’s at least (max label width + 2 mm) horizontal gap. 
- Footer block includes:
      - 'CREATED' date (if available)
      - Data file name
      - Center text: “Reproduction of Target from reference data”
      - 'ORIGINATOR', 'DESCRIPTOR', and 'MANUFACTURER' fields (right-aligned)
      - Some files converted by AryllCMS tools to cie type may use very different defining parameter names for the above. To get the info displayed correctly with rectarg you should rename the appropriate parameter according names mentioned above. Those are based on parameters used in Wolf Faust IT8.7/2 Target



### Output

- Default: 16-bit TIFF with embedded DPI.
- Optional PNG preview (`--png`).

### Diagnostics

**Normal mode:** Summary only.  
**Debug mode:** Detailed info on scaling, geometry, patch mapping, and colors.

---

## Notes

- Compatible with Wolf Faust, LaserSoft, Hutchcolor, and similar targets.
- Handles LAB/RGB field naming differences.
- Maintains geometry, margins, and fiducials.
- Ideal for calibration, visualization, and reference reprints.

---
"""


#!/usr/bin/env python3
from pathlib import Path
import re, math, argparse, sys, os, fnmatch, string
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import importlib.util

def debug_print(*args, **kwargs):
    """Print only when --debug flag is active."""
    if globals().get("DEBUG_PARSE", False):
        print(*args, **kwargs)

# ---------------------------
# Dependency Checker
# ---------------------------

REQUIRED_MODULES = ["numpy", "PIL", "tifffile", "argparse"]
OPTIONAL_MODULES = ["scipy"]

missing = []

for mod in REQUIRED_MODULES:
    if importlib.util.find_spec(mod) is None:
        missing.append(mod)

if missing:
    print("[ERROR] Missing required dependencies:")
    for m in missing:
        print(f"  - {m}\n    ➜ Install via: pip install {m}")
    sys.exit(1)

for mod in OPTIONAL_MODULES:
    if importlib.util.find_spec(mod) is None:
        print(f"[Warning] Optional dependency not found: {mod}")

try:
    import tifffile
    HAVE_TIFF = True
except Exception:
    HAVE_TIFF = False

# ---------------------------
# Defaults and precise scaling constants (based on 100-dpi units -> target DPI)
# ---------------------------
# DEFAULT_TARGET_DPI is None to allow "not specified" to be detected reliably.
DEFAULT_TARGET_DPI = None   # None means "not specified"

PRECISE_SCALES = {
    100: (1.000000, 1.000000),
    200: (2.000000, 2.001000),
    300: (2.99879081, 3.00085543),
    600: (5.99879081, 6.0020)
}

FALLBACK_SX_CORR = 0.9996
FALLBACK_SY_CORR = 1.0003

FID_OUTER_PX_AT_300 = 40.0
FID_LINE_PX_AT_300 = 5.0

# ---------------------------
# Utilities: parsing files
# ---------------------------
def read_text(path):
    return Path(path).read_text(encoding='utf-8', errors='replace')

def parse_cht(path):
    txt = read_text(path)
    out = {'raw': txt, 'fids': [], 'box_shrink': 0.0, 'areas': [], 'xl': [], 'yl': []}

    # -------------------------
    # Fiducial coordinates
    # -------------------------
    fline = None
    for ln in txt.splitlines():
        if ln.strip().upper().startswith('F '):
            fline = ln.strip()
            break
    if not fline:
        raise RuntimeError("F fiducial line not found in .cht file.")

    nums = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', fline)]
    start = 0
    while (len(nums)-start) % 2 != 0 and start < len(nums):
        start += 1
    coords = [(nums[i], nums[i+1]) for i in range(start, len(nums)-1, 2)]
    if len(coords) >= 4:
        coords = coords[:4]
    elif len(coords) == 3:
        xs = [c[0] for c in coords]; ys = [c[1] for c in coords]
        left, right, top, bottom = min(xs), max(xs), min(ys), max(ys)
        coords = [(left, top), (right, top), (right, bottom), (left, bottom)]
    else:
        raise RuntimeError("Insufficient fiducial coordinate pairs in F line.")
    out['fids'] = coords

    # -------------------------
    # Global shrink factor
    # -------------------------
    mbs = re.search(r'(?mi)^\s*BOX_SHRINK\s+([-+]?\d*\.?\d+)', txt)
    if mbs:
        out['box_shrink'] = float(mbs.group(1))

    # -------------------------
    # X/Y coordinate lists
    # -------------------------
    m_x = re.search(r'(?ms)^\s*XLIST\b.*?\n(.*?)(?=^\s*YLIST\b|\Z)', txt, flags=re.M)
    if m_x:
        for ln in m_x.group(1).splitlines():
            fs = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', ln)
            if fs:
                out['xl'].append(float(fs[0]))

    m_y = re.search(r'(?ms)^\s*YLIST\b.*?\n(.*?)(?=^\s*(?:EXPECTED|BOX_SHRINK|REF_ROTATION|\Z))', txt, flags=re.M)
    if m_y:
        for ln in m_y.group(1).splitlines():
            fs = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', ln)
            if fs:
                out['yl'].append(float(fs[0]))

    # -------------------------
    # Patch area definitions
    # -------------------------
    area_re = re.compile(
        r'(?mi)^[ \t]*([XY])\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+((?:[-+]?\d*\.?\d+\s+){5}[-+]?\d*\.?\d+)',
        flags=re.M
    )

    for m in area_re.finditer(txt):
        axis = m.group(1).upper()
        xstart, xend = m.group(2), m.group(3)
        ystart, yend = m.group(4), m.group(5)

        nums = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', m.group(6))]
        if len(nums) != 6:
            rest = m.group(0).split()[5:]
            nums = []
            for tok in rest:
                try:
                    nums.append(float(tok))
                except Exception:
                    pass
        if len(nums) != 6:
            continue

        # --- Detect prefixed labels like "2A"
        def is_prefixed_alpha(label):
            return bool(re.match(r'^\d+[A-Z]$', label, re.I))

        label_mode = None
        if is_prefixed_alpha(xstart) or is_prefixed_alpha(xend):
            label_mode = "prefixed_x"
        elif is_prefixed_alpha(ystart) or is_prefixed_alpha(yend):
            label_mode = "prefixed_y"

        area = {
            'axis': axis,
            'xstart': xstart, 'xend': xend,
            'ystart': ystart, 'yend': yend,
            'tile_x': nums[0], 'tile_y': nums[1],
            'pre_x': nums[2], 'pre_y': nums[3],
            'post_x': nums[4], 'post_y': nums[5],
            'label_mode': label_mode  # <-- NEW
        }
        out['areas'].append(area)

    if not out['areas']:
        raise RuntimeError("No X/Y area definitions found in .cht. v8 expects explicit area lines.")

    return out



def parse_it8_or_cie(path, color_space='lab'):
    txt = read_text(path)
    header = {}
    for key in ('ORIGINATOR', 'DESCRIPTOR', 'CREATED', 'MANUFACTURER', 'SERIAL', 'PROD_DATE'):
        m = re.search(rf'(?mi)^\s*{key}\s+"?(.*?)"?\s*$', txt)
        if m:
            header[key.upper()] = m.group(1).strip()

    # --- Parse format block
    fmt = []
    mfmt = re.search(r'(?ms)^\s*BEGIN_DATA_FORMAT\b(.*?)^\s*END_DATA_FORMAT\b', txt)
    if mfmt:
        for ln in mfmt.group(1).splitlines():
            for tok in re.split(r'\s+', ln.strip()):
                if tok:
                    fmt.append(tok)
    fmt_upper = [f.upper() for f in fmt]

    # --- Find possible label columns dynamically
    label_cols = []
    for candidate in ('SAMPLE_LOC', 'SAMPLE_LABEL', 'SAMPLE_NAME', 'SAMPLE_ID'):
        if candidate in fmt_upper:
            label_cols.append(fmt_upper.index(candidate))

    # --- Find LAB (or RGB) columns dynamically
    idxL = next((i for i, f in enumerate(fmt_upper) if f.startswith('LAB_L') or f == 'L'), None)
    idxA = next((i for i, f in enumerate(fmt_upper) if f.startswith('LAB_A') or f == 'A'), None)
    idxB = next((i for i, f in enumerate(fmt_upper) if f.startswith('LAB_B') or f == 'B'), None)

    # --- Fallbacks for alternate label variants like L*, Lab-L, etc. ---
    if idxL is None:
        idxL = next((i for i, f in enumerate(fmt_upper)
                     if re.match(r'^(L\*|LAB[-_]?L|LCH_L)$', f, re.I)), None)
    if idxA is None:
        idxA = next((i for i, f in enumerate(fmt_upper)
                     if re.match(r'^(A\*|LAB[-_]?A|LCH_A)$', f, re.I)), None)
    if idxB is None:
        idxB = next((i for i, f in enumerate(fmt_upper)
                     if re.match(r'^(B\*|LAB[-_]?B|LCH_B)$', f, re.I)), None)

    idxR = next((i for i, f in enumerate(fmt_upper) if f in ('RGB_R', 'R')), None)
    idxG = next((i for i, f in enumerate(fmt_upper) if f in ('RGB_G', 'G')), None)
    idxB_rgb = next((i for i, f in enumerate(fmt_upper) if f in ('RGB_B', 'B')), None)
    idxX = next((i for i, f in enumerate(fmt_upper) if f in ('XYZ_X', 'X')), None)
    idxY = next((i for i, f in enumerate(fmt_upper) if f in ('XYZ_Y', 'Y')), None)
    idxZ = next((i for i, f in enumerate(fmt_upper) if f in ('XYZ_Z', 'Z')), None)

    data = []
    mdata = re.search(r'(?ms)^\s*BEGIN_DATA\b(.*?)^\s*END_DATA\b', txt)
    if not mdata:
        return fmt, {}, header

    for ln in mdata.group(1).splitlines():
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        parts = re.findall(r'"[^"]*"|\S+', ln)
        if len(parts) < 2:
            continue

        # --- Determine sample label (try multiple columns)
        sid = None
        for c in label_cols:
            if c < len(parts):
                candidate = parts[c].strip('"').strip()
                # Accept plausible labels like A01, GS10, etc.
                if re.match(r'^[A-Z0-9]+$', candidate, flags=re.I) or re.match(r'^(GS\d+)$', candidate, flags=re.I):
                    sid = candidate
                    break
        if not sid:
            sid = parts[0].strip('"').strip()

        # --- Preserve all numeric columns exactly as defined in fmt ---
        vals = []
        for tok in parts:
            try:
                vals.append(float(tok))
            except ValueError:
                vals.append(tok)

        data.append((sid, vals))

    # Normalize into map form for quick lookup, depending on color space
    data_map = {}
    for sid, vals in data:
        entry = {"vals": vals}

        if color_space.lower() == "lab":
            entry.update({
                "space": "lab",
                "i1": idxL, "i2": idxA, "i3": idxB
            })
        elif color_space.lower() == "rgb":
            entry.update({
                "space": "rgb",
                "i1": idxR, "i2": idxG, "i3": idxB_rgb
            })
        elif color_space.lower() == "xyz":
            entry.update({
                "space": "xyz",
                "i1": idxX, "i2": idxY, "i3": idxZ
            })
        else:
            entry.update({
                "space": "lab",
                "i1": idxL, "i2": idxA, "i3": idxB
            })

        data_map[sid.upper()] = entry

    # --- Optional debug output for verifying column detection ---
    if globals().get("DEBUG_PARSE", False):
        print(f"[Debug] Detected indices: LAB=({idxL},{idxA},{idxB}), "
            f"RGB=({idxR},{idxG},{idxB_rgb}), XYZ=({idxX},{idxY},{idxZ})")
        # print one example record
        if data_map:
            sample_key = next(iter(data_map))
            vals = data_map[sample_key]["vals"]
            print(f"[Debug] Example entry: {sample_key} -> LAB=({vals[idxL] if idxL is not None else 'N/A'}, "
                  f"{vals[idxA] if idxA is not None else 'N/A'}, "
                  f"{vals[idxB] if idxB is not None else 'N/A'})")
            
    debug_print(f"Loaded {len(data_map)} CIE entries. Example keys: {list(data_map.keys())[:20]}")
    return fmt, data_map, header

# ---------------------------
# Color conversion functions
# ---------------------------
# These follow the CIE 1976 (L*a*b*) standard, which defines 
# the color space and LAB↔XYZ or XYZ↔sRGB conversion.
def lab_to_xyz(L, a, b):
    fy = (L + 16.0) / 116.0
    fx = fy + a / 500.0
    fz = fy - b / 200.0
    d = 6.0 / 29.0
    def invf(t):
        return t**3 if t > d else 3*(d**2)*(t - 4.0/29.0)
    xr, yr, zr = invf(fx), invf(fy), invf(fz)
    return xr * 0.96422, yr * 1.0, zr * 0.82521

def xyz_d50_to_srgb_intent(X, Y, Z, intent="display", clip=False):
    """
    Convert XYZ (D50) to sRGB, with intent control.

    Args:
        X, Y, Z: Tristimulus values (scaled 0–1 or 0–100).
        intent: 'absolute' = linear (colorimetric reference),
                'display'  = gamma-encoded (screen view).
        clip:   Whether to clip result to [0,1] range.

    Returns:
        np.ndarray of 3 floats (R, G, B)
    """
    # --- Bradford chromatic adaptation: D50 → D65 ---
    M = np.array([[0.8951, 0.2664, -0.1614],
                  [-0.7502, 1.7135, 0.0367],
                  [0.0389, -0.0685, 1.0296]])
    Mi = np.linalg.inv(M)
    D50 = np.array([0.96422, 1.0, 0.82521])
    D65 = np.array([0.95047, 1.0, 1.08883])
    adapt = Mi @ np.diag((M @ D65) / (M @ D50)) @ M
    X_a, Y_a, Z_a = adapt @ np.array([X, Y, Z])

    # --- XYZ → linear sRGB ---
    M2 = np.array([
        [ 3.2406, -1.5372, -0.4986],
        [-0.9689,  1.8758,  0.0415],
        [ 0.0557, -0.2040,  1.0570]
    ])
    rgb_lin = M2 @ np.array([X_a, Y_a, Z_a])

    # --- Apply intent ---
    if intent.lower() in ("display", "perceptual", "relative"):
        # Apply sRGB gamma encoding
        def comp_gamma(u):
            if u <= 0.0:
                return 0.0
            if u <= 0.0031308:
                return 12.92 * u
            else:
                return 1.055 * (u ** (1.0/2.4)) - 0.055
        rgb = np.array([comp_gamma(v) for v in rgb_lin])
    else:
        # Absolute (linear) intent
        rgb = rgb_lin

    if clip:
        rgb = np.clip(rgb, 0.0, 1.0)

    return rgb

# ---------------------------
# Helpers: labels and geometry
# ---------------------------
def generate_labels(start_tok, end_tok):
    """
    Generate a list of patch labels between start_tok and end_tok.
    Supports:
      - GS01..GS24
      - 01..19
      - A..Z, A..AX, AA..AD (Excel-style wrap)
      - 2A..2D (numeric prefix + alpha range)
      - single values (A..A, 01..01)
      - '_' tokens (disabled axis)
    """

    if start_tok == '_' or end_tok == '_':
        return []

    s = start_tok.strip().upper()
    e = end_tok.strip().upper()

    # 1. GS grayscale range
    m1 = re.match(r'^(GS)(\d+)$', s)
    m2 = re.match(r'^(GS)(\d+)$', e)
    if m1 and m2:
        a = int(m1.group(2)); b = int(m2.group(2))
        width = max(len(m1.group(2)), len(m2.group(2)))
        return [f"GS{idx:0{width}d}" for idx in range(a, b + 1)]

    # 2. Pure numeric range
    if re.match(r'^\d+$', s) and re.match(r'^\d+$', e):
        a = int(s); b = int(e)
        width = max(len(s), len(e))
        return [f"{idx:0{width}d}" for idx in range(a, b + 1)]

    # 3. Prefixed alphanumeric range (e.g. 2A..2D, 10A..10C)
    m3 = re.match(r'^(\d+)([A-Z]+)$', s)
    m4 = re.match(r'^(\d+)([A-Z]+)$', e)
    if m3 and m4 and m3.group(1) == m4.group(1):
        prefix = m3.group(1)
        sub_start = m3.group(2)
        sub_end = m4.group(2)
        subs = _alpha_range(sub_start, sub_end)
        return [f"{prefix}{x}" for x in subs]

    # 4. Pure alphabetic range, including Excel-style multi-letter (A..AX, AA..AD)
    if re.match(r'^[A-Z]+$', s) and re.match(r'^[A-Z]+$', e):
        return _alpha_range(s, e)

    # 5. Single-token / fallback
    return [s] if s == e else [s, e]


def _alpha_range(start, end):
    """
    Generate Excel-style alphabetic ranges:
      A..Z, A..AA, A..AX, AA..AD, etc.
    """
    def alpha_to_num(a):
        n = 0
        for c in a:
            n = n * 26 + (ord(c) - 64)
        return n

    def num_to_alpha(n):
        s = ""
        while n > 0:
            n, r = divmod(n - 1, 26)
            s = chr(65 + r) + s
        return s

    n1 = alpha_to_num(start)
    n2 = alpha_to_num(end)
    if n2 < n1:
        n1, n2 = n2, n1  # ensure increasing
    return [num_to_alpha(i) for i in range(n1, n2 + 1)]


def compute_canvas_extents_from_areas(areas, sx, sy):
    """
    Compute the min/max pixel extents for all defined chart areas.
    Supports single-row/column cases when '_' disables one axis.
    """
    minx = float('inf')
    miny = float('inf')
    maxx = -float('inf')
    maxy = -float('inf')

    for area in areas:
        cols = generate_labels(area['xstart'], area['xend'])
        rows = generate_labels(area['ystart'], area['yend'])

        # if disabled axis → treat as 1 row/column
        ncols = len(cols) if cols else 1
        nrows = len(rows) if rows else 1

        left_px = area['pre_x'] * sx
        top_px = area['pre_y'] * sy
        right_px = left_px + (ncols * area['tile_x'] * sx)
        bottom_px = top_px + (nrows * area['tile_y'] * sy)

        minx = min(minx, left_px)
        miny = min(miny, top_px)
        maxx = max(maxx, right_px)
        maxy = max(maxy, bottom_px)

    if minx == float('inf'):
        return 0.0, 0.0, 0.0, 0.0

    return minx, miny, maxx, maxy

# ---------------------------
# DPI detection helper
# ---------------------------
A4_DPI_TABLE = {
    72:  (595, 842),
    96:  (794, 1123),
    100: (827, 1169),
    120: (992, 1403),
    150: (1240, 1754),
    200: (1654, 2339),
    250: (2067, 2923),
    300: (2480, 3508),
    600: (4961, 7016),
    1200: (9921, 14031)
}

def detect_best_a4_dpi(chart_px_w, chart_px_h, margin_mm):
    """
    Detect which A4 DPI (portrait or landscape) best fits the chart's pixel dimensions.

    The .cht chart dimensions are already given in pixels (not in any normalized unit).
    We therefore directly compare the chart's raw pixel width/height to A4 pixel sizes
    at standard DPIs, with a safety margin in millimeters converted to pixels per DPI.

    Returns:
        The smallest A4 DPI in A4_DPI_TABLE where the chart (plus margins) fits,
        preferring landscape fit if both orientations are possible.
    """
    best_fit = None
    candidates = sorted(A4_DPI_TABLE.keys())

    for dpi in candidates:
        aw, ah = A4_DPI_TABLE[dpi]  # A4 width,height in pixels at this dpi
        margin_px = int(round(margin_mm * (dpi / 25.4)))

        # total chart including margin
        total_w = chart_px_w + 2 * margin_px
        total_h = chart_px_h + 2 * margin_px

        fits_portrait = total_w <= aw and total_h <= ah
        fits_landscape = total_w <= ah and total_h <= aw

        if fits_portrait or fits_landscape:
            best_fit = dpi
            break

    # if none fit, default to highest DPI so scaling will downsize safely
    if best_fit is None:
        best_fit = max(candidates)

    return best_fit


# ---------------------------
# TTC/TTF helper and antialiased rendering (guarantee final height)
# ---------------------------
def try_load_truetype(fontfile, size, index=None):
    if not fontfile:
        raise IOError("No fontfile provided")
    fontfile = str(fontfile)
    try:
        if fontfile.lower().endswith('.ttc'):
            if index is None:
                for i in range(0,8):
                    try:
                        return ImageFont.truetype(fontfile, size, index=i)
                    except Exception:
                        continue
                return ImageFont.truetype(fontfile, size)
            else:
                return ImageFont.truetype(fontfile, size, index=index)
        else:
            return ImageFont.truetype(fontfile, size)
    except Exception:
        raise

def render_text_exact_height(text, fontfile, desired_px_height, scale_factor=8, rotate_deg=0):
    """
    Render text so final cap-height ~ desired_px_height using oversampling + resample.
    rotate_deg rotates clockwise; final image has expand=True behavior.
    """
    if not fontfile:
        f = ImageFont.load_default()
        bbox = ImageDraw.Draw(Image.new('L', (1,1))).textbbox((0,0), text, font=f)
        w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
        im = Image.new('L', (w+4, h+4), 255)
        ImageDraw.Draw(im).text((2,2), text, font=f, fill=0)
        newh = max(1, int(round(desired_px_height)))
        neww = max(1, int(round((w+4) * (newh / float(h+4)))))
        im = im.resize((neww, newh), resample=Image.Resampling.LANCZOS)
        if rotate_deg:
            im = im.rotate(-rotate_deg, expand=True)
        from PIL import ImageOps
        im = ImageOps.invert(im)
        return im

    # oversampled render for better antialiasing
    trial_px = max(48, int(math.ceil(desired_px_height * scale_factor)))
    font = try_load_truetype(fontfile, trial_px)

    # initial render
    tmp = Image.new('L', (trial_px*10, trial_px*4), 255)
    dr = ImageDraw.Draw(tmp)
    bbox = dr.textbbox((0, 0), text, font=font)
    w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
    pad = 8
    im_s = Image.new('L', (w+pad*2, h+pad*2), 255)
    dr2 = ImageDraw.Draw(im_s)
    dr2.text((pad - bbox[0], pad - bbox[1]), text, font=font, fill=0)

    # Estimate cap-height by measuring capital letters
    cap_text = "H"
    bbox_cap = dr.textbbox((0, 0), cap_text, font=font)
    cap_h = bbox_cap[3] - bbox_cap[1]
    if cap_h == 0:
        cap_h = h

    scale = desired_px_height / float(cap_h)
    new_w = max(1, int(round(im_s.size[0] * scale)))
    new_h = max(1, int(round(im_s.size[1] * scale)))
    im = im_s.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)
    im = im.filter(ImageFilter.GaussianBlur(radius=0.3))
    
    if rotate_deg:
        im = im.rotate(-rotate_deg, expand=True)

    from PIL import ImageOps
    im = ImageOps.invert(im)  # <-- FIX: invert before returning
    return im


# ----------------------------
# Missing patch reporting + consistency check between .cht and .cie
# ----------------------------
def normalize_sid_global(sid):
    """
    Normalize sample IDs to a consistent canonical form.

    Handles:
      A1, A01, A001        -> A1
      AA01, AA1            -> AA1
      2A01, 2A1            -> 2A1
      GS01, GS1            -> GS1
      Numeric only (e.g., 001) -> 1
    """
    sid_orig = str(sid or "").strip()
    sid_up = sid_orig.upper()

    debug_print(f"[normalize_sid_global] raw='{sid_orig}' upper='{sid_up}'")

    # --- Gray strip special case (GS00–GS99 etc.)
    m = re.match(r"^(GS)0*(\d+)$", sid_up)
    if m:
        base, num = m.groups()
        normalized = f"{base}{int(num)}"
        debug_print(f" → Matched gray strip: '{sid_up}' → '{normalized}'")
        return normalized

    # --- Numeric prefix + alphabetic + numeric suffix, e.g. 2A01, 10AB12
    m = re.match(r"^(\d+)([A-Z]+)0*(\d+)$", sid_up)
    if m:
        num_prefix, letters, num_suffix = m.groups()
        normalized = f"{num_prefix}{letters}{int(num_suffix)}"
        debug_print(f" → Matched prefixed form: '{sid_up}' → '{normalized}'")
        return normalized

    # --- Pure alphabetic + numeric (handles A01, AA1, AX02, etc.)
    m = re.match(r"^([A-Z]+)0*(\d+)$", sid_up)
    if m:
        letters, num_suffix = m.groups()
        normalized = f"{letters}{int(num_suffix)}"
        debug_print(f" → Matched alpha+num form: '{sid_up}' → '{normalized}'")
        return normalized

    # --- Pure numeric patch (rare, but valid in test charts)
    if re.match(r"^\d+$", sid_up):
        normalized = str(int(sid_up))
        debug_print(f" → Pure numeric: '{sid_up}' → '{normalized}'")
        return normalized

    # --- Pure alphabetic patch (single chip names like 'A', 'AA', etc.)
    if re.match(r"^[A-Z]+$", sid_up):
        debug_print(f" → Pure alphabetic patch: '{sid_up}' unchanged")
        return sid_up

    # --- Fallback: return as-is
    debug_print(f" → No match: returning unchanged '{sid_up}'")
    return sid_up


# ---------------------------
# Main rendering function
# ---------------------------
#map_fids not used
#def recreate(cht_path, cie_path, out_path, target_dpi=DEFAULT_TARGET_DPI,
#             font_path=None, map_fids=None, output_png=False, font_mm_tuple=None,
#             background_patch=None, color_space='lab', intent='display', 
#             label_axis_visible=None, page_margin_mm=15.0):
def recreate(cht_path, cie_path, out_path, target_dpi=DEFAULT_TARGET_DPI,
             font_path=None, output_png=False, font_mm_tuple=None,
             background_patch=None, color_space='lab', intent='display', 
             label_axis_visible=None, page_margin_mm=15.0):
    """
    1.Parse .cht
    2.Parse .cie
    3.Immediately detect the global scale factor
    4.Continue with geometry, DPI, etc.
    5.Apply the background color (using that same scale_factor)
    6.Render all patches"""
    
    
    cht = parse_cht(cht_path)
    # parse CIE/IT8 file
    fmt, data_map, header = parse_it8_or_cie(cie_path, color_space=color_space)

    # -------------------------------------------------------
    # Manual per-area label visibility override from CLI
    # -------------------------------------------------------
    manual_label_visibility = {}
    if label_axis_visible:
        # Expect items like ["X=B", "Y=LT", "Z=ALL", "W=NONE"]
        for entry in label_axis_visible:
            if not entry or '=' not in entry:
                continue
            area_id, flags = entry.split('=', 1)
            area_id = area_id.strip().upper()
            flags = flags.strip().upper()

            # --- Accept special keywords before filtering ---
            if flags in ("ALL", "NONE"):
                manual_label_visibility[area_id] = flags
            else:
                # Keep only valid LTRB characters
                filtered = ''.join(ch for ch in flags if ch in 'LTRB')
                if filtered:
                    manual_label_visibility[area_id] = filtered
    
    # -------------------------------------------------------------
    # Detect and set global normalization scale based on color_space
    # -------------------------------------------------------------
    def detect_scale_for_space(data_map, space, debug_print):
        """Determine a global normalization factor for the active color space using per-record index mapping."""
        vals_all = []

        # Collect all numeric values from records of the chosen color space
        for rec in data_map.values():
            if rec.get("space", "").lower() != space:
                continue
            vals = rec.get("vals")
            i1, i2, i3 = rec.get("i1"), rec.get("i2"), rec.get("i3")
            if vals and None not in (i1, i2, i3):
                try:
                    v1, v2, v3 = float(vals[i1]), float(vals[i2]), float(vals[i3])
                    vals_all.extend([v1, v2, v3])
                except Exception:
                    continue

        if not vals_all:
            debug_print(f"[ScaleDetect] No numeric data found for {space.upper()} → scale=1.0")
            return 1.0

        vmax = max(vals_all)
        vmean = sum(vals_all) / len(vals_all)

        # Decide scaling factor by magnitude range
        if space == "xyz":
            if vmax > 5.0:
                factor = 1.0 / 100.0
                debug_print(f"[ScaleDetect] XYZ range ~0–100 (vmax={vmax:.2f}, mean={vmean:.2f}) → apply /100")
            else:
                factor = 1.0
                debug_print(f"[ScaleDetect] XYZ range ~0–1 (vmax={vmax:.2f}) → no scaling")

        elif space == "rgb":
            if vmax > 5.0 and vmax <= 255.0:
                factor = 1.0 / 255.0
                debug_print(f"[ScaleDetect] RGB range ~0–255 (vmax={vmax:.2f}, mean={vmean:.2f}) → apply /255")
            elif vmax > 255.0:
                factor = 1.0 / 65535.0
                debug_print(f"[ScaleDetect] RGB range ~0–65535 (vmax={vmax:.2f}, mean={vmean:.2f}) → apply /65535")
            else:
                factor = 1.0
                debug_print(f"[ScaleDetect] RGB range ~0–1 (vmax={vmax:.2f}) → no scaling")

        else:
            factor = 1.0
            debug_print(f"[ScaleDetect] LAB space → unitless, no scaling")

        return factor

    # Apply global detection based on selected color_space
    scale_factor = detect_scale_for_space(data_map, color_space.lower(), debug_print)     


    
    # If older parse returned a list (sid, vals) rather than a dict, convert it to the normalized map:
    if not isinstance(data_map, dict):
        tmp = {}
        # assume data_map is a list of (sid, vals)
        for sid, vals in data_map:
            tmp[sid.strip().upper()] = {
                "vals": vals,
                "iL": None, "iA": None, "iB": None
            }
        data_map = tmp

    # ---------- helper: find normalized entry for a SID (nested so it can see data_map) ----------
    def find_vals_for_sid(sid):
        """
        Return normalized entry dict or None.
        Tries all reasonable label variants (A1 ↔ A01 ↔ A001, GS1 ↔ GS01, etc.)
        """

        if not sid:
            return None
        debug_print(f"→ find_vals_for_sid('{sid}')")
        s = str(sid).strip().upper()

        # Direct match
        if s in data_map:
            debug_print(f"✅ Direct match: '{s}' found in data_map")
            return data_map[s]

        # Handle GS / grayscale variants
        m = re.match(r'^(GS)(0*)(\d+)$', s, flags=re.I)
        if m:
            base, _, num = m.groups()
            num = int(num)
            for w in (1, 2, 3):
                cand = f"{base.upper()}{num:0{w}d}"
                if cand in data_map:
                    return data_map[cand]
            cand = f"{base.upper()}{num}"
            if cand in data_map:
                return data_map[cand]

        # Generic letter-number forms (A1 ↔ A01)
        m2 = re.match(r'^([A-Z]+)(0*)(\d+)$', s)
        if m2:
            prefix, _, num = m2.groups()
            num = int(num)
            for w in (1, 2, 3):
                cand = f"{prefix.upper()}{num:0{w}d}"
                if cand in data_map:
                    return data_map[cand]
            cand = f"{prefix.upper()}{num}"
            if cand in data_map:
                return data_map[cand]

        debug_print(f"❌ No match for '{sid}' (normalized: '{s}')")
        return None

        
    areas = cht.get('areas', [])
    if not areas:
        raise RuntimeError("No X/Y area definitions found in .cht. v8 expects explicit area lines.")

    box_shrink_units = float(cht.get('box_shrink', 0.0))
    fids_units = cht['fids']

    # label/footer default sizes (2mm default as per tests)
    if font_mm_tuple is None:
        label_mm = 2.0; footer_mm = 2.0
    else:
        label_mm = float(font_mm_tuple[0]); footer_mm = float(font_mm_tuple[1])

    # compute chart extents in .cht units (units are 100dpi units)
    minx_u, miny_u, maxx_u, maxy_u = compute_canvas_extents_from_areas(areas, 1.0, 1.0)
    fxs_u = [xu for xu,yu in fids_units]; fys_u = [yu for xu,yu in fids_units]
    minx_u = min(minx_u, min(fxs_u))
    miny_u = min(miny_u, min(fys_u))
    maxx_u = max(maxx_u, max(fxs_u))
    maxy_u = max(maxy_u, max(fys_u))
    chart_units_w = maxx_u - minx_u
    chart_units_h = maxy_u - miny_u

    # --- Detect which standard A4 DPI the chart fits within ---
    detected_dpi = detect_best_a4_dpi(chart_units_w, chart_units_h, margin_mm=page_margin_mm)
    user_specified_dpi = (target_dpi is not None)

    # If user specified a target DPI, use that; otherwise default to 300
    used_dpi = float(target_dpi) if user_specified_dpi else 300.0

    # Print diagnostic info
    print(f"Detected native chart DPI (fit to A4): {detected_dpi} dpi. ", end="")
    if user_specified_dpi:
        print(f"Requested target_dpi={used_dpi} dpi.")
    else:
        print(f"No target_dpi specified -> rendering at {used_dpi} dpi by default (preserve physical size).")

    # --- Compute scale factors relative to the detected A4 match ---
    # Each A4 DPI has a known pixel size (A4_DPI_TABLE)
    if int(round(detected_dpi)) in A4_DPI_TABLE:
        det_w, det_h = A4_DPI_TABLE[int(round(detected_dpi))]
    else:
        det_w = int(round(210.0 / 25.4 * detected_dpi))
        det_h = int(round(297.0 / 25.4 * detected_dpi))

    if int(round(used_dpi)) in A4_DPI_TABLE:
        tgt_w, tgt_h = A4_DPI_TABLE[int(round(used_dpi))]
    else:
        tgt_w = int(round(210.0 / 25.4 * used_dpi))
        tgt_h = int(round(297.0 / 25.4 * used_dpi))

    # --- Scale factors from detected→target DPI (preserve physical size with high precision) ---
    if used_dpi == detected_dpi:
        # No scaling needed
        scale_x = scale_y = 1.0
    else:
        # Physical scaling ratio (DPI ratio)
        dpi_ratio = used_dpi / detected_dpi

        # A4 aspect correction: use width/height ratio between A4 pixel sizes at the two DPIs
        det_w, det_h = A4_DPI_TABLE.get(int(round(detected_dpi)),
                                        (int(210/25.4*detected_dpi), int(297/25.4*detected_dpi)))
        tgt_w, tgt_h = A4_DPI_TABLE.get(int(round(used_dpi)),
                                        (int(210/25.4*used_dpi), int(297/25.4*used_dpi)))

        # Combine both factors — but in the correct direction
        scale_x = dpi_ratio * (tgt_w / det_w) / (used_dpi / detected_dpi)
        scale_y = dpi_ratio * (tgt_h / det_h) / (used_dpi / detected_dpi)

    SX = scale_x
    SY = scale_y
    px_per_mm = used_dpi / 25.4

    debug_print(f"Scaling from detected {detected_dpi} dpi → target {used_dpi} dpi.")
    debug_print(f"   scale_x = {scale_x:.10f}, scale_y = {scale_y:.10f}")
    debug_print(f"   SX = {SX:.10f} px/unit, SY = {SY:.10f} px/unit")


    # If user did not specify and detected_dpi differs from used_dpi, print scale factors
    if not user_specified_dpi and detected_dpi != used_dpi:
        debug_print(f"Scaling: detected {detected_dpi} -> used {used_dpi} dpi (will change pixel density but preserve physical chart size).")

    def unit_to_px(xu, yu):
        return xu * SX, yu * SY

    mapping_method = 'units_to_px'
    A = None
#map_fids argument not used
#    if map_fids is not None:
#        parts = map_fids
#        if len(parts) != 8:
#            raise ValueError("--map-fids requires 8 numbers")
#        dst = [(parts[i], parts[i+1]) for i in range(0,8,2)]
#        src = np.array(fids_units, dtype=float)
#        dst_a = np.array(dst, dtype=float)
#        if src.shape[0] >= 3:
#            try:
#                A = fit_affine(fids_units, dst)
#                def unit_to_px_aff(xu, yu):
#                    v = A @ np.array([xu, yu, 1.0])
#                    return float(v[0]), float(v[1])
#                unit_to_px = unit_to_px_aff
#                mapping_method = 'affine_from_user_map'
#            except Exception:
#                pass

    # --- Compute full extents including both Y and X areas ---
    minx_area, miny_area, maxx_area, maxy_area = compute_canvas_extents_from_areas(areas, SX, SY)

    # The 'X' area (GS row) often extends further down — include it
    for area in areas:
        if area['axis'].upper() == 'X':
            gs_bottom = (area['pre_y'] + area['tile_y']) * SY
            if gs_bottom > maxy_area:
                maxy_area = gs_bottom
                
    fids_px_raw = [unit_to_px(xu, yu) for xu, yu in fids_units]
    fxs_raw = [p[0] for p in fids_px_raw]; fys_raw = [p[1] for p in fids_px_raw]
    minx_raw = min(minx_area, min(fxs_raw))
    miny_raw = min(miny_area, min(fys_raw))
    maxx_raw = max(maxx_area, max(fxs_raw))
    maxy_raw = max(maxy_area, max(fys_raw))

    margin_px = int(round(page_margin_mm * px_per_mm))
    offset_x = margin_px - minx_raw
    offset_y = margin_px - miny_raw
    fids_px = [(fx + offset_x, fy + offset_y) for fx, fy in fids_px_raw]
    minx = minx_raw + offset_x; miny = miny_raw + offset_y
    maxx = maxx_raw + offset_x; maxy = maxy_raw + offset_y

    footer_space_px = int(round(12.0 * px_per_mm))
    W = int(math.ceil(maxx + margin_px))
    H = int(math.ceil(maxy + margin_px + footer_space_px))
    W = max(W, 400); H = max(H, 300)

    canvas = np.full((H, W, 3), 65535, dtype=np.uint16)

    # data_map is already normalized by parser — nothing to reassign
    # data_map = data no longer needed.


    # --- Optional background color from specified patch label ---
    if background_patch:
        bg_label = background_patch.strip().upper()
        rec_bg = None
        try:
            rec_bg = find_vals_for_sid(bg_label)
        except Exception:
            rec_bg = None
        if rec_bg and rec_bg.get("vals"):
            try:
                vals_bg = rec_bg["vals"]
                space = rec_bg.get("space", color_space.lower())
                i1, i2, i3 = rec_bg.get("i1"), rec_bg.get("i2"), rec_bg.get("i3")

                if None not in (i1, i2, i3):
                    c1, c2, c3 = float(vals_bg[i1]), float(vals_bg[i2]), float(vals_bg[i3])

                    if space == "lab":
                        X, Y, Z = lab_to_xyz(c1, c2, c3)
                        # In XYZ/LAB paths, scale_factor applied before sending values to xyz_d50_to_srgb_intent()
                        rgb_lin = xyz_d50_to_srgb_intent(X, Y, Z, intent=intent, clip=False)

                    elif space == "xyz":
                        # In XYZ/LAB paths, scale_factor applied before sending values to xyz_d50_to_srgb_intent()
                        c1, c2, c3 = c1 * scale_factor, c2 * scale_factor, c3 * scale_factor
                        rgb_lin = xyz_d50_to_srgb_intent(c1, c2, c3, intent=intent, clip=False)

                    elif space == "rgb":
                        # Treat as already gamma-encoded sRGB
                        rgb_lin = np.array([c1, c2, c3]) * scale_factor
                        #c1, c2, c3 = c1 * scale_factor, c2 * scale_factor, c3 * scale_factor
                        #rgb_lin = np.array([c1, c2, c3])

                    else:
                        rgb_lin = np.array([0.5, 0.5, 0.5])
                else:
                    rgb_lin = np.array([0.5, 0.5, 0.5])

                rgb_display = np.clip(rgb_lin, 0.0, 1.0)
                rgb16 = (rgb_display * 65535.0).astype(np.uint16)
                canvas[:, :, :] = rgb16
                print(f"Background filled from patch '{bg_label}' → RGB {rgb_display}")

            except Exception as e:
                print(f"Warning: failed to apply background from patch '{bg_label}': {e}", file=sys.stderr)
        else:
            print(f"Warning: background patch '{bg_label}' not found in CIE data.", file=sys.stderr)

            
    # Determine actual expected labels only from defined .cht patch positions
    # to prevent false "missing" warnings for non-existent inferred labels.
    patch_positions = {}
    missing_labels = set()
    sample_order_list = []
    color_debug_list = []
    
    def make_patch_label(area, rlabel, clabel):
        """Combine row/column labels depending on area label_mode."""
        mode = area.get("label_mode", None)
        if rlabel == "_" or rlabel is None:
            return normalize_sid_global(clabel)
        if clabel == "_" or clabel is None:
            return normalize_sid_global(rlabel)

        if mode == "prefixed_y":
            return normalize_sid_global(f"{rlabel}{clabel}")
        elif mode == "prefixed_x":
            return normalize_sid_global(f"{clabel}{rlabel}")

        # Heuristic for normal areas:
        # - if rlabel is alphabetic and clabel numeric → A1 form
        # - if rlabel numeric and clabel alphabetic → A1 form (swap)
        # - otherwise concatenate as-is
        if rlabel[0].isalpha() and clabel[0].isdigit():
            return normalize_sid_global(f"{rlabel}{clabel}")
        elif rlabel[0].isdigit() and clabel[0].isalpha():
            return normalize_sid_global(f"{clabel}{rlabel}")
        else:
            return normalize_sid_global(f"{rlabel}{clabel}")       

    # --- Prepare annotation canvas and font before drawing patches ---
    annot = Image.new('L', (W, H), 255)
    draw = ImageDraw.Draw(annot)

    # Font find: case-insensitive search and support for macOS TTC names
    chosen_font = None
    user_font_provided = (font_path is not None)
    
    if user_font_provided:
        # Accept the exact path if it exists; if not, try case-insensitive matching on directory
        if os.path.exists(font_path):
            chosen_font = str(font_path)
        else:
            # try to find case-insensitive match in the provided path's directory
            p = Path(font_path)
            parent = p.parent if p.parent.exists() else None
            if parent and parent.is_dir():
                target_name = p.name.lower()
                for f in parent.iterdir():
                    if f.name.lower() == target_name:
                        chosen_font = str(f)
                        break
            # else fall through to generic search
    if not chosen_font:
        candidates_dirs = [
            "/System/Library/Fonts",
            "/Library/Fonts",
            "/usr/share/fonts/truetype",
            "/usr/share/fonts",
            str(Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts")
        ]
        font_names = ["Palatino.ttc", "Helvetica.ttc", "Times.ttc", "DejaVuSans.ttf", "Arial.ttf"]
        for d in candidates_dirs:
            pd = Path(d)
            if pd.exists() and pd.is_dir():
                for fn in font_names:
                    for fx in pd.glob("**/*"):
                        if fx.is_file() and fx.name.lower() == fn.lower():
                            chosen_font = str(fx)
                            break
                    if chosen_font:
                        break
            if chosen_font:
                break
    if not chosen_font:
        try:
            ImageFont.truetype("Palatino.ttf", 10)
            chosen_font = "Palatino.ttf"
        except Exception:
            chosen_font = None

    if not chosen_font:
        print(f"Warning: no font TTF/TTC found; text mm control may be inexact.", file=sys.stderr)

    # compute label sizes in pixels (exact)
    label_px_target = max(6, int(round(label_mm * px_per_mm)))
    footer_px_target = max(6, int(round(footer_mm * px_per_mm)))
    # unify footer font size for all footer texts (avoid per-line rounding differences)
    footer_font_px = footer_px_target
    debug_print(f"Footer text target height: {footer_font_px}px ({footer_mm:.2f} mm at {used_dpi} dpi)")
    label_gap_px = int(round(1.0 * px_per_mm))
    small_gap_px = int(round(0.5 * px_per_mm))


    # Unified area renderer — handles any X/Y definition consistently
    for area in areas:
        axis = area['axis']
        labels_x = generate_labels(area['xstart'], area['xend'])
        labels_y = generate_labels(area['ystart'], area['yend'])
        ncols = len(labels_x)
        nrows = len(labels_y)
        tile_x = area['tile_x']; tile_y = area['tile_y']
        pre_x = area['pre_x']; pre_y = area['pre_y']
        post_x = area['post_x']; post_y = area['post_y']

        start_x_px = pre_x * SX + offset_x
        start_y_px = pre_y * SY + offset_y

        shrink_x_px = box_shrink_units * SX
        shrink_y_px = box_shrink_units * SY

        # --- compute total physical extents ---
        total_w = ncols * tile_x * SX if ncols > 0 else tile_x * SX
        total_h = nrows * tile_y * SY if nrows > 0 else tile_y * SY

        # --- compute x, y grid edges with integer rounding ---
        if ncols > 0:
            base_w = int(math.floor(total_w / ncols))
            remainder_w = int(round(total_w - base_w * ncols))
            widths = [base_w + (1 if i < remainder_w else 0) for i in range(ncols)]
            x_edges = [int(round(start_x_px))]
            for w in widths:
                x_edges.append(x_edges[-1] + w)
        else:
            x_edges = [int(round(start_x_px)), int(round(start_x_px + total_w))]

        if nrows > 0:
            base_h = int(math.floor(total_h / nrows))
            remainder_h = int(round(total_h - base_h * nrows))
            heights = [base_h + (1 if i < remainder_h else 0) for i in range(nrows)]
            y_edges = [int(round(start_y_px))]
            for h in heights:
                y_edges.append(y_edges[-1] + h)
        else:
            y_edges = [int(round(start_y_px)), int(round(start_y_px + total_h))]

        # --- unified patch drawing loop ---
        # even if nrows == 0, we still iterate once; same for ncols == 0
        if nrows == 0:
            labels_y = ['_']
            y_edges = [int(round(start_y_px)), int(round(start_y_px + total_h))]
            nrows = 1
        if ncols == 0:
            labels_x = ['_']
            x_edges = [int(round(start_x_px)), int(round(start_x_px + total_w))]
            ncols = 1

        for r_idx, rlabel in enumerate(labels_y):
            for c_idx, clabel in enumerate(labels_x):
                sid = make_patch_label(area, rlabel, clabel)

                x0f = x_edges[c_idx]
                x1f = x_edges[c_idx + 1]
                y0f = y_edges[r_idx]
                y1f = y_edges[r_idx + 1]

                debug_print(f"Checking patch label '{sid}' from .cht")
                rec = find_vals_for_sid(sid.upper())
                if not rec:
                    debug_print(f"⚠️ Missing CIE entry for '{sid.upper()}' — using gray fallback")
                rgb = np.array([0.5, 0.5, 0.5])

                if rec and rec.get("vals"):
                    vals = rec["vals"]
                    space = rec.get("space", color_space.lower())
                    i1 = rec.get("i1"); i2 = rec.get("i2"); i3 = rec.get("i3")

                    if None not in (i1, i2, i3):
                        try:
                            c1, c2, c3 = float(vals[i1]), float(vals[i2]), float(vals[i3])
                            if space == "lab":
                                rgb = xyz_d50_to_srgb_intent(*lab_to_xyz(c1, c2, c3), intent=intent, clip=False)
                            elif space == "xyz":
                                rgb = xyz_d50_to_srgb_intent(c1 * scale_factor,
                                                             c2 * scale_factor,
                                                             c3 * scale_factor,
                                                             intent=intent, clip=False)
                            elif space == "rgb":
                                rgb = np.array([c1, c2, c3]) * scale_factor
                            else:
                                rgb = np.array([0.5, 0.5, 0.5])
                        except Exception as e:
                            debug_print(f"❌ Conversion failed for {sid}: {e}")
                    else:
                        try:
                            rgb = np.array([float(v) for v in vals[:3]])
                            if np.max(rgb) > 1.5:
                                rgb /= 255.0
                        except Exception:
                            pass
                else:
                    missing_labels.add(sid.upper())

                rgb_display = np.clip(rgb, 0.0, 1.0)
                rgb16 = (rgb_display * 65535.0).astype(np.uint16)
                # DEBUG: inspect a few patch RGB values to verify scaling/gamma
                if sid.upper() in ("A1", "M10"):  # choose 1–3 representative patches
                    debug_print(f"[DEBUG] Check RGB {sid.upper()} → rgb_display = {rgb_display}")

                x0c = max(0, min(W, x0f)); x1c = max(0, min(W, x1f))
                y0c = max(0, min(H, y0f)); y1c = max(0, min(H, y1f))
                if x1c > x0c and y1c > y0c:
                    canvas[y0c:y1c, x0c:x1c, 0] = int(rgb16[0])
                    canvas[y0c:y1c, x0c:x1c, 1] = int(rgb16[1])
                    canvas[y0c:y1c, x0c:x1c, 2] = int(rgb16[2])

                sample_order_list.append((sid.upper(), (x0c, y0c, x1c, y1c)))
                color_debug_list.append((sid.upper(),
                                         tuple(map(float, rgb)),
                                         tuple(map(int, rgb16)),
                                         (x0c, y0c, x1c, y1c)))

                
        # ---------------------- Neighbour detection Start --------------------------

        # --- After drawing all patches for this area, draw axis labels ---
        # Compute edge bounds in pixels for this area
        ncols = len(labels_x)
        nrows = len(labels_y)
        if ncols == 0 or nrows == 0:
            continue

        # Compute area boundaries
        left_px  = x_edges[0]
        right_px = x_edges[-1]
        top_px   = y_edges[0]
        bottom_px = y_edges[-1]
        tile_w_px = area['tile_x'] * SX
        tile_h_px = area['tile_y'] * SY

        # --- Measure rendered label sizes (used to compute clearance) ---
        test_imgs_x = [render_text_exact_height(lbl, chosen_font, label_px_target, scale_factor=4)
                       for lbl in labels_x]
        widths_x = [im.size[0] for im in test_imgs_x] if test_imgs_x else [0]
        heights_x = [im.size[1] for im in test_imgs_x] if test_imgs_x else [0]

        # Decide if column labels will be rotated (same logic you used earlier)
        need_rotate = any(w > 0.95 * tile_w_px for w in widths_x)
        max_label_w = max(widths_x) if widths_x else 0
        max_label_h = max(heights_x) if heights_x else 0

        # Clearance we require between adjacent areas to safely display labels:
        # label height (or rotated width) + 2 * 1mm gap
        label_gap_mm = 1.0
        label_gap_px = label_gap_mm * px_per_mm
        clearance_h_px = (max_label_h if not need_rotate else max_label_w) + 2 * label_gap_px
        clearance_w_px = max_label_w + 2 * label_gap_px

        # --- Helpers using the same coordinate system (pixels with offsets) ---
        def area_bounds(a):
            cols = len(generate_labels(a['xstart'], a['xend']))
            rows = len(generate_labels(a['ystart'], a['yend']))
            left = a['pre_x'] * SX + offset_x
            top = a['pre_y'] * SY + offset_y
            right = left + max(1, cols) * a['tile_x'] * SX
            bottom = top + max(1, rows) * a['tile_y'] * SY
            return left, top, right, bottom

        def horiz_gap(a1, a2):
            """Positive = gap in px between horizontally adjacent areas (0 = touching). -1 = overlap."""
            l1, _, r1, _ = area_bounds(a1)
            l2, _, r2, _ = area_bounds(a2)
            if r1 <= l2:
                return l2 - r1
            if r2 <= l1:
                return l1 - r2
            return -1

        def vert_gap(a1, a2):
            """Positive = gap in px between vertically adjacent areas (0 = touching). -1 = overlap."""
            _, t1, _, b1 = area_bounds(a1)
            _, t2, _, b2 = area_bounds(a2)
            if b1 <= t2:
                return t2 - b1
            if b2 <= t1:
                return t1 - b2
            return -1

        def horiz_overlap(a1, a2):
            l1, _, r1, _ = area_bounds(a1); l2, _, r2, _ = area_bounds(a2)
            return not (r1 <= l2 or r2 <= l1)

        def vert_overlap(a1, a2):
            _, t1, _, b1 = area_bounds(a1); _, t2, _, b2 = area_bounds(a2)
            return not (b1 <= t2 or b2 <= t1)

        # --- Start with all sides visible, then suppress only the inner faces where necessary ---
        draw_left_labels   = True
        draw_right_labels  = True
        draw_top_labels    = True
        draw_bottom_labels = True

        # For every other area, detect adjacency within required clearance.
        # If two areas are horizontally adjacent (left/right) and overlap vertically,
        # then suppress the inner faces (right face of left area, left face of right area).
        # If vertically adjacent and overlap horizontally, suppress inner faces analogously.
        for a in areas:
            if a is area:
                continue
            la, ta, ra, ba = area_bounds(a)

            # --- Horizontal adjacency check ---
            g = horiz_gap(area, a)
            if g >= 0 and g < clearance_w_px and vert_overlap(area, a):
                # This area is left of 'a'
                if right_px <= la:
                    draw_right_labels = False  # hide right labels (neighbor immediately on right)
                    debug_print(f"  → hide RIGHT labels (neighbor {a['xstart']}..{a['xend']} touches on right)")
                # This area is right of 'a'
                elif ra <= left_px:
                    draw_left_labels = False   # hide left labels (neighbor immediately on left)
                    debug_print(f"  → hide LEFT labels (neighbor {a['xstart']}..{a['xend']} touches on left)")

            # --- Vertical adjacency check ---
            g = vert_gap(area, a)
            if g >= 0 and g < clearance_h_px and horiz_overlap(area, a):
                if bottom_px <= ta:
                    draw_bottom_labels = False  # hide bottom labels (neighbor below)
                    debug_print(f"  → hide BOTTOM labels (neighbor {a['xstart']}..{a['xend']} below)")
                elif ba <= top_px:
                    draw_top_labels = False     # hide top labels (neighbor above)
                    debug_print(f"  → hide TOP labels (neighbor {a['xstart']}..{a['xend']} above)")

            debug_print(
                f"Neighbor flags for area {area['xstart']}..{area['xend']}: "
                f"L={draw_left_labels}, R={draw_right_labels}, "
                f"T={draw_top_labels}, B={draw_bottom_labels}"
            )
        # Future suggestion if desired: clamp label flags with a sanity check (if no space at image edge etc.)
        # (optional, but safe) if area is touching image left edge, still allow left labels
        # The default flags remain; later drawing code will place labels using these flags.

        # ---------------------- Neighbour detection End --------------------------

        # --- Apply manual visibility override if provided ---
        axis_id = area.get('axis', '').strip().upper()
        if axis_id in manual_label_visibility:
            vis_flags = manual_label_visibility[axis_id].upper().strip()

            if vis_flags == 'ALL':
                draw_left_labels = draw_right_labels = draw_top_labels = draw_bottom_labels = True
            elif vis_flags == 'NONE':
                draw_left_labels = draw_right_labels = draw_top_labels = draw_bottom_labels = False
            else:
                draw_left_labels   = 'L' in vis_flags
                draw_right_labels  = 'R' in vis_flags
                draw_top_labels    = 'T' in vis_flags
                draw_bottom_labels = 'B' in vis_flags

            debug_print(f"[MANUAL OVERRIDE] Label visibility override for Area={axis_id} → L={draw_left_labels}, R={draw_right_labels}, T={draw_top_labels}, B={draw_bottom_labels}")
        
        # --- Auto-suppress labels when there’s only one row or one column ---
        # Prevent drawing '-' or empty single-row/col labels entirely.
        if len(labels_y) == 1:
            draw_left_labels = draw_right_labels = False
            debug_print(f"[AUTO-SUPPRESS] Area={axis_id}: single-row detected, hiding row labels.")
        if len(labels_x) == 1:
            draw_top_labels = draw_bottom_labels = False
            debug_print(f"[AUTO-SUPPRESS] Area={axis_id}: single-column detected, hiding column labels.")

        # --- Draw area labels (row/column) ---
        # Column (X-axis) labels
        if draw_top_labels:
            for c, lbl in enumerate(labels_x):
                imlbl = render_text_exact_height(lbl, chosen_font, label_px_target, scale_factor=4)
                tw, th = imlbl.size
                cx = (x_edges[c] + x_edges[c+1]) // 2
                px = int(round(cx - tw / 2))
                py = int(round(top_px - th - label_gap_px))
                annot.paste(Image.new('L', imlbl.size, 0), (px, py), mask=imlbl)
                debug_print(f"  → top lbl '{lbl}' at ({px},{py})")

        if draw_bottom_labels:
            for c, lbl in enumerate(labels_x):
                imlbl = render_text_exact_height(lbl, chosen_font, label_px_target, scale_factor=4)
                tw, th = imlbl.size
                cx = (x_edges[c] + x_edges[c+1]) // 2
                px = int(round(cx - tw / 2))
                py = int(round(bottom_px + label_gap_px))
                annot.paste(Image.new('L', imlbl.size, 0), (px, py), mask=imlbl)
                debug_print(f"  → bottom lbl '{lbl}' at ({px},{py})")

        # Row (Y-axis) labels
        if draw_left_labels:
            for r, lbl in enumerate(labels_y):
                imlbl = render_text_exact_height(lbl, chosen_font, label_px_target, scale_factor=4)
                tw, th = imlbl.size
                cy = (y_edges[r] + y_edges[r+1]) // 2
                px = int(round(left_px - tw - label_gap_px))
                py = int(round(cy - th / 2))
                annot.paste(Image.new('L', imlbl.size, 0), (px, py), mask=imlbl)
                debug_print(f"  → left lbl '{lbl}' at ({px},{py})")

        if draw_right_labels:
            for r, lbl in enumerate(labels_y):
                imlbl = render_text_exact_height(lbl, chosen_font, label_px_target, scale_factor=4)
                tw, th = imlbl.size
                cy = (y_edges[r] + y_edges[r+1]) // 2
                px = int(round(right_px + label_gap_px))
                py = int(round(cy - th / 2))
                annot.paste(Image.new('L', imlbl.size, 0), (px, py), mask=imlbl)
                debug_print(f"  → right lbl '{lbl}' at ({px},{py})")

                
    # --------------------
    # Annotations: fiducials and labels
    # --------------------
    try:
        block_cx = (minx + maxx) / 2.0 if maxx > minx else (W / 2.0)
        block_cy = (miny + maxy) / 2.0 if maxy > miny else (H / 2.0)
    except Exception:
        block_cx = W / 2.0
        block_cy = H / 2.0

    outer_fid_px = int(round(FID_OUTER_PX_AT_300 * (used_dpi / 300.0)))
    fid_thick = max(1, int(round(FID_LINE_PX_AT_300 * (used_dpi / 300.0))))

    for (fxp, fyp) in fids_px:
        dx = fxp - block_cx; dy = fyp - block_cy
        if dx < 0 and dy < 0:
            dirs = [(1,0),(0,1)]
        elif dx > 0 and dy < 0:
            dirs = [(-1,0),(0,1)]
        elif dx > 0 and dy > 0:
            dirs = [(-1,0),(0,-1)]
        else:
            dirs = [(1,0),(0,-1)]
        for vx, vy in dirs:
            x2 = fxp + vx * outer_fid_px; y2 = fyp + vy * outer_fid_px
            draw.line([(fxp, fyp), (x2, y2)], fill=0, width=fid_thick)
        half = max(1, fid_thick // 2)
        draw.rectangle([fxp-half, fyp-half, fxp+half, fyp+half], fill=0)

                    
    # --- Footer layout left/center/right (use rendered images) ---
    datafile = Path(cie_path).name

    # Determine the first non-empty non-comment token in the CIE file (e.g., IT8.7/2, CIE)
    format_token = ""
    try:
        with open(cie_path, 'r', encoding='utf-8', errors='ignore') as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                format_token = line.split()[0]
                break
    except Exception:
        pass

    # --- Header text: "Created with rectarg" (top-right corner, fixed above margin) ---
    # The text should always sit 1 mm above the top margin area,
    # regardless of fiducial or label placement.

    # Distance from image edge (in px)
    text_gap_mm = 1.0
    text_gap_px = int(round(text_gap_mm * px_per_mm))

    # Render header image
    imhdr = render_text_exact_height(
        "Created with rectarg",
        chosen_font,
        footer_font_px,   # same vertical scale as footer
        scale_factor=4
    )
    tw, th = imhdr.size

    # Compute coordinates:
    # - Bottom edge of text is (page_margin_mm - text_gap_mm) from image top edge
    # - Right edge is page_margin_mm from image right edge
    header_bottom_y = int(round(page_margin_mm * px_per_mm - text_gap_px))
    header_y = max(0, header_bottom_y - th)  # y coordinate for text top
    header_x = int(round(W - page_margin_mm * px_per_mm - tw))

    # Paste text
    annot.paste(Image.new('L', imhdr.size, 0), (header_x, header_y), mask=imhdr)
    debug_print(f"[HEADER] 'Created with rectarg' at ({header_x},{header_y}) "
                f"(margin={page_margin_mm}mm, gap={text_gap_mm}mm)")

    # --- End header text ---

    # Retrieve standard header fields
    origin = header.get('ORIGINATOR', '')
    created = header.get('CREATED', '')
    measured = header.get('MEASURE_DATE', '')
    descriptor = header.get('DESCRIPTOR', '')
    manufacturer = header.get('MANUFACTURER', '')

    # Compose Originator + format token
    if origin:
        origin_line = f"{origin}, {format_token}" if format_token else origin
    else:
        origin_line = format_token

    # Prefer measure date over created date
    if measured:
        created_label = f"Measure Date: {measured}"
    elif created:
        created_label = f"Created: {created}"
    else:
        created_label = ""

    left_x_ref = fids_px[0][0] if fids_px else margin_px
    left_x = int(round(left_x_ref))
    left_y = int(round(maxy + margin_px // 2))

    center_line = "Reproduction of Target from reference data:"
    right_x_ref = fids_px[1][0] if len(fids_px) > 1 else (W - margin_px)
    right_x = int(round(right_x_ref))

    nexty = left_y
    line_spacing_factor = 1.5

    # --- Left-aligned footer block (Created + Data File) ---
    if created:
        imc = render_text_exact_height(f"Created: {created}", chosen_font, footer_font_px, scale_factor=4)
        ww, hh = imc.size
        px = left_x
        py = nexty
        annot.paste(Image.new('L', imc.size, 0), (px, py), mask=imc)
        nexty += int(round(hh * line_spacing_factor))
    else:
        # still advance spacing even if missing
        nexty += int(round(footer_font_px * line_spacing_factor))

    imdf = render_text_exact_height(f"Data File: {datafile}", chosen_font, footer_font_px, scale_factor=4)
    ww, hh = imdf.size
    px = max(0, min(W - ww, left_x))
    annot.paste(Image.new('L', imdf.size, 0), (px, nexty), mask=imdf)
    nexty += int(round(hh * line_spacing_factor))

    imcenter = render_text_exact_height(center_line, chosen_font, footer_font_px, scale_factor=4)
    fw = imcenter.size[0]
    footer_x_center = max(0, int((W - fw)/2.0))
    left_y = max(0, min(H - imcenter.size[1] - 2, left_y))
    annot.paste(Image.new('L', imcenter.size, 0), (footer_x_center, left_y), mask=imcenter)

    ry = left_y

    # Build footer lines only for existing fields
    footer_texts = []
    if origin_line:
        footer_texts.append(origin_line)
    if descriptor:
        footer_texts.append(descriptor)
    if manufacturer:
        footer_texts.append(f"Manufacturer: {manufacturer}")

    for txt in footer_texts:
        imr = render_text_exact_height(txt, chosen_font, footer_font_px, scale_factor=4)
        tw = imr.size[0]
        px = int(round(right_x - tw))
        px = max(0, min(W - tw, px))
        annot.paste(Image.new('L', imr.size, 0), (px, ry), mask=imr)
        ry += imr.size[1] + 2

    # --- Correct anti-aliased black text compositing, blend 
    # inline-rendered labels (and fiducials) into the main canvas ---
    annot_arr = np.array(annot, dtype=np.float32)  # 0–255 grayscale
    alpha = (255.0 - annot_arr) / 255.0            # 1.0 = full text, 0.0 = background

    if np.any(alpha > 0):
        # Draw solid black text using the alpha as opacity
        for ch in range(3):
            canvas[..., ch] = (
                (1.0 - alpha) * canvas[..., ch].astype(np.float32)
            ).astype(np.uint16)

    # Save TIFF (16-bit) or PNG fallback
    outp = Path(out_path)
    if HAVE_TIFF:
        tifffile.imwrite(str(outp), canvas, photometric='rgb',
                         resolution=(int(round(used_dpi)), int(round(used_dpi))),
                         resolutionunit='inch')
    else:
        tmp = (canvas.astype(np.uint32) >> 8).astype(np.uint8)
        Image.fromarray(tmp).save(str(outp.with_suffix('.png')))
        print("Warning: tifffile not installed — saved 8-bit PNG fallback.", file=sys.stderr)

    if output_png and HAVE_TIFF:
        tmp = (canvas.astype(np.uint32) >> 8).astype(np.uint8)
        Image.fromarray(tmp).save(str(outp.with_suffix('.preview.png')))

    # --- Apply normalization before comparing labels ---
    defined_labels = set(normalize_sid_global(sid) for sid, _ in sample_order_list)
    cie_labels = set(normalize_sid_global(k) for k in data_map.keys())
    missing_labels = defined_labels - cie_labels


    # --- Extract expected patch count from .cht and .cie files ---
    expected_cht_patches = None
    expected_cie_patches = None

    def extract_patch_count_from_file(path):
        val = None
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line_up = line.strip().upper()
                if line_up.startswith("EXPECTED XYZ"):
                    parts = re.split(r"\s+", line_up)
                    if len(parts) >= 3:
                        try:
                            val = int(parts[2])
                            break
                        except ValueError:
                            pass
                elif "PATCHES_ACTIVE" in line_up:
                    parts = re.split(r"\s+", line_up)
                    for p in parts:
                        if p.isdigit():
                            val = int(p)
                            break
                elif "NUMBER_OF_SETS" in line_up:
                    parts = re.split(r"\s+", line_up)
                    for p in parts:
                        if p.isdigit():
                            val = int(p)
                            break
        return val

    expected_cht_patches = extract_patch_count_from_file(cht_path)
    expected_cie_patches = extract_patch_count_from_file(cie_path)
    measured_patch_count = len(cie_labels)

    # --- Filter labels that truly exist in defined chart areas ---
    explicit_labels = set()
    for area in areas:
        labels_x = generate_labels(area['xstart'], area['xend'])
        labels_y = generate_labels(area['ystart'], area['yend'])
        # If there’s only one row and label is '-', suppress it entirely
#        if len(labels_y) == 1 and labels_y[0] == '-':
#            labels_y = ['_']  # placeholder indicating “no row label”
        # If there’s only one column and label is '-', suppress it entirely
#        if len(labels_x) == 1 and labels_x[0] == '-':
#            labels_x = ['_']  # placeholder indicating “no row label”
            
        for rlabel in labels_y:
            for clabel in labels_x:
                sid = f"{rlabel}{clabel}" if (rlabel and clabel) else (clabel or rlabel)
                explicit_labels.add(sid.upper())

    truly_missing = sorted([m for m in missing_labels if m in explicit_labels])

    # --- Suppress missing warnings if expected counts match ---
    if expected_cht_patches and expected_cie_patches:
        if expected_cht_patches == expected_cie_patches == measured_patch_count:
            truly_missing = []
        else:
            cie_field_name = "(unknown)"
            with open(cie_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line_up = line.strip().upper()
                    if "PATCHES_ACTIVE" in line_up:
                        cie_field_name = "PATCHES_ACTIVE"
                        break
                    elif "NUMBER_OF_SETS" in line_up:
                        cie_field_name = "NUMBER_OF_SETS"
                        break

            print("\n⚠️  Patch count mismatch:")
            print(f"   .cht EXPECTED XYZ:   {expected_cht_patches}")
            print(f"   .cie {cie_field_name}: {expected_cie_patches}")
            print(f"   .cie measured:        {measured_patch_count}")
            if expected_cht_patches != expected_cie_patches:
                print("   → Warning: .cht and .cie disagree on expected patch count!")
            elif expected_cie_patches != measured_patch_count:
                print("   → Warning: .cie contains fewer measured patches than declared.")

    elif expected_cie_patches and expected_cie_patches == measured_patch_count:
        truly_missing = []

    # --- Print results ---
    if truly_missing:
        print("\n⚠️  Missing patch labels in .cie/.txt (only those actually defined in .cht):")
        for m in truly_missing[:50]:
            print("   ", m)
        if len(truly_missing) > 50:
            print(f"   ... and {len(truly_missing)-50} more")
    else:
        debug_print("\n✅  All patch labels accounted for (no missing patches detected).")
        
    # Diagnostics & verification prints
    def px2mm(px): return px / (used_dpi / 25.4)
    print()
    print(f"Saved: {outp}  ({W} x {H} px @ {used_dpi} dpi)  (mapping: {mapping_method})")
    debug_print(f"SX = {SX:.6f} px per .cht-unit, SY = {SY:.6f} px per .cht-unit (used_dpi={used_dpi})")
    debug_print(f"BOX_SHRINK (cht units): {box_shrink_units:.4f} -> applied shrink: {box_shrink_units*SX:.2f}px x {box_shrink_units*SY:.2f}px")
    debug_print(f"Margin applied around content: {page_margin_mm:.2f} mm -> {margin_px} px (offset_x={offset_x:.2f}, offset_y={offset_y:.2f}) at {used_dpi} dpi")

    debug_print("\n=== Fiducials (from .cht units -> px) ===")
    labels = ("Top-left","Top-right","Bottom-right","Bottom-left")
    for i, (xu,yu) in enumerate(fids_units):
        px, py = unit_to_px(xu, yu)
        debug_print(f" {labels[i]:>11}: .cht ({xu:.3f}, {yu:.3f}) -> px ({px+offset_x:.2f}, {py+offset_y:.2f}) -> mm ({px2mm(px+offset_x):.2f}, {px2mm(py+offset_y):.2f})")
    fxs = [unit_to_px(xu,yu)[0]+offset_x for xu,yu in fids_units]
    fys = [unit_to_px(xu,yu)[1]+offset_y for xu,yu in fids_units]
    span_h = max(fxs) - min(fxs); span_v = max(fys) - min(fys)
    debug_print(f" Fiducial span (px): H = {span_h:.2f} px ({px2mm(span_h):.2f} mm), V = {span_v:.2f} px ({px2mm(span_v):.2f} mm)")

    expected_h_300 = 1825.0; expected_v_300 = 1072.0
    expected_h = expected_h_300 * (used_dpi / 300.0)
    expected_v = expected_v_300 * (used_dpi / 300.0)
    debug_print(f" Reference fiducial span (scaled to target dpi): {expected_h:.2f} px (H) x {expected_v:.2f} px (V)")
    debug_print(f" Difference: H {span_h - expected_h:.2f} px, V {span_v - expected_v:.2f} px")

    debug_print("\n=== Areas extents (computed from X/Y area lines, origin is .cht (0,0)) ===")
    for area in areas:
        axis = area['axis']
        labels_x = generate_labels(area['xstart'], area['xend'])
        labels_y = generate_labels(area['ystart'], area['yend'])
        ncols = len(labels_x); nrows = len(labels_y)
        left_px = area['pre_x'] * SX + offset_x
        top_px = area['pre_y'] * SY + offset_y
        right_px = left_px + max(1, ncols) * area['tile_x'] * SX
        bottom_px = top_px + max(1, nrows) * area['tile_y'] * SY
        debug_print(f" Area axis={axis}: start labels X={area['xstart']}..{area['xend']} Y={area['ystart']}..{area['yend']}")
        debug_print(f"  pre (units) = ({area['pre_x']:.4f}, {area['pre_y']:.4f}), tile (units) = ({area['tile_x']:.4f}, {area['tile_y']:.4f}), post (units)=({area['post_x']:.4f},{area['post_y']:.4f})")
        debug_print(f"  pixel box: left {left_px:.2f}px ({px2mm(left_px):.2f}mm), top {top_px:.2f}px ({px2mm(top_px):.2f}mm), right {right_px:.2f}px ({px2mm(right_px):.2f}mm), bottom {bottom_px:.2f}px ({px2mm(bottom_px):.2f}mm)")
        debug_print(f"  counts: cols={ncols}, rows={nrows}")

    rep_area = None
    for area in areas:
        if area['axis'] == 'Y':
            rep_area = area; break
    if not rep_area:
        rep_area = areas[0]
    rep_tile_w_px = rep_area['tile_x'] * SX
    rep_tile_h_px = rep_area['tile_y'] * SY
    debug_print("\n=== Representative patch size (from area's tile_x/tile_y) ===")
    debug_print(f" Patch tile (px) area Y: width = {rep_tile_w_px:.2f} px ({px2mm(rep_tile_w_px):.2f} mm), height = {rep_tile_h_px:.2f} px ({px2mm(rep_tile_h_px):.2f} mm)")
    for area in areas:
        if area['axis'] == 'X':
            gs_h_px = area['tile_y'] * SY
            debug_print(f" Patch tile height (px) area X: {gs_h_px:.2f} px ({px2mm(gs_h_px):.2f} mm)")

    debug_print("\n=== Sample patch placements (first 12) ===")
    for i, (sid, bbox) in enumerate(sample_order_list[:12]):
        x0,y0,x1,y1 = bbox
        debug_print(f" {sid:6s}: box px ({x0},{y0})-({x1},{y1}) size {x1-x0}x{y1-y0} px")


    # --------------------
    # Debug: assigned patch colors (first N shown)
    # --------------------
    if color_debug_list:
        debug_print("\n=== Debug: assigned patch colors (first 50 shown) ===")
        for entry in color_debug_list[:50]:
            sid_dbg, rgbf, rgb16vals, bbox = entry
            debug_print(f" {sid_dbg:6s} -> RGBf {rgbf[0]:.4f},{rgbf[1]:.4f},{rgbf[2]:.4f}  RGB16 {rgb16vals[0]},{rgb16vals[1]},{rgb16vals[2]}  box {bbox}")
    else:
        debug_print("\n(No patch color assignments recorded.)")

    print("\nDone.\n")


# ---------------------------
# CLI
# ---------------------------
def main():
    p = argparse.ArgumentParser(description='Recreate target from .cht + .cie/IT8 (v8).')
    p.add_argument('cht', help='.cht file')
    p.add_argument('cie', help='.cie/.txt file')
    p.add_argument('out', help='output filename (prefer .tiff)')
    p.add_argument('--target_dpi', type=float, default=None, help='Output DPI: 100,200,300,600 etc. Default=None -> script uses detected A4-fit DPI as reference and renders at 300dpi to preserve physical size')
    p.add_argument('--font', type=str, default=None, help='TTF/TTC font path for exact text sizing')
#Not used
#    p.add_argument('--map-fids', type=str, default=None, help='Optional measured pixel fiducials x1,y1,x2,y2,x3,y3,x4,y4 (overrides units->px mapping with affine)')
    p.add_argument('--png', action='store_true', help='Also write a PNG preview')
    p.add_argument('--font_mm', type=float, nargs=2, metavar=('LABEL_MM','FOOTER_MM'), help='Label and footer text heights in mm. Example: --font_mm 2.0 2.0')
    p.add_argument('--background-color', dest='background_patch', type=str, help='Patch label whose color is used for the image background (e.g. GS10)')
    p.add_argument('--debug', action='store_true', help='Enable parser debug output')
#    p.add_argument(
#        "--color_space",
#        choices=["lab", "rgb", "xyz"],
#        default="lab",
#        help="Select color space to use from input data file (.cie/.txt). More than one may be present in data file.           FLAG may be lab, xyz or rgb. Default: lab"
#    )
    p.add_argument(
        "--color_space",
        choices=["lab", "xyz"],
        default="lab",
        help="Select color space to use from input data file (.cie/.txt). More than one may be present in data file.           FLAG may be lab, xyz (rgb not implemented). Default: lab"
    )
    p.add_argument(
        "--intent",
        choices=["absolute", "display"],
        default="display",
        help="Color rendering intent: 'absolute' = colorimetric reference (linear), "
             "'display' (default) = gamma-encoded preview for screen."
    )
    p.add_argument(
        "--label_axis_visible",
        action="append",
        metavar="AREA_NAME=FLAGS",
        help=(
            "Manual label visibility override per area. Can be added multiple time."
            "Example: --label_axis_visible X=B --label_axis_visible Y=RT. "
            "Flags can include L, T, R, B (Left, Top, Right, Bottom), NONE or ALL. "
        )
    )
    p.add_argument(
        "--margin",
        dest="page_margin_mm",
        type=float,
        default=15.0,
        help="Page margin in millimeters (default: 15.0 mm)"
    )
    args = p.parse_args()

    # make DEBUG_PARSE visible globally
    global DEBUG_PARSE
    DEBUG_PARSE = args.debug
    
    if not Path(args.cht).exists():
        print(f"Error: .cht file not found: {args.cht}", file=sys.stderr); sys.exit(2)
    if not Path(args.cie).exists():
        print(f"Error: .cie/.txt file not found: {args.cie}", file=sys.stderr); sys.exit(2)

#   map_fids = None
#   if args.map_fids:
#       try:
#           parts = [float(x.strip()) for x in args.map_fids.split(',')]
#           if len(parts) != 8:
#               raise ValueError()
#           map_fids = parts
#       except Exception:
#           print("Error parsing --map-fids. Provide 8 comma-separated numbers: x1,y1,x2,y2,x3,y3,x4,y4", file=sys.stderr)
#           sys.exit(2)

#    recreate(args.cht, args.cie, args.out, target_dpi=args.target_dpi,
#            font_path=args.font, map_fids=map_fids, output_png=args.png,
#            font_mm_tuple=args.font_mm, background_patch=args.background_patch,
#            color_space=args.color_space, intent=args.intent, 
#            label_axis_visible=args.label_axis_visible,
#            page_margin_mm=args.page_margin_mm
#           )
    recreate(args.cht, args.cie, args.out, target_dpi=args.target_dpi,
             font_path=args.font, output_png=args.png,
             font_mm_tuple=args.font_mm, background_patch=args.background_patch,
             color_space=args.color_space, intent=args.intent, 
             label_axis_visible=args.label_axis_visible,
             page_margin_mm=args.page_margin_mm
            )

if __name__ == '__main__':
    main()
