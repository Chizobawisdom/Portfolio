
import os
import io
import math
import numpy as np
import pandas as pd
from datetime import datetime

from reportlab.lib.pagesizes import A4  # fallback if template size can't be read
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

from PyPDF2 import PdfReader, PdfWriter

# I/O: Read CSV/Excel
def load_data(input_path: str) -> pd.DataFrame:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    ext = os.path.splitext(input_path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(input_path)
    elif ext in [".xlsx", ".xls"]:
        engine = "openpyxl" if ext == ".xlsx" else "xlrd"
        df = pd.read_excel(input_path, engine=engine)
    else:
        raise ValueError("Unsupported file type. Use .csv, .xlsx or .xls")
    return df

# Detect format: wide vs long
def is_long_format(df: pd.DataFrame) -> bool:
    cols = set(c.lower() for c in df.columns)
    return {"characteristic", "value"}.issubset(cols)

# Capability calculations
def capability_metrics(values: np.ndarray, lsl: float, usl: float):
    """Compute Cp, Cpk, Pp, Ppk + summary stats. Handles NaNs and edge cases."""
    vals = values[~np.isnan(values)]
    n = len(vals)
    if n < 2:
        return np.nan, np.nan, np.nan, np.nan, n, np.nan, np.nan, np.nan, np.nan

    mean = np.mean(vals)
    s_within = np.std(vals, ddof=1)    # sample stdev (proxy; no subgroups)
    s_total  = np.std(vals, ddof=1)    # same as within without subgroups

    if s_within == 0 or s_total == 0:
        cp = cpk = pp = ppk = float("inf")
    else:
        tol = usl - lsl if (lsl == lsl and usl == usl) else np.nan
        cp  = (tol / (6 * s_within)) if tol == tol else np.nan
        cpu = (usl - mean) / (3 * s_within) if (usl == usl) else np.nan
        cpl = (mean - lsl) / (3 * s_within) if (lsl == lsl) else np.nan
        cpk = np.nanmin([cpu, cpl]) if (cpu == cpu and cpl == cpl) else (cpu if lsl != lsl else cpl)

        pp  = (tol / (6 * s_total)) if tol == tol else np.nan
        ppu = (usl - mean) / (3 * s_total) if (usl == usl) else np.nan
        ppl = (mean - lsl) / (3 * s_total) if (lsl == lsl) else np.nan
        ppk = np.nanmin([ppu, ppl]) if (ppu == ppu and ppl == ppl) else (ppu if lsl != lsl else ppl)

    return cp, cpk, pp, ppk, n, mean, s_within, np.min(vals), np.max(vals)

# Build tables from WIDE format
# Expect: columns like Diameter, Diameter_LSL, Diameter_USL
def build_tables_from_wide(df: pd.DataFrame):
    cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    admin_guess = {"lot","partnumber","partname","supplier","customer","date"}
    admin_cols = [c for c in cols if c.lower() in admin_guess]
    candidates = [c for c in numeric_cols
                  if not c.lower().endswith(("_lsl","_usl"))
                  and c not in admin_cols]

    cap_rows, insp_rows = [], []
    for c in candidates:
        lsl_col = c + "_LSL" if c + "_LSL" in cols else (c + "_lsl" if c + "_lsl" in cols else None)
        usl_col = c + "_USL" if c + "_USL" in cols else (c + "_usl" if c + "_usl" in cols else None)
        lsl = df[lsl_col].dropna().iloc[0] if lsl_col and df[lsl_col].notna().any() else np.nan
        usl = df[usl_col].dropna().iloc[0] if usl_col and df[usl_col].notna().any() else np.nan

        values = pd.to_numeric(df[c], errors="coerce").to_numpy()
        cp, cpk, pp, ppk, n, mean, s, vmin, vmax = capability_metrics(values, lsl, usl)

        # Pass/fail
        if lsl == lsl and usl == usl:
            pass_mask = (values >= lsl) & (values <= usl)
        elif lsl == lsl:
            pass_mask = (values >= lsl)
        elif usl == usl:
            pass_mask = (values <= usl)
        else:
            pass_mask = np.ones_like(values, dtype=bool)

        pass_count = int(np.nansum(pass_mask))
        fail_count = int(np.sum(~pass_mask)) if (lsl == lsl or usl == usl) else 0
        pass_rate = pass_count / max(1, n)

        cap_rows.append([
            c,
            "" if lsl != lsl else lsl,
            "" if usl != usl else usl,
            n,
            "" if mean != mean else round(mean, 5),
            "" if s != s else round(s, 5),
            "∞" if (cp == float("inf")) else ("" if cp != cp else round(cp, 3)),
            "∞" if (cpk == float("inf")) else ("" if cpk != cpk else round(cpk, 3)),
            "∞" if (pp == float("inf")) else ("" if pp != pp else round(pp, 3)),
            "∞" if (ppk == float("inf")) else ("" if ppk != ppk else round(ppk, 3)),
            "" if vmin != vmin else round(vmin, 5),
            "" if vmax != vmax else round(vmax, 5),
        ])

        insp_rows.append([c, n, pass_count, fail_count, f"{pass_rate*100:.1f}%"])

    cap_header  = ["Characteristic", "LSL", "USL", "N", "Mean", "Stdev", "Cp", "Cpk", "Pp", "Ppk", "Min", "Max"]
    insp_header = ["Characteristic", "N", "Pass", "Fail", "Pass Rate"]
    return (cap_header, cap_rows), (insp_header, insp_rows)

# Build tables from LONG format
# Expect columns: Characteristic, Value, LSL, USL
def build_tables_from_long(df: pd.DataFrame):
    rename_map = {}
    for col in df.columns:
        lc = col.lower()
        if lc == "characteristic": rename_map[col] = "Characteristic"
        elif lc == "value":        rename_map[col] = "Value"
        elif lc == "lsl":          rename_map[col] = "LSL"
        elif lc == "usl":          rename_map[col] = "USL"
    df = df.rename(columns=rename_map)

    cap_rows, insp_rows = [], []
    for char, sub in df.groupby("Characteristic"):
        values = pd.to_numeric(sub["Value"], errors="coerce").to_numpy()
        lsl = pd.to_numeric(sub["LSL"], errors="coerce").dropna().iloc[0] if "LSL" in sub.columns and sub["LSL"].notna().any() else np.nan
        usl = pd.to_numeric(sub["USL"], errors="coerce").dropna().iloc[0] if "USL" in sub.columns and sub["USL"].notna().any() else np.nan

        cp, cpk, pp, ppk, n, mean, s, vmin, vmax = capability_metrics(values, lsl, usl)

        if lsl == lsl and usl == usl:
            pass_mask = (values >= lsl) & (values <= usl)
        elif lsl == lsl:
            pass_mask = (values >= lsl)
        elif usl == usl:
            pass_mask = (values <= usl)
        else:
            pass_mask = np.ones_like(values, dtype=bool)

        pass_count = int(np.nansum(pass_mask))
        fail_count = int(np.sum(~pass_mask)) if (lsl == lsl or usl == usl) else 0
        pass_rate = pass_count / max(1, n)

        cap_rows.append([
            char,
            "" if lsl != lsl else lsl,
            "" if usl != usl else usl,
            n,
            "" if mean != mean else round(mean, 5),
            "" if s != s else round(s, 5),
            "∞" if (cp == float("inf")) else ("" if cp != cp else round(cp, 3)),
            "∞" if (cpk == float("inf")) else ("" if cpk != cpk else round(cpk, 3)),
            "∞" if (pp == float("inf")) else ("" if pp != pp else round(pp, 3)),
            "∞" if (ppk == float("inf")) else ("" if ppk != ppk else round(ppk, 3)),
            "" if vmin != vmin else round(vmin, 5),
            "" if vmax != vmax else round(vmax, 5),
        ])

        insp_rows.append([char, n, pass_count, fail_count, f"{pass_rate*100:.1f}%"])

    cap_header  = ["Characteristic", "LSL", "USL", "N", "Mean", "Stdev", "Cp", "Cpk", "Pp", "Ppk", "Min", "Max"]
    insp_header = ["Characteristic", "N", "Pass", "Fail", "Pass Rate"]
    return (cap_header, cap_rows), (insp_header, insp_rows)

# Extract admin/header info
def extract_header_info(df: pd.DataFrame):
    get_first = lambda col: (df[col].dropna().astype(str).iloc[0]
                             if col in df.columns and df[col].notna().any() else "")
    return {
        "Customer":   get_first("Customer"),
        "Supplier":   get_first("Supplier"),
        "PartNumber": get_first("PartNumber"),
        "PartName":   get_first("PartName"),
        "Lot":        get_first("Lot"),
        "Date":       get_first("Date") or datetime.today().strftime("%Y-%m-%d"),
    }

# Build flowables (title, meta, capability & inspection tables)
# These will be laid out inside the BODY area (margins respected).
def build_flowables(header_info, cap_table, insp_table, report_title="PPAP / CDC – Capability & Inspection"):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", fontSize=8, leading=10))
    styles.add(ParagraphStyle(name="Header", fontSize=14, leading=16, spaceAfter=8, spaceBefore=2))
    styles.add(ParagraphStyle(name="SubHeader", fontSize=11, leading=14, spaceAfter=4, spaceBefore=8))

    content = []
    content.append(Paragraph(report_title, styles["Header"]))

    # Meta block (kept compact so it fits in body area top)
    meta_data = [
        ["Customer", header_info.get("Customer",""), "Supplier", header_info.get("Supplier","")],
        ["Part Number", header_info.get("PartNumber",""), "Part Name", header_info.get("PartName","")],
        ["Lot", header_info.get("Lot",""), "Date", header_info.get("Date","")],
    ]
    meta_tbl = Table(meta_data, colWidths=[25*mm, 55*mm, 25*mm, 55*mm])
    meta_tbl.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.75, colors.black),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONT", (0,0), (-1,-1), "Helvetica", 9),
    ]))
    content.append(meta_tbl)
    content.append(Spacer(1, 6))

    # Capability table
    cap_header, cap_rows = cap_table
    content.append(Paragraph("Capability Study", styles["SubHeader"]))
    cap_data = [cap_header] + cap_rows
    cap_tbl = Table(cap_data, repeatRows=1)  # widths auto-fit to body width by DocTemplate
    cap_tbl.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.75, colors.black),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold", 8),
        ("FONT", (0,1), (-1,-1), "Helvetica", 8),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    content.append(cap_tbl)
    content.append(Spacer(1, 6))

    # Inspection table
    insp_header, insp_rows = insp_table
    content.append(Paragraph("Inspection Summary", styles["SubHeader"]))
    insp_data = [insp_header] + insp_rows
    insp_tbl = Table(insp_data, repeatRows=1)
    insp_tbl.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.75, colors.black),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold", 8),
        ("FONT", (0,1), (-1,-1), "Helvetica", 8),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    content.append(insp_tbl)

    content.append(Spacer(1, 8))
    content.append(Paragraph(
        "Notes: Cp/Cpk use sample stdev as a within-process proxy (no subgroups provided). "
        "Pp/Ppk use overall stdev. ∞ indicates zero observed variation for the sample.",
        styles["Small"]
    ))

    return content

# Render overlay PDF (transparent pages) sized to match the template.
# Margins ensure we do not write over header/footer.
def render_overlay(flowables, page_size, body_margins, out_buffer=None):
    """
    body_margins: dict with left, right, top, bottom margins in points.
                  These margins define the BODY area (between header/footer).
    """
    if out_buffer is None:
        out_buffer = io.BytesIO()

    left = body_margins.get("left", 15*mm)
    right = body_margins.get("right", 15*mm)
    top = body_margins.get("top", 35*mm)       # Increase top to avoid header area
    bottom = body_margins.get("bottom", 20*mm) # Increase bottom to avoid footer area

    doc = SimpleDocTemplate(
        out_buffer,
        pagesize=page_size,
        leftMargin=left,
        rightMargin=right,
        topMargin=top,
        bottomMargin=bottom,
    )
    doc.build(flowables)
    out_buffer.seek(0)
    return out_buffer

# Merge overlay pages onto template pages.
# Reuse the last template page if overlays exceed template length.
def merge_overlay_with_template(template_pdf_path, overlay_pdf_buffer, output_pdf_path, reuse_last_template_page=True):
    template_reader = PdfReader(template_pdf_path)
    overlay_reader  = PdfReader(overlay_pdf_buffer)
    writer = PdfWriter()

    tmpl_pages = template_reader.pages
    over_pages = overlay_reader.pages

    T = len(tmpl_pages)
    M = len(over_pages)

    for i in range(max(T, M)):
        if i < T:
            base_page = tmpl_pages[i]
        else:
            if reuse_last_template_page:
                base_page = tmpl_pages[-1]
            else:
                # If not reusing last page, just append an overlay page alone (rare)
                base_page = None

        if i < M:
            overlay_page = over_pages[i]
        else:
            overlay_page = None

        if base_page is not None and overlay_page is not None:
            # Merge overlay on base (header/footer preserved beneath)
            base_page.merge_page(overlay_page)
            writer.add_page(base_page)
        elif base_page is not None and overlay_page is None:
            # No overlay content for this page -> add template page as is
            writer.add_page(base_page)
        elif base_page is None and overlay_page is not None:
            # No base template page -> add overlay page alone
            writer.add_page(overlay_page)

    with open(output_pdf_path, "wb") as f:
        writer.write(f)

    return output_pdf_path

# Main pipeline
def generate_ppap_overlay_pdf(input_path, template_pdf, output_pdf,
                              report_title="PPAP / CDC – Capability & Inspection",
                              body_margins_pts=None):
    df = load_data(input_path)
    header_info = extract_header_info(df)

    # Compute tables
    if is_long_format(df):
        cap_table, insp_table = build_tables_from_long(df)
    else:
        cap_table, insp_table = build_tables_from_wide(df)

    # Read template size (first page). Fallback to A4 if missing.
    try:
        treader = PdfReader(template_pdf)
        mbox = treader.pages[0].mediabox
        page_size = (float(mbox.width), float(mbox.height))
    except Exception:
        page_size = A4

    # Build the PPAP/CDC flowables for the BODY area
    flowables = build_flowables(header_info, cap_table, insp_table, report_title=report_title)

    # Margins to protect header/footer area on the template
    if body_margins_pts is None:
        body_margins_pts = {
            "left": 15*mm,
            "right": 15*mm,
            "top": 40*mm,     # adjust upward to clear your header
            "bottom": 25*mm,  # adjust downward to clear your footer
        }

    # Render overlay PDF (may create multiple pages if content overflows)
    overlay_buf = render_overlay(flowables, page_size, body_margins_pts)

    # Merge overlay pages onto template pages
    merged_path = merge_overlay_with_template(template_pdf, overlay_buf, output_pdf)
    return merged_path

# Example usage:
if __name__ == "__main__":
     input_data = "Chizobawisdom/Portfolio/Utility_and_Automation/PPAP-CDC-Automation/src/cdc_sample_wide.xlsx"  # or .csv
     template   = "ppap_static_template.pdf"
     output     = "ppap_filled_overlay.pdf"
     print("Generating PPAP/CDC overlay...")
     result_path = generate_ppap_overlay_pdf(
         input_data, template, output,
         report_title="PPAP / CDC – Capability & Inspection Report",
         body_margins_pts={"left": 15*mm, "right": 15*mm, "top": 42*mm, "bottom": 28*mm}
     )
     print(f"Saved: {result_path}")
