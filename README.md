 # ID Document Masking Tool

A web-based tool for masking sensitive information (SSN, Date of Birth, Name) in ID document images using OCR and computer vision.

## Features

- **Upload ID images** (`PNG`, `JPG`, `JPEG`)
- **Mask SSN, Date of Birth, and Name** fields automatically
- **Download the masked result**

## How It Works

1. **Upload** an image of an ID document.
2. **Select** which fields to mask (SSN, DOB, Name).
3. The tool uses **OCR** to detect and mask selected fields.
4. **Download** the processed image.

## Setup

### 1. Install Dependencies

```sh
pip install flask opencv-python pytesseract numpy
```

### 2. Install Tesseract OCR

- **Windows**: Download Tesseract OCR from [UB Mannheim](https://github.com/tesseract-ocr/tesseract/wiki).
- Ensure Tesseract is installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`.
- If installed elsewhere, update the Tesseract path in `app.py`:

  ```python
  pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
  ```

- **macOS**:  
  ```sh
  brew install tesseract
  ```
- **Linux**:  
  ```sh
  sudo apt-get install tesseract-ocr
  ```

### 3. Run the App

```sh
python app.py
```

Open your browser and visit [http://localhost:5000](http://localhost:5000).

## Folder Structure

```
static/
  ├── results/     # Masked images are saved here
  └── uploads/     # Uploaded images are saved here
templates/
  └── index.html   # Main HTML file
app.py             # Main Flask application
README.md          # This file
```

## Usage

1. Start the Flask server.
2. Go to [http://localhost:5000](http://localhost:5000).
3. Upload your ID document image.
4. Select the fields you want to mask (SSN, DOB, Name).
5. Download your masked document.

![Dashboard Preview](output.png.png)


## Notes

- Make sure Tesseract OCR is properly installed and the path is configured in `app.py`.
- Supports image formats: PNG, JPG, JPEG.
- The masking is performed by detecting text regions using OCR; accuracy depends on image quality.




