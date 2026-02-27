
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
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

from PyPDF2 import PdfReader, PdfWriter

# Comment this out if you only use local files.
def download_if_url(path_or_url: str, out_name: str) -> str:
    if path_or_url.lower().startswith("http"):
        # Requires requests; if not available, save locally manually instead.
        import requests
        r = requests.get(path_or_url, timeout=30)
        r.raise_for_status()
        with open(out_name, "wb") as f:
            f.write(r.content)
        return out_name
    return path_or_url

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
def build_flowables(header_info, cap_table, insp_table, report_title="PPAP / CDC – Capability & Inspection"):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", fontSize=8, leading=10))
    styles.add(ParagraphStyle(name="Header", fontSize=14, leading=16, spaceAfter=8, spaceBefore=2))
    styles.add(ParagraphStyle(name="SubHeader", fontSize=11, leading=14, spaceAfter=4, spaceBefore=8))

    content = []
    content.append(Paragraph(report_title, styles["Header"]))

    # Meta block
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
    cap_tbl = Table(cap_data, repeatRows=1)
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
def render_overlay(flowables, page_size, body_margins, out_buffer=None):
    if out_buffer is None:
        out_buffer = io.BytesIO()

    left = body_margins.get("left", 15*mm)
    right = body_margins.get("right", 15*mm)
    top = body_margins.get("top", 35*mm)       # below header
    bottom = body_margins.get("bottom", 20*mm) # above footer

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

# Merge overlay with template
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
            base_page = tmpl_pages[-1] if reuse_last_template_page else None

        overlay_page = over_pages[i] if i < M else None

        if base_page is not None and overlay_page is not None:
            base_page.merge_page(overlay_page)
            writer.add_page(base_page)
        elif base_page is not None and overlay_page is None:
            writer.add_page(base_page)
        elif base_page is None and overlay_page is not None:
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

    # Read template size (first page). Fallback to A4
    try:
        treader = PdfReader(template_pdf)
        mbox = treader.pages[0].mediabox
        page_size = (float(mbox.width), float(mbox.height))
    except Exception:
        page_size = A4

    flowables = build_flowables(header_info, cap_table, insp_table, report_title=report_title)

    if body_margins_pts is None:
        body_margins_pts = {"left": 15*mm, "right": 15*mm, "top": 40*mm, "bottom": 25*mm}

    overlay_buf = render_overlay(flowables, page_size, body_margins_pts)
    merged_path = merge_overlay_with_template(template_pdf, overlay_buf, output_pdf)
    return merged_path

# Example usage
if __name__ == "__main__":
    raw_xlsx = "https://raw.githubusercontent.com/Chizobawisdom/Portfolio/main/Utility_and_Automation/PPAP-CDC-Automation/src/cdc_sample_wide.xlsx"
    raw_pdf  = "https://raw.githubusercontent.com/Chizobawisdom/Portfolio/main/Utility_and_Automation/PPAP-CDC-Automation/src/cdc_template.pdf"
    input_data = download_if_url(raw_xlsx, "cdc_sample_wide.xlsx")
    template   = download_if_url(raw_pdf, "cdc_template.pdf")

    # For now, assume local files exist:
    # input_data = "cdc_sample_wide.xlsx"
    # template   = "cdc_template.pdf"
    output     = os.path.join(os.getcwd(), "ppap_filled_overlay.pdf")

    print("Generating PPAP/CDC overlay...")
    result_path = generate_ppap_overlay_pdf(
        input_data, template, output,
        report_title="PPAP / CDC – Capability & Inspection Report",
        body_margins_pts={"left": 15*mm, "right": 15*mm, "top": 42*mm, "bottom": 28*mm}
    )
    print(f"Saved: {result_path}")
