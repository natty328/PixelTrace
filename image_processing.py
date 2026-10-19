
"""
PixelTrace - Image Processing Module
------------------------------------

Computer vision functions for digital image analysis.

This module handles:
    1. Image enhancement (brightness and contrast)
    2. Text and pattern isolation (thresholding)
    3. Evidence annotation (rectangles and labels)

All functions operate on NumPy image arrays.
Input color images use OpenCV's BGR color format.

IMPORTANT:
Processed images are derivatives of the original evidence.
Original evidence should always be preserved separately.
"""


# ============================================================
# 1. IMPORTS
# ============================================================

import cv2
import numpy as np


# ============================================================
# 2. IMAGE ENHANCEMENT
# ============================================================

def enhance_image(image, brightness=0, contrast=1.0):
    """
    Enhance an image by adjusting brightness and contrast.

    Parameters:
        image (np.ndarray):
            Original image in BGR format.

        brightness (int):
            Brightness adjustment from -100 to 100.

        contrast (float):
            Contrast multiplier from 0.5 to 3.0.


    Returns:
        np.ndarray:
            Enhanced image in BGR format (uint8).

    Notes:
        Calculations use floating-point values to avoid
        unintended uint8 overflow during processing.
        Final pixel values are clipped to 0-255.
    """

    # Step 1: Convert to floating-point values

    working_image = image.astype(np.float32)

    # Step 2: Adjust contrast across all color channels

    working_image = cv2.multiply(
        working_image,
        (contrast, contrast, contrast, contrast)
    )

    # Step 3: Adjust brightness across all color channels

    working_image = cv2.add(
        working_image,
        (brightness, brightness, brightness, brightness)
    )

    # Step 4: Keep pixel values within the valid range

    working_image = np.clip(working_image, 0, 255)

    # Step 5: Convert back to uint8 for image display
    return working_image.astype(np.uint8)


# ============================================================
# 3. TEXT & PATTERN ISOLATION
# ============================================================

def isolate_patterns(
    image,
    method="Global",
    threshold=127,
    block_size=11,
    c_value=2
):
    """
    Isolate visual patterns using grayscale thresholding.

    Supported methods:
        Global:
            Applies one threshold to the entire image.

        Adaptive:
            Calculates a local threshold for each pixel
            using its surrounding neighborhood.

        Otsu:
            Automatically calculates a global threshold
            from the image's grayscale histogram.

    Parameters:
        image (np.ndarray):
            Original image in BGR format.

        method (str):
            Thresholding method:
            "Global", "Adaptive", or "Otsu".

        threshold (int):
            Global threshold value from 0 to 255.
            Ignored by Adaptive and Otsu.

        block_size (int):
            Neighborhood size for Adaptive thresholding.
            Must be odd and at least 3.

        c_value (int):
            Constant subtracted from the locally
            calculated Adaptive threshold.

    Returns:
        tuple:
            processed_image (np.ndarray):
                Binary grayscale image (uint8).

            used_threshold (float or None):
                Actual threshold used for Global/Otsu.
                None for Adaptive.

    Notes:
        Thresholding converts grayscale intensity into
        black (0) or white (255) pixels.

        This may reveal text, boundaries, or patterns,
        but can also remove image information.
    """

    # Step 1: Convert BGR image to grayscale

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # --------------------------------------------------------
    # Method A: Global Thresholding
    # --------------------------------------------------------

    if method == "Global":


        used_threshold, processed_image = cv2.threshold(
            gray,
            threshold,
            255,
            cv2.THRESH_BINARY
        )

    # --------------------------------------------------------
    # Method B: Adaptive Thresholding
    # --------------------------------------------------------

    elif method == "Adaptive":

        # Step 2A: Validate neighborhood size

        if block_size < 3 or block_size % 2 == 0:
            raise ValueError(
                "Block size must be odd and >= 3."
            )

        # Step 2B: Calculate local thresholds

        processed_image = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            block_size,
            c_value
        )

        used_threshold = None

    # --------------------------------------------------------
    # Method C: Otsu Thresholding
    # --------------------------------------------------------

    elif method == "Otsu":


        used_threshold, processed_image = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

    # --------------------------------------------------------
    # Error Handling
    # --------------------------------------------------------

    else:


        raise ValueError(
            f"Unknown threshold method: {method}"
        )

    # Step 3: Return processed image and threshold metadata
    return processed_image, used_threshold


# ============================================================
# 4. EVIDENCE ANNOTATION
# ============================================================

def annotate_image(
    image,
    x=50,
    y=50,
    width=150,
    height=100,
    label="Area of Interest"
):
    """
    Annotate an image with a rectangle and text label.

    This function highlights a selected region of interest
    without modifying the original image array.

    Parameters:
        image (np.ndarray):
            Original image in BGR format.

        x (int):
            Horizontal coordinate of the rectangle's
            upper-left corner.

        y (int):
            Vertical coordinate of the rectangle's
            upper-left corner.

        width (int):
            Width of the annotation rectangle in pixels.

        height (int):
            Height of the annotation rectangle in pixels.

        label (str):
            Text displayed near the highlighted region.

    Returns:
        np.ndarray:
            Annotated copy of the image in BGR format.

    Notes:
        OpenCV uses BGR color ordering.
        The color (0, 0, 255) represents red.

        Image coordinates begin at (0, 0)
        in the upper-left corner.
    """

    # Step 1: Create a copy of the image

    annotated = image.copy()

    # Step 2: Retrieve image dimensions

    image_height, image_width = annotated.shape[:2]

    # Step 3: Validate the rectangle's starting coordinates

    x = max(0, min(int(x), image_width - 1))
    y = max(0, min(int(y), image_height - 1))

    # Step 4: Calculate the rectangle's ending coordinates

    x2 = min(x + int(width), image_width - 1)
    y2 = min(y + int(height), image_height - 1)

    # Step 5: Draw a red rectangle around the selected region
    cv2.rectangle(
        annotated,
        (x, y),
        (x2, y2),
        (0, 0, 255),
        3
    )

    # Step 6: Add a descriptive text label

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

    # Step 7: Return the annotated image
    return annotated
