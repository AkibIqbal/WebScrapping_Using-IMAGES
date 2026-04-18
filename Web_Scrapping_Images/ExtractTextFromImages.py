#This Code is for extracting text from a picture using python. 


def extract_text_from_image(image_path):
    import os
    import pytesseract
    from PIL import Image

    # Tesseract path set
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    """
    Extract text from an image using OCR (Tesseract) and save to a text file.
    """
    import re
    from datetime import datetime
    
    try:
        # Ensure Tesseract executable is available before OCR.
        pytesseract.get_tesseract_version()

        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        
        # Extract source and product from image_path (assuming format: SCREENSHOTS/source_product_timestamp.png)
        filename = os.path.basename(image_path)
        match = re.match(r'(\w+)_(.+)_(\d{8}_\d{6})\.png', filename)
        if match:
            source, product, timestamp = match.groups()
        else:
            source = 'unknown'
            product = 'unknown'
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to TEXTS folder
        os.makedirs('TEXTS', exist_ok=True)
        text_filename = f'TEXTS/{source}_{product}_{timestamp}.txt'
        with open(text_filename, 'w', encoding="utf-8") as file:
            file.write(text)
        
        print(f'Text saved to: {text_filename}')
        return text_filename
    except pytesseract.TesseractNotFoundError:
        print('Error extracting text: tesseract is not installed or not found on PATH.')
        return ""
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""
