--------------------------------------------------------------------------------
rectarg.py v1.1 — Complete Reference and Usage Notes
--------------------------------------------------------------------------------
Author: Knut Larsson

Recreate a calibration target as an image from ArgyllCMS-style `.cht` + `.cie` 
pair, that preserve the target’s colorimetric values and physical sizing for 
printing and display softproofing. The tool implements color conversions 
(LAB → XYZ (D50) → sRGB (D65 via Bradford)), renders fiducials, labels, exact 
patch geometry, and supports options for DPI, text sizing, mapping fiducials, 
and color intent.

Calibration targets are used for calibration of scanners and displays so 
that screen and scanned material look the same. Usually, those that sell 
Calibration Targets keep their original digital image for them self, for business 
reasons.

With a digital image with colors representing the physical calibration target one 
can do the following (and possibly more): 
  - For Displays: One could compare display calibration on screen against the physical
    target directly.
  - For Printer: One could print a clean target without scanning errors and compare
    printout of the target against physical target.
  - For Scanner: Compare a scanned target using a calibrated profile against original
    colors directly on screen.

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

This version of rectarg has been tested on the following targets
  - Wolf Faust IT8.7/2 Targets (12641-1)
  - LaserSoft Advanced Color Calibration Target IT8 (12641-2)
  - CMP_Digital_Target-4 Target
  - Hutchcolor HCT
  - LaserSoft DCPro Studio Target
  - QPcard_202 Target
  - SpyderChecker Target
  - SpyderChecker24 Target

There is a good chance rectarg may be used successfully on other cht cie file, 
however ColorCheckerPassport is not supported, as cht file has parametes that this
script is not designed for yet.

The script automatically detects and adapts column naming and patch positions. 
It attempts to faitfully reproduce the geometry, colors, fiducials, and text 
labels as defined by the .cht and .cie files. If margins, font size or axis 
labels are not positioned well, these parameters can be modified manually, 
to experiment with best visal fit. rectarg has been designed according the 
assumption that fiducials should be placed outside of the row and column labels
normally around the color patch area. When moving fiducels by changing the 
cht file specificaiton lines placement of text may clash with fiducials or 
labels if not adhering to this rule.

Note!
For the LaserSoft ISO 12641-2 reflective chart, the ISO12641_2_1.cht file that
supplied by ArgyllCMS (available after installation) is used. And, LaserSoft
does not supply a .cie type file, but is created using the supplied reference 
.CxF file downloaded from the Silverfast website, and the ArgyllCMS command
cxf2ti3 Rnnnnnn.cxf Rnnnnnn

If output comes as gray patches only, it is likely the cie file does not use
lab color space, which is defualt. Change to xyz with "--intent xyz". 

See information on ArgyleCMS https://argyllcms.com/doc/Scenarios.html#PS2
for various Types of test charts and if cie and cht files exist from them.
If some suppliers deliver propietary files and cie-type data reference file
will have to be made manually (not that much work). I that case, using the
format and names used by the Wolf Faust IT8.7/2 Target is the best bit for
rectarg to work proberly.

--------------------------------------------------------------------------------
Methods for Assigning / Converting to ICC Profiles
--------------------------------------------------------------------------------
In some use cases an ICC profile neds to be applied to an image. For these 
intances one may, for example, use one of the following applications:
  - ArgyllCMS
  - ImageMagic, or
  - Photoshop
  - Gimp (Open Source)
  - ColorSync Utility (Mac OS)

Examples:
1. macOS ColorSync Utility
  Assign Profile: changes declared space (no pixel change).
  Convert to Profile: colorimetrically converts pixel values.
  Use only for scans or proof conversions — not for rectarg outputs.
2. Adobe Photoshop
  Edit → Assign Profile… (only for untagged files).
  Edit → Convert to Profile… (for proof conversions).
3. GIMP (open source)
  Image → Color Management → Assign Color Profile…
  Image → Color Management → Convert to Color Profile…
  Use for scanner ICC assignments or proof conversions.

--------------------------------------------------------------------------------
Use Cases for Created Target Image
--------------------------------------------------------------------------------
Generally:
  - Use absolute intent image is colorimetric truth for numerical or colorimetric
    comparison only, like when measuring Lab values etc. Image is too dark for
    printing or comparison against physical reference target.
  - Use display intent image is visually faithful representation → for visual
    side-by-side comparison with the physical target or softproofing.

• If you want to produce a printable target that looks like the physical chart 
  (for visual comparison) you can do the following:
  Option 1: Use rectarg display intent image directly. Print it with color 
            management ON (normal sRGB → printer conversion through your 
            calibrated printer profile). That should yield a print that perceptually 
            matches the physical target, for comparison against original physical
            reference target.

  Option 2: Comparison of Printed Image against Soft-Proofing Image
            Create a soft-proofing image for on-screen comparison against a printed target.
            Use display-intent image from rectarg and apply a printer's ICC profile
            via an application to create the soft-proofing image, for example:

        # Example command using ImageMagic
        magic rectarg_image_display.tif -profile printer.icc rectarg_image_printproof.tif

        # Example command using ArgyllCMS, applying perceptual intent
        cctiff -i p -v printer.icm rectarg_image_display.tif rectarg_image_printproof.tif

• If you want to compare a scanned image of the reference target on-screen against
  created image from rectarg:
  Use rectarg display intent image directly. Compare against scanned image on-screen,
  assuming scanner uses calibrated icc/icm profile. If scanner output is raw, without
  any profile, then apply a scanner profile onto scanned image before comparing
  against rectarg display intent image.

• If you want to compare a calibrated display against physical reference target:
  Use rectarg display intent image directly, on the display that has color
  management ON (using its icc/icm profile). Then compare against physical target.

Overview:
| Use Case                       | Image Intent        | Already Tagged As | Should You Assign / Convert ICC? | Color Management Setting   | Purpose                               |
| ------------------------------ | ------------------- | ----------------- | -------------------------------- | -------------------------- | ------------------------------------- |
| **Display measurement**        | absolute            | linear sRGB       | ❌ No                             | System CM ON (monitor ICC) | Compare numeric accuracy              |
| **Display visual check**       | display             | sRGB (gamma 2.2)  | ❌ No                             | System CM ON               | Visual layout & color check           |
| **Printer visual comparison**  | display             | sRGB              | ✅ Convert through printer ICC    | Printer CM ON              | Match physical chart visually         |
| **Printer profiling**          | display             | —                 | —                                 | CM OFF                     | Use true device stimuli. Rectarg not considered try device stimuly, but try and see.               |
| **Scanner profiling**          | — (physical target) | —                 | -                                 | CM OFF                      | Build/verify scanner profile          |
| **Scanner visual comparison**  | display             | sRGB              | ❌ No                             | CM ON                      | Visual compare scan vs. target        |
| **Scanner numeric comparison** | absolute            | linear sRGB       | ❌ No                             | CM ON                      | Compare measured Lab vs. reference    |




--------------------------------------------------------------------------------
Provided CHT Files
--------------------------------------------------------------------------------
Most targets tested with this script were provided with the ArgyllCMS software,
and many of those have probably been made manually, as several had odd config-
urations and dummy data, which caused bad images by rectarg. 

For the purpose of generating nice looking images I have edited the definition 
part of several of the .cht files. Those that want to experiment with getting 
exact match of fiducials to original target may modify the cht file, or use those 
provided for a nice printout. Details on how to interpret the specification inside 
the cht file is provided further down.

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

• Renders multiple defined color patche areas (modeled on Wolf Faust Target, 
  LaserSoft Advanced Target and Christophe Métairie's Digital Target - 4):
  - LAB → XYZ (D50) → sRGB (D65 via Bradford) conversion
  - May use LAB, XYZ data in CIE file (RGB handling not implemented).
  - Keeps exact colorimetric data, for reference and calibration.
  - 16-bit integer RGB output ensures full precision

• Creates fiducial corner marks with DPI-scaled thickness and offset geometry

• Adds complete labeling:
  - Patch IDs automatically generated from label start/end tokens
  - Top and left patch labels, plus mirrored labels on bottom and right sides
  - Physical sizing in mm maintained via exact pixel scaling
  - Footer text block with origin, descriptor, manufacturer, and creation info
  - Text Font and Size can be specified for better fit ('--font' and '--font_mm')
  - Hides labels if two patch areas are too close to each other.
  - Required clearance between defined patch areas is calculated dynamically, 
    based on the maximum label size plus 2 mm buffer.
    That way: 
        - Column labels appear only if there’s at least (font_height + 2 mm) 
          vertical gap. If column labels are rotated, rotated label’s longest 
          dimension is used instead of font_height.
        - Row labels appear only if there’s at least (max_label_width + 2 mm) 
          horizontal gap. 

• Background color can be set from any patch ID (`--background-color`)

• Outputs:
  - 16-bit RGB TIFF (via tifffile)
  - Optional 8-bit PNG preview
  - Embedded resolution metadata matches target DPI
  - Adds 15mm margin around generated target, but may be adjusted.
  - If color label cannot be found/identified patch color defaults to gray.
  - Chose intent, for use as calibration reference (default) or viewing on display.

• Debug mode (`--debug`) enables or suppresses detailed diagnostic output

--------------------------------------------------------------------------------
COMMAND LINE USAGE
--------------------------------------------------------------------------------

    For simplicity: Go to a folder in terminal. Place this script as well as 
    .cht and .cie file in folder. Run command as shown below.

    python3 rectarg.py <chart.cht> <data.cie> <output.tif>
        [--target_dpi DPI]
        [--background-color PATCH_ID]
        [--intent INTENT]
        [--color_space FLAG]
        [--label_axis_visible AXIS_NAME=FLAG]
        [--margin PAGE_MARGIN_MM]
        [--font /path/to/font.ttf]
        [--font_mm LABEL_MM FOOTER_MM]
        [--map-fids x1,y1,x2,y2,x3,y3,x4,y4]
        [--png]
        [--debug]

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
        Use a specified patch’s color as the background by naming label reference 
        Example: `GS10` (Wolf Faust), `M33` (LaserSoft)).

  --intent INTENT
        Select color conversion for specific use.
        - 'absolute' (default): Calibration reference / technical validation (to compare 
          numerically or in color-managed software). Keeps exact colorimetric data, for reference 
          and calibration. Linear sRGB, 16-bit TIFF. D50→D65 adaptation only (no gamma), 
          no perceptual modification
        - 'display': Screen visualization / preview image (to look correct on a calibrated sRGB display). 
          Same adaptation, but with gamma encoding (nonlinear tone mapping), 16-bit TIFF with gamma.

  --color_space FLAG
        Select color space to use from input data file (.cie/.txt). More than one may be present in 
        data file. FLAG may be lab, xyz (rgb handling not implemented). Default: lab

  --label_axis_visible AXIS_NAME=FLAG
        Manual label visibility override per chart patch area defined in the CHT file.
        Flags can include L, T, R, B (Left, Top, Right, Bottom), NONE or ALL.
        Examples: --label_axis_visible X=B --label_axis_visible Y=RT 
                    Forces only bottom label for area X, as well as right and top labels for area Y
                  --label_axis_visible X=ALL	Forces all four sides to show labels for area X
                  --label_axis_visible X=NONE	Suppresses all labels for area X
                  --label_axis_visible Y=RT     Shows only right & top labels for area Y
                                                Unlisted areas	Continue to use automatic detection

  --margin PAGE_MARGIN_MM
        Page margin in millimeters (default: 15.0 mm)

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
EXAMPLES
--------------------------------------------------------------------------------
The following commands have been used to create a nice looking target, using sample 
cie and cht files. Use your own cie files to get a correct image for your target:

# Wolf Faust IT8.7/2 target for display
python3 rectarg.py R230122W.cht R230122W.txt output.tif --target_dpi 300 \
    --background GS10 --intent display --label_axis_visible X=B

# LaserSoft Advanced Color Calibration Target, Absolute Colorimetric.
python3 rectarg.py ISO12641_2_1.cht R250715.cie R250715_200dpi.tif \
    --background-color M33 --target_dpi 200

# Hutchcolor HCT, Absolute Colorimetric
python3 rectarg.py Hutchcolor.cht 0579.txt Hutchcolor-200dpi.tif \
    --target_dpi 200 --color_space xyz

# CMP_Digital_Target-4 target for display
python3 rectarg.py CMP_Digital_Target-4.cht CMP_Digital_Target-4.cie \
    CMP_Digital_Target-4-200dpi.tif --target_dpi 200 --color_space xyz \
    --intent display --label_axis_visible X=TRB

# LaserSoft DCPro Studio Target for display
python3 rectarg.py LaserSoftDCPro.cht D120104.txt LaserSoftDCPro-200dpi.tif \
    --target_dpi 200 --intent display --font_mm 1 1 --margin 7

# QPcard_202 Target, Absolute Colorimetric
python3 rectarg.py QPcard_202.cht QPcard_202.cie QPcard_202-200dpi.tif \
    --target_dpi 200 --font_mm 2.5 2.5

# SpyderChecker Target, Absolute Colorimetric
python3 rectarg.py SpyderChecker.cht SpyderChecker.cie SpyderChecker-200dpi.tif \
    --target_dpi 200 --color_space xyz

# SpyderChecker24, Absolute Colorimetric
python3 rectarg.py SpyderChecker24.cht SpyderChecker24.cie SpyderChecker24-200dpi.tif \
    --target_dpi 200 --color_space xyz

# Wolf Faust IT8.7/2 target with custom font and text size (in mm)
python3 rectarg.py R230122W.cht R230122W.txt output_font.tif \
    --font /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf --font_mm 3.0 2.0

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
Full Chart Definition
--------------------------------------------------------------------------------

The line defined by 'D' at the start of the line, in the cht file, may look like this:
D ALL ALL _ _ 613 433 49.0 33.0 0 0

The two first numbers shown here usually depict the full size of the complete 
chart. These numbers must be calculated and provided, else the rectarg script may 
give odd output, missing rows etc. However, the main defining area of the image
generated is the fiducial positions and the Patch Area definitions.

--------------------------------------------------------------------------------
PATCH AREA DEFINITIONS (Y and X lines)
--------------------------------------------------------------------------------

• “Y” area defines the main color patch grid (rows × columns)
• “X” area defines a second patch grid set

Several patch areas are supported, but it is preferred they have individual names.

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
  (A1 vs "A1"), or special labels with preceding number, like "2A1".

--------------------------------------------------------------------------------
COLOR CONVERSION
--------------------------------------------------------------------------------

• Default data columns from cie file: LAB_L / LAB_A / LAB_B  
  Fallbacks: “L*”, “A*”, “B*” or equivalent variants. 
  Alterntively, data columns can be selected to use XYZ columns.

• Conversion pipeline:
      LAB (D50) → XYZ (D50) → XYZ (D65 via Bradford) → sRGB (IEC 61966-2-1)

• Resulting RGB values are not clipped or manipulated to preserve true reference 
  colors.

--------------------------------------------------------------------------------
LABELS AND TEXT
--------------------------------------------------------------------------------

• All labels use physical mm height conversion based on target DPI.  
  Example: 2.0 mm → 24 px at 300 DPI.

• Patch grid labels, depending on cht file definition:
  By default column and row labels are placed on all sides of a patch area.
  This can be configured by --label_axis_visible AXIS_NAME=FLAG

• Footer block includes:
    - 'CREATED' date (if available)
    - Data file name
    - Center text: “Reproduction of Target from reference data”
    - 'ORIGINATOR', 'DESCRIPTOR', and 'MANUFACTURER' fields (right-aligned)
  Some files converted by AryllCMS tools to cie type may use very different 
  defining parameter names for the above. To get the info displayed correctly
  with rectarg you should rename the appropriate parameter according names 
  mentioned above. Those are based on parameters used in Wolf Faust IT8.7/2 Target

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
    Prints summary lines for detected DPI, background patch, and save confirmation.

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
