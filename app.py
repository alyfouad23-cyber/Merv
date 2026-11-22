import io
import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Ultrasound Image Explorer", page_icon="🔬", layout="wide")

st.title("Ultrasound Image Explorer")
st.caption("An educational image-processing prototype for exploring ultrasound images.")

st.warning(
    "Research prototype only. This app does not diagnose disease, identify anatomy, "
    "or determine whether an area is a hematoma, seroma, or another condition. "
    "Do not use it to make medical decisions."
)

st.markdown(
    "Upload a de-identified ultrasound image to view a contrast-enhanced version "
    "and explore regions highlighted by a simple image-processing method."
)

uploaded_file = st.file_uploader(
    "Choose an ultrasound image",
    type=["png", "jpg", "jpeg", "bmp", "tif", "tiff"]
)

with st.sidebar:
    st.header("Image processing")
    clip_limit = st.slider("Contrast enhancement", 1.0, 5.0, 2.0, 0.5)
    grid_size = st.slider("Enhancement detail", 4, 16, 8, 2)
    threshold_value = st.slider("Dark-region threshold", 0, 120, 45, 5)
    min_area = st.slider("Minimum region size (pixels)", 10, 2000, 100, 10)
    st.caption("These controls change image processing only. They are not medical settings.")

if uploaded_file is not None:
    try:
        image_bytes = uploaded_file.getvalue()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        original = np.array(pil_image)
        gray = cv2.cvtColor(original, cv2.COLOR_RGB2GRAY)

        clahe = cv2.createCLAHE(
            clipLimit=float(clip_limit),
            tileGridSize=(int(grid_size), int(grid_size))
        )
        enhanced = clahe.apply(gray)

        blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
        _, dark_mask = cv2.threshold(
            blurred, int(threshold_value), 255, cv2.THRESH_BINARY_INV
        )

        kernel = np.ones((3, 3), np.uint8)
        cleaned_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel)
        count, labels, stats, centroids = cv2.connectedComponentsWithStats(
            cleaned_mask, connectivity=8
        )

        overlay = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
        rows = []
        region_number = 0

        for label_index in range(1, count):
            x, y, width, height, area = stats[label_index]
            if area < int(min_area):
                continue

            region_number += 1
            component = (labels == label_index).astype(np.uint8) * 255
            contours, _ = cv2.findContours(
                component, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            cv2.drawContours(overlay, contours, -1, (255, 145, 0), 2)

            rows.append({
                "Region": region_number,
                "Area (pixels)": int(area),
                "Width (pixels)": int(width),
                "Height (pixels)": int(height),
                "Center X (pixels)": round(float(centroids[label_index][0]), 1),
                "Center Y (pixels)": round(float(centroids[label_index][1]), 1)
            })

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original image")
            st.image(original, use_container_width=True)
        with col2:
            st.subheader("Enhanced image")
            st.image(enhanced, clamp=True, use_container_width=True)

        st.subheader("Highlighted image-processing regions")
        st.image(overlay, use_container_width=True)
        st.caption(
            "Orange outlines show dark regions found by thresholding. They are "
            "not confirmed fluid collections or anatomical structures."
        )

        st.subheader("Region measurements")
        if rows:
            results = pd.DataFrame(rows)
            st.dataframe(results, use_container_width=True, hide_index=True)
            csv_data = results.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download measurements (CSV)",
                data=csv_data,
                file_name="region_measurements.csv",
                mime="text/csv"
            )
        else:
            st.info("No regions met the selected minimum-size setting.")

        enhanced_image = Image.fromarray(enhanced)
        image_buffer = io.BytesIO()
        enhanced_image.save(image_buffer, format="PNG")
        st.download_button(
            "Download enhanced image (PNG)",
            data=image_buffer.getvalue(),
            file_name="enhanced_ultrasound.png",
            mime="image/png"
        )

    except Exception as error:
        st.error("The image could not be processed. Try another supported image file.")
        st.caption(f"Technical detail: {error}")
else:
    st.info("Upload an image to begin exploring the image-processing features.")

st.divider()
st.subheader("Limitations")
st.markdown(
    "- The app uses basic contrast enhancement and pixel thresholding.\n"
    "- Dark regions may be caused by many things, including image settings and artifacts.\n"
    "- Measurements are in pixels, not millimetres, because image scale information is not provided.\n"
    "- The app has not been clinically validated and must not be used for diagnosis or treatment."
)
