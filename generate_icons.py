import math
from PIL import Image, ImageDraw, ImageFilter

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
    return rotated.crop((left, top, left + size, top + size))

def generate_icon(output_size):
    render_size = output_size * 4
    
    # EXACT Dark Theme Background Colors
    # --bg-top: #0f172a (15, 23, 42) - Koyu Lacivert/Slate
    # --bg-bot: #020617 (2, 6, 23) - Gece Siyahı
    c1 = (15, 23, 42)
    c2 = (2, 6, 23)
    
    img = create_gradient_canvas(render_size, c1, c2)
    img = img.convert("RGBA")
    
    cx, cy = render_size // 2, render_size // 2
    
    # Scale factor for making the old design much bigger
    S = 1.6
    
    # Glow Mask
    glow_mask = Image.new("L", (render_size, render_size), 0)
    glow_draw = ImageDraw.Draw(glow_mask)
    glow_radius = int(render_size * 0.28 * S)
    glow_draw.ellipse([cx - glow_radius, cy - glow_radius, cx + glow_radius, cy + glow_radius], fill=120)
    blurred_glow = glow_mask.filter(ImageFilter.GaussianBlur(glow_radius // 2))
    
    # Glow Color: EXACT Dark Theme Accent
    # --accent: #38bdf8 (56, 189, 248) - Mavi/Camgöbeği (Moon)
    glow_layer = Image.new("RGBA", (render_size, render_size), (56, 189, 248, 255))
    img.paste(glow_layer, (0, 0), blurred_glow)
    
    # Emblem Mask
    emblem_mask = Image.new("L", (render_size, render_size), 0)
    emblem_draw = ImageDraw.Draw(emblem_mask)
    
    # EXACT Old Design Logic, just multiplied by S
    
    # 1. Crescent
    r1 = int(render_size * 0.22 * S)
    emblem_draw.ellipse([cx - r1, cy - r1 - int(render_size * 0.03 * S), cx + r1, cy + r1 - int(render_size * 0.03 * S)], fill=255)
    
    r2 = int(render_size * 0.205 * S)
    offset_x = int(render_size * 0.05 * S)
    offset_y = -int(render_size * 0.01 * S)
    emblem_draw.ellipse([cx - r2 + offset_x, cy - r2 - int(render_size * 0.03 * S) + offset_y, cx + r2 + offset_x, cy + r2 - int(render_size * 0.03 * S) + offset_y], fill=0)
    
    # 2. Dome
    dome_w = int(render_size * 0.18 * S)
    dome_h = int(render_size * 0.16 * S)
    dome_bottom = cy + int(render_size * 0.18 * S)
    dome_top = dome_bottom - dome_h
    
    emblem_draw.ellipse([cx - dome_w//2, dome_top, cx + dome_w//2, dome_top + dome_w], fill=255)
    emblem_draw.rectangle([0, dome_bottom, render_size, render_size], fill=0)
    
    emblem_draw.rounded_rectangle([cx - dome_w//2 - int(render_size * 0.02 * S), dome_bottom - int(render_size * 0.015 * S), cx + dome_w//2 + int(render_size * 0.02 * S), dome_bottom], radius=int(render_size * 0.01 * S), fill=255)
    
    # 3. Spire
    spire_w = int(render_size * 0.01 * S)
    spire_h = int(render_size * 0.05 * S)
    emblem_draw.rectangle([cx - spire_w//2, dome_top - spire_h + int(render_size * 0.01 * S), cx + spire_w//2, dome_top + int(render_size * 0.01 * S)], fill=255)
    emblem_draw.ellipse([cx - spire_w, dome_top - spire_h, cx + spire_w, dome_top - spire_h + spire_w*2], fill=255)
    
    # Draw Emblem in White
    emblem_layer = Image.new("RGBA", (render_size, render_size), (248, 250, 252, 255))
    img.paste(emblem_layer, (0, 0), emblem_mask)
    
    final_img = img.resize((output_size, output_size), Image.Resampling.LANCZOS)
    return final_img

icon512 = generate_icon(512)
icon512.save("icon-512.png", "PNG")
icon192 = generate_icon(192)
icon192.save("icon-192.png", "PNG")
print("Icons generated successfully!")
