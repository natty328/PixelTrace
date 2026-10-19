
"""
PixelTrace - Digital Evidence & Image Analysis

Computer vision toolkit for cybersecurity-focused
visual inspection.

Modes:
1. Image Enhancement
2. Text & Pattern Isolation
3. Evidence Annotation

Original uploaded image bytes are never overwritten.
"""

import hashlib
import io
import json

import cv2
import numpy as np
import streamlit as st

from PIL import Image
from streamlit_drawable_canvas import st_canvas

from image_processing import (
    enhance_image,
    isolate_patterns,
    rectangle_records,
    numbered_annotation_preview
)


# ============================================================
# 1. APP CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PixelTrace | Visual Analysis Lab",
    page_icon="🔎",
    layout="wide"
)

st.title("PixelTrace")
st.header("Digital Evidence & Image Analysis")

st.write(
    "A computer vision toolkit with a cybersecurity "
    "twist for examining screenshots, suspicious emails, "
    "documents, and digital images."
)

st.warning(
    "For visual analysis only. Processed images are "
    "derivatives; always preserve original evidence."
)


# ============================================================
# 2. SIDEBAR CONTROLS
# ============================================================

st.sidebar.header("Analysis Controls")

analysis_mode = st.sidebar.selectbox(
    "Analysis Mode",
    [
        "Image Enhancement",
        "Text & Pattern Isolation",
        "Evidence Annotation"
    ]
)

uploaded_file = st.sidebar.file_uploader(
    "Upload an image",
    type=["png", "jpg", "jpeg"]
)


# ============================================================
# 3. MODE-SPECIFIC SETTINGS
# ============================================================

if analysis_mode == "Image Enhancement":

    st.sidebar.subheader("Enhancement Settings")

    brightness = st.sidebar.slider(
        "Brightness",
        min_value=-100,
        max_value=100,
        value=0
    )

    contrast = st.sidebar.slider(
        "Contrast",
        min_value=0.5,
        max_value=3.0,
        value=1.0,
        step=0.1
    )

    st.sidebar.caption(
        "Adjust brightness and contrast to reveal "
        "details in dark or low-contrast images."
    )

elif analysis_mode == "Text & Pattern Isolation":

    st.sidebar.subheader("Threshold Settings")

    method = st.sidebar.selectbox(
        "Threshold Method",
        ["Global", "Adaptive", "Otsu"]
    )

    threshold = 127
    block_size = 11
    c_value = 2

    if method == "Global":

        threshold = st.sidebar.slider(
            "Threshold Value",
            0, 255, 127
        )

    elif method == "Adaptive":

        block_size = st.sidebar.slider(
            "Neighborhood Size",
            min_value=3,
            max_value=51,
            value=11,
            step=2
        )

        c_value = st.sidebar.slider(
            "C Value",
            min_value=-20,
            max_value=20,
            value=2
        )

    elif method == "Otsu":

        st.sidebar.info(
            "Otsu automatically selects a threshold "
            "using the image's grayscale histogram."
        )

elif analysis_mode == "Evidence Annotation":

    st.sidebar.subheader("Annotation Settings")

    st.sidebar.caption(
        "Draw multiple regions directly on the image. "
        "Add labels, record notes, and export your results."
    )


# ============================================================
# 4. UPLOAD AND VALIDATE IMAGE
# ============================================================

if uploaded_file is None:

    st.info(
        "Upload an image using the sidebar "
        "to begin your analysis."
    )

else:

    image_bytes = uploaded_file.getvalue()

    image_hash = hashlib.sha256(
        image_bytes
    ).hexdigest()

    file_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    bgr_image = cv2.imdecode(
        file_array,
        cv2.IMREAD_COLOR
    )

    if bgr_image is None:
        st.error("Unable to decode the uploaded image.")
        st.stop()

    original_rgb = cv2.cvtColor(
        bgr_image,
        cv2.COLOR_BGR2RGB
    )

    original_height, original_width = original_rgb.shape[:2]


    # ========================================================
    # 5. IMAGE ENHANCEMENT
    # ========================================================

    if analysis_mode == "Image Enhancement":

        enhanced_bgr = enhance_image(
            bgr_image,
            brightness=brightness,
            contrast=contrast
        )

        processed_image = cv2.cvtColor(
            enhanced_bgr,
            cv2.COLOR_BGR2RGB
        )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Original Evidence")
            st.image(
                original_rgb,
                use_container_width=True
            )

        with col2:
            st.subheader("Enhanced Image")
            st.image(
                processed_image,
                use_container_width=True
            )

        st.info(
            f"Brightness: {brightness} | "
            f"Contrast: {contrast:.1f}"
        )

        st.success("Image enhancement complete!")


    # ========================================================
    # 6. TEXT AND PATTERN ISOLATION
    # ========================================================

    elif analysis_mode == "Text & Pattern Isolation":

        processed_image, used_threshold = isolate_patterns(
            bgr_image,
            method=method,
            threshold=threshold,
            block_size=block_size,
            c_value=c_value
        )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Original Evidence")
            st.image(
                original_rgb,
                use_container_width=True
            )

        with col2:
            st.subheader("Processed Image")
            st.image(
                processed_image,
                use_container_width=True
            )

        st.write(f"**Threshold Method:** {method}")

        if used_threshold is not None:
            st.info(
                f"Threshold used: {used_threshold:.1f}"
            )
        else:
            st.info(
                "Adaptive thresholding calculates "
                "different thresholds for local regions."
            )

        st.success("Pattern isolation complete!")


    # ========================================================
    # 7. INTERACTIVE EVIDENCE ANNOTATION
    # ========================================================

    elif analysis_mode == "Evidence Annotation":

        st.divider()

        st.subheader("Original Evidence")

        st.image(
            original_rgb,
            width=350
        )

        st.caption(
            f"Original dimensions: "
            f"{original_width} × {original_height} pixels"
        )

        # ----------------------------------------------------
        # Prepare canvas display
        # ----------------------------------------------------

        display_width = min(700, original_width)

        display_height = max(
            1,
            round(
                original_height
                * display_width / original_width
            )
        )

        display_image = Image.fromarray(
            original_rgb
        ).resize(
            (display_width, display_height),
            Image.Resampling.LANCZOS
        )

        # ----------------------------------------------------
        # Interactive canvas
        # ----------------------------------------------------

        st.subheader("1. Select Regions of Interest")

        st.caption(
            "Draw multiple rectangles around suspicious "
            "areas. Use the toolbar's Edit control "
            "to move or resize them."
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
            key=f"pixeltrace_canvas_{image_hash}"
        )

        # ----------------------------------------------------
        # Extract rectangles
        # ----------------------------------------------------

        objects = []

        if canvas_result.json_data is not None:
            objects = canvas_result.json_data.get(
                "objects",
                []
            )

        annotations = rectangle_records(
            objects,
            (original_width, original_height),
            (display_width, display_height)
        )

        st.write(
            f"**Regions identified: {len(annotations)}**"
        )

        # ----------------------------------------------------
        # Numbered preview
        # ----------------------------------------------------

        st.subheader("2. Numbered Annotation Preview")

        preview = numbered_annotation_preview(
            original_rgb,
            annotations,
            display_width
        )

        if annotations:

            display_preview = preview.resize(
                (display_width, display_height),
                Image.Resampling.LANCZOS
            )

            st.image(
                display_preview,
                caption="Numbered annotation preview"
            )

        else:

            st.info(
                "Draw a rectangle above to generate "
                "the numbered preview."
            )

        # ----------------------------------------------------
        # Analyst labels and notes
        # ----------------------------------------------------

        st.subheader("3. Analyst Annotations")

        st.caption(
            "Each annotation number corresponds to "
            "a numbered rectangle in the preview."
        )

        for annotation in annotations:

            index = annotation["region_number"]
            region_id = annotation["region_id"]
            coords = annotation["coordinates"]

            with st.expander(
                region_id,
                expanded=True
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
                    )
                )

                notes = st.text_area(
                    "Analyst Notes",
                    key=f"{image_hash}_notes_{index}",
                    placeholder=(
                        "Describe your observation "
                        "and why this region matters."
                    )
                )

                annotation["label"] = label
                annotation["notes"] = notes

        # ----------------------------------------------------
        # Export data
        # ----------------------------------------------------

        st.subheader("4. Export Results")

        evidence_record = {
            "application": "PixelTrace",
            "record_type": "Experimental image annotations",
            "source_filename": uploaded_file.name,
            "source_sha256": image_hash,
            "original_dimensions": {
                "width": original_width,
                "height": original_height
            },
            "coordinate_system": "Original image pixels",
            "annotations": annotations,
            "limitations": (
                "Region numbers follow canvas order. "
                "Deleting or reordering rectangles may "
                "change their associated labels. "
                "Only unrotated rectangles are supported. "
                "This prototype does not establish "
                "a forensic chain of custody."
            )
        }

        json_bytes = json.dumps(
            evidence_record,
            indent=2
        ).encode("utf-8")

        jpeg_buffer = io.BytesIO()

        preview.save(
            jpeg_buffer,
            format="JPEG",
            quality=95
        )

        col1, col2 = st.columns(2)

        with col1:

            st.download_button(
                label="Download Annotated JPEG",
                data=jpeg_buffer.getvalue(),
                file_name="pixeltrace_annotated.jpg",
                mime="image/jpeg",
                disabled=not annotations
            )

        with col2:

            st.download_button(
                label="Download Annotation JSON",
                data=json_bytes,
                file_name="pixeltrace_annotations.json",
                mime="application/json",
                disabled=not annotations
            )

        st.caption(
            "The JPEG contains the numbered visual "
            "annotations. The JSON preserves coordinates, "
            "labels, notes, and the original file hash. "
            "Neither download overwrites the uploaded image."
        )

        st.caption(
            "Prototype limitation: labels are associated "
            "with region numbers, not permanent rectangle IDs."
        )

        # ----------------------------------------------------
        # Debug information
        # ----------------------------------------------------

        with st.expander(
            "Developer Debug Information",
            expanded=False
        ):

            st.write(
                "Original SHA-256:",
                image_hash
            )

            st.write(
                "Canvas dimensions:",
                (display_width, display_height)
            )

            st.json(objects)

        st.success("Annotation workspace ready!")
