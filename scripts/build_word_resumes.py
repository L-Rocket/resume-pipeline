"""Generate the English Word resumes from the application-ready LaTeX sources."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
LATEX_DIR = ROOT / "latex"
OUTPUT_DIR = ROOT / "build" / "docx"
SECTION_NAMES = ("Education", "Work Experience", "Project Experience", "Technical Skills")


@dataclass(frozen=True)
class Heading:
    title: str
    subtitle: str
    dates: str
    location: str
    bullets: tuple[str, ...]


@dataclass(frozen=True)
class Resume:
    name: str
    email: str
    phone: str
    github: str
    linkedin: str
    objective: str
    education: tuple[tuple[str, ...], ...]
    experience: tuple[Heading, ...]
    projects: tuple[Heading, ...]
    skills: tuple[tuple[str, str], ...]


def strip_comments(text: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", text)


def command_args(text: str, command: str, count: int) -> list[tuple[tuple[str, ...], int, int]]:
    """Return balanced-brace arguments and source spans for a LaTeX command."""
    results: list[tuple[tuple[str, ...], int, int]] = []
    needle = "\\" + command
    cursor = 0
    while True:
        start = text.find(needle, cursor)
        if start < 0:
            break
        pos = start + len(needle)
        args: list[str] = []
        for _ in range(count):
            while pos < len(text) and text[pos].isspace():
                pos += 1
            if pos >= len(text) or text[pos] != "{":
                raise ValueError(f"Malformed {needle} at offset {start}")
            depth = 1
            begin = pos + 1
            pos += 1
            while depth and pos < len(text):
                if text[pos] == "{" and (pos == 0 or text[pos - 1] != "\\"):
                    depth += 1
                elif text[pos] == "}" and (pos == 0 or text[pos - 1] != "\\"):
                    depth -= 1
                pos += 1
            if depth:
                raise ValueError(f"Unclosed argument for {needle} at offset {start}")
            args.append(text[begin : pos - 1])
        results.append((tuple(args), start, pos))
        cursor = pos
    return results


def decode_latex(text: str) -> str:
    replacements = {
        r"\%": "%",
        r"\&": "&",
        r"\_": "_",
        r"\textbar": "|",
        "--": "–",
        "~": " ",
    }
    value = text
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = re.sub(r"\\(?:small|normalsize|justifying|bfseries|itshape)\b", "", value)
    value = re.sub(r"\\(?:textbf|textit|emph)\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\quad\b", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def decode_segment(text: str) -> str:
    """Decode an inline fragment without losing spaces around formatting runs."""
    leading = bool(text and text[0].isspace())
    trailing = bool(text and text[-1].isspace())
    value = decode_latex(text)
    return (" " if leading else "") + value + (" " if trailing else "")


def section(text: str, name: str) -> str:
    marker = f"\\section{{{name}}}"
    start = text.index(marker) + len(marker)
    later = [text.find(f"\\section{{{candidate}}}", start) for candidate in SECTION_NAMES]
    ends = [position for position in later if position >= 0]
    return text[start : min(ends) if ends else len(text)]


def heading_blocks(text: str) -> tuple[Heading, ...]:
    headings = command_args(text, "resumeHeading", 4)
    blocks: list[Heading] = []
    for index, (args, _start, end) in enumerate(headings):
        next_start = headings[index + 1][1] if index + 1 < len(headings) else len(text)
        bullets = tuple(item[0][0].strip() for item in command_args(text[end:next_start], "resumeItem", 1))
        blocks.append(Heading(*(decode_latex(value) for value in args), bullets))
    return tuple(blocks)


def parse_resume(path: Path) -> Resume:
    text = strip_comments(path.read_text(encoding="utf-8"))
    document = text.split(r"\begin{document}", 1)[1]
    header = document.split(r"\section{Education}", 1)[0]

    name_match = re.search(r"\\bfseries\s+([^{}\\]+)\\par", header)
    if not name_match:
        raise ValueError("Could not find the name in the centered header")
    links = command_args(header, "href", 2)
    hrefs = [(decode_latex(args[0]), decode_latex(args[1])) for args, _, _ in links]
    email = next(label for target, label in hrefs if target.startswith("mailto:"))
    github = next(label for target, label in hrefs if "github.com" in target)
    linkedin = next(label for target, label in hrefs if "linkedin.com" in target)
    phone_match = re.search(r"\+1\s*\(555\)\s*\d{3}-\d{4}", header)
    if not phone_match:
        raise ValueError("Use an explicit North American phone number in the header")
    objectives = command_args(header, "textit", 1)
    objective = decode_latex(objectives[-1][0][0]) if objectives else ""

    education = tuple(
        tuple(decode_latex(value) for value in args)
        for args, _, _ in command_args(section(document, "Education"), "resumeEducation", 5)
    )
    skills = tuple(
        tuple(decode_latex(value) for value in args)
        for args, _, _ in command_args(section(document, "Technical Skills"), "skillItem", 2)
    )
    return Resume(
        name=decode_latex(name_match.group(1)),
        email=email,
        phone=phone_match.group(0),
        github=github,
        linkedin=linkedin,
        objective=objective,
        education=education,
        experience=heading_blocks(section(document, "Work Experience")),
        projects=heading_blocks(section(document, "Project Experience")),
        skills=skills,
    )


def set_cell_borderless(paragraph) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "111827")
    borders.append(bottom)
    p_pr.append(borders)


def add_hyperlink(paragraph, text: str, target: str) -> None:
    relationship_id = paragraph.part.relate_to(
        target,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), relationship_id)
    run = OxmlElement("w:r")
    properties = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "111827")
    properties.append(color)
    run.append(properties)
    node = OxmlElement("w:t")
    node.text = text
    run.append(node)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def add_section(document: Document, label: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.style = "Resume Section"
    paragraph.add_run(label)
    set_cell_borderless(paragraph)


def add_entry_header(document: Document, left: str, right: str, *, italic: bool = False) -> None:
    paragraph = document.add_paragraph()
    paragraph.style = "Resume Entry"
    left_run = paragraph.add_run(left)
    left_run.bold = not italic
    left_run.italic = italic
    paragraph.add_run("\t")
    right_run = paragraph.add_run(right)
    right_run.italic = italic


def add_bullet(document: Document, text: str) -> None:
    paragraph = document.add_paragraph(style="Resume Bullet")
    cursor = 0
    for match in re.finditer(r"\\textbf\{([^{}]*)\}", text):
        paragraph.add_run(decode_segment(text[cursor : match.start()]))
        bold = paragraph.add_run(decode_latex(match.group(1)))
        bold.bold = True
        cursor = match.end()
    paragraph.add_run(decode_segment(text[cursor:]))


def configure_styles(document: Document) -> None:
    styles = document.styles
    normal = styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(9.5)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    section_style = styles.add_style("Resume Section", WD_STYLE_TYPE.PARAGRAPH)
    section_style.base_style = normal
    section_style.font.name = "Arial"
    section_style.font.size = Pt(10.5)
    section_style.font.bold = True
    section_style.font.color.rgb = RGBColor(0, 0, 0)
    section_style.paragraph_format.space_before = Pt(5)
    section_style.paragraph_format.space_after = Pt(2)
    section_style.paragraph_format.keep_with_next = True

    entry_style = styles.add_style("Resume Entry", WD_STYLE_TYPE.PARAGRAPH)
    entry_style.base_style = normal
    entry_style.font.name = "Arial"
    entry_style.font.size = Pt(9.5)
    entry_style.paragraph_format.space_before = Pt(2.5)
    entry_style.paragraph_format.keep_with_next = True
    entry_style.paragraph_format.tab_stops.add_tab_stop(Inches(7.15), WD_TAB_ALIGNMENT.RIGHT)

    bullet_style = styles.add_style("Resume Bullet", WD_STYLE_TYPE.PARAGRAPH)
    bullet_style.base_style = normal
    bullet_style.font.name = "Arial"
    bullet_style.font.size = Pt(9.5)
    bullet_style.paragraph_format.left_indent = Inches(0.16)
    bullet_style.paragraph_format.first_line_indent = Inches(-0.11)
    bullet_style.paragraph_format.space_before = Pt(1)
    bullet_style.paragraph_format.keep_together = True


def build_document(resume: Resume, output: Path) -> None:
    document = Document()
    section_settings = document.sections[0]
    section_settings.start_type = WD_SECTION.NEW_PAGE
    section_settings.page_width = Inches(8.5)
    section_settings.page_height = Inches(11)
    section_settings.left_margin = Inches(0.65)
    section_settings.right_margin = Inches(0.65)
    section_settings.top_margin = Inches(0.5)
    section_settings.bottom_margin = Inches(0.5)
    configure_styles(document)

    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(3)
    title_run = title.add_run(resume.name)
    title_run.bold = True
    title_run.font.name = "Arial"
    title_run.font.size = Pt(16)
    title_run.font.color.rgb = RGBColor(0, 0, 0)

    contact = document.add_paragraph()
    contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
    contact.paragraph_format.space_after = Pt(1)
    add_hyperlink(contact, resume.email, f"mailto:{resume.email}")
    contact.add_run(f"  |  {resume.phone}  |  ")
    add_hyperlink(contact, resume.github, f"https://{resume.github}")
    contact.add_run("  |  ")
    add_hyperlink(contact, resume.linkedin, f"https://{resume.linkedin}")

    objective = document.add_paragraph(resume.objective)
    objective.alignment = WD_ALIGN_PARAGRAPH.CENTER
    objective.paragraph_format.space_after = Pt(1)
    for run in objective.runs:
        run.italic = True

    add_section(document, "Education")
    for school, dates, degree, location, detail in resume.education:
        add_entry_header(document, school, location)
        add_entry_header(document, degree, dates, italic=True)
        paragraph = document.add_paragraph(detail)
        paragraph.paragraph_format.space_after = Pt(1)

    add_section(document, "Work Experience")
    for entry in resume.experience:
        add_entry_header(document, entry.title, entry.location)
        add_entry_header(document, entry.subtitle, entry.dates, italic=True)
        for bullet in entry.bullets:
            add_bullet(document, "• " + bullet)

    add_section(document, "Project Experience")
    for entry in resume.projects:
        add_entry_header(document, entry.title, entry.dates)
        subtitle = document.add_paragraph(entry.subtitle)
        subtitle.runs[0].italic = True
        subtitle.paragraph_format.keep_with_next = True
        for bullet in entry.bullets:
            add_bullet(document, "• " + bullet)

    add_section(document, "Technical Skills")
    for label, value in resume.skills:
        paragraph = document.add_paragraph()
        label_run = paragraph.add_run(label + " ")
        label_run.bold = True
        paragraph.add_run(value)

    document.core_properties.title = "Resume Template"
    document.core_properties.author = ""
    document.core_properties.last_modified_by = ""
    document.core_properties.comments = "Generated from the LaTeX source"
    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)


def main() -> None:
    for stem in ("resume_full_time", "resume_coop"):
        resume = parse_resume(LATEX_DIR / f"{stem}.tex")
        output = OUTPUT_DIR / f"{stem}.docx"
        build_document(resume, output)
        print(f"wrote {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
