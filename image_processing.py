
"""
PixelTrace - Image Processing Module

All OpenCV color images use BGR format.
Processing functions return new images and do not
modify the original evidence.
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


# ============================================================
# IMAGE ENHANCEMENT
# ============================================================

def enhance_image(image, brightness=0, contrast=1.0):
    """Adjust brightness and contrast with safe clipping."""

    working = image.astype(np.float32)

    working = cv2.multiply(
        working,
        (contrast, contrast, contrast, contrast)
    )

    working = cv2.add(
        working,
        (brightness, brightness, brightness, brightness)
    )

    return np.clip(working, 0, 255).astype(np.uint8)


# ============================================================
# THRESHOLDING
# ============================================================

def isolate_patterns(
    image,
    method="Global",
    threshold=127,
    block_size=11,
    c_value=2
):
    """Apply global, adaptive, or Otsu thresholding."""

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if method == "Global":

        used_threshold, result = cv2.threshold(
            gray,
            threshold,
            255,
            cv2.THRESH_BINARY
        )

    elif method == "Adaptive":

        if block_size < 3 or block_size % 2 == 0:
            raise ValueError(
                "Block size must be odd and at least 3."
            )

        result = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            block_size,
            c_value
        )

        used_threshold = None

    elif method == "Otsu":

        used_threshold, result = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

    else:
        raise ValueError(
            f"Unknown threshold method: {method}"
        )

    return result, used_threshold


# ============================================================
# ORIGINAL SINGLE-REGION ANNOTATION
# ============================================================

def annotate_image(
    image,
    x=50,
    y=50,
    width=150,
    height=100,
    label="Area of Interest"
):
    """Retained for compatibility with earlier versions."""

    annotated = image.copy()
    image_height, image_width = annotated.shape[:2]

    x = max(0, min(int(x), image_width - 1))
    y = max(0, min(int(y), image_height - 1))

    x2 = min(x + int(width), image_width - 1)
    y2 = min(y + int(height), image_height - 1)

    cv2.rectangle(
        annotated,
        (x, y),
        (x2, y2),
        (0, 0, 255),
        3
    )

    cv2.putText(
        annotated,
        label,
        (x, max(20, y - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2,
        cv2.LINE_AA
    )

    return annotated


# ============================================================
# CONVERT CANVAS RECTANGLES TO ORIGINAL PIXELS
# ============================================================

def rectangle_records(objects, original_size, canvas_size):
    """
    Extract unrotated rectangles from Fabric.js data.

    Convert display coordinates to original-image pixels.
    """

    original_width, original_height = original_size
    canvas_width, canvas_height = canvas_size

    records = []

    for obj in objects:

        if str(obj.get("type", "")).lower() != "rect":
            continue

        # Rotation and skew require additional transforms.
        if (
            float(obj.get("angle", 0)) != 0
            or float(obj.get("skewX", 0)) != 0
            or float(obj.get("skewY", 0)) != 0
        ):
            continue

        left = float(obj.get("left", 0))
        top = float(obj.get("top", 0))

        width = (
            float(obj.get("width", 0))
            * float(obj.get("scaleX", 1))
        )

        height = (
            float(obj.get("height", 0))
            * float(obj.get("scaleY", 1))
        )

        x1 = round(
            min(left, left + width)
            * original_width / canvas_width
        )

        y1 = round(
            min(top, top + height)
            * original_height / canvas_height
        )

        x2 = round(
            max(left, left + width)
            * original_width / canvas_width
        )

        y2 = round(
            max(top, top + height)
            * original_height / canvas_height
        )

        x1 = max(0, min(original_width - 1, x1))
        y1 = max(0, min(original_height - 1, y1))
        x2 = max(0, min(original_width - 1, x2))
        y2 = max(0, min(original_height - 1, y2))

        if x2 <= x1 or y2 <= y1:
            continue

        number = len(records) + 1

        records.append({
            "region_id": f"Region {number}",
            "region_number": number,
            "coordinates": {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "width": x2 - x1,
                "height": y2 - y1
            }
        })

    return records


# ============================================================
# SCALABLE ANNOTATION FONT
# ============================================================

def load_annotation_font(size):
    """Load a readable font on macOS or Linux."""

    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
    ]

    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            continue

    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


# ============================================================
# CREATE NUMBERED ANNOTATION PREVIEW
# ============================================================

def numbered_annotation_preview(
    original_rgb,
    records,
    canvas_width
):
    """
    Draw numbered rectangles on a COPY of the image.

    Returns a full-resolution PIL image for preview/export.
    """

    preview = Image.fromarray(
        original_rgb.copy()
    ).convert("RGB")

    draw = ImageDraw.Draw(preview)

    image_width, image_height = preview.size

    scale = min(
        1.0,
        canvas_width / image_width
    )

    border_width = max(3, round(3 / scale))
    badge_size = max(30, round(36 / scale))
    font_size = max(18, round(24 / scale))

    font = load_annotation_font(font_size)

    for record in records:

        coords = record["coordinates"]

        x1 = coords["x1"]
        y1 = coords["y1"]
        x2 = coords["x2"]
        y2 = coords["y2"]

        draw.rectangle(
            [x1, y1, x2, y2],
            outline=(255, 0, 0),
            width=border_width
        )

        badge_x = min(
            max(0, x1 + 5),
            max(0, image_width - badge_size)
        )

        badge_y = min(
            max(0, y1 + 5),
            max(0, image_height - badge_size)
        )

        draw.rectangle(
            [
                badge_x,
                badge_y,
                badge_x + badge_size,
                badge_y + badge_size
            ],
            fill=(220, 30, 30),
            outline=(255, 255, 255),
            width=max(2, round(2 / scale))
        )

        draw.text(
            (
                badge_x + badge_size / 2,
                badge_y + badge_size / 2
            ),
            str(record["region_number"]),
            fill=(255, 255, 255),
            font=font,
            anchor="mm"
        )

    return preview
