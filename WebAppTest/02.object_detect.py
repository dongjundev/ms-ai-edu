import requests
from dotenv import load_dotenv
import os
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

SUBSCRIPTION_KEY=os.getenv("SUBSCRIPTION_KEY")
ENDPOINT=os.getenv("ENDPOINT")

def analyze_image(image_path):
    ENDPOINT_URL = ENDPOINT + "vision/v3.2/analyze"

    params = {"visualFeatures": "Categories,Description,Color"}
    headers = {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Content-Type": "application/octet-stream"
    }

    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
    except Exception as e:
        print(f"Error reading image file: {e}")
        return None
    
    response = requests.post(ENDPOINT_URL, params=params, headers=headers, data=image_data)
    if response.status_code == 200:
        analysis = response.json()
        return analysis
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
# Object detect function
def object_detect(image_path):
    ENDPOINT_URL = ENDPOINT + "vision/v3.2/detect"

    headers = {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Content-Type": "application/octet-stream"
    }

    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
    except Exception as e:
        print(f"Error reading image file: {e}")
        return None
    
    response = requests.post(ENDPOINT_URL, headers=headers, data=image_data)
    if response.status_code == 200:
        detection = response.json()
        return detection
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# create bounding box function
def create_bounding_box(image_path, detection_data):
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image file: {e}")
        return None
    
    draw = ImageDraw.Draw(image)

    for obj in detection_data.get('objects', []):
        rect = obj['rectangle']
        x, y, w, h = rect['x'], rect['y'], rect['w'], rect['h']
        draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
        draw.text((x, y), obj['object'], fill="red")

    # Save the modified image
    parts = image_path.rsplit('.', 1)

    if len(parts) ==2:
        output_path = f"{parts[0]}_annotated.{parts[1]}"
    else:
        output_path = f"{image_path}_annotated"

    image.save(output_path)
    print(f"Annotated image saved as {output_path}")
    image.show()

# OCR function
def ocr_image(image_path):
    ENDPOINT_URL = ENDPOINT + "vision/v3.2/ocr"

    headers = {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Content-Type": "application/octet-stream"
    }

    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
    except Exception as e:
        print(f"Error reading image file: {e}")
        return None
    
    response = requests.post(ENDPOINT_URL, headers=headers, data=image_data)
    if response.status_code == 200:
        ocr_result = response.json()
        return ocr_result
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def main():
    image_path = input("Enter the path to the image file: ")

    print("1. Analyze Image")
    print("2. Object Detect")
    print("3. OCR Image")
    choice = input("Choose an option (1, 2, or 3): ")

    if choice == '1':
        result = analyze_image(image_path)
        if result:
            print("Result:")
            print(result)
    elif choice == '2':
        result = object_detect(image_path)
        if result:
            create_bounding_box(image_path, result)
        else:
            print("No objects detected or an error occurred.")
    elif choice == '3':
        result = ocr_image(image_path)
        if result:
            print("OCR Result:")
            print(result)
        else:
            print("No text detected or an error occurred.")
    else:
        print("Invalid choice. Please select 1, 2, or 3.")
        return

if __name__ == "__main__":
    main()