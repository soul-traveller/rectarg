#!/usr/bin/env python3

"""
================================================================================
        rectarg.py v1.0  —  Complete Reference and Usage Notes
================================================================================
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

================================================================================
"""


#!/usr/bin/env python3
from pathlib import Path
import re, math, argparse, sys, os, fnmatch
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

    # F line (first line starting with 'F ')
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

    mbs = re.search(r'(?mi)^\s*BOX_SHRINK\s+([-+]?\d*\.?\d+)', txt)
    if mbs:
        out['box_shrink'] = float(mbs.group(1))

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

    area_re = re.compile(r'(?mi)^[ \t]*([XY])\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+((?:[-+]?\d*\.?\d+\s+){5}[-+]?\d*\.?\d+)', flags=re.M)
    for m in area_re.finditer(txt):
        axis = m.group(1).upper()
        xstart = m.group(2)
        xend = m.group(3)
        ystart = m.group(4)
        yend = m.group(5)
        nums = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', m.group(6))]
        if len(nums) != 6:
            rest = m.group(0).split()[5:]
            nums = []
            for tok in rest:
                try:
                    nums.append(float(tok))
                except:
                    pass
        if len(nums) != 6:
            continue
        area = {
            'axis': axis,
            'xstart': xstart, 'xend': xend,
            'ystart': ystart, 'yend': yend,
            'tile_x': nums[0], 'tile_y': nums[1],
            'pre_x': nums[2], 'pre_y': nums[3],
            'post_x': nums[4], 'post_y': nums[5]
        }
        out['areas'].append(area)

    return out

def parse_it8_or_cie(path):
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
                if re.match(r'^[A-Z]+\d+$', candidate, flags=re.I) or re.match(r'^(GS\d+)$', candidate, flags=re.I):
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

    # Normalize into map form for quick lookup
    data_map = {}
    for sid, vals in data:
        data_map[sid.upper()] = {
            "vals": vals,
            "iL": idxL,
            "iA": idxA,
            "iB": idxB,
            "iR": idxR,
            "iG": idxG,
            "iB_rgb": idxB_rgb
        }

    # --- Optional debug output for verifying column detection ---
    if globals().get("DEBUG_PARSE", False):
        debug_print(f"[Debug] Detected LAB column indices: L={idxL}, A={idxA}, B={idxB}")
        # print one example record
        if data_map:
            sample_key = next(iter(data_map))
            vals = data_map[sample_key]["vals"]
            debug_print(f"[Debug] Example entry: {sample_key} -> LAB=({vals[idxL] if idxL is not None else 'N/A'}, "
                  f"{vals[idxA] if idxA is not None else 'N/A'}, "
                  f"{vals[idxB] if idxB is not None else 'N/A'})")

    return fmt, data_map, header

# ---------------------------
# Color conversion functions
# ---------------------------
def lab_to_xyz(L, a, b):
    fy = (L + 16.0) / 116.0
    fx = fy + a / 500.0
    fz = fy - b / 200.0
    d = 6.0 / 29.0
    def invf(t):
        return t**3 if t > d else 3*(d**2)*(t - 4.0/29.0)
    xr, yr, zr = invf(fx), invf(fy), invf(fz)
    return xr * 0.96422, yr * 1.0, zr * 0.82521

def xyz_d50_to_srgb(X, Y, Z):
    M = np.array([[0.8951, 0.2664, -0.1614],
                  [-0.7502, 1.7135, 0.0367],
                  [0.0389, -0.0685, 1.0296]])
    Mi = np.linalg.inv(M)
    D50 = np.array([0.96422, 1.0, 0.82521])
    D65 = np.array([0.95047, 1.0, 1.08883])
    src = M @ D50
    dst = M @ D65
    adapt = Mi @ np.diag(dst / src) @ M
    X_a, Y_a, Z_a = adapt @ np.array([X, Y, Z])
    M2 = np.array([[ 3.2406, -1.5372, -0.4986],
                   [-0.9689,  1.8758,  0.0415],
                   [ 0.0557, -0.2040,  1.0570]])
    rgb_lin = M2 @ np.array([X_a, Y_a, Z_a])
    def comp_gamma(u):
        if u <= 0.0:
            return 0.0
        if u <= 0.0031308:
            return 12.92 * u
        else:
            return 1.055 * (u ** (1.0/2.4)) - 0.055
    rgb = np.array([comp_gamma(v) for v in rgb_lin])
    return np.clip(rgb, 0.0, 1.0)

# ---------------------------
# Helpers: labels and geometry
# ---------------------------
def generate_labels(start_tok, end_tok):
    if start_tok == '_' or end_tok == '_':
        return []
    s = start_tok.strip()
    e = end_tok.strip()
    m1 = re.match(r'(?i)GS(\d+)$', s)
    m2 = re.match(r'(?i)GS(\d+)$', e)
    if m1 and m2:
        a = int(m1.group(1)); b = int(m2.group(1))
        return [f"GS{idx:02d}" for idx in range(a, b+1)]
    if re.match(r'^\d+$', s) and re.match(r'^\d+$', e):
        a = int(s); b = int(e)
        width = max(len(s), len(e))
        fmt = f"0{width}d"
        return [format(idx, fmt) for idx in range(a, b+1)]
    if re.match(r'^[A-Za-z]$', s) and re.match(r'^[A-Za-z]$', e):
        a = ord(s.upper()); b = ord(e.upper())
        return [chr(i) for i in range(a, b+1)]
    return [s] if s == e else [s, e]

def compute_canvas_extents_from_areas(areas, sx, sy):
    minx = float('inf'); miny = float('inf'); maxx = -float('inf'); maxy = -float('inf')
    for area in areas:
        cols = generate_labels(area['xstart'], area['xend'])
        rows = generate_labels(area['ystart'], area['yend'])
        ncols = len(cols) if cols else 0
        nrows = len(rows) if rows else 0
        left_px = 0.0 + area['pre_x'] * sx
        top_px = 0.0 + area['pre_y'] * sy
        right_px = left_px + (ncols * area['tile_x'] * sx) if ncols else left_px + (area['tile_x'] * sx)
        bottom_px = top_px + (nrows * area['tile_y'] * sy) if nrows else top_px + (area['tile_y'] * sy)
        minx = min(minx, left_px); miny = min(miny, top_px)
        maxx = max(maxx, right_px); maxy = max(maxy, bottom_px)
    if minx == float('inf'):
        return 0,0,0,0
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

def detect_best_a4_dpi(chart_px_w, chart_px_h, margin_mm=15.0):
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
# ---------------------------
# Main rendering function
# ---------------------------
def recreate(cht_path, cie_path, out_path, target_dpi=DEFAULT_TARGET_DPI,
             font_path=None, map_fids=None, output_png=False, font_mm_tuple=None,
             background_patch=None):
    cht = parse_cht(cht_path)
    # parse CIE/IT8 file
    fmt, data_map, header = parse_it8_or_cie(cie_path)

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

    def normalize_sid(sid: str) -> str:
        """
        Normalize IDs to handle differences like A1 <-> A01 or GS1 <-> GS01.
        Returns canonical uppercase form (unpadded single digit).
        """
        sid = sid.strip().upper()
        # Normalize GS patches first
        sid = re.sub(r"^GS0?([0-9]+)$", r"GS\1", sid)
        # Normalize generic letter-number pairs (A01 -> A1, A001 -> A1)
        sid = re.sub(r"^([A-Z]+)0+([0-9]+)$", r"\1\2", sid)
        return sid

    # ---------- helper: find normalized entry for a SID (nested so it can see data_map) ----------
    def find_vals_for_sid(sid):
        """
        Return normalized entry dict or None.
        Tries all reasonable label variants (A1 ↔ A01 ↔ A001, GS1 ↔ GS01, etc.)
        """
        if not sid:
            return None
        s = str(sid).strip().upper()

        # Direct match
        if s in data_map:
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
    detected_dpi = detect_best_a4_dpi(chart_units_w, chart_units_h, margin_mm=15.0)
    user_specified_dpi = (target_dpi is not None)

    # If user specified a target DPI, use that; otherwise default to 300
    used_dpi = float(target_dpi) if user_specified_dpi else 300.0

    # Print diagnostic info
    debug_print(f"Detected native chart DPI (fit to A4): {detected_dpi} dpi. ", end="")
    if user_specified_dpi:
        debug_print(f"Requested target_dpi={used_dpi} dpi.")
    else:
        debug_print(f"No target_dpi specified -> rendering at {used_dpi} dpi by default (preserve physical size).")

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
    if map_fids is not None:
        parts = map_fids
        if len(parts) != 8:
            raise ValueError("--map-fids requires 8 numbers")
        dst = [(parts[i], parts[i+1]) for i in range(0,8,2)]
        src = np.array(fids_units, dtype=float)
        dst_a = np.array(dst, dtype=float)
        if src.shape[0] >= 3:
            try:
                A = fit_affine(fids_units, dst)
                def unit_to_px_aff(xu, yu):
                    v = A @ np.array([xu, yu, 1.0])
                    return float(v[0]), float(v[1])
                unit_to_px = unit_to_px_aff
                mapping_method = 'affine_from_user_map'
            except Exception:
                pass

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

    margin_mm = 15.0
    margin_px = int(round(margin_mm * px_per_mm))
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
                iL = rec_bg.get("iL"); iA = rec_bg.get("iA"); iB = rec_bg.get("iB")
                if iL is not None and iA is not None and iB is not None:
                    L = float(vals_bg[iL]); A_ = float(vals_bg[iA]); B_ = float(vals_bg[iB])
                    X, Y, Z = lab_to_xyz(L, A_, B_)
                    rgbf = xyz_d50_to_srgb(X, Y, Z)
                else:
                    nums = [float(v) for v in vals_bg if isinstance(v, (int, float)) or re.match(r'^[-+]?[0-9]*\.?[0-9]+$', str(v))]
                    rgbf = np.array(nums[:3]) / 100.0 if len(nums) >= 3 else np.array([0.5, 0.5, 0.5])
                rgb16 = (np.clip(rgbf, 0.0, 1.0) * 65535.0).astype(np.uint16)
                canvas[:, :, :] = rgb16
                debug_print(f"Background filled from patch '{bg_label}' → RGB16 {tuple(int(v) for v in rgb16)}")
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

    def normalize_sid(sid: str) -> str:
        """Normalize IDs like A1→A01, GS9→GS09, ensures consistency between .cht and .cie."""
        m = re.match(r"^([A-Za-z]+)(\d+)$", sid.strip())
        if m:
            prefix, num = m.groups()
            return f"{prefix.upper()}{int(num):02d}"
        return sid.strip().upper()


    # --------------------
    # Paint patches with integer-distribution widths (prevents last-column runaway)
    # --------------------
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

        if axis == 'Y':
            # compute total continuous width/height
            total_w = ncols * tile_x * SX if ncols > 0 else tile_x * SX
            total_h = nrows * tile_y * SY if nrows > 0 else tile_y * SY

            # integer width distribution
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

            for r_idx, rlabel in enumerate(labels_y):
                for c_idx, clabel in enumerate(labels_x):
                    sid = normalize_sid(f"{rlabel}{clabel}" if (rlabel and clabel) else (clabel or rlabel))
                    x0f = x_edges[c_idx]
                    x1f = x_edges[c_idx + 1]
                    y0f = y_edges[r_idx]
                    y1f = y_edges[r_idx + 1]
                    # no shrink here — handled visually only if needed

                    rec = find_vals_for_sid(sid.upper())
                    rgb = np.array([0.5, 0.5, 0.5])  # default mid-gray

                    if rec and rec.get("vals"):
                        vals = rec["vals"]
                        iL = rec.get("iL"); iA = rec.get("iA"); iB = rec.get("iB")
                        if iL is not None and iA is not None and iB is not None:
                            try:
                                L = float(vals[iL])
                                A_ = float(vals[iA])
                                B_ = float(vals[iB])
                                X, Y, Z = lab_to_xyz(L, A_, B_)
                                rgb = xyz_d50_to_srgb(X, Y, Z)
                            except Exception:
                                pass
                        elif len(vals) >= 3:
                            # fallback: assume first 3 are normalized RGB (rare case)
                            try:
                                rgb = np.array([float(v) for v in vals[:3]])
                                if np.max(rgb) > 1.5:  # if 0–255 scale
                                    rgb /= 255.0
                            except Exception:
                                pass
                    else:
                        missing_labels.add(sid.upper())
                        rgb = np.array([0.5,0.5,0.5])

                    rgb16 = (np.clip(rgb,0.0,1.0) * 65535.0).astype(np.uint16)

                    x0c = max(0, min(W, x0f)); x1c = max(0, min(W, x1f))
                    y0c = max(0, min(H, y0f)); y1c = max(0, min(H, y1f))
                    if x1c > x0c and y1c > y0c:
                        canvas[y0c:y1c, x0c:x1c, 0] = int(rgb16[0])
                        canvas[y0c:y1c, x0c:x1c, 1] = int(rgb16[1])
                        canvas[y0c:y1c, x0c:x1c, 2] = int(rgb16[2])
                    sample_order_list.append((sid.upper(), (x0c,y0c,x1c,y1c)))
                    color_debug_list.append((sid.upper(), tuple(map(float, rgb)), tuple(map(int, rgb16)), (x0c,y0c,x1c,y1c)))

        elif axis == 'X':
            total_w = ncols * tile_x * SX if ncols > 0 else tile_x * SX
            total_h = tile_y * SY

            if ncols > 0:
                base_w = int(math.floor(total_w / ncols))
                remainder_w = int(round(total_w - base_w * ncols))
                widths = [base_w + (1 if i < remainder_w else 0) for i in range(ncols)]
                x_edges = [int(round(start_x_px))]
                for w in widths:
                    x_edges.append(x_edges[-1] + w)
            else:
                x_edges = [int(round(start_x_px)), int(round(start_x_px + total_w))]

            y0i = int(round(start_y_px)); y1i = int(round(start_y_px + total_h))

            for c_idx, clabel in enumerate(labels_x):
                sid = normalize_sid(clabel)
                x0f = x_edges[c_idx]; x1f = x_edges[c_idx+1]
                x0f = int(round(x_edges[c_idx]))
                x1f = int(round(x_edges[c_idx + 1]))
                # GS strip occupies its own full height (tile_y * SY) starting at start_y_px
                y0f = int(round(start_y_px))
                y1f = int(round(start_y_px + tile_y * SY))

                rec = find_vals_for_sid(sid.upper())
                rgb = np.array([0.5, 0.5, 0.5])  # default mid-gray

                if rec and rec.get("vals"):
                    vals = rec["vals"]
                    iL = rec.get("iL"); iA = rec.get("iA"); iB = rec.get("iB")
                    if iL is not None and iA is not None and iB is not None:
                        try:
                            L = float(vals[iL])
                            A_ = float(vals[iA])
                            B_ = float(vals[iB])
                            X, Y, Z = lab_to_xyz(L, A_, B_)
                            rgb = xyz_d50_to_srgb(X, Y, Z)
                        except Exception:
                            pass
                    elif len(vals) >= 3:
                        try:
                            rgb = np.array([float(v) for v in vals[:3]])
                            if np.max(rgb) > 1.5:
                                rgb /= 255.0
                        except Exception:
                            pass
                else:
                    missing_labels.add(sid.upper())
                    rgb = np.array([0.5,0.5,0.5])
                rgb16 = (np.clip(rgb,0.0,1.0) * 65535.0).astype(np.uint16)
                x0c = max(0, min(W, x0f)); x1c = max(0, min(W, x1f))
                y0c = max(0, min(H, y0f)); y1c = max(0, min(H, y1f))
                if x1c > x0c and y1c > y0c:
                    canvas[y0c:y1c, x0c:x1c, 0] = int(rgb16[0])
                    canvas[y0c:y1c, x0c:x1c, 1] = int(rgb16[1])
                    canvas[y0c:y1c, x0c:x1c, 2] = int(rgb16[2])
                sample_order_list.append((sid, (x0c,y0c,x1c,y1c)))
                color_debug_list.append((sid, tuple(map(float, rgb)), tuple(map(int, rgb16)), (x0c,y0c,x1c,y1c)))
        else:
            continue

    # --------------------
    # Annotations: fiducials and labels
    # --------------------
    annot = Image.new('L', (W, H), 255)
    draw = ImageDraw.Draw(annot)

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
                # case-insensitive pattern search
                for fn in font_names:
                    for fx in pd.glob("**/*"):
                        if fx.is_file() and fx.name.lower() == fn.lower():
                            chosen_font = str(fx)
                            break
                    if chosen_font:
                        break
            if chosen_font:
                break
        # last-resort: try PIL default TTF names
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

    # Draw labels using render_text_exact_height for consistent physical size
    for area in areas:
        axis = area['axis']
        labels_x = generate_labels(area['xstart'], area['xend'])
        labels_y = generate_labels(area['ystart'], area['yend'])
        tile_x = area['tile_x']; tile_y = area['tile_y']
        start_x_px = area['pre_x'] * SX + offset_x
        start_y_px = area['pre_y'] * SY + offset_y
        if axis == 'Y' and labels_x and labels_y:
            for c_idx, clabel in enumerate(labels_x):
                cx = start_x_px + (c_idx + 0.5) * tile_x * SX
                tile_w_px = tile_x * SX
                max_letter_h = max(1, int(round(0.9 * tile_w_px)))
                label_h_px = min(label_px_target, max_letter_h)
                txt_img = render_text_exact_height(clabel, chosen_font, label_h_px, scale_factor=4)
                tw, th = txt_img.size
                x_text = int(round(cx - tw/2.0))
                y_text = int(round(start_y_px - label_gap_px - th))
                annot.paste(Image.new('L', txt_img.size, 0), (x_text, y_text), mask=txt_img)

            for r_idx, rlabel in enumerate(labels_y):
                cy = start_y_px + (r_idx + 0.5) * tile_y * SY
                tile_w_px = tile_x * SX
                max_letter_h = max(1, int(round(0.9 * tile_w_px)))
                label_h_px = min(label_px_target, max_letter_h)
                txt_img = render_text_exact_height(rlabel, chosen_font, label_h_px, scale_factor=4)
                tw, th = txt_img.size
                x_text = int(round(start_x_px - label_gap_px - tw))
                y_text = int(round(cy - th/2.0))
                annot.paste(Image.new('L', txt_img.size, 0), (x_text, y_text), mask=txt_img)

        elif axis == 'X' and labels_x:
            # --- Measure all GS label sizes to decide rotation mode ---
            test_imgs = [render_text_exact_height(lbl, chosen_font, label_px_target, scale_factor=4) for lbl in labels_x]
            widths = [im.size[0] for im in test_imgs]
            heights = [im.size[1] for im in test_imgs]
            tile_w_px = tile_x * SX
            tile_h_px = tile_y * SY
            max_letter_h = max(1, int(round(0.9 * tile_w_px)))

            need_rotate = any(w > 0.95 * tile_w_px or h > max_letter_h for w, h in zip(widths, heights))

            for c_idx, clabel in enumerate(labels_x):
                cx = start_x_px + (c_idx + 0.5) * tile_x * SX
                if need_rotate:
                    # Draw all vertically
                    txt_img_r = render_text_exact_height(clabel, chosen_font, label_px_target, scale_factor=4, rotate_deg=90)
                    tw, th = txt_img_r.size
                    x_text = int(round(cx - tw / 2.0))
                    y_text = int(round(start_y_px + (tile_h_px / 2.0) - th / 2.0))
                    x_text = max(0, min(W - tw, x_text))
                    y_text = max(0, min(H - th, y_text))
                    annot.paste(Image.new('L', txt_img_r.size, 0), (x_text, y_text), mask=txt_img_r)
                else:
                    # Draw all horizontal below patches
                    txt_img = test_imgs[c_idx]
                    w, h = txt_img.size
                    x_text = int(round(cx - w / 2.0))
                    y_text = int(round(start_y_px + tile_h_px + small_gap_px))
                    x_text = max(0, min(W - w, x_text))
                    y_text = max(0, min(H - h, y_text))
                    annot.paste(Image.new('L', txt_img.size, 0), (x_text, y_text), mask=txt_img)

    # --- Add right (letters) and bottom (numbers) labels ---
    for area in areas:
        axis = area['axis']
        if axis != 'Y':
            continue
        labels_x = generate_labels(area['xstart'], area['xend'])
        labels_y = generate_labels(area['ystart'], area['yend'])
        tile_x = area['tile_x']; tile_y = area['tile_y']
        start_x_px = area['pre_x'] * SX + offset_x
        start_y_px = area['pre_y'] * SY + offset_y

        # Rebuild x/y edges from known counts
        ncols = len(labels_x)
        nrows = len(labels_y)
        x_edges = [start_x_px + i * tile_x * SX for i in range(ncols + 1)]
        y_edges = [start_y_px + i * tile_y * SY for i in range(nrows + 1)]

        # --- Bottom numeric labels ---
        for c_idx, clabel in enumerate(labels_x):
            x_center = (x_edges[c_idx] + x_edges[c_idx + 1]) / 2
            y_bottom = int(round(y_edges[-1] + label_gap_px))
            txt_img = render_text_exact_height(clabel, chosen_font, label_px_target, scale_factor=4)
            w, h = txt_img.size
            px = int(round(x_center - w / 2))
            py = y_bottom
            annot.paste(Image.new('L', txt_img.size, 0), (px, py), mask=txt_img)

        # --- Right alphabetic labels ---
        for r_idx, rlabel in enumerate(labels_y):
            y_center = (y_edges[r_idx] + y_edges[r_idx + 1]) / 2
            x_right = int(round(x_edges[-1] + label_gap_px))
            txt_img = render_text_exact_height(rlabel, chosen_font, label_px_target, scale_factor=4)
            w, h = txt_img.size
            px = x_right
            py = int(round(y_center - h / 2))
            annot.paste(Image.new('L', txt_img.size, 0), (px, py), mask=txt_img)

                    
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

    # --- Header text: "Created by rectarg" (top-right area) ---
    # Determine top margin offset (10 mm from image top)
    header_y = int(round((8.0 / 25.4) * used_dpi))

    # Right reference: align to top-right fiducial outer edge
    if fids_px and len(fids_px) > 1:
        right_x_ref = fids_px[1][0]
    else:
        right_x_ref = W - margin_px

    right_x = int(round(right_x_ref))

    # Render the header text with same font logic as footer
    imhdr = render_text_exact_height("Created by rectarg",
                                     chosen_font,
                                     footer_font_px,   # same height control as footer
                                     scale_factor=4)
    tw, th = imhdr.size

    # Right-align header text with top-right fiducial
    px = int(round(right_x - tw))
    px = max(0, min(W - tw, px))  # clamp to image bounds
    py = header_y

    # Paste the rendered header
    annot.paste(Image.new('L', imhdr.size, 0), (px, py), mask=imhdr)
    debug_print(f"[DEBUG] Header placed at x={px}, y={py}, width={tw}, height={th}")

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

    # --- Correct anti-aliased black text compositing ---
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

    # ----------------------------
    # Missing patch reporting + consistency check between .cht and .cie
    # ----------------------------
    def normalize_sid_global(sid):
        """Normalize IDs like A1↔A01, GS1↔GS01 (for set comparisons)."""
        sid = str(sid).strip().upper()
        m = re.match(r"^(GS)(0*)(\d+)$", sid)
        if m:
            base, _, num = m.groups()
            return f"{base.upper()}{int(num)}"
        m2 = re.match(r"^([A-Z]+)(0*)(\d+)$", sid)
        if m2:
            prefix, _, num = m2.groups()
            return f"{prefix.upper()}{int(num)}"
        return sid

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
    debug_print(f"Margin applied around content: {margin_mm:.1f} mm -> {margin_px} px (offset_x={offset_x:.2f}, offset_y={offset_y:.2f})")

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
    p.add_argument('--map-fids', type=str, default=None, help='Optional measured pixel fiducials x1,y1,x2,y2,x3,y3,x4,y4 (overrides units->px mapping with affine)')
    p.add_argument('--png', action='store_true', help='Also write a PNG preview')
    p.add_argument('--font_mm', type=float, nargs=2, metavar=('LABEL_MM','FOOTER_MM'), help='Label and footer text heights in mm. Example: --font_mm 2.0 2.0')
    p.add_argument('--background-color', dest='background_patch', type=str, help='Patch label whose color is used for the image background (e.g. GS10)')
    p.add_argument('--debug', action='store_true', help='Enable parser debug output')
    args = p.parse_args()

    # make DEBUG_PARSE visible globally
    global DEBUG_PARSE
    DEBUG_PARSE = args.debug
    
    if not Path(args.cht).exists():
        print(f"Error: .cht file not found: {args.cht}", file=sys.stderr); sys.exit(2)
    if not Path(args.cie).exists():
        print(f"Error: .cie/.txt file not found: {args.cie}", file=sys.stderr); sys.exit(2)

    map_fids = None
    if args.map_fids:
        try:
            parts = [float(x.strip()) for x in args.map_fids.split(',')]
            if len(parts) != 8:
                raise ValueError()
            map_fids = parts
        except Exception:
            print("Error parsing --map-fids. Provide 8 comma-separated numbers: x1,y1,x2,y2,x3,y3,x4,y4", file=sys.stderr)
            sys.exit(2)

    recreate(args.cht, args.cie, args.out, target_dpi=args.target_dpi,
             font_path=args.font, map_fids=map_fids, output_png=args.png,
             font_mm_tuple=args.font_mm, background_patch=args.background_patch)

if __name__ == '__main__':
    main()
