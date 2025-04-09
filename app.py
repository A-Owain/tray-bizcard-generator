import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(layout="centered", page_title="TRAY Business Card Generator")

def reshape_arabic(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

def load_logo(path, size=(120, 120)):
    try:
        logo = Image.open(path).convert("RGBA")
        return ImageOps.contain(logo, size)
    except FileNotFoundError:
        st.warning(f"⚠️ Logo not found: {path}")
        return Image.new("RGBA", size, "gray")

def load_icon(path):
    try:
        return Image.open(path).convert("RGBA").resize((40, 40))
    except FileNotFoundError:
        st.warning(f"⚠️ Missing icon: {path}")
        return Image.new("RGBA", (40, 40), "gray")

# Load assets
icon_email = load_icon("assets/icons/email.png")
icon_phone = load_icon("assets/icons/phone.png")

# Fonts
try:
    font_ar_regular = "fonts/NotoSansArabic-Regular.ttf"
    font_ar_bold = "fonts/NotoSansArabic-SemiBold.ttf"
    font_en_bold = "fonts/PlusJakartaSans-Bold.ttf"
    font_en_medium = "fonts/PlusJakartaSans-Medium.ttf"

    def load_fonts(scale=1.0):
        return {
            "ar_name": ImageFont.truetype(font_ar_bold, int(34 * scale)),
            "ar_title": ImageFont.truetype(font_ar_regular, int(28 * scale)),
            "ar_info": ImageFont.truetype(font_ar_regular, int(24 * scale)),
            "en_name": ImageFont.truetype(font_en_bold, int(34 * scale)),
            "en_title": ImageFont.truetype(font_en_medium, int(28 * scale)),
            "en_info": ImageFont.truetype(font_en_medium, int(24 * scale)),
        }
except Exception as e:
    st.error("❌ Font loading error.")
    st.stop()

# Sidebar
with st.sidebar:
    st.title("🪪 معلومات البطاقة")
    name_ar = st.text_input("الاسم بالعربية", "عبدالله رجب")
    title_ar = st.text_input("المسمى بالعربية", "مدير تطوير الأعمال")
    name_en = st.text_input("Full Name", "Abdullah Rajab")
    title_en = st.text_input("Job Title", "Business Development Manager")
    email = st.text_input("Email", "abdullah.rajab@alraedahdigital.sa")
    phone = st.text_input("Phone", "+966 59 294 8994")

# Constants
text_color = "#002C5F"
red_color = "#ea2f2f"

# ================= FRONT & BACK GENERATORS ===================

def generate_front(width, height, fonts, logo_path, logo_size):
    logo = load_logo(logo_path, size=logo_size)
    card = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(card)

    margin = 100
    content_top = int(height * 0.2)
    spacing = 60

    # Arabic
    draw.text((width - margin, content_top), reshape_arabic(name_ar), font=fonts["ar_name"], fill=text_color, anchor="ra")
    draw.text((width - margin, content_top + spacing), reshape_arabic(title_ar), font=fonts["ar_title"], fill=text_color, anchor="ra")

    # English
    draw.text((margin, content_top + 5), name_en, font=fonts["en_name"], fill=text_color)
    draw.text((margin, content_top + spacing + 5), title_en, font=fonts["en_title"], fill=text_color)

    # Contact
    contact_top = int(height * 0.7)
    card.paste(icon_email, (margin, contact_top), mask=icon_email)
    card.paste(icon_phone, (margin, contact_top + spacing), mask=icon_phone)
    draw.text((margin + 50, contact_top), email, font=fonts["en_info"], fill=text_color)
    draw.text((margin + 50, contact_top + spacing), phone, font=fonts["en_info"], fill=text_color)

    # Center logo
    logo_pos = ((width - logo.width) // 2, int(height * 0.45))
    card.paste(logo, logo_pos, mask=logo)
    return card

def generate_back(width, height, logo_path, logo_size):
    logo = load_logo(logo_path, size=logo_size)
    back = Image.new("RGB", (width, height), color=red_color)
    logo_pos = ((width - logo.width) // 2, (height - logo.height) // 2)
    back.paste(logo, logo_pos, mask=logo)
    return back

# ================= SIZES ===================
W_4K, H_4K = 3840, 2160
W_BC, H_BC = 1062, 591  # 9x5cm @ 300DPI

fonts_4k = load_fonts(scale=2.5)
fonts_bc = load_fonts(scale=1.0)

front_4k = generate_front(W_4K, H_4K, fonts_4k, "assets/tray_logo.png", (250, 250))
back_4k = generate_back(W_4K, H_4K, "assets/Tray_logo_white.png", (250, 250))

front_bc = generate_front(W_BC, H_BC, fonts_bc, "assets/tray_logo.png", (120, 120))
back_bc = generate_back(W_BC, H_BC, "assets/Tray_logo_white.png", (120, 120))

# ================= STREAMLIT ===================
st.subheader("🔍 Preview (Front)")
st.image(front_4k.resize((1200, 675)))

# 4K PDF
buf_4k = io.BytesIO()
front_4k.convert("RGB").save(buf_4k, format="PDF", save_all=True, append_images=[back_4k.convert("RGB")])
st.download_button("⬇️ تحميل PDF دقة 4K", buf_4k.getvalue(), "tray_card_4K.pdf", "application/pdf")

# Business Card PDF
buf_bc = io.BytesIO()
front_bc.convert("RGB").save(buf_bc, format="PDF", save_all=True, append_images=[back_bc.convert("RGB")])
st.download_button("⬇️ تحميل PDF للطباعة (9×5سم)", buf_bc.getvalue(), "tray_card_print.pdf", "application/pdf")
