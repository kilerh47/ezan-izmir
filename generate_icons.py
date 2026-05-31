import math
from PIL import Image, ImageDraw, ImageFilter, ImageOps

def create_gradient_canvas(size, color1, color2):
    # Create a 1D gradient image and scale it up
    base = Image.new("RGB", (1, 256))
    for y in range(256):
        # Interpolate between color1 and color2
        r = int(color1[0] + (color2[0] - color1[0]) * (y / 255.0))
        g = int(color1[1] + (color2[1] - color1[1]) * (y / 255.0))
        b = int(color1[2] + (color2[2] - color1[2]) * (y / 255.0))
        base.putpixel((0, y), (r, g, b))
    
    # Resize to size x size to stretch the gradient
    gradient = base.resize((size * 2, size * 2), Image.Resampling.BILINEAR)
    # Rotate by 45 degrees to get a beautiful diagonal gradient
    rotated = gradient.rotate(45, Image.Resampling.BICUBIC)
    # Crop the center to the desired size
    left = (rotated.width - size) // 2
    top = (rotated.height - size) // 2
    return rotated.crop((left, top, left + size, top + size))

def generate_icon(output_size):
    # Render at 4x resolution for super-smooth antialiasing (LANCZOS downsampling)
    render_size = output_size * 4
    
    # Premium deep indigo to violet-purple gradient
    # Color 1: #1e1b4b (deep indigo), Color 2: #4c1d95 (deep purple)
    c1 = (30, 27, 75)
    c2 = (76, 29, 149)
    
    img = create_gradient_canvas(render_size, c1, c2)
    
    # We will use an alpha mask for the drawing to keep things crisp and transparent if needed
    # but for PWA icons, a fully solid premium background with a nice glowing emblem is best.
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Let's draw a glowing ambient radial overlay in the center to make the emblem pop
    # Create a white glow mask, blur it, and composite it
    glow_mask = Image.new("L", (render_size, render_size), 0)
    glow_draw = ImageDraw.Draw(glow_mask)
    glow_radius = int(render_size * 0.28)
    glow_draw.ellipse(
        [
            render_size // 2 - glow_radius,
            render_size // 2 - glow_radius,
            render_size // 2 + glow_radius,
            render_size // 2 + glow_radius
        ],
        fill=64 # Soft glow intensity
    )
    blurred_glow = glow_mask.filter(ImageFilter.GaussianBlur(glow_radius // 2))
    
    # Apply glow (gold-like glowing color: #fbbf24 at 30% opacity)
    glow_layer = Image.new("RGBA", (render_size, render_size), (251, 191, 36, 60))
    img.paste(glow_layer, (0, 0), blurred_glow)
    
    # Now draw the elegant emblem (Minimalist Mosque Dome + Hilal/Crescent)
    # We will draw this on a high-res black & white mask to get perfect anti-aliasing
    emblem_mask = Image.new("L", (render_size, render_size), 0)
    emblem_draw = ImageDraw.Draw(emblem_mask)
    
    cx, cy = render_size // 2, render_size // 2
    
    # 1. Draw the elegant crescent moon wrapping the dome
    # Large circle for crescent
    r1 = int(render_size * 0.22)
    emblem_draw.ellipse([cx - r1, cy - r1 - int(render_size * 0.03), cx + r1, cy + r1 - int(render_size * 0.03)], fill=255)
    # Subtracting circle to make it a crescent (offset to top-right)
    r2 = int(render_size * 0.205)
    offset_x = int(render_size * 0.05)
    offset_y = -int(render_size * 0.01)
    emblem_draw.ellipse([cx - r2 + offset_x, cy - r2 - int(render_size * 0.03) + offset_y, cx + r2 + offset_x, cy + r2 - int(render_size * 0.03) + offset_y], fill=0)
    
    # 2. Draw a sleek, modern mosque dome silhouette in the center
    # Dome base coordinates
    dome_w = int(render_size * 0.18)
    dome_h = int(render_size * 0.16)
    dome_bottom = cy + int(render_size * 0.18)
    dome_top = dome_bottom - dome_h
    
    # Dome body (beautiful arch)
    # Draw an ellipse for the dome curve
    emblem_draw.ellipse([cx - dome_w//2, dome_top, cx + dome_w//2, dome_top + dome_w], fill=255)
    # Clip the bottom of the dome ellipse to make a flat base
    emblem_draw.rectangle([0, dome_bottom, render_size, render_size], fill=0)
    
    # Sleek base lines
    emblem_draw.rounded_rectangle([cx - dome_w//2 - int(render_size * 0.02), dome_bottom - int(render_size * 0.015), cx + dome_w//2 + int(render_size * 0.02), dome_bottom], radius=int(render_size * 0.01), fill=255)
    
    # 3. Draw a tiny elegant spire (Alef) on top of the dome
    spire_w = int(render_size * 0.01)
    spire_h = int(render_size * 0.05)
    emblem_draw.rectangle([cx - spire_w//2, dome_top - spire_h + int(render_size * 0.01), cx + spire_w//2, dome_top + int(render_size * 0.01)], fill=255)
    # Small spire ball details
    emblem_draw.ellipse([cx - spire_w, dome_top - spire_h, cx + spire_w, dome_top - spire_h + spire_w*2], fill=255)
    
    # Let's apply the emblem using a gold-white gradient or solid white with gold tint
    # For a high-contrast luxury feel, we will fill it with solid warm white (#f8fafc) and a gold outline
    emblem_layer = Image.new("RGBA", (render_size, render_size), (248, 250, 252, 255))
    img.paste(emblem_layer, (0, 0), emblem_mask)
    
    # Gold border will be created below using the working dilated mask logic.
    
    # Paste gold glow onto background BEFORE pasting emblem, or paste as an outline
    # Let's composite the gold outline on top of emblem
    # Gold border
    border_mask = Image.new("L", (render_size, render_size), 0)
    border_draw = ImageDraw.Draw(border_mask)
    # Draw border by subtracting original mask from dilated mask
    dilated = emblem_mask.filter(ImageFilter.MaxFilter(int(render_size * 0.012) | 1))
    border_mask = Image.new("L", (render_size, render_size), 0)
    border_mask.paste(dilated, (0,0))
    border_mask.paste(Image.new("L", (render_size, render_size), 0), (0,0), emblem_mask)
    
    border_layer = Image.new("RGBA", (render_size, render_size), (251, 191, 36, 255)) # Gold #fbbf24
    img.paste(border_layer, (0,0), border_mask)
    
    # Resize down to target size with Lanczos (gorgeous anti-aliased output)
    final_img = img.resize((output_size, output_size), Image.Resampling.LANCZOS)
    return final_img

# Generate both icons
icon512 = generate_icon(512)
icon512.save("icon-512.png", "PNG")

icon192 = generate_icon(192)
icon192.save("icon-192.png", "PNG")

print("Icons generated successfully!")
