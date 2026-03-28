CDC / PPAP Automated Report Generator
Reads inspection data → Computes capability & inspection tables → Overlays onto a PDF template → Generates a polished CDC/PPAP report

---

Overview
This project automates the creation of Certificate of Dimensional Conformance (CDC) and PPAP-style capability reports by taking raw inspection data (CSV/Excel), computing statistical metrics (Cp, Cpk, Pp, Ppk), building formatted tables, and overlaying the results onto a static PDF template that already contains your company’s header and footer.
The output is a finalized, print-ready PDF that visually matches customer documentation standards while keeping all logic dynamically generated from data.

---

Key Features
1. Read data from CSV or Excel
Supports:

 - Wide format (recommended): one row per part, with columns like Diameter, Diameter_LSL, Diameter_USL
 - Long format: one row per characteristic per part

2. Automatically compute:

 - Mean, Standard Deviation
 - Cp, Cpk
 - Pp, Ppk
 - Min/Max
 - Pass/Fail counts and Pass Rate

3. Generate PPAP/CDC-style content

 - Report title
 - Customer information
 - Supplier information
 - Part number & name
 - Lot information
 - Capability study table
 - Inspection summary table
 - Notes block

4. Overlay content onto existing PDF template
The template’s:

 - Header
 - Footer
 - Branding
 - Page numbering

…are preserved exactly as-is.

5. Multi-page support
If the report exceeds one page, additional overlay pages are automatically merged with template pages.