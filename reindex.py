#import sys
#from PIL import Image
#import math
import sys
from PIL import Image
from scipy.spatial import cKDTree
import numpy as np

def load_hex_palette(path):
    """Load colors from a GIMP-exported hex palette text file"""
    colors = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") and len(line) == 7:
                try:
                    r = int(line[1:3], 16)
                    g = int(line[3:5], 16)
                    b = int(line[5:7], 16)
                    colors.append((r, g, b))
                except ValueError:
                    continue
    return colors

'''
def find_nearest_color(color, palette):
    """Find the nearest color index in the palette"""
    r1, g1, b1 = color
    min_dist = float('inf')
    nearest_index = 0
    for i, (r2, g2, b2) in enumerate(palette):
        dist = (r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2
        if dist < min_dist:
            min_dist = dist
            nearest_index = i
    return nearest_index

def convert_to_indexed(input_path, palette_path, output_path):
    img = Image.open(input_path).convert("RGB")
    width, height = img.size
    src_pixels = img.load()

    palette = load_hex_palette(palette_path)
    if len(palette) > 256:
        print("Error: Palette has more than 256 colors.")
        sys.exit(1)

    # Prepare target image
    indexed_img = Image.new("P", (width, height))

    # Flatten the palette to fit Pillow's expected format
    flat_palette = [0] * (256 * 3)
    for i, (r, g, b) in enumerate(palette):
        flat_palette[i*3:i*3+3] = [r, g, b]
    indexed_img.putpalette(flat_palette)

    dst_pixels = indexed_img.load()
    for y in range(height):
        for x in range(width):
            dst_pixels[x, y] = find_nearest_color(src_pixels[x, y], palette)

    indexed_img.save(output_path, format="PNG")
#    print(f"Saved indexed PNG to: {output_path}")
'''
'''
def convert_to_indexed(input_path, palette_path, output_path):
    # Load image
    img = Image.open(input_path).convert("RGB")
    pixels = np.array(img)
    height, width, _ = pixels.shape

    # Load palette and build KD-tree
    palette = load_hex_palette(palette_path)
    if len(palette) > 256:
        print("Error: Palette has more than 256 colors.")
        sys.exit(1)

    palette_array = np.array(palette)
    kdtree = cKDTree(palette_array)

    # Flatten image to Nx3, query KD-tree
    flat_pixels = pixels.reshape(-1, 3)
    _, indices = kdtree.query(flat_pixels)

    # Rebuild indexed image
    indexed_image = Image.fromarray(indices.reshape((height, width)).astype(np.uint8), mode='P')

    # Set palette
    flat_palette = [0] * 768
    for i, (r, g, b) in enumerate(palette):
        flat_palette[i*3:i*3+3] = [r, g, b]
    indexed_image.putpalette(flat_palette)

    # Save result
    indexed_image.save(output_path, format="PNG")

    # Save raw index data
    with open(output_raw, "wb") as f:
        f.write(index_data.tobytes())
    print(f"Saved raw index data to: {output_raw}")
'''
'''
def convert_to_indexed(input_path, palette_path, output_png, output_raw):
    # Load image as RGB
    img = Image.open(input_path).convert("RGB")
    pixels = np.array(img)
    height, width, _ = pixels.shape

    # Load palette and create KD-tree
    palette = load_hex_palette(palette_path)
    if len(palette) > 256:
        print("Error: Palette has more than 256 colors.")
        sys.exit(1)

    palette_array = np.array(palette)
    kdtree = cKDTree(palette_array)

    # Flatten image and find nearest palette color
    flat_pixels = pixels.reshape(-1, 3)
    _, indices = kdtree.query(flat_pixels)
    index_data = indices.astype(np.uint8).reshape((height, width))

    # Save indexed PNG
    indexed_image = Image.fromarray(index_data, mode='P')
    flat_palette = [0] * 768
    for i, (r, g, b) in enumerate(palette):
        flat_palette[i*3:i*3+3] = [r, g, b]
    indexed_image.putpalette(flat_palette)
    indexed_image.save(output_png, format="PNG")
    print(f"Saved indexed PNG to: {output_png}")

    # Save raw index data
    with open(output_raw, "wb") as f:
        f.write(index_data.tobytes())
    print(f"Saved raw index data to: {output_raw}")
'''


def twiddle_index(x, y):
    """Interleave the bits of x and y (Morton order / Z-order curve)"""
    def part1by1(n):
        n &= 0xFFFF
        n = (n | (n << 8)) & 0x00FF00FF
        n = (n | (n << 4)) & 0x0F0F0F0F
        n = (n | (n << 2)) & 0x33333333
        n = (n | (n << 1)) & 0x55555555
        return n
    return part1by1(y) | (part1by1(x) << 1)

def convert_to_indexed(input_path, palette_path, output_png, output_raw):
    # Load image
    img = Image.open(input_path).convert("RGB")
    width, height = img.size
    if width != height or (width & (width - 1)) != 0:
        print("Error: Image must be square and power-of-two dimensions (e.g. 32x32, 64x64).")
        sys.exit(1)

    pixels = np.array(img)
    palette = load_hex_palette(palette_path)
    if len(palette) > 256:
        print("Error: Palette has more than 256 colors.")
        sys.exit(1)

    # KD-tree for fast color matching
    kdtree = cKDTree(np.array(palette))
    flat_pixels = pixels.reshape(-1, 3)
    _, indices = kdtree.query(flat_pixels)
    indexed = indices.astype(np.uint8).reshape((height, width))

    # Save indexed PNG
    indexed_image = Image.fromarray(indexed, mode='P')
    flat_palette = [0] * 768
    for i, (r, g, b) in enumerate(palette):
        flat_palette[i*3:i*3+3] = [r, g, b]
    indexed_image.putpalette(flat_palette)
    indexed_image.save(output_png)
#    print(f"Saved indexed PNG to: {output_png}")

    # Generate twiddled data
    twiddled_data = bytearray(width * height)
    for y in range(height):
        for x in range(width):
            addr = twiddle_index(x, y)
            twiddled_data[addr] = indexed[y, x]

    with open(output_raw, "wb") as f:
        f.write(twiddled_data)
#    print(f"Saved twiddled raw data to: {output_raw}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python quantize_with_gimp_hex_palette.py input.png palette.txt output.png")
        sys.exit(1)

    input_file_prefix = sys.argv[1]
    output_file_prefix = sys.argv[2]

    for i in range(0,321):
        formatted = f"{i:03d}"
        full_infile_name = input_file_prefix + formatted + ".png"
        full_outfile_name = output_file_prefix + formatted + ".png"
        full_outraw_name = output_file_prefix + formatted + ".raw"
#        replace_fully_transparent_with_magenta(full_infile_name, full_outfile_name)
        convert_to_indexed(full_infile_name, sys.argv[3], full_outfile_name, full_outraw_name)
