import sys
from PIL import Image

def replace_fully_transparent_with_magenta(input_path, output_path):
    # Open the input image and ensure it's RGBA
    img = Image.open(input_path).convert("RGBA")
    pixels = img.load()

    width, height = img.size
    MAGENTA = (255, 0, 255, 255)

    # Replace fully transparent pixels with magenta
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                pixels[x, y] = MAGENTA

    # Convert to RGB (fully opaque) and save
    img.convert("RGB").save(output_path)
#    print(f"Saved: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python replace_transparent.py input.png output.png")
        sys.exit(1)

    input_file_prefix = sys.argv[1]
    output_file_prefix = sys.argv[2]

    for i in range(0,321):
        formatted = f"{i:03d}"
        full_infile_name = input_file_prefix + formatted + ".png"
        full_outfile_name = output_file_prefix + formatted + ".png"
        replace_fully_transparent_with_magenta(full_infile_name, full_outfile_name)
