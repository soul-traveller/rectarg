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

**End of README**
