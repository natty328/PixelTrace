
"""
PixelTrace - Interactive Forensic Annotation Lab

Experimental image annotation module.

Features:
- Upload images
- Draw and edit rectangular annotations
- Display numbered annotation markers
- Record analyst labels and notes
- Convert canvas coordinates to original-image coordinates
- Export annotated JPEG and JSON metadata
- Calculate source image SHA-256 hash

The original uploaded image is never overwritten.
"""

import hashlib
import io
import json
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from streamlit_drawable_canvas import st_canvas


# ============================================================
# 1. APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PixelTrace | Annotation Lab",
    page_icon="🔎",
    layout="wide",
)

st.title("PixelTrace | Forensic Annotation Lab")

st.caption(
    "Identify, label, and document regions of interest "
    "without modifying the original evidence image."
)


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def load_annotation_font(size):
    """
    Load a scalable font for numbered annotation markers.

    Supports common macOS and Linux font locations.
    Falls back to Pillow's scalable default font.
    """

    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]

    for font_path in font_paths:
        if Path(font_path).exists():
            try:
                return ImageFont.truetype(
                    font_path,
                    size=size,
                )
            except OSError:
                pass

    # Pillow 10.1+ supports a scalable default font.
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


# ============================================================
# 3. SESSION STATE
# ============================================================

if "active_image_id" not in st.session_state:
    st.session_state.active_image_id = None


# ============================================================
# 4. IMAGE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload an image",
    type=["png", "jpg", "jpeg"],
)

if uploaded_file is None:

    st.info("Upload an image to begin annotating.")

else:

    # ========================================================
    # 5. READ ORIGINAL IMAGE
    # ========================================================

    image_bytes = uploaded_file.getvalue()

    image_hash = hashlib.sha256(
        image_bytes
    ).hexdigest()

    st.session_state.active_image_id = image_hash

    original = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    original_width, original_height = original.size

    # Limit the interactive canvas to 700 pixels wide.
    max_canvas_width = 700

    scale = min(
        1.0,
        max_canvas_width / original_width,
    )

    display_width = max(
        1,
        round(original_width * scale),
    )

    display_height = max(
        1,
        round(original_height * scale),
    )

    display_image = original.resize(
        (display_width, display_height),
        Image.Resampling.LANCZOS,
    )

    # Conversion factors for original-image coordinates.
    x_ratio = original_width / display_width
    y_ratio = original_height / display_height

    st.write(
        f"**Original image dimensions:** "
        f"{original_width} × {original_height} pixels"
    )

    # ========================================================
    # 6. INTERACTIVE ANNOTATION CANVAS
    # ========================================================

    st.subheader("1. Select Regions of Interest")

    st.caption(
        "Draw rectangles around suspicious regions. "
        "Use the canvas toolbar's Edit option to "
        "move or resize existing rectangles."
    )

    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.15)",
        stroke_width=2,
        stroke_color="#FF0000",
        background_image=display_image,
        update_streamlit=True,
        height=display_height,
        width=display_width,
        drawing_mode="rect",
        key=f"canvas_{image_hash}",
    )

    # ========================================================
    # 7. EXTRACT RECTANGLES
    # ========================================================

    objects = []

    if canvas_result.json_data is not None:
        objects = canvas_result.json_data.get(
            "objects",
            [],
        )

    rectangles = [
        obj
        for obj in objects
        if str(obj.get("type", "")).lower() == "rect"
    ]

    st.write(
        f"**Regions identified: {len(rectangles)}**"
    )

    # ========================================================
    # 8. CREATE NUMBERED ANNOTATION PREVIEW
    # ========================================================

    st.subheader("2. Numbered Annotation Preview")

    # Work on a copy of the image.
    # The original uploaded image remains untouched.
    preview = original.copy()

    draw = ImageDraw.Draw(preview)

    # Scale annotation graphics to remain readable
    # when the full-resolution image is displayed smaller.
    border_width = max(
        3,
        round(3 / scale),
    )

    badge_size = max(
        30,
        round(36 / scale),
    )

    number_font_size = max(
        18,
        round(24 / scale),
    )

    number_font = load_annotation_font(
        number_font_size
    )

    annotations = []

    for index, rectangle in enumerate(
        rectangles,
        start=1,
    ):

        region_id = f"Region {index}"

        # ----------------------------------------------------
        # Canvas coordinates
        # ----------------------------------------------------

        left = float(
            rectangle.get("left", 0)
        )

        top = float(
            rectangle.get("top", 0)
        )

        width = (
            float(rectangle.get("width", 0))
            * float(rectangle.get("scaleX", 1))
        )

        height = (
            float(rectangle.get("height", 0))
            * float(rectangle.get("scaleY", 1))
        )

        # ----------------------------------------------------
        # Convert to original-image coordinates
        # ----------------------------------------------------

        x1 = round(
            min(left, left + width) * x_ratio
        )

        y1 = round(
            min(top, top + height) * y_ratio
        )

        x2 = round(
            max(left, left + width) * x_ratio
        )

        y2 = round(
            max(top, top + height) * y_ratio
        )

        # Keep coordinates inside image boundaries.
        x1 = max(
            0,
            min(original_width - 1, x1),
        )

        y1 = max(
            0,
            min(original_height - 1, y1),
        )

        x2 = max(
            0,
            min(original_width - 1, x2),
        )

        y2 = max(
            0,
            min(original_height - 1, y2),
        )

        # ----------------------------------------------------
        # Draw red rectangle
        # ----------------------------------------------------

        draw.rectangle(
            [x1, y1, x2, y2],
            outline=(255, 0, 0),
            width=border_width,
        )

        # ----------------------------------------------------
        # Draw large numbered badge
        # ----------------------------------------------------

        badge_x = min(
            max(0, x1 + 5),
            max(0, original_width - badge_size),
        )

        badge_y = min(
            max(0, y1 + 5),
            max(0, original_height - badge_size),
        )

        draw.rectangle(
            [
                badge_x,
                badge_y,
                badge_x + badge_size,
                badge_y + badge_size,
            ],
            fill=(220, 30, 30),
            outline=(255, 255, 255),
            width=max(2, round(2 / scale)),
        )

        # Center the annotation number in the badge.
        draw.text(
            (
                badge_x + badge_size / 2,
                badge_y + badge_size / 2,
            ),
            str(index),
            fill=(255, 255, 255),
            font=number_font,
            anchor="mm",
            stroke_width=max(1, round(1 / scale)),
            stroke_fill=(80, 0, 0),
        )

        # ----------------------------------------------------
        # Store annotation coordinates
        # ----------------------------------------------------

        annotations.append({
            "region_id": region_id,
            "region_number": index,
            "coordinates": {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "width": abs(x2 - x1),
                "height": abs(y2 - y1),
            },
        })

    # ========================================================
    # 9. DISPLAY NUMBERED PREVIEW
    # ========================================================

    if annotations:

        # Resize only for screen display.
        # The exported JPEG remains full resolution.
        display_preview = preview.resize(
            (display_width, display_height),
            Image.Resampling.LANCZOS,
        )

        st.image(
            display_preview,
            caption="Numbered annotation preview",
        )

    else:

        st.info(
            "Draw at least one rectangle above "
            "to generate the numbered preview."
        )

    # ========================================================
    # 10. ANALYST ANNOTATIONS
    # ========================================================

    st.subheader("3. Analyst Annotations")

    st.caption(
        "Each annotation number corresponds to "
        "a numbered region in the preview."
    )

    for annotation in annotations:

        index = annotation["region_number"]
        region_id = annotation["region_id"]

        coords = annotation["coordinates"]

        with st.expander(
            region_id,
            expanded=True,
        ):

            st.write(
                f"**Original-image coordinates:** "
                f"({coords['x1']}, {coords['y1']}) "
                f"to ({coords['x2']}, {coords['y2']})"
            )

            label = st.text_input(
                "Annotation Label",
                key=f"{image_hash}_label_{index}",
                placeholder=(
                    "Example: Suspicious solder joint"
                ),
            )

            notes = st.text_area(
                "Analyst Notes",
                key=f"{image_hash}_notes_{index}",
                placeholder=(
                    "Describe your observation "
                    "and why this region matters."
                ),
            )

            annotation["label"] = label
            annotation["notes"] = notes

    # ========================================================
    # 11. EXPORT RESULTS
    # ========================================================

    st.subheader("4. Export Results")

    evidence_record = {
        "application": "PixelTrace",
        "record_type": "Experimental image annotations",
        "source_filename": uploaded_file.name,
        "source_sha256": image_hash,
        "original_dimensions": {
            "width": original_width,
            "height": original_height,
        },
        "coordinate_system": "Original image pixels",
        "annotations": annotations,
        "limitations": (
            "Region numbers are assigned by canvas order. "
            "Deleting or reordering rectangles may change "
            "their associated labels. This prototype does "
            "not establish a forensic chain of custody."
        ),
    }

    json_bytes = json.dumps(
        evidence_record,
        indent=2,
    ).encode("utf-8")

    # Save annotated JPEG to memory.
    # Never overwrite the uploaded image.
    jpeg_buffer = io.BytesIO()

    preview.convert("RGB").save(
        jpeg_buffer,
        format="JPEG",
        quality=95,
    )

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            label="Download Annotation JSON",
            data=json_bytes,
            file_name="pixeltrace_annotations.json",
            mime="application/json",
            disabled=not annotations,
        )

    with col2:

        st.download_button(
            label="Download Annotated JPEG",
            data=jpeg_buffer.getvalue(),
            file_name="pixeltrace_annotated.jpg",
            mime="image/jpeg",
            disabled=not annotations,
        )

    st.caption(
        "The JSON contains coordinates, analyst notes, "
        "and the source image hash. The JPEG contains "
        "the visual annotations. Neither export "
        "overwrites the uploaded image."
    )

    # ========================================================
    # 12. DEBUG INFORMATION
    # ========================================================

    with st.expander(
        "Developer Debug Information",
        expanded=False,
    ):

        st.write(
            "Original SHA-256:",
            image_hash,
        )

        st.write(
            "Canvas scale:",
            scale,
        )

        st.write(
            "Annotation font size:",
            number_font_size,
        )

        st.write(
            "Annotation badge size:",
            badge_size,
        )

        st.write(
            "Loaded font:",
            str(number_font),
        )

        st.json(objects)

    # ========================================================
    # 13. EVIDENCE INTEGRITY NOTICE
    # ========================================================

    st.divider()

    st.caption(
        "PixelTrace creates annotated copies and "
        "metadata records without modifying the "
        "uploaded source image. This prototype "
        "is intended for educational use and does "
        "not implement a complete forensic "
        "chain-of-custody workflow."
    )
