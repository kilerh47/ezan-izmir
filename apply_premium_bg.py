from PIL import Image, ImageDraw, ImageFilter

base_img = Image.open('base_icon.png').convert('RGBA')
width, height = base_img.size
pixels = base_img.load()

# Sample the teal background from the middle left edge
tr, tg, tb, _ = pixels[5, height // 2]

mosque_mask = Image.new('L', (width, height), 0)
mask_pixels = mosque_mask.load()

margin = 40
min_x, max_x, min_y, max_y = width, 0, height, 0

# Determine which color channel gives the best alpha separation
# We want the channel where the difference between White (255) and Teal is greatest
diff_r = 255.0 - tr
diff_g = 255.0 - tg
diff_b = 255.0 - tb

for y in range(height):
    for x in range(width):
        r, g, b, _ = pixels[x, y]
        
        # Calculate alpha
        if diff_r > diff_g and diff_r > diff_b:
            alpha = (r - tr) / diff_r
        elif diff_g > diff_b:
            alpha = (g - tg) / diff_g
        else:
            alpha = (b - tb) / diff_b
            
        alpha = max(0.0, min(1.0, alpha))
        
        # We only want the central mosque, not the white corners
        if margin < x < width - margin and margin < y < height - margin:
            # Also, some artifacts might be very dark. We only care if alpha > 0
            if alpha > 0.05: 
                val = int(alpha * 255)
                mask_pixels[x, y] = val
                if val > 50: # Only count solid parts for bounding box
                    if x < min_x: min_x = x
                    if x > max_x: max_x = x
                    if y < min_y: min_y = y
                    if y > max_y: max_y = y

mosque_cropped = mosque_mask.crop((min_x, min_y, max_x, max_y))

target_h = int(height * 0.65)
scale = target_h / mosque_cropped.height
target_w = int(mosque_cropped.width * scale)

# LANCZOS gives buttery smooth scaling
mosque_scaled = mosque_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

def create_gradient_canvas(size, color1, color2):
    base = Image.new("RGB", (1, 256))
    for y in range(256):
        r = int(color1[0] + (color2[0] - color1[0]) * (y / 255.0))
        g = int(color1[1] + (color2[1] - color1[1]) * (y / 255.0))
        b = int(color1[2] + (color2[2] - color1[2]) * (y / 255.0))
        base.putpixel((0, y), (r, g, b))
    gradient = base.resize((size * 2, size * 2), Image.Resampling.BILINEAR)
    rotated = gradient.rotate(45, Image.Resampling.BICUBIC)
    left = (rotated.width - size) // 2
    top = (rotated.height - size) // 2
    return rotated.crop((left, top, left + size, top + size)).convert("RGBA")

c1 = (15, 23, 42)
c2 = (2, 6, 23)
bg = create_gradient_canvas(width, c1, c2)

cx, cy = width // 2, height // 2
glow_mask = Image.new("L", (width, height), 0)
glow_draw = ImageDraw.Draw(glow_mask)
glow_radius = int(width * 0.35)
glow_draw.ellipse([cx - glow_radius, cy - glow_radius, cx + glow_radius, cy + glow_radius], fill=150)
blurred_glow = glow_mask.filter(ImageFilter.GaussianBlur(glow_radius // 2))

glow_layer = Image.new("RGBA", (width, height), (56, 189, 248, 255))
bg.paste(glow_layer, (0, 0), blurred_glow)

paste_x = (width - target_w) // 2
paste_y = (height - target_h) // 2

# Create a solid white layer, and use our perfectly anti-aliased mask
mosque_color_layer = Image.new("RGBA", (target_w, target_h), (255, 255, 255, 255))
bg.paste(mosque_color_layer, (paste_x, paste_y), mosque_scaled)

bg.save("icon-512.png", "PNG")
bg_192 = bg.resize((192, 192), Image.Resampling.LANCZOS)
bg_192.save("icon-192.png", "PNG")

print("Ultra-smooth icons successfully generated!")
