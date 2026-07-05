import os
import unicodedata

import pytesseract
from PIL import Image

from core.image_processor import preprocess_image, suggest_psm, upscale_if_needed
from core.pdf_handler import pdf_to_images

PSM_REASONS = {
    "single_line": {"en": "single line of text", "fa": "یک خط متن"},
    "sparse": {"en": "sparse text", "fa": "متن پراکنده"},
    "screenshot": {"en": "screenshot / UI", "fa": "اسکرین‌شات / رابط کاربری"},
    "document": {"en": "full document", "fa": "سند کامل"},
}


def build_tesseract_config(psm=3, oem=1):
    return f"--psm {psm} --oem {oem}"


def resolve_tesseract_path(resource_dir=None):
    import shutil

    candidates = []
    if resource_dir:
        bundled_dir = os.path.join(resource_dir, "Tesseract")
        candidates.extend([
            os.path.join(bundled_dir, "tesseract.exe"),
            os.path.join(bundled_dir, "tesseract"),
        ])

    system_tesseract = shutil.which("tesseract")
    if system_tesseract:
        candidates.append(system_tesseract)

    candidates.extend([
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ])

    for candidate in candidates:
        if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def configure_tesseract(tesseract_path):
    if not tesseract_path:
        raise RuntimeError(
            "Tesseract OCR engine was not found. Install Tesseract or place it in the "
            "project's Tesseract folder."
        )
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    bundled_tessdata = os.path.join(os.path.dirname(tesseract_path), "tessdata")
    if os.path.isdir(bundled_tessdata):
        os.environ["TESSDATA_PREFIX"] = bundled_tessdata
    return pytesseract


def normalize_persian_text(text):
    if not text:
        return text
    text = unicodedata.normalize("NFC", text)
    replacements = {
        "ي": "ی",
        "ك": "ک",
        "ة": "ه",
        "ۀ": "ه",
        "\u0640": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def get_psm_reason_label(reason, language="fa"):
    labels = PSM_REASONS.get(reason, PSM_REASONS["document"])
    return labels.get(language, labels["en"])


def run_ocr(
    image,
    tesseract_path,
    lang="fas+eng",
    tesseract_config=None,
    preprocess=True,
    binarize=False,
    auto_psm=False,
    psm=None,
):
    pytesseract = configure_tesseract(tesseract_path)

    working_image = image.convert("RGB")
    if preprocess:
        working_image = preprocess_image(working_image, binarize=binarize, upscale=True)
    else:
        working_image = upscale_if_needed(working_image)

    if auto_psm:
        psm, _ = suggest_psm(image)
        config = build_tesseract_config(psm=psm)
    else:
        config = tesseract_config or build_tesseract_config(psm=psm or 3)

    text = pytesseract.image_to_string(working_image, lang=lang, config=config)
    if "fas" in lang:
        text = normalize_persian_text(text)
    return text


def ocr_single_file(file_path, options, cancel_event=None, progress_callback=None):
    ext = os.path.splitext(file_path)[1].lower()
    parts = []

    if ext == ".pdf":
        images = pdf_to_images(
            file_path, dpi=300,
            first_page=options["page_from"], last_page=options["page_to"],
        )
        for i, img in enumerate(images):
            if cancel_event and cancel_event.is_set():
                break
            page_num = options["page_from"] + i
            text = run_ocr(
                img, options["tesseract_path"],
                lang=options["lang"],
                tesseract_config=options["tesseract_config"],
                preprocess=options["preprocess"],
                binarize=options["binarize"],
                auto_psm=options["auto_psm"],
            )
            parts.append(f"\n--- Page {page_num} ---\n{text}")
            if progress_callback:
                progress_callback((i + 1) / len(images), page_num, len(images))
    else:
        with Image.open(file_path) as img:
            parts.append(run_ocr(
                img, options["tesseract_path"],
                lang=options["lang"],
                tesseract_config=options["tesseract_config"],
                preprocess=options["preprocess"],
                binarize=options["binarize"],
                auto_psm=options["auto_psm"],
            ))

    return "\n".join(parts)
