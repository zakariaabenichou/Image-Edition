from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import uuid
import random

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    print("Webhook received!")
    data = request.json
    top_url = data.get('top_image_url')
    bottom_url = data.get('bottom_image_url')
    title = data.get('title')

    MAKE_WEBHOOK_URL = 'https://hook.eu2.make.com/jb4961zu83d8bwvpxzs2ushd7ecg8ais'
    SAVE_DIRECTORY = r"C:\Users\admin\PycharmProjects\Image\images"

    if not top_url or not bottom_url or not title:
        return jsonify({'error': 'Missing top_image_url, bottom_image_url, or title'}), 400

    try:
        # Download and resize images
        def load_image(url):
            res = requests.get(url)
            res.raise_for_status()
            img = Image.open(BytesIO(res.content)).convert("RGBA")
            return img.resize((1000, 750))
        
        top_img = load_image(top_url)
        bottom_img = load_image(bottom_url)

    except Exception as e:
        print(f"Error loading images: {e}")
        return jsonify({'error': f'Failed to load or process image: {e}'}), 500

    # Create pin canvas
    final_width, final_height = 1000, 1500
    pin = Image.new("RGBA", (final_width, final_height))
    pin.paste(top_img, (0, 0))
    pin.paste(bottom_img, (0, 750))

    # Draw title
    draw = ImageDraw.Draw(pin)
    try:
        font = ImageFont.truetype("LeckerliOne-Regular.ttf", 70)
    except IOError:
        print("Leckerli font not found. Using default.")
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), title, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    padding_x, padding_y, radius = 40, 40, 20
    box_width = text_width + 2 * padding_x
    box_height = text_height + 2 * padding_y
    box_x = (final_width - box_width) // 2 + random.randint(-3, 3)
    box_y = (final_height - box_height) // 2 + random.randint(-3, 3)

    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_width, box_y + box_height],
        radius=radius,
        fill="white"
    )
    draw.text((box_x + padding_x, box_y + padding_y), title, font=font, fill="black")

    # Save image
    sanitized_title = "".join(c for c in title if c.isalnum() or c in (' ', '.', '_')).rstrip().replace(' ', '_')
    unique_id = uuid.uuid4().hex[:8]
    image_filename = f"{sanitized_title}_{unique_id}.png"
    full_image_path = os.path.join(SAVE_DIRECTORY, image_filename)

    try:
        os.makedirs(SAVE_DIRECTORY, exist_ok=True)
        pin.save(full_image_path)
        print(f"Saved to {full_image_path}")
    except Exception as e:
        print(f"Save error: {e}")
        return jsonify({'error': f'Failed to save image: {e}'}), 500

    # Send to Make.com
    try:
        with open(full_image_path, 'rb') as f:
            files = {'image': (image_filename, f.read(), 'image/png')}
            payload = {'title': title}
            print(f"Sending to Make.com: {MAKE_WEBHOOK_URL}")
            response = requests.post(MAKE_WEBHOOK_URL, data=payload, files=files)
            response.raise_for_status()
            print(f"Response: {response.status_code} - {response.text}")
        os.remove(full_image_path)
    except Exception as e:
        print(f"Make.com error: {e}")
        return jsonify({'error': f'Failed to send image to Make.com: {e}'}), 500

    return jsonify({
        'message': 'Image created and sent to Make.com',
        'filename': image_filename,
        'status': response.status_code
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
