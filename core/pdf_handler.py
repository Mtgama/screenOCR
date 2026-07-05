import fitz
from PIL import Image


def open_pdf(file_path):
    doc = fitz.open(file_path)
    try:
        catalog = doc.pdf_catalog()
        if catalog:
            doc.xref_set_key(catalog, "StructTreeRoot", "null")
    except Exception:
        pass
    fitz.TOOLS.mupdf_warnings(reset=True)
    return doc


def get_pdf_page_count(file_path):
    doc = open_pdf(file_path)
    count = len(doc)
    doc.close()
    return count


def pdf_to_images(file_path, dpi=300, first_page=None, last_page=None):
    doc = open_pdf(file_path)
    total_pages = len(doc)
    start = max((first_page or 1) - 1, 0)
    end = min((last_page or total_pages) - 1, total_pages - 1)
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    images = []
    for page_num in range(start, end + 1):
        pix = doc[page_num].get_pixmap(matrix=matrix)
        images.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
    doc.close()
    return images
