"""Build a professional PowerPoint from SLIDES.md."""

import re

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

# -- Colour palette --
BG_DARK = RGBColor(0x1A, 0x1A, 0x2E)  # dark navy for title/section slides
BG_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ACCENT = RGBColor(0x00, 0x7A, 0xCC)  # blue accent
ACCENT_LIGHT = RGBColor(0xE8, 0xF4, 0xFD)  # light blue for code bg
TEXT_DARK = RGBColor(0x2D, 0x2D, 0x2D)
TEXT_LIGHT = RGBColor(0xFF, 0xFF, 0xFF)
TEXT_MUTED = RGBColor(0x66, 0x66, 0x66)
CODE_BG = RGBColor(0xF5, 0xF5, 0xF5)
CODE_FG = RGBColor(0x33, 0x33, 0x33)
TABLE_HEADER_BG = RGBColor(0x00, 0x7A, 0xCC)
TABLE_ALT_BG = RGBColor(0xF0, 0xF6, 0xFC)

# -- Diagram palette --
DIAGRAM_BORDER = RGBColor(0x99, 0x99, 0x99)
GREEN_LIGHT = RGBColor(0xE8, 0xFD, 0xE8)
GREEN_BORDER = RGBColor(0x2E, 0x8B, 0x57)
ORANGE_LIGHT = RGBColor(0xFF, 0xF3, 0xE0)
ORANGE_BORDER = RGBColor(0xE6, 0x7E, 0x22)
PURPLE_LIGHT = RGBColor(0xF3, 0xE8, 0xFD)
PURPLE_BORDER = RGBColor(0x8E, 0x44, 0xAD)


def set_slide_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_textbox(
    slide,
    left,
    top,
    width,
    height,
    text,
    font_size=14,
    bold=False,
    color=TEXT_DARK,
    font_name="Calibri",
    alignment=PP_ALIGN.LEFT,
):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    return tf


def add_code_block(slide, left, top, width, code_text, max_height=None):
    """Add a code block with grey background."""
    lines = code_text.rstrip().split("\n")
    line_count = len(lines)
    line_height_pt = 13
    padding = Pt(16)
    text_height = Pt(line_count * line_height_pt) + padding * 2

    if max_height and text_height > max_height:
        text_height = max_height

    # Background rectangle
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, text_height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = CODE_BG
    shape.line.fill.background()
    shape.adjustments[0] = 0.02  # subtle rounding

    # Text
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Pt(12)
    tf.margin_right = Pt(12)
    tf.margin_top = Pt(8)
    tf.margin_bottom = Pt(8)

    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = line
        p.font.size = Pt(10)
        p.font.name = "Consolas"
        p.font.color.rgb = CODE_FG
        p.space_after = Pt(1)
        p.space_before = Pt(0)

    return text_height


def add_bullet_list(slide, left, top, width, height, items, font_size=14):
    """Add a bulleted list."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True

    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()

        # Handle bold prefixes like **word**
        clean = item.lstrip("- ")
        bold_match = re.match(r"\*\*(.+?)\*\*(.+)", clean)
        if bold_match:
            run1 = p.add_run()
            run1.text = bold_match.group(1)
            run1.font.bold = True
            run1.font.size = Pt(font_size)
            run1.font.color.rgb = TEXT_DARK
            run1.font.name = "Calibri"
            run2 = p.add_run()
            run2.text = bold_match.group(2)
            run2.font.size = Pt(font_size)
            run2.font.color.rgb = TEXT_DARK
            run2.font.name = "Calibri"
        else:
            p.text = clean
            p.font.size = Pt(font_size)
            p.font.color.rgb = TEXT_DARK
            p.font.name = "Calibri"

        p.space_after = Pt(4)
        p.level = 0

    return tf


def add_table_slide(slide, left, top, width, headers, rows, col_widths=None):
    """Add a formatted table."""
    row_count = len(rows) + 1
    col_count = len(headers)
    height = Inches(0.35) * row_count

    table_shape = slide.shapes.add_table(row_count, col_count, left, top, width, height)
    table = table_shape.table

    # Set column widths
    if col_widths:
        for i, w in enumerate(col_widths):
            table.columns[i].width = w

    # Header row
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = TABLE_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT
        p.font.name = "Calibri"

    # Data rows
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = table.cell(r + 1, c)
            cell.text = val
            if r % 2 == 1:
                cell.fill.solid()
                cell.fill.fore_color.rgb = TABLE_ALT_BG
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(10)
            p.font.color.rgb = TEXT_DARK
            p.font.name = "Calibri"

    return table_shape


# -- Diagram helpers --


def add_rect_box(
    slide,
    left,
    top,
    width,
    height,
    lines,
    fill_color=None,
    border_color=ACCENT,
    font_size=11,
    bold_first=False,
    text_color=TEXT_DARK,
    alignment=PP_ALIGN.LEFT,
    anchor=MSO_ANCHOR.MIDDLE,
):
    """Draw a rounded rectangle with multi-line text."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.5)
    shape.adjustments[0] = 0.04

    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Pt(10)
    tf.margin_right = Pt(10)
    tf.margin_top = Pt(6)
    tf.margin_bottom = Pt(6)
    tf.vertical_anchor = anchor

    for i, line_text in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line_text
        p.font.size = Pt(font_size)
        p.font.name = "Calibri"
        p.font.color.rgb = text_color
        p.alignment = alignment
        if i == 0 and bold_first:
            p.font.bold = True
        p.space_after = Pt(2)
        p.space_before = Pt(0)

    return shape


_DEFAULT_ARROW_HEIGHT = Inches(0.3)


def add_down_arrow(slide, center_x, top, height=_DEFAULT_ARROW_HEIGHT):
    """Add a downward arrow between diagram elements."""
    arrow_w = Inches(0.25)
    shape = slide.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, center_x - arrow_w // 2, top, arrow_w, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = ACCENT
    shape.line.fill.background()
    return shape


def add_up_arrow(slide, center_x, top, height=_DEFAULT_ARROW_HEIGHT):
    """Add an upward arrow between diagram elements."""
    arrow_w = Inches(0.25)
    shape = slide.shapes.add_shape(MSO_SHAPE.UP_ARROW, center_x - arrow_w // 2, top, arrow_w, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = ACCENT
    shape.line.fill.background()
    return shape


_DEFAULT_LR_ARROW_WIDTH = Inches(0.6)


def add_lr_arrow(slide, left, center_y, width=_DEFAULT_LR_ARROW_WIDTH):
    """Add a left-right arrow."""
    arrow_h = Inches(0.2)
    shape = slide.shapes.add_shape(MSO_SHAPE.LEFT_RIGHT_ARROW, left, center_y - arrow_h // 2, width, arrow_h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = ACCENT
    shape.line.fill.background()
    return shape


# -- Native diagram renderers --


def draw_docker_diagram(slide, left, top, width, max_height):
    """Docker container architecture diagram."""
    dw = Inches(9)
    dl = left + (width - dw) // 2
    oh = Inches(3.2)

    # Outer box — Host OS
    add_rect_box(slide, dl, top, dw, oh, [""], fill_color=CODE_BG, border_color=DIAGRAM_BORDER, anchor=MSO_ANCHOR.TOP)

    add_textbox(
        slide,
        dl + Pt(16),
        top + Pt(10),
        Inches(4),
        Inches(0.3),
        "Your Machine (Host OS)",
        font_size=13,
        bold=True,
        color=TEXT_DARK,
    )

    # Container boxes
    bt = top + Inches(0.6)
    bh = Inches(1.6)
    gap = Inches(0.5)
    bw = (dw - Inches(1.2) - gap) // 2

    add_rect_box(
        slide,
        dl + Inches(0.6),
        bt,
        bw,
        bh,
        ["Container: Odoo 19", "Python 3.12", "Dependencies"],
        fill_color=ACCENT_LIGHT,
        border_color=ACCENT,
        font_size=12,
        bold_first=True,
    )

    add_rect_box(
        slide,
        dl + Inches(0.6) + bw + gap,
        bt,
        bw,
        bh,
        ["Container: PostgreSQL 18", "", "Database storage"],
        fill_color=GREEN_LIGHT,
        border_color=GREEN_BORDER,
        font_size=12,
        bold_first=True,
    )

    # Kernel label
    add_textbox(
        slide,
        dl,
        top + oh - Inches(0.45),
        dw,
        Inches(0.3),
        "Shared OS Kernel",
        font_size=12,
        color=TEXT_MUTED,
        alignment=PP_ALIGN.CENTER,
    )

    return oh


def draw_architecture_diagram(slide, left, top, width, max_height):
    """Project Docker Compose architecture diagram."""
    dw = Inches(10)
    dl = left + (width - dw) // 2
    oh = Inches(4.5)

    # Outer box
    add_rect_box(slide, dl, top, dw, oh, [""], fill_color=CODE_BG, border_color=DIAGRAM_BORDER, anchor=MSO_ANCHOR.TOP)

    add_textbox(
        slide,
        dl + Pt(16),
        top + Pt(8),
        Inches(4),
        Inches(0.3),
        "Host Machine",
        font_size=14,
        bold=True,
        color=TEXT_DARK,
    )

    # Service boxes — 2x2 grid
    bw = Inches(3.8)
    bh = Inches(1.2)
    gap_x = Inches(0.8)
    gap_y = Inches(0.3)
    grid_left = dl + (dw - 2 * bw - gap_x) // 2
    row1_top = top + Inches(0.6)
    row2_top = row1_top + bh + gap_y

    # odoo-app
    add_rect_box(
        slide,
        grid_left,
        row1_top,
        bw,
        bh,
        ["odoo-app", "(ui profile) \u00b7 Port 8069"],
        fill_color=ACCENT_LIGHT,
        border_color=ACCENT,
        font_size=12,
        bold_first=True,
    )

    # db
    db_left = grid_left + bw + gap_x
    add_rect_box(
        slide,
        db_left,
        row1_top,
        bw,
        bh,
        ["db", "PostgreSQL 18 (PostGIS)"],
        fill_color=GREEN_LIGHT,
        border_color=GREEN_BORDER,
        font_size=12,
        bold_first=True,
    )

    # Arrow between odoo-app and db
    add_lr_arrow(slide, grid_left + bw, row1_top + bh // 2, width=gap_x)

    # odoo-dev
    add_rect_box(
        slide,
        grid_left,
        row2_top,
        bw,
        bh,
        ["odoo-dev", "(dev profile) \u00b7 dynamic port"],
        fill_color=ACCENT_LIGHT,
        border_color=ACCENT,
        font_size=12,
        bold_first=True,
    )

    # test
    add_rect_box(
        slide,
        db_left,
        row2_top,
        bw,
        bh,
        ["test", "(one-off) \u00b7 isolated tests"],
        fill_color=ORANGE_LIGHT,
        border_color=ORANGE_BORDER,
        font_size=12,
        bold_first=True,
    )

    # Footer
    footer_top = row2_top + bh + Inches(0.15)
    add_textbox(
        slide,
        dl + Inches(0.5),
        footer_top,
        dw - Inches(1),
        Inches(0.25),
        "Volumes: postgres_data, odoo_data    |    " "Network: odoo-net (bridge)",
        font_size=11,
        color=TEXT_MUTED,
        alignment=PP_ALIGN.CENTER,
    )

    return oh


def draw_precommit_flow(slide, left, top, width, max_height):
    """Pre-commit hooks flow diagram."""
    center_x = left + width // 2
    dw = Inches(6)
    dl = center_x - dw // 2

    # Step 1: command text
    add_textbox(
        slide,
        dl,
        top,
        dw,
        Inches(0.35),
        'git commit -m "feat: add student model"',
        font_size=12,
        color=TEXT_DARK,
        alignment=PP_ALIGN.CENTER,
        font_name="Consolas",
    )
    y = top + Inches(0.4)

    add_down_arrow(slide, center_x, y, Inches(0.3))
    y += Inches(0.35)

    # Hooks box
    hook_h = Inches(1.8)
    add_rect_box(
        slide,
        dl,
        y,
        dw,
        hook_h,
        [
            "Pre-commit hooks run automatically:",
            "",
            "  \u2713  Linter (ruff) \u2014 catches bugs & style issues",
            "  \u2713  Formatter (ruff-format) \u2014 consistent style",
            "  \u2713  XML/MD (prettier) \u2014 clean formatting",
            "  \u2717  Syntax error! \u2014 blocks the commit",
        ],
        fill_color=ACCENT_LIGHT,
        border_color=ACCENT,
        font_size=11,
        bold_first=True,
        anchor=MSO_ANCHOR.TOP,
    )
    y += hook_h + Inches(0.05)

    add_down_arrow(slide, center_x, y, Inches(0.3))
    y += Inches(0.35)

    add_textbox(
        slide,
        dl,
        y,
        dw,
        Inches(0.35),
        "Fix the issue, stage changes, then commit again",
        font_size=12,
        color=TEXT_DARK,
        alignment=PP_ALIGN.CENTER,
    )
    return y - top + Inches(0.4)


def draw_plan_mode_box(slide, left, top, width, max_height):
    """Plan Mode capabilities box."""
    dw = Inches(8)
    dl = left + (width - dw) // 2
    bh = Inches(3.8)

    add_rect_box(
        slide,
        dl,
        top,
        dw,
        bh,
        [
            "PLAN MODE",
            "",
            "Claude CAN:",
            "  \u2713  Read files (Glob, Grep, Read)",
            "  \u2713  Search the codebase",
            "  \u2713  Analyze existing code",
            "  \u2713  Propose an implementation approach",
            "",
            "Claude CANNOT:",
            "  \u2717  Write or edit files",
            "  \u2717  Run commands",
            "  \u2717  Make any changes to the codebase",
            "",
            "Exit: Shift+Tab twice (or approve the plan)",
        ],
        fill_color=ACCENT_LIGHT,
        border_color=ACCENT,
        font_size=12,
        bold_first=True,
        anchor=MSO_ANCHOR.TOP,
    )

    return bh


def draw_github_workflow(slide, left, top, width, max_height):
    """Git branching workflow diagram."""
    dw = Inches(10)
    dl = left + (width - dw) // 2

    line_h = Pt(4)
    dot_r = Inches(0.15)

    # Main branch line
    main_y = top + Inches(0.8)
    main_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, dl + Inches(1), main_y, Inches(8), line_h)
    main_line.fill.solid()
    main_line.fill.fore_color.rgb = ACCENT
    main_line.line.fill.background()

    add_textbox(slide, dl, main_y - Inches(0.15), Inches(1), Inches(0.3), "main", font_size=13, bold=True, color=ACCENT)
    add_textbox(
        slide,
        dl + Inches(9.2),
        main_y - Inches(0.15),
        Inches(2.5),
        Inches(0.3),
        "(stable)",
        font_size=10,
        color=TEXT_MUTED,
    )

    # Branch point on main
    bp_x = dl + Inches(2.5)
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, bp_x - dot_r, main_y - dot_r + line_h // 2, dot_r * 2, dot_r * 2)
    dot.fill.solid()
    dot.fill.fore_color.rgb = ACCENT
    dot.line.fill.background()

    # Merge point on main
    mp_x = dl + Inches(7)
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, mp_x - dot_r, main_y - dot_r + line_h // 2, dot_r * 2, dot_r * 2)
    dot.fill.solid()
    dot.fill.fore_color.rgb = ACCENT
    dot.line.fill.background()

    # Feature branch line
    feat_y = main_y + Inches(1.2)
    feat_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, dl + Inches(2.5), feat_y, Inches(4.5), line_h)
    feat_line.fill.solid()
    feat_line.fill.fore_color.rgb = GREEN_BORDER
    feat_line.line.fill.background()

    add_textbox(
        slide,
        dl,
        feat_y - Inches(0.15),
        Inches(2.2),
        Inches(0.3),
        "feature",
        font_size=13,
        bold=True,
        color=GREEN_BORDER,
    )
    add_textbox(
        slide,
        dl + Inches(7.2),
        feat_y - Inches(0.15),
        Inches(2.5),
        Inches(0.3),
        "(your work)",
        font_size=10,
        color=TEXT_MUTED,
    )

    # Commit dots on feature
    for cx in [Inches(3.5), Inches(4.5), Inches(5.5)]:
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, dl + cx - dot_r, feat_y - dot_r + line_h // 2, dot_r * 2, dot_r * 2
        )
        dot.fill.solid()
        dot.fill.fore_color.rgb = GREEN_BORDER
        dot.line.fill.background()

    add_textbox(
        slide,
        dl + Inches(2.8),
        feat_y + Inches(0.3),
        Inches(4),
        Inches(0.3),
        "commit          commit          commit",
        font_size=10,
        color=TEXT_MUTED,
    )

    # Branch/merge annotations
    add_textbox(
        slide,
        dl + Inches(2.0),
        main_y + Inches(0.2),
        Inches(1.5),
        Inches(0.3),
        "branch \u2198",
        font_size=10,
        color=TEXT_MUTED,
    )
    add_textbox(
        slide,
        dl + Inches(6.5),
        main_y + Inches(0.2),
        Inches(1.5),
        Inches(0.3),
        "\u2197 merge PR",
        font_size=10,
        color=TEXT_MUTED,
    )

    return Inches(2.5)


def draw_module_layers(slide, left, top, width, max_height):
    """Module layer architecture with stacked boxes."""
    dw = Inches(9)
    dl = left + (width - dw) // 2
    bh = Inches(0.7)
    gap = Inches(0.15)
    arrow_h = Inches(0.25)

    layers = [
        ("Layer 3", "DOMAIN EXTENSIONS", "(sis_reports, sis_api)", PURPLE_LIGHT, PURPLE_BORDER),
        ("Layer 2", "DOMAIN CORE", "(sis_student, sis_course, sis_enrollment)", ACCENT_LIGHT, ACCENT),
        ("Layer 1", "FOUNDATION", "(sis_security, sis_vocabulary)", GREEN_LIGHT, GREEN_BORDER),
        ("Layer 0", "ODOO CORE", "(base, hr, stock, account, portal)", CODE_BG, DIAGRAM_BORDER),
    ]

    y = top
    center_x = dl + dw // 2

    for i, (layer_num, name, examples, fill, border) in enumerate(layers):
        add_rect_box(
            slide,
            dl,
            y,
            dw,
            bh,
            [f"{layer_num}:  {name}    {examples}"],
            fill_color=fill,
            border_color=border,
            font_size=13,
            bold_first=True,
            alignment=PP_ALIGN.CENTER,
        )
        y += bh

        if i < len(layers) - 1:
            y += gap
            add_down_arrow(slide, center_x, y, arrow_h)
            y += arrow_h + gap

    return y - top


def draw_security_tiers(slide, left, top, width, max_height):
    """Three-tier security model diagram."""
    dw = Inches(9)
    dl = left + (width - dw) // 2
    bh = Inches(1.0)
    gap = Inches(0.1)
    arrow_h = Inches(0.25)

    tiers = [
        ("Tier 1", "ROLES", "Composite, cross-domain.  Example: 'Field Officer'", PURPLE_LIGHT, PURPLE_BORDER),
        ("Tier 2", "FUNCTIONAL PRIVILEGES", "Per domain: viewer \u2192 officer \u2192 manager", ACCENT_LIGHT, ACCENT),
        ("Tier 3", "BASE PERMISSIONS", "Technical, granular: read, write, create, delete", GREEN_LIGHT, GREEN_BORDER),
    ]

    y = top
    center_x = dl + dw // 2

    for i, (tier_num, name, desc, fill, border) in enumerate(tiers):
        add_rect_box(
            slide,
            dl,
            y,
            dw,
            bh,
            [f"{tier_num}:  {name}", desc],
            fill_color=fill,
            border_color=border,
            font_size=13,
            bold_first=True,
            alignment=PP_ALIGN.CENTER,
        )
        y += bh

        if i < len(tiers) - 1:
            y += gap
            add_up_arrow(slide, center_x, y, arrow_h)
            y += arrow_h + gap

    return y - top


# Map slide titles to custom diagram renderers.
# These slides get native PowerPoint shapes instead of ASCII art code blocks.
DIAGRAM_RENDERERS = {
    "What Is Docker?": draw_docker_diagram,
    "Project Architecture Diagram": draw_architecture_diagram,
    "What Are Pre-Commit Hooks?": draw_precommit_flow,
    "Plan Mode \u2014 How It Works": draw_plan_mode_box,
    "GitHub Workflow": draw_github_workflow,
    "Module Layers": draw_module_layers,
    "Three-Tier Security Model": draw_security_tiers,
}


def is_diagram_code(code_text):
    """Check if a code block is an ASCII art diagram (not actual code)."""
    box_chars = set("\u250c\u2510\u2514\u2518\u2502\u2500\u251c\u2524\u2514\u2500")
    # Also count tree characters
    tree_chars = set("\u251c\u2514\u2502")
    count = sum(1 for c in code_text if c in box_chars | tree_chars)
    return count > 3


def clean_diagram_text(code_text):
    """Replace Unicode tree/box characters with reliable ASCII."""
    text = code_text
    # Order matters: replace multi-char patterns first
    text = text.replace("\u251c\u2500\u2500 ", "  - ")
    text = text.replace("\u2514\u2500\u2500 ", "  - ")
    text = text.replace("\u251c\u2500\u2500", "  -")
    text = text.replace("\u2514\u2500\u2500", "  -")
    text = text.replace("\u2502   ", "    ")
    text = text.replace("\u2502", " ")
    # Clean remaining box-drawing chars
    text = text.replace("\u250c", "+")
    text = text.replace("\u2510", "+")
    text = text.replace("\u2518", "+")
    text = text.replace("\u2500", "-")
    text = text.replace("\u2524", "+")
    return text


# -- Parse SLIDES.md --
def parse_slides(filepath):
    """Parse SLIDES.md into structured sections and slides."""
    with open(filepath) as f:
        content = f.read()

    sections = []
    current_section = None
    current_slide = None

    for line in content.split("\n"):
        # Section header (## Section ...)
        if line.startswith("## Section") or line.startswith("## "):
            if current_slide and current_section:
                current_section["slides"].append(current_slide)
            if current_section:
                sections.append(current_section)
            title = line.lstrip("# ").strip()
            # Clean up (~N slides) suffix
            title = re.sub(r"\s*\(~\d+ slides\)", "", title)
            current_section = {"title": title, "slides": []}
            current_slide = None

        # Slide header (### Slide ...)
        elif line.startswith("### Slide"):
            if current_slide and current_section:
                current_section["slides"].append(current_slide)
            title = re.sub(r"^### Slide \d+[A-Z]?-\d+:\s*", "", line).strip()
            current_slide = {"title": title, "content": []}

        # Content line
        elif current_slide is not None:
            current_slide["content"].append(line)

    # Flush
    if current_slide and current_section:
        current_section["slides"].append(current_slide)
    if current_section:
        sections.append(current_section)

    return sections


def classify_content(lines):
    """Classify content blocks into types: bullet, code, table, text."""
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Code block
        if line.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            blocks.append(("code", "\n".join(code_lines)))

        # Table
        elif "|" in line and i + 1 < len(lines) and "---" in lines[i + 1]:
            headers = [c.strip() for c in line.strip("|").split("|")]
            i += 2  # skip header + separator
            rows = []
            while i < len(lines) and "|" in lines[i]:
                row = [c.strip() for c in lines[i].strip("|").split("|")]
                # Clean markdown formatting
                row = [re.sub(r"[`*]", "", c) for c in row]
                rows.append(row)
                i += 1
            headers = [re.sub(r"[`*]", "", h) for h in headers]
            blocks.append(("table", (headers, rows)))

        # Bullet point
        elif line.startswith("- ") or line.startswith("  - "):
            bullets = []
            while i < len(lines) and (
                lines[i].startswith("- ") or lines[i].startswith("  - ") or lines[i].startswith("  ")
            ):
                bullets.append(lines[i])
                i += 1
            blocks.append(("bullet", bullets))

        # Empty line
        elif line.strip() == "" or line.strip() == "---":
            i += 1

        # Regular text
        else:
            text_lines = []
            while (
                i < len(lines)
                and lines[i].strip()
                and not lines[i].startswith("- ")
                and not lines[i].startswith("```")
                and not ("|" in lines[i] and i + 1 < len(lines) and "---" in lines[i + 1])
            ):
                text_lines.append(lines[i])
                i += 1
            if text_lines:
                text = " ".join(text_lines)
                text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # strip bold markers
                text = re.sub(r"`(.+?)`", r"\1", text)  # strip code markers
                blocks.append(("text", text))

    return blocks


def build_pptx(sections, output_path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 widescreen
    prs.slide_height = Inches(7.5)

    MARGIN_LEFT = Inches(0.8)
    MARGIN_TOP = Inches(0.3)
    CONTENT_WIDTH = Inches(11.7)
    TITLE_HEIGHT = Inches(0.9)

    # -- Title slide --
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    set_slide_bg(slide, BG_DARK)
    add_textbox(
        slide,
        MARGIN_LEFT,
        Inches(2.0),
        CONTENT_WIDTH,
        Inches(1.2),
        "Developer Training",
        font_size=44,
        bold=True,
        color=TEXT_LIGHT,
        alignment=PP_ALIGN.CENTER,
    )
    add_textbox(
        slide,
        MARGIN_LEFT,
        Inches(3.2),
        CONTENT_WIDTH,
        Inches(0.8),
        "Student Information System — Odoo 19",
        font_size=28,
        color=ACCENT,
        alignment=PP_ALIGN.CENTER,
    )
    add_textbox(
        slide,
        MARGIN_LEFT,
        Inches(4.5),
        CONTENT_WIDTH,
        Inches(0.5),
        "Hands-on workshop with Claude Code",
        font_size=18,
        color=TEXT_MUTED,
        alignment=PP_ALIGN.CENTER,
    )
    add_textbox(
        slide,
        MARGIN_LEFT,
        Inches(5.5),
        CONTENT_WIDTH,
        Inches(0.4),
        "Edwin Gonzales",
        font_size=16,
        color=TEXT_LIGHT,
        alignment=PP_ALIGN.CENTER,
    )
    add_textbox(
        slide,
        MARGIN_LEFT,
        Inches(6.0),
        CONTENT_WIDTH,
        Inches(0.4),
        "March 4, 2026",
        font_size=13,
        color=TEXT_MUTED,
        alignment=PP_ALIGN.CENTER,
    )

    # -- Section and content slides --
    for section in sections:
        # Section divider slide
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        set_slide_bg(slide, BG_DARK)
        add_textbox(
            slide,
            MARGIN_LEFT,
            Inches(2.5),
            CONTENT_WIDTH,
            Inches(1.0),
            section["title"],
            font_size=36,
            bold=True,
            color=TEXT_LIGHT,
            alignment=PP_ALIGN.CENTER,
        )

        # Accent line
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5.5), Inches(3.6), Inches(2.3), Pt(3))
        shape.fill.solid()
        shape.fill.fore_color.rgb = ACCENT
        shape.line.fill.background()

        # Content slides
        for slide_data in section["slides"]:
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            set_slide_bg(slide, BG_WHITE)

            # Slide title
            add_textbox(
                slide,
                MARGIN_LEFT,
                MARGIN_TOP,
                CONTENT_WIDTH,
                TITLE_HEIGHT,
                slide_data["title"],
                font_size=28,
                bold=True,
                color=ACCENT,
            )

            # Accent underline
            shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, MARGIN_LEFT, Inches(1.1), Inches(2.0), Pt(3))
            shape.fill.solid()
            shape.fill.fore_color.rgb = ACCENT
            shape.line.fill.background()

            # Classify and render content blocks
            blocks = classify_content(slide_data["content"])
            y_pos = Inches(1.4)
            remaining = Inches(7.5) - y_pos - Inches(0.3)

            for block_type, block_data in blocks:
                if y_pos > Inches(6.8):
                    break  # don't overflow

                if block_type == "bullet":
                    item_count = len(block_data)
                    height = min(Pt(item_count * 22) + Pt(16), remaining)
                    add_bullet_list(slide, MARGIN_LEFT, y_pos, CONTENT_WIDTH, height, block_data, font_size=13)
                    y_pos += height + Pt(8)

                elif block_type == "code":
                    slide_title = slide_data["title"]
                    if slide_title in DIAGRAM_RENDERERS and is_diagram_code(block_data):
                        renderer = DIAGRAM_RENDERERS[slide_title]
                        h = renderer(slide, MARGIN_LEFT, y_pos, CONTENT_WIDTH, remaining)
                        y_pos += h + Pt(12)
                    elif is_diagram_code(block_data):
                        cleaned = clean_diagram_text(block_data)
                        max_h = min(Inches(4.0), remaining)
                        h = add_code_block(slide, MARGIN_LEFT, y_pos, CONTENT_WIDTH, cleaned, max_height=max_h)
                        y_pos += h + Pt(12)
                    else:
                        max_h = min(Inches(4.0), remaining)
                        h = add_code_block(slide, MARGIN_LEFT, y_pos, CONTENT_WIDTH, block_data, max_height=max_h)
                        y_pos += h + Pt(12)

                elif block_type == "table":
                    headers, rows = block_data
                    if headers and rows:
                        display_rows = rows[:12]  # cap rows to fit
                        add_table_slide(slide, MARGIN_LEFT, y_pos, CONTENT_WIDTH, headers, display_rows)
                        row_h = Inches(0.35) * (len(display_rows) + 1)
                        y_pos += row_h + Pt(12)

                elif block_type == "text":
                    height = Inches(0.5)
                    add_textbox(
                        slide, MARGIN_LEFT, y_pos, CONTENT_WIDTH, height, block_data, font_size=13, color=TEXT_DARK
                    )
                    y_pos += height + Pt(4)

    # -- Thank you slide --
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_DARK)
    add_textbox(
        slide,
        MARGIN_LEFT,
        Inches(2.5),
        CONTENT_WIDTH,
        Inches(1.0),
        "Thank You!",
        font_size=44,
        bold=True,
        color=TEXT_LIGHT,
        alignment=PP_ALIGN.CENTER,
    )
    add_textbox(
        slide,
        MARGIN_LEFT,
        Inches(3.6),
        CONTENT_WIDTH,
        Inches(0.6),
        "Time for hands-on!",
        font_size=24,
        color=ACCENT,
        alignment=PP_ALIGN.CENTER,
    )

    prs.save(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    sections = parse_slides("SLIDES.md")
    print(f"Parsed {len(sections)} sections, " f"{sum(len(s['slides']) for s in sections)} slides total")
    build_pptx(sections, "SLIDES.pptx")
