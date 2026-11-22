# Ultrasound Image Explorer

An educational Streamlit prototype for exploring ultrasound images with basic image processing.

## What it does

- Accepts PNG, JPG, JPEG, BMP, and TIFF images.
- Displays the uploaded image.
- Applies CLAHE contrast enhancement.
- Highlights dark image regions using thresholding and connected-component analysis.
- Reports region dimensions and pixel area.
- Exports measurements as CSV and the enhanced image as PNG.

## Run on Windows

1. Install Python 3.10 or newer.
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

5. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt and run:

   ```bat
   .venv\Scripts\activate.bat
   ```

6. Install the packages:

   ```bash
   python -m pip install -r requirements.txt
   ```

7. Start the app:

   ```bash
   python -m streamlit run app.py
   ```

## Important research limitation

This is an image-processing demonstration, not a medical device. It does not identify anatomy, diagnose a condition, or classify hematoma versus seroma. Dark image regions are only candidates produced by a simple thresholding method. The app has not been clinically validated. Do not use it for medical decisions.

Use only images you are authorized to use and remove patient names, dates of birth, identifiers, and other personal information before uploading them.
