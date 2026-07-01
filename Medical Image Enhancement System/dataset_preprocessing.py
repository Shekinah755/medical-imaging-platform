import os
import cv2
import numpy as np


# ============================================================
# DATASET CONFIGURATION
# ============================================================

INPUT_OUTPUT_PAIRS = [
    (
        "mini_chest_xray_dataset/Train/normal",
        "processed_dataset/Train/normal"
    ),
    (
        "mini_chest_xray_dataset/Train/pathological",
        "processed_dataset/Train/pathological"
    ),
    (
        "mini_chest_xray_dataset/Test/normal",
        "processed_dataset/Test/normal"
    ),
    (
        "mini_chest_xray_dataset/Test/pathological",
        "processed_dataset/Test/pathological"
    ),
    (
        "mini_chest_xray_dataset/val/normal",
        "processed_dataset/val/normal"
    ),
    (
        "mini_chest_xray_dataset/val/pathological",
        "processed_dataset/val/pathological"
    )
]


# ============================================================
# CREATE OUTPUT DIRECTORIES
# ============================================================

def create_output_directories():
  #  """
 #   Create output folders if they do not already exist.
   # """
    for _, output_folder in INPUT_OUTPUT_PAIRS:
        os.makedirs(output_folder, exist_ok=True)


# ============================================================
# IMAGE PREPROCESSING PIPELINE
# ============================================================

def preprocess_image(image_path):
   # """
    #Preprocess a chest X-ray image.

    # #Steps:
    # #1. Load image
    # 2. Convert to grayscale
    # 3. Resize to 224x224
    # 4. Normalize intensity values
    # 5. Apply Non-Local Means Denoising
    # 6. Apply CLAHE enhancement
    # """

    image = cv2.imread(image_path)

    if image is None:
        return None

    grayscale = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    resized = cv2.resize(
        grayscale,
        (224, 224)
    )

    normalized = cv2.normalize(
        resized,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    ).astype(np.uint8)

    denoised = cv2.fastNlMeansDenoising(
        normalized,
        None,
        h=10,
        templateWindowSize=7,
        searchWindowSize=21
    )

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(denoised)

    return enhanced


# ============================================================
# PROCESS ENTIRE FOLDER
# ============================================================

def process_folder(input_folder, output_folder):

    if not os.path.exists(input_folder):
        print(f"[ERROR] Folder not found: {input_folder}")
        return

    processed_count = 0
    skipped_count = 0

    print(f"\nProcessing: {input_folder}")

    for filename in os.listdir(input_folder):

        if not filename.lower().endswith(
            (".png", ".jpg", ".jpeg")
        ):
            continue

        input_path = os.path.join(
            input_folder,
            filename
        )

        output_path = os.path.join(
            output_folder,
            filename
        )

        if os.path.exists(output_path):
            skipped_count += 1
            continue

        processed_image = preprocess_image(
            input_path
        )

        if processed_image is None:
            continue

        cv2.imwrite(
            output_path,
            processed_image
        )

        processed_count += 1

    print(
        f"Completed | "
        f"Processed: {processed_count} | "
        f"Skipped: {skipped_count}"
    )


# ============================================================
# IMAGE COUNT VERIFICATION
# ============================================================

def count_images(folder):

    if not os.path.exists(folder):
        return 0

    return len([
        file for file in os.listdir(folder)
        if file.lower().endswith(
            (".png", ".jpg", ".jpeg")
        )
    ])


def verify_dataset():

    print("\n========== DATASET VERIFICATION ==========")

    for input_folder, output_folder in INPUT_OUTPUT_PAIRS:

        input_count = count_images(
            input_folder
        )

        output_count = count_images(
            output_folder
        )

        status = (
            "PASS"
            if input_count == output_count
            else "MISMATCH"
        )

        print(f"\n{input_folder}")
        print(f"Input Images : {input_count}")
        print(f"Output Images: {output_count}")
        print(f"Status       : {status}")


# ============================================================
# CORRUPT IMAGE CHECK
# ============================================================

def check_corrupt_images(folder):

    corrupt_count = 0

    for filename in os.listdir(folder):

        image_path = os.path.join(
            folder,
            filename
        )

        image = cv2.imread(image_path)

        if image is None:
            corrupt_count += 1

    print(
        f"{folder} -> "
        f"Corrupt Images: {corrupt_count}"
    )


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

    create_output_directories()

    for input_folder, output_folder in INPUT_OUTPUT_PAIRS:

        process_folder(
            input_folder,
            output_folder
        )

    verify_dataset()

    print(
        "\nDataset preprocessing completed successfully."
    )