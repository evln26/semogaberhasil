import cv2
import requests
from pyzbar.pyzbar import decode
from time import sleep
from rpi_lcd import LCD

# Ubidots API Credentials
TOKEN = "BBFF-b81449a3167b17037771ad91d96b8508ff5"
DEVICE_LABEL = "kelompoku"
BARCODE_LABEL = "barcode"
STOCK_IN_LABEL = "stock_in"
STOCK_OUT_LABEL = "stock_out"

# Initialize the camera
cap = cv2.VideoCapture(0)  # 0 indicates the default camera (usually the laptop's built-in camera)

# Initialize the LCD
lcd = LCD()

# Dictionary to store individual barcode counts
barcode_counts = {
    "sepatu": 0,
    "topi": 0,
    "dasi": 0,
    "sabuk": 0,
    "penggaris": 0
}

def send_data_to_ubidots(label, quantity):
    # Send the stock data to the respective variable
    stock_payload = {
        label: quantity
    }

    url = f"https://stem.ubidots.com/app/devices/64db21c4358957000c29f935"
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    try:
        response = requests.post(url=url, headers=headers, json=stock_payload)
        if response.status_code == 200:
            print(f"Stock data sent to Ubidots: {label}={quantity}")
        else:
            print(f"Failed to send stock data to Ubidots. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print("Connection error:", e)

def display_on_lcd(text):
    lcd.text(text, 1)

item_count = 0

lcd.text("Scan the Code... ", 1)

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    # Decode the barcode in the frame
    barcodes = decode(frame)

    # Loop through all detected barcodes
    for barcode in barcodes:
        # Extract the data from the barcode
        barcode_data = barcode.data.decode('utf-8')

        # Get the location of the barcode
        rect_points = barcode.rect

        # Draw a rectangle around the barcode
        cv2.rectangle(frame, (rect_points[0], rect_points[1]), (rect_points[0] + rect_points[2], rect_points[1] + rect_points[3]), (0, 255, 0), 2)

        # Display the barcode data
        cv2.putText(frame, barcode_data, (rect_points[0], rect_points[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Check if the scanned barcode is one of the fixed barcodes
        if barcode_data in barcode_counts:
            # Determine whether it's a stock in or stock out operation (you should implement this logic)
            is_stock_in = True  # Example: Assume all barcodes are for stock in

            # Update the count for the barcode
            barcode_counts[barcode_data] += 1

            # Send stock data to Ubidots based on stock in or stock out
            if is_stock_in:
                send_data_to_ubidots(STOCK_IN_LABEL, 1)  # Increase stock in by 1
            else:
                send_data_to_ubidots(STOCK_OUT_LABEL, 1)  # Increase stock out by 1


            # Display the barcode data on the LCD
            display_on_lcd(f"Scanned Barcode is {barcode_data}")
            sleep(2)  # Display for 2 seconds
            display_on_lcd("   Item Added")
            sleep(2)


            # Update and print the total item count
            item_count += 1
            print(f"Scanned Barcode is {barcode_data}")
            print("   Item Added")
            print(f"  Total Item = {item_count}")


            display_on_lcd(f"  Total Item = {item_count}")
            sleep(1)
    # Display the frame with detected barcodes
    cv2.imshow('Barcode Reader', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()
