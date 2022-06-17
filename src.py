
import sys
import os
import time
import datetime
import random
import string
import subprocess

import numpy as np
import cv2

from PIL import Image

import argparse

parser = argparse.ArgumentParser(description='PNG to SNES Tile Converter')
parser.add_argument('-i', '--input', dest='input_file', required=True, help='Input PNG file')
parser.add_argument('-o', '--output', dest='output_file', required=True, help='Output SMC file')
parser.add_argument('-b', '--bank', dest='bank', type=int, default=0, help='Bank number')
parser.add_argument('-a', '--address', dest='address', type=int, default=0, help='Starting address')
parser.add_argument('-c', '--compress', dest='compress', type=int, default=0, help='Compress output file')
parser.add_argument('-p', '--palette', dest='palette_file', help='Palette file')
parser.add_argument('-t', '--tileset', dest='tileset_file', help='Tileset file')
args = parser.parse_args()

input_file = args.input_file
output_file = args.output_file
bank = args.bank
address = args.address
compress = args.compress
palette_file = args.palette_file
tileset_file = args.tileset_file

# Load image
img = Image.open(input_file)

# Get image dimensions
width, height = img.size

# Check image dimensions
if width % 8 != 0 or height % 8 != 0:
    print('Image dimensions must be a multiple of 8')
    sys.exit()

# Get image pixels
pixels = img.load()

# Convert pixels to 2D array
pixel_array = np.zeros((height, width), dtype=np.uint8)
for y in range(height):
    for x in range(width):
        pixel = pixels[x, y]
        pixel_array[y, x] = pixel[0]

# Convert image to grayscale
gray_image = cv2.cvtColor(pixel_array, cv2.COLOR_BGR2GRAY)

# Invert image
inverted_image = cv2.bitwise_not(gray_image)

# Threshold image
ret, thresh_image = cv2.threshold(inverted_image, 127, 255, cv2.THRESH_BINARY)

# Get image dimensions
height, width = thresh_image.shape

# Initialize tile ID
tile_id = 0

# Initialize address
cur_address = address

# Initialize byte array
byte_array = bytearray()

# Process image
for y in range(0, height, 8):
    for x in range(0, width, 8):
        # Get tile pixels
        tile_pixels = thresh_image[y:y+8, x:x+8]

        # Flip tile vertically
        flipped_tile_pixels = np.flip(tile_pixels, 0)

        # Convert tile to 1D array
        tile_array = flipped_tile_pixels.ravel()

        # Loop through tile pixels
        for i in range(0, len(tile_array), 2):
            # Get pixel values
            p1 = tile_array[i]
            p2 = tile_array[i+1]

            # Calculate pixel values
            b1 = p1 // 16
            b2 = (p1 % 16) * 16
            b3 = p2 // 16
            b4 = (p2 % 16) * 16

            # Calculate byte value
            byte_val = b1 + b2 + b3 + b4

            # Add byte to array
            byte_array.append(byte_val)

        # Increment tile ID
        tile_id += 1

        # Increment address
        cur_address += 16

        # Check for end of bank
        if cur_address == 0x8000:
            cur_address = 0
            bank += 1

# Get output file path
output_path = os.path.abspath(output_file)

# Get output file name
output_name = os.path.basename(output_path)

# Get output file directory
output_dir = os.path.dirname(output_path)

# Check if output directory exists
if not os.path.exists(output_dir):
    # Create output directory
    os.makedirs(output_dir)

# Open output file
with open(output_path, 'wb') as f:
    # Write bank number
    f.write(bank.to_bytes(1, byteorder='little'))

    # Write tile ID
    f.write(tile_id.to_bytes(2, byteorder='little'))

    # Write address
    f.write(address.to_bytes(2, byteorder='little'))

    # Write byte array
    f.write(byte_array)

# Check if file should be compressed
if compress:
    # Get file name without extension
    output_name_no_ext = os.path.splitext(output_name)[0]

    # Get temp file path
    temp_path = os.path.join(output_dir, output_name_no_ext + '.tmp')

    # Open output file
    with open(output_path, 'rb') as f_in, open(temp_path, 'wb') as f_out:
        # Compress file
        subprocess.run(['snescom', '-o', output_name, output_name], stdin=f_in, stdout=f_out)

    # Remove output file
    os.remove(output_path)

    # Rename temp file
    os.rename(temp_path, output_path)

# Check if palette file was specified
if palette_file:
    # Get palette file path
    palette_path = os.path.abspath(palette_file)

    # Get palette file name
    palette_name = os.path.basename(palette_path)

    # Get palette file directory
    palette_dir = os.path.dirname(palette_path)

    # Check if palette directory exists
    if not os.path.exists(palette_dir):
        # Create palette directory
        os.makedirs(palette_dir)

    # Open palette file
    with open(palette_path, 'w') as f:
        # Write palette
        for i in range(0, 16):
            # Calculate palette valuesRESTART PILOT:
            r = i * 16
            g = i * 16
            b = i * 16

            # Write palette entry
            f.write('{:02X}{:02X}{:02X}\n'.format(r, g, b))

# Check if tileset file was specified
if tileset_file:
    # Get tileset file path
    tileset_path = os.path.abspath(tileset_file)

    # Get tileset file name
    tileset_name = os.path.basename(tileset_path)

    # Get tileset file directory
    tileset_dir = os.path.dirname(tileset_path)

    # Check if tileset directory exists
    if not os.path.exists(tileset_dir):
        # Create tileset directory
        os.makedirs(tileset_dir)

    # Open tileset file
    with open(tileset_path, 'wb') as f:
        # Write tileset
        for y in range(0, height, 8):
            for x in range(0, width, 8):
                # Get tile pixels
                tile_pixels = thresh_image[y:y+8, x:x+8]

                # Flip tile vertically
                flipped_tile_pixels = np.flip(tile_pixels, 0)

                # Convert tile to 1D array
                tile_array = flipped_tile_pixels.ravel()

                # Loop through tile pixels
                for i in range(0, len(tile_array), 2):
                    # Get pixel values
                    p1 = tile_array[i]
                    p2 = tile_array[i+1]

                    # Calculate pixel values
                    b1 = p1 // 16
                    b2 = (p1 % 16) * 16
                    b3 = p2 // 16
                    b4 = (p2 % 16) * 16

                    # Calculate byte value
                    byte_val = b1 + b2 + b3 + b4

                    # Add byte to array
                    f.write(byte_val.to_bytes(1, byteorder='little'))
