--------------------------------------------------------------------------------
        rectarg.py v1.0  —  Complete Reference and Usage Notes
--------------------------------------------------------------------------------
Author: Knut Larsson

Recreate a calibration target as an image from ArgyllCMS-style `.cht` + `.cie` 
pair. 

With a digital image with colors representing the physical calibration target one 
can do the following (and possibly more):
        - For Displays: One could compare display calibration on screen against 
                        the physical target directly.
        - For Printer:  One could print a clean target without scanning errors and 
                        compare printout of the target against physical target.
        - For Scanner:  Compare a scanned target using a calibrated profile against
                        original colors directly on screen.

Calibration targets are used for calibration of scanners and displays so 
that screen and scanned material look the same. Usually, those that sell 
Calibration Targets keep their original digital image for them self, for business 
reasons.

Examples of Targets can be found at:
Wolf Faust's IT8 targets (12641-1): 
http://www.targets.coloraid.de
LaserSoft's Advanced IT8 target (12641-2): 
https://www.silverfast.com/products-overview-products-company-lasersoft-imaging/it8-targets-for-scanner-calibration-profiling-for-predictable-brilliant-colors/

Specialized software and hardware are often used for calibration of displays and 
printers, but an open source alternative, which also is used by many professional 
software products, is ArgyllCMS (http://argyllcms.com/index.html). This python 
script allows anyone to create a digital image with the same colors that the 
pysical target has, which they bought.

This version of rectarg has been tested on **Wolf Faust**, **LaserSoft** and 
**Hutchcolor** target formats, automatically detecting and adapting column naming 
and patch positions. It attempts to faitfully reproduce the geometry, colors, 
fiducials, and text labels as defined by the .cht and .cie files.

Note!
For the LaserSoft ISO 12641-2 reflective chart, the ISO12641_2_1.cht file that
supplied by ArgyllCMS (available after installation) is used. And, LaserSoft
does not supply a .cie type file, but is created using the supplied reference 
.CxF file downloaded from the Silverfast website, and the ArgyllCMS command
cxf2ti3 Rnnnnnn.cxf Rnnnnnn

See information on ArgyleCMS https://argyllcms.com/doc/Scenarios.html#PS2
for various Types of test charts and if cie and cht files exist from them.
If some suppliers deliver propietary files and cie-type data reference file
will have to be made manually (not that much work). I that case, using the
format and names used by the Wolf Faust IT8.7/2 Target is the best bit for
rectarg to work proberly.

--------------------------------------------------------------------------------
KEY FEATURES
--------------------------------------------------------------------------------
• Parses `.cht` layout definitions:
  - Fiducials (`F` line)
  - Patch areas (`Y` and `X` lines)
  - Handles optional `XLIST` / `YLIST` fallback definitions

• Reads `.cie`, `.txt`, or IT8 reference data:
  - Supports both Wolf Faust (SAMPLE_ID) and LaserSoft (SAMPLE_LOC) formats
  - Automatically normalizes LAB field naming conventions (`L*`, `LAB_L`, etc.)

• Uses `.cht` coordinates directly (origin at 0,0) — no fiducial offset applied

• Renders color patches and optional grayscale rows (modeled on Wolf Faust Target):
  - Patch IDs automatically generated from label start/end tokens
  - LAB → XYZ (D50) → sRGB (D65 via Bradford) conversion
  - 16-bit integer RGB output ensures full precision

• Creates fiducial corner marks with DPI-scaled thickness and offset geometry

• Adds complete labeling:
  - Top and left patch labels, **plus mirrored labels on bottom and right sides**
  - Physical sizing in mm maintained via exact pixel scaling
  - Footer text block with origin, descriptor, manufacturer, and creation info
  - Text Font and Size can be specified for better fit ('--font' and '--font_mm')

• Background color can be set from any patch ID (`--background-color`)

• Outputs:
  - 16-bit RGB TIFF (via tifffile)
  - Optional 8-bit PNG preview
  - Embedded resolution metadata matches target DPI
  - Adds 15mm margin around generated target
  - If color label cannot be found/identified patch color defaults to gray.

• Debug mode (`--debug`) enables or suppresses detailed diagnostic output

--------------------------------------------------------------------------------
COMMAND LINE USAGE
--------------------------------------------------------------------------------

    For simplicity: Go to a folder in terminal. Place this script as well as 
    .cht and .cie file in folder. Run command as shown below.

    python3 rectarg.py <chart.cht> <data.cie> <output.tif>
        [--target_dpi DPI]
        [--font /path/to/font.ttf]
        [--font_mm LABEL_MM FOOTER_MM]
        [--background-color PATCH_ID]
        [--map-fids x1,y1,x2,y2,x3,y3,x4,y4]
        [--png]
        [--debug]

--------------------------------------------------------------------------------
EXAMPLES
--------------------------------------------------------------------------------

# Standard 300 DPI reconstruction for Wolf Faust IT8.7/2 target
python3 rectarg.py R230122W.cht R230122W.txt output_300dpi.tif --background-color GS10

# LaserSoft Advanced Color Calibration Target (sample files)
python3 rectarg.py R250715.cht R250715.cie output_300dpi.tif --background-color M33

# High-resolution 600 DPI render
python3 rectarg.py R230122W.cht R230122W.txt output_600dpi.tif --target_dpi 600

# Geometrically aligned output using measured fiducial pixels
python3 rectarg.py R230122W.cht R230122W.txt output_aligned.tif \
    --map-fids 94,94,1919,95,1918,1164,94,1166

# Custom font and text size (in mm)
python3 rectarg.py R230122W.cht R230122W.txt output_font.tif \
    --font /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf --font_mm 3.0 2.0

--------------------------------------------------------------------------------
ARGUMENTS
--------------------------------------------------------------------------------

Positional:
  <chart.cht>        Chart definition file (ArgyllCMS .cht)
  <data.cie>         Reference or measurement data (.cie, .txt, or IT8 format)
  <output.tif>       Output filename (16-bit TIFF)

Optional flags:
  --target_dpi DPI
        Output resolution. Defaults to auto-detected A4-fit DPI, scaled to 300 DPI.

        Physical chart size is preserved regardless of DPI choice.
        Supported reference scales: 72, 100, 200, 300, 600, 1200 DPI.

  --background-color PATCH_ID
        Use the specified patch’s color as the background (e.g. `GS10` (Wolf Faust), 
        `M33` (LaserSoft)).

  --font PATH
        TrueType/TTC/TTF font file for label and footer rendering. If not found,
        the script searches common system font paths (Palatino, Helvetica, Times, Arial, DejaVuSans).

  --font_mm LABEL_MM FOOTER_MM
        Physical text heights for patch labels and footer text (default = 2.0 mm each).

  --map-fids x1,y1,x2,y2,x3,y3,x4,y4
        Use measured fiducial pixel coordinates to fit an affine transformation
        (overrides standard scaling). Order: top-left, top-right, bottom-right, bottom-left.

  --png
        Also saves a PNG preview beside the TIFF output.

  --debug
        Enables detailed debug output for parser diagnostics, scaling, patch mapping,
        and color conversion verification. Normal mode prints minimal summary only.

--------------------------------------------------------------------------------
SCALING MODEL (unit → pixel)
--------------------------------------------------------------------------------

• Coordinates in the `.cht` file is used to find best match A4 format with dpi, 
  but scaled up or down to 300dpi if not specifed in the command arguments.
  The script dynamically rescales to the target DPI while preserving the
  physical chart dimensions.

• For known A4-fit DPIs (72, 100, 200, 300, 600, 1200), scaling is derived from exact
  A4 dimensions to maintain consistent physical proportions.

• If 100dpi is detected, scaling factor is calulated in reference to 300 DPI:
      scale_x ≈ 2.9988 px/unit
      scale_y ≈ 3.0009 px/unit
  → Each 25.625 unit patch (at 100dpi) becomes ≈ 77×77 px (≈ 6.52 mm per side)

--------------------------------------------------------------------------------
FIDUCIAL MARKS
--------------------------------------------------------------------------------

• Defined by `F` lines in `.cht` file as four coordinate pairs (clockwise from top-left)
• Drawn as L-shaped corner marks; size and line thickness scale with DPI
  (≈ 5 px at 300 DPI)
• Used to verify geometry, or (with `--map-fids`) to warp to measured pixel locations

--------------------------------------------------------------------------------
PATCH AREA DEFINITIONS (Y and X lines)
--------------------------------------------------------------------------------

• “Y” area defines the main color patch grid (rows × columns)
• “X” area defines a second patch grid set

Syntax example, from Wolf Faust Target:
    Y 01 22 A L 25.625 25.625 26.625 26.625 25.625 25.625
    X GS00 GS23 _ _ 25.625 51.25 1.0 360.5 25.625 0

Interpreted as:
    [xstart, xend, ystart, yend, tile_x, tile_y, pre_x, pre_y, post_x, post_y]

  • Labels:
      - Numeric [xstart, xend]: 01–22 → “01”…“22”
      - Alphabetic [ystart, yend]: A–L → “A”…“L”
      - Prefixed [xstart, xend]: GS00–GS23 → “GS00”…“GS23”
      - “_” disables labels for that axis

  • Grid defining coordinates:
      - [tile_x, tile_y]: Pixel units (at a given dpi defined by originator) 
        for color patch.
      - [pre_x, pre_y]: Chart area padding. Pixcel units from reference (0,0) where first patch is 
        placed.
      - [post_x, post_y]: Chart area padding. Pixel units added in x direction 
        after last column for the specifed patch grid area, and added in y direction 
        after last row placement.

• Each patch ID (e.g. A01) is matched to corresponding data in `.cie`. Supports
  recognition of label differences, such as A1 vs A01, or with or without quotes
  (A1 vs "A1").

--------------------------------------------------------------------------------
COLOR CONVERSION
--------------------------------------------------------------------------------

• Preferred data columns: LAB_L / LAB_A / LAB_B  
  Fallbacks: “L*”, “A*”, “B*” or equivalent variants.

• Conversion pipeline:
      LAB (D50) → XYZ (D50) → XYZ (D65 via Bradford) → sRGB (IEC 61966-2-1)

• Resulting RGB values are clipped to [0–1] and scaled to 16-bit integers.

--------------------------------------------------------------------------------
LABELS AND TEXT
--------------------------------------------------------------------------------

• All labels use physical mm height conversion based on target DPI.  
  Example: 2.0 mm → 24 px at 300 DPI.

• Patch grid labels, depending on cht file definition:
    For Wolf Faust and Lasersoft Targets:
    - Columns (numbers) → top + bottom
    - Rows (letters) → left + right

• Footer block includes:
    - CREATED date (if available)
    - Data file name
    - Center text: “Reproduction of Target from reference data”
    - ORIGINATOR, DESCRIPTOR, and MANUFACTURER fields (right-aligned)

--------------------------------------------------------------------------------
OUTPUT
--------------------------------------------------------------------------------

• Default: 16-bit RGB TIFF (with DPI metadata)
• Fallback: 8-bit PNG (if `tifffile` is unavailable)
• Optional: `.preview.png` created if `--png` flag is used

--------------------------------------------------------------------------------
DIAGNOSTICS
--------------------------------------------------------------------------------

Normal mode:
    Prints summary lines for detected DPI, scaling, background patch, footer size,
    and save confirmation.

Debug mode (`--debug`):
    Prints detailed breakdowns of:
      - Chart scaling and unit conversions
      - Fiducial locations (unit → px → mm)
      - Area geometry and patch counts
      - Representative patch dimensions
      - Sample patch placements (first 12)
      - Assigned patch RGB values (first 50)
      - Any missing patch labels or data mismatches

Required dependencies:
      numpy, Pillow (PIL), tifffile, argparse
    Optional:
      scipy (for advanced interpolation)

To install all dependencies:
      pip install numpy Pillow tifffile argparse scipy

--------------------------------------------------------------------------------
NOTES
--------------------------------------------------------------------------------

• Compatible with Wolf Faust IT8.7/2, LaserSoft and Hutchcolor target data files 
• Automatically corrects for LAB/RGB field naming differences  
• Accurately preserves patch layout, margins, and fiducial geometry  
• Ideal for verification, visualization, or reprinting reference targets  

--------------------------------------------------------------------------------
