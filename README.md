# PixelTrace

**A computer vision toolkit for digital evidence and image analysis.**

PixelTrace is a Python web application that applies computer vision techniques to screenshots, documents, photographs, and other digital images. Built with a cybersecurity focus, it allows users to enhance image details, isolate visual patterns, and document regions of interest.

The application was developed as a computer vision course project and is being expanded as a cybersecurity portfolio project.

## Features

### 1. Image Enhancement

- Adjust brightness and contrast using interactive sliders.
- Apply OpenCV image arithmetic.
- Use NumPy clipping to keep pixel values within valid bounds.
- Compare the original and enhanced images.

### 2. Text & Pattern Isolation

- Global thresholding with an adjustable threshold.
- Adaptive Gaussian thresholding for uneven lighting.
- Otsu thresholding for automatic threshold selection.
- Side-by-side original and processed image comparison.

### 3. Evidence Annotation

- Draw multiple rectangles directly on uploaded images.
- Move and resize selected regions.
- Generate a preview with numbered annotation markers.
- Add descriptive labels and analyst notes.
- Record coordinates relative to the original image resolution.
- Export annotated JPEG images and structured JSON records.
- Calculate a SHA-256 hash of the uploaded source file.

## Technologies

- **Python** — Application and processing logic
- **Streamlit** — Interactive web interface
- **OpenCV** — Image processing and computer vision
- **NumPy** — Image arrays and pixel arithmetic
- **Pillow** — Image rendering and export
- **streamlit-drawable-canvas** — Interactive rectangle annotation

## Getting Started

Clone the repository:

```bash
git clone https://github.com/natty328/PixelTrace.git
cd PixelTrace
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the application:

```bash
python -m streamlit run app.py
```

Open the local Streamlit URL displayed in your terminal.

## Project Structure

```text
PixelTrace/
├── app.py                 # Streamlit user interface
├── image_processing.py    # Image processing and annotation logic
├── canvas_test.py         # Experimental annotation prototype
├── requirements.txt       # Python dependencies
├── .gitignore
└── README.md
```

## Evidence Integrity

PixelTrace processes uploaded images in memory and generates separate derivatives. The application does not intentionally overwrite the original uploaded file.

Annotation JSON records include the source file's SHA-256 hash, image dimensions, region coordinates, labels, and analyst notes.

**Important:** PixelTrace is an educational visual analysis prototype. It does not authenticate evidence, detect tampering, or implement a complete forensic chain-of-custody system.

Current limitations include region labels being associated with rectangle order rather than permanent annotation IDs. The interactive annotation tool supports unrotated rectangles.

## Future Development

Potential improvements include persistent annotation identifiers, additional masking and segmentation tools, case-based evidence organization, and more comprehensive evidence documentation.

## Author

Natty Martinez

[GitHub Profile](https://github.com/natty328)

