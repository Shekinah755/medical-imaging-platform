import cv2
import numpy as np
import matplotlib.pyplot as plt


# ==========================
# LOAD + PREPROCESS IMAGE
# ==========================
def load_image(path):
    img = cv2.imread(path)

    if img is None:
        raise ValueError("Image not found at given path")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.normalize(
        gray,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    ).astype(np.uint8)

    return img, gray


# ==========================
# DENOISING
# ==========================
def denoise_image(gray):
    return cv2.fastNlMeansDenoising(
        gray,
        None,
        h=10,
        templateWindowSize=7,
        searchWindowSize=21
    )


# ==========================
# CONTRAST ENHANCEMENT
# CLAHE + GAMMA CORRECTION
# ==========================
def enhance_contrast(img):
    # CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img = clahe.apply(img)

    # Gamma correction
    gamma = 1.3
    lookup = np.array([
        ((i / 255.0) ** (1 / gamma)) * 255
        for i in range(256)
    ]).astype("uint8")

    img = cv2.LUT(img, lookup)

    return img


# ==========================
# SHARPEN IMAGE
# ==========================
def sharpen_image(img):
    blurred = cv2.GaussianBlur(img, (9, 9), 10)

    sharp = cv2.addWeighted(
        img,
        1.5,
        blurred,
        -0.5,
        0
    )

    return sharp


# ==========================
# EDGE DETECTION (SOBEL)
# ==========================
def detect_edges(img):
    sobel_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, 3)
    sobel_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, 3)

    sobel = cv2.magnitude(sobel_x, sobel_y)

    return cv2.convertScaleAbs(sobel)


# ==========================
# FULL PIPELINE
# ==========================
def process_image(path, save_path="enhanced_xray.jpg"):
    original, gray = load_image(path)

    denoised = denoise_image(gray)
    enhanced = enhance_contrast(denoised)
    sharpened = sharpen_image(enhanced)
    edges = detect_edges(sharpened)

    # Save final output
    cv2.imwrite(save_path, sharpened)

    print("Processing complete.")
    print(f"Saved enhanced image at: {save_path}")

    return {
        "original": original,
        "gray": gray,
        "denoised": denoised,
        "enhanced": enhanced,
        "sharpened": sharpened,
        "edges": edges
    }






# ==========================
# Display Results
# ==========================





def show_results(results):
    titles = list(results.keys())
    images = list(results.values())

    plt.figure(figsize=(15, 10))

    for i in range(len(images)):
        plt.subplot(2, 3, i + 1)

        if len(images[i].shape) == 2:
            plt.imshow(images[i], cmap="gray")
        else:
            plt.imshow(cv2.cvtColor(images[i], cv2.COLOR_BGR2RGB))

        plt.title(titles[i])
        plt.axis("off")

    plt.tight_layout()
    plt.show()


# ==========================
# MAIN EXECUTION
# ==========================
if __name__ == "__main__":
    IMAGE_PATH = "../../Radiology_AI_Project/noisy xray image.png"
    results =  process_image(IMAGE_PATH)
    show_results(results)
