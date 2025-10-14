--------------------------------------------------------------------------------
rectarg.py v1.0  —  Complete Reference and Usage Notes
--------------------------------------------------------------------------------
Author: Knut Larsson with support from ChatGPT

Recreate a calibration target as an image from ArgyllCMS-style `.cht` + `.cie` pair.

This version has been tested on **Wolf Faust**, **LaserSoft** and **Hutchcolor**
target formats, automatically detecting and adapting column naming differences
(e.g., SAMPLE_ID/SAMPLE_LOC vs. SAMPLE_ID/SAMPLE_NAME). It reproduces the
geometry, colors, fiducials, and text labels exactly as defined by the .cht file.

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

• Renders color patches and optional grayscale rows:
  - Patch IDs automatically generated from label start/end tokens
  - LAB → XYZ (D50) → sRGB (D65 via Bradford) conversion
  - 16-bit integer RGB output ensures full precision

• Creates fiducial corner marks with DPI-scaled thickness and offset geometry

• Adds complete labeling:
  - Top and left patch labels, **plus mirrored labels on bottom and right sides**
  - Physical sizing in mm maintained via exact pixel scaling
  - Footer text block with origin, descriptor, manufacturer, and creation info

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
    .cht and cie file in folder. Run command as shown below.

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
python3 rectarg.py R230122W.cht R230122W.txt output_300dpi.tif \
    --background-color GS10

# LaserSoft Advanced Color Calibration Target (sample files)
python3 rectarg.py R250715.cht R250715.cie output_300dpi.tif \
    --background-color M33

# High-resolution 600 DPI render
python3 rectarg.py R230122W.cht R230122W.txt output_600dpi.tif \
    --target_dpi 600

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
        Use the specified patch’s color as the background (e.g. `GS10`, `M33`).

  --font PATH
        TrueType/TTC font file for label and footer rendering. If not found,
        the script searches common system font paths (DejaVuSans, Helvetica, Arial).

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

• All coordinates in the `.cht` are defined in **100-DPI units**.
  The script dynamically rescales these to the target DPI while preserving the
  physical chart dimensions.

• For known A4-fit DPIs (72, 100, 200, 300, 600, 1200), scaling is derived from exact
  A4 dimensions to maintain consistent physical proportions.

• Example at 300 DPI:
      scale_x ≈ 2.9988 px/unit
      scale_y ≈ 3.0009 px/unit
  → Each 25.625 unit patch becomes ≈ 77×77 px (≈ 6.52 mm per side)

--------------------------------------------------------------------------------
FIDUCIAL MARKS
--------------------------------------------------------------------------------

• Defined by `F` lines in `.cht` as four coordinate pairs (clockwise from top-left)
• Drawn as L-shaped corner marks; size and line thickness scale with DPI
  (≈ 5 px at 300 DPI)
• Used to verify geometry, or (with `--map-fids`) to warp to measured pixel locations

--------------------------------------------------------------------------------
PATCH AREA DEFINITIONS (Y and X lines)
--------------------------------------------------------------------------------

• “Y” area defines the main color patch grid (rows × columns)
• “X” area usually defines grayscale strips or supplementary rows

Syntax example:
    Y 01 22 A L 25.625 25.625 26.625 26.625 25.625 25.625
    X GS00 GS23 _ _ 25.625 51.25 1.0 360.5 25.625 0

Interpreted as:
    [xstart, xend, ystart, yend, tile_x, tile_y, pre_x, pre_y, post_x, post_y]

• Labels:
    - Numeric: 01–22 → “01”…“22”
    - Alphabetic: A–L → “A”…“L”
    - Prefixed: GS00–GS23 → “GS00”…“GS23”
    - “_” disables labels for that axis

• Each patch ID (e.g. A01) is matched to corresponding data in `.cie`.

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
