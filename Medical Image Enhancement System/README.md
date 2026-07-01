Medical Image Enhancement System

Overview

The Medical Image Enhancement System is an image processing project developed using Python and OpenCV to improve the visual quality of medical images such as chest X-rays.

The system applies multiple image enhancement techniques including noise reduction, contrast enhancement, brightness adjustment, image sharpening, and edge detection to improve image visibility and aid image interpretation.

---

Objectives

- Reduce image noise while preserving important anatomical structures.
- Improve local image contrast.
- Enhance image brightness and visibility.
- Sharpen image details.
- Visualize image edges and structural boundaries.
- Demonstrate the application of digital image processing techniques in medical imaging.

Features

Image Preprocessing

- Image loading and validation
- Grayscale conversion
- Image normalization
- Image resizing for standardized processing

Noise Reduction

- Non-Local Means Denoising for noise suppression while preserving image details

Contrast Enhancement

- Contrast Limited Adaptive Histogram Equalization (CLAHE) for improved local contrast

Brightness Enhancement

- Gamma Correction for improved visibility of low-intensity regions

Image Sharpening

- Unsharp Masking
- Kernel-based image sharpening

Edge Detection

- Sobel Edge Detection
- Canny Edge Detection

Dataset Processing

- Batch processing of chest X-ray datasets
- Automated preprocessing of training, testing, and validation images
- Creation of organized output datasets for machine learning workflows

Quality Assurance Tools

- Image count verification
- Corrupt image detection
- Sample image visualization for preprocessing validation

Experimental Techniques

The project notebook includes comparative experiments using:

- Mean Filtering
- Gaussian Filtering
- Median Filtering
- Histogram Equalization
- Adaptive Thresholding
- Alternative edge detection methods

Output Generation

- Enhanced image export
- Processed dataset generation
- Visualization of intermediate and final processing stages

Project Structure

Medical_Image_Enhancement_System/

├── main.py

├── experiments.ipynb

├── outputs/

│   ├── enhanced_xray.jpg



└── README.md

---

Technologies Used

- Python
- OpenCV
- NumPy
- Matplotlib
- Jupyter Notebook

---

Processing Pipeline

1. Load image
2. Convert image to grayscale
3. Normalize pixel intensities
4. Apply Non-Local Means Denoising
5. Apply CLAHE for contrast enhancement
6. Apply Gamma Correction
7. Apply Unsharp Masking
8. Generate edge map using Sobel operator
9. Save enhanced image

---

Results

The enhancement pipeline improves image visibility by reducing noise, increasing local contrast, enhancing brightness, and sharpening important image details while preserving anatomical structures.

Sample output images can be found in the outputs folder.

---

Future Improvements

- Support for DICOM images
- Graphical User Interface (GUI)
- Batch image processing
- Deep learning-based enhancement methods
- Integration with Radiology Information Systems (RIS)

---

Author

Denuabu Peters Goodness Godslove

Medical Imaging Student

Project developed for learning and research purposes in medical image processing and enhancement.