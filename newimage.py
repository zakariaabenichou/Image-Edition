import random
from PIL import Image, ImageDraw, ImageFont

def create_pinterest_pin(top_image_path, bottom_image_path, title, output_path):
    final_width = 1000
    final_height = 1500
    half_height = final_height // 2

    # Load and resize top and bottom images to 1000x750
    top_img = Image.open(top_image_path).convert("RGBA").resize((final_width, half_height))
    bottom_img = Image.open(bottom_image_path).convert("RGBA").resize((final_width, half_height))

    # Create final blank canvas
    pin = Image.new("RGBA", (final_width, final_height))

    # Paste both images
    pin.paste(top_img, (0, 0))
    pin.paste(bottom_img, (0, half_height))

    # Prepare for drawing
    draw = ImageDraw.Draw(pin)

    # Load custom font
    try:
        font = ImageFont.truetype("LeckerliOne-Regular.ttf", 70)
    except IOError:
        print("Leckerli One font not found, using default font.")
        font = ImageFont.load_default()

    # Measure text
    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Padding and button styling
    padding_x = 40
    padding_y = 20
    radius = 20

    # Compute background box dimensions
    box_width = text_width + 2 * padding_x
    box_height = text_height + 2 * padding_y
    box_x = (final_width - box_width) // 2
    box_y = (final_height - box_height) // 2

    # Draw rounded background
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_width, box_y + box_height],
        radius=radius,
        fill="white"
    )

    # Draw the title text
    text_x = box_x + padding_x
    text_y = box_y + padding_y
    draw.text((text_x, text_y), title, font=font, fill="black")

    # Save the image
    pin.save(output_path)
    print(f"Saved 1000x1500 pin to {output_path}")

# Example usage:
create_pinterest_pin("top.jpg", "top.jpg", "Banana Bread Recipe For U", "pinterest_pin.png")
