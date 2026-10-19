
"""
PixelTrace
----------------------------------

Interactive cybersecurity visual analysis lab

This application provides three analysis modes:
    1. Image Enhancement
       Adjust brightness and contrast.

    2. Text & Pattern Isolation
       Apply Global, Adaptive, or Otsu thresholding.

    3. Evidence Annotation
       Highlight regions of interest with rectangles
       and descriptive text labels.

App responsibilities:
    - Configure the Streamlit interface.
    - Accept and validate uploaded images.
    - Collect user-selected processing parameters.
    - Call functions from image_processing.py.
    - Display original and processed images.
    - Explain relevant processing results.

IMPORTANT:
PixelTrace is a visual analysis tool, not a forensic
validation or evidence authentication system.

Processed images are derivatives. Original evidence
must be preserved separately and remain unmodified.
"""


# ============================================================
# 1. IMPORTS & APPLICATION CONFIGURATION
# ============================================================

import cv2
import numpy as np
import streamlit as st

from image_processing import (
    enhance_image,
    isolate_patterns,
    annotate_image
)


# ------------------------------------------------------------
# Configure the browser tab and application layout
# ------------------------------------------------------------

st.set_page_config(
    page_title="PixelTrace | Visual Analysis Lab",
    page_icon="🔎",
    layout="wide"
)


# ------------------------------------------------------------
# Display application title and introduction
# ------------------------------------------------------------

st.title("PixelTrace")

st.header("Digital Evidence & Image Analysis")

st.write(
    "A computer vision toolkit with a cybersecurity twist "
    "for examining screenshots, suspicious emails, and "
    "digital images."
)

st.warning(
    "For visual analysis only. Processed images are "
    "derivatives; always preserve original evidence."
)


# ============================================================
# 2. SIDEBAR: ANALYSIS CONTROLS
# ============================================================

st.sidebar.header("Analysis Controls")


# ------------------------------------------------------------
# Step 1: Select an analysis mode
# ------------------------------------------------------------

analysis_mode = st.sidebar.selectbox(
    "Analysis Mode",
    [
        "Image Enhancement",
        "Text & Pattern Isolation",
        "Evidence Annotation"
    ]
)


# ------------------------------------------------------------
# Step 2: Upload an image for analysis
# ------------------------------------------------------------

uploaded_file = st.sidebar.file_uploader(
    "Upload an image",
    type=["png", "jpg", "jpeg"]
)


# ============================================================
# 3. MODE-SPECIFIC CONTROLS
# ============================================================

# Each analysis mode displays only its relevant controls.
# Streamlit automatically reruns the application when
# a user changes a slider or dropdown selection.


# ------------------------------------------------------------
# Mode A: Image Enhancement
# ------------------------------------------------------------

if analysis_mode == "Image Enhancement":

    st.sidebar.subheader("Enhancement Settings")

    # Brightness
    brightness = st.sidebar.slider(
        "Brightness",
        min_value=-100,
        max_value=100,
        value=0
    )

    # Contrast
    contrast = st.sidebar.slider(
        "Contrast",
        min_value=0.5,
        max_value=3.0,
        value=1.0,
        step=0.1
    )

    st.sidebar.caption(
        "Adjust brightness and contrast to improve "
        "the visibility of image details."
    )


# ------------------------------------------------------------
# Mode B: Text & Pattern Isolation
# ------------------------------------------------------------

elif analysis_mode == "Text & Pattern Isolation":

    st.sidebar.subheader("Threshold Settings")

    # Select one of three thresholding algorithms.
    method = st.sidebar.selectbox(
        "Threshold Method",
        ["Global", "Adaptive", "Otsu"]
    )

    # Initialize default values for all threshold methods.

    threshold = 127
    block_size = 11
    c_value = 2

    # --------------------------------------------------------
    # Method A: Global Thresholding
    # --------------------------------------------------------

    if method == "Global":

        threshold = st.sidebar.slider(
            "Threshold Value",
            min_value=0,
            max_value=255,
            value=127
        )

        st.sidebar.caption(
            "Pixels above this value become white; "
            "others become black."
        )

    # --------------------------------------------------------
    # Method B: Adaptive Thresholding
    # --------------------------------------------------------

    elif method == "Adaptive":

        # Neighborhood size must be odd and at least 3.
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

        st.sidebar.caption(
            "Adaptive thresholding calculates a local "
            "threshold for each neighborhood."
        )

    # --------------------------------------------------------
    # Method C: Otsu Thresholding
    # --------------------------------------------------------

    elif method == "Otsu":

        st.sidebar.info(
            "Otsu automatically calculates a global "
            "threshold using the grayscale histogram."
        )


# ------------------------------------------------------------
# Mode C: Evidence Annotation
# ------------------------------------------------------------

elif analysis_mode == "Evidence Annotation":

    st.sidebar.subheader("Annotation Settings")

    st.sidebar.caption(
        "Highlight a region of interest using a red "
        "rectangle and descriptive label."
    )

    # Coordinates represent the rectangle's upper-left corner

    x = st.sidebar.number_input(
        "Starting X Coordinate",
        min_value=0,
        value=50,
        step=10
    )

    y = st.sidebar.number_input(
        "Starting Y Coordinate",
        min_value=0,
        value=50,
        step=10
    )


    annotation_width = st.sidebar.number_input(
        "Rectangle Width",
        min_value=1,
        value=150,
        step=10
    )

    annotation_height = st.sidebar.number_input(
        "Rectangle Height",
        min_value=1,
        value=100,
        step=10
    )

    # The label describes the highlighted region.
    annotation_label = st.sidebar.text_input(
        "Annotation Label",
        value="Area of Interest",
        max_chars=100
    )

    st.sidebar.caption(
        "Coordinates begin at (0, 0) in the upper-left "
        "corner of the original image."
    )


# ============================================================
# 4. IMAGE LOADING & VALIDATION
# ============================================================

if uploaded_file is None:

    st.info(
        "Upload an image using the sidebar to begin "
        "your analysis."
    )

else:

    # --------------------------------------------------------
    # Step 1: Read uploaded image bytes
    # --------------------------------------------------------

    file_bytes = np.frombuffer(
        uploaded_file.getvalue(),
        dtype=np.uint8
    )

    # --------------------------------------------------------
    # Step 2: Decode the image using OpenCV
    # --------------------------------------------------------

    bgr_image = cv2.imdecode(
        file_bytes,
        cv2.IMREAD_COLOR
    )

    # --------------------------------------------------------
    # Step 3: Validate successful decoding
    # --------------------------------------------------------

    if bgr_image is None:

        st.error(
            "The uploaded file could not be decoded "
            "as an image."
        )

        st.stop()

    # --------------------------------------------------------
    # Step 4: Prepare the original image for display
    # --------------------------------------------------------

    # OpenCV uses BGR; Streamlit displays RGB arrays.
    original_rgb = cv2.cvtColor(
        bgr_image,
        cv2.COLOR_BGR2RGB
    )



    # ========================================================
    # 5. IMAGE PROCESSING
    # ========================================================


    # --------------------------------------------------------
    # Mode A: Image Enhancement
    # --------------------------------------------------------

    if analysis_mode == "Image Enhancement":

        # Apply the selected brightness and contrast.
        enhanced_bgr = enhance_image(
            bgr_image,
            brightness=brightness,
            contrast=contrast
        )

        # Convert the processed BGR image to RGB.
        processed_image = cv2.cvtColor(
            enhanced_bgr,
            cv2.COLOR_BGR2RGB
        )

        result_title = "Enhanced Image"
        used_threshold = None


    # --------------------------------------------------------
    # Mode B: Text & Pattern Isolation
    # --------------------------------------------------------

    elif analysis_mode == "Text & Pattern Isolation":

        # Apply the selected thresholding algorithm.
        processed_image, used_threshold = isolate_patterns(
            bgr_image,
            method=method,
            threshold=threshold,
            block_size=block_size,
            c_value=c_value
        )


        result_title = "Processed Image"


    # --------------------------------------------------------
    # Mode C: Evidence Annotation
    # --------------------------------------------------------

    elif analysis_mode == "Evidence Annotation":

        # Draw a rectangle and label on a copied image.
        annotated_bgr = annotate_image(
            bgr_image,
            x=x,
            y=y,
            width=annotation_width,
            height=annotation_height,
            label=annotation_label
        )

        # Convert annotated image from BGR to RGB.
        processed_image = cv2.cvtColor(
            annotated_bgr,
            cv2.COLOR_BGR2RGB
        )

        result_title = "Annotated Evidence"
        used_threshold = None


    # ========================================================
    # 6. DISPLAY RESULTS
    # ========================================================


    st.divider()

    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # Left Column: Original Evidence
    # --------------------------------------------------------

    with col1:

        st.subheader("Original Evidence")

        st.image(
            original_rgb,
            width="stretch"
        )


    # --------------------------------------------------------
    # Right Column: Processed Image
    # --------------------------------------------------------

    with col2:

        st.subheader(result_title)

        st.image(
            processed_image,
            width="stretch",
            clamp=True
        )


    # ========================================================
    # 7. ANALYSIS INFORMATION
    # ========================================================

    # Provide contextual information about the selected
    # processing method and its parameters.


    # --------------------------------------------------------
    # Thresholding Information
    # --------------------------------------------------------

    if analysis_mode == "Text & Pattern Isolation":

        st.write(
            f"**Threshold Method:** {method}"
        )

        # Global and Otsu return a numeric threshold.
        if used_threshold is not None:

            st.info(
                f"Threshold used: {used_threshold:.1f}"
            )

        # Adaptive calculates different local thresholds.
        else:

            st.info(
                "Adaptive thresholding uses locally "
                "calculated thresholds."
            )


    # --------------------------------------------------------
    # Annotation Information
    # --------------------------------------------------------

    elif analysis_mode == "Evidence Annotation":

        st.write(
            f"**Annotation Label:** {annotation_label}"
        )

        st.info(
            f"Starting coordinates: ({x}, {y}) | "
            f"Rectangle dimensions: "
            f"{annotation_width} × {annotation_height} pixels"
        )

        st.caption(
            "Annotations are visual overlays. "
            "They do not establish the authenticity "
            "or meaning of the highlighted content."
        )


    # --------------------------------------------------------
    # Processing Status
    # --------------------------------------------------------

    st.success("Image processing complete!")
