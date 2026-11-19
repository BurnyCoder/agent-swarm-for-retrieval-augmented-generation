"""Exercise actual parser libraries and source links for the supported binary formats."""


def test_office_and_pdf_source_locations(tmp_path):
    from types import SimpleNamespace
    from docx import Document
    from pptx import Presentation
    from openpyxl import Workbook
    from reportlab.pdfgen.canvas import Canvas
    from folderrag.corpus import snapshot
    from folderrag.commands import source_links

    source = tmp_path / "input"
    source.mkdir()
    doc = Document()
    doc.add_heading("Timetable")
    doc.add_paragraph("Copper 41")
    doc.save(source / "notes.docx")
    slides = Presentation()
    slide = slides.slides.add_slide(slides.slide_layouts[0])
    slide.shapes.title.text = "Copper 41"
    slides.save(source / "slides.pptx")
    book = Workbook()
    book.active.title = "Service"
    book.active.append(["Copper 41"])
    book.save(source / "table.xlsx")
    pdf = Canvas(str(source / "route.pdf"))
    pdf.drawString(40, 700, "Header")
    pdf.showPage()
    pdf.drawString(40, 700, "Copper 41")
    pdf.save()
    root = snapshot(source, tmp_path / "snapshots")
    expected = {
        "notes.docx": "Paragraph 2",
        "slides.pptx": "Slide 1",
        "table.xlsx": "Service row 1",
        "route.pdf": "Page 2",
    }
    for name, label in expected.items():
        text = (root / name).read_text()
        pos = text.index("Copper 41")
        cite = dict(
            valid=True,
            path=name,
            offset=pos,
            line=text[:pos].count("\n") + 1,
            quote="Copper 41",
        )
        source_links(source, SimpleNamespace(root=root), [cite])
        assert cite["location"] == label
        assert cite["text_uri"].endswith(f"#L{cite['line']}")
        if name.endswith(".pdf"):
            assert cite["source_uri"].endswith("#page=2")
