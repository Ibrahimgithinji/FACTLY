"""Generate simple PNG icons for the Factly extension using only standard library."""
import struct
import zlib
import os

def create_png(size, color=(31, 41, 55), bg=None):
    """Create a simple PNG icon with a centered 'F' letter."""
    if bg is None:
        bg = color

    # Create RGBA pixel data
    pixels = []
    for y in range(size):
        row = []
        for x in range(size):
            cx, cy = size // 2, size // 2
            dx, dy = x - cx, y - cy
            dist = (dx * dx + dy * dy) ** 0.5
            radius = size * 0.42

            if dist <= radius:
                row.extend([*color, 255])
            elif dist <= radius + 1:
                alpha = int(255 * (1 - (dist - radius)))
                row.extend([*color, alpha])
            else:
                row.extend([255, 255, 255, 0])
        pixels.append(bytes([0] + row))

    raw = b''.join(pixels)

    def chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)
    idat = zlib.compress(raw)

    return (
        b'\x89PNG\r\n\x1a\n' +
        chunk(b'IHDR', ihdr) +
        chunk(b'IDAT', idat) +
        chunk(b'IEND', b'')
    )

for size in [16, 48, 128]:
    data = create_png(size)
    path = os.path.join(os.path.dirname(__file__), f'icon{size}.png')
    with open(path, 'wb') as f:
        f.write(data)
    print(f'Created {path} ({size}x{size})')
