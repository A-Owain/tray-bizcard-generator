import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(layout="centered", page_title="TRAY Business Card Generator")

# Arabic reshaping
def reshape_arabic(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

# Load image assets
def load_logo(path):
    try:
        return Image.open(path).convert("RGBA")
    except FileNotFoundError:
        st.warning(f"⚠️ Logo not found: {path}")
        return Image.new("RGBA", (1, 1), "gray")

def load_icon(path):
    try:
        return Image.open(path).convert("RGBA").resize((40, 40))
    except FileNotFoundError:
        st.warning(f"⚠️ Icon missing: {path}")
        return Image.new("RGBA", (40, 40), "gray")

# Load assets
logo_front = load_logo("assets/tray_logo.png")
logo_back = load_logo("assets/Tray_logo_white.png")
icon_email = load_icon("assets/icons/email.png")
icon_phone = load_icon("assets/icons/phone.png")

# Fonts
try:
    font_ar_regular = "fonts/NotoSansArabic-Regular.ttf"
    font_ar_bold = "fonts/NotoSansArabic-SemiBold.ttf"
    font_en_bold = "fonts/PlusJakartaSans-Bold.ttf"
    font_en_medium = "fonts/PlusJakartaSans-Medium.ttf"

    font_name_ar = ImageFont.truetype(font_ar_bold, 80)
    font_title_ar = ImageFont.truetype(font_ar_regular, 60)
    font_info_ar = ImageFont.truetype(font_ar_regular, 48)

    font_name_en = ImageFont.truetype(font_en_bold, 80)
    font_title_en = ImageFont.truetype(font_en_medium, 60)
    font_info_en = ImageFont.truetype(font_en_medium, 48)
except Exception as e:
    st.error("❌ Font loading error.")
    st.stop()

# Sidebar inputs
with st.sidebar:
    st.title("🪪 معلومات البطاقة")
    name_ar = st.text_input("الاسم بالعربية", "عبدالله رجب")
    title_ar = st.text_input("المسمى بالعربية", "مدير تطوير الأعمال")
    name_en = st.text_input("Full Name", "Abdullah Rajab")
    title_en = st.text_input("Job Title", "Business Development Manager")
    email = st.text_input("Email", "abdullah.rajab@alraedahdigital.sa")
    phone = st.text_input("Phone", "+966 59 294 8994")

# Color & layout
text_color = "#002C5F"
red_color = "#ea2f2f"

# Generate card (front or back)
def generate_front_canvas(width, height):
    card = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(card)

    # Layout anchors
    margin = 150
    name_top = 350
    spacing = 100

    # Arabic (right)
    draw.text((width - margin, name_top), reshape_arabic(name_ar), font=font_name_ar, fill=text_color, anchor="ra")
    draw.text((width - margin, name_top + spacing), reshape_arabic(title_ar), font=font_title_ar, fill=text_color, anchor="ra")

    # English (left)
    draw.text((margin, name_top + 5), name_en, font=font_name_en, fill=text_color)
    draw.text((margin, name_top + spacing + 5), title_en, font=font_title_en, fill=text_color)

    # Contact info
    contact_top = int(height * 0.72)
    card.paste(icon_email, (margin, contact_top), mask=icon_email)
    card.paste(icon_phone, (margin, contact_top + spacing), mask=icon_phone)

    draw.text((margin + 60, contact_top), email, font=font_info_en, fill=text_color)
    draw.text((margin + 60, contact_top + spacing), phone, font=font_info_en, fill=text_color)

    # Center logo
    logo_pos = ((width - logo_front.width) // 2, int(height * 0.42))
    card.paste(logo_front, logo_pos, mask=logo_front)
    return card

def generate_back_canvas(width, height):
    card = Image.new("RGB", (width, height), color=red_color)
    logo_pos = ((width - logo_back.width) // 2, (height - logo_back.height) // 2)
    card.paste(logo_back, logo_pos, mask=logo_back)
    return card

# Sizes
W_4K, H_4K = 3840, 2160
W_PRINT, H_PRINT = 1062, 591  # 9x5cm @ 300DPI

# Generate both versions with same font/icon/logo sizes
front_4k = generate_front_canvas(W_4K, H_4K)
back_4k = generate_back_canvas(W_4K, H_4K)

front_print = generate_front_canvas(W_PRINT, H_PRINT)
back_print = generate_back_canvas(W_PRINT, H_PRINT)

# Preview
st.subheader("🔍 Preview (Front)")
st.image(front_4k.resize((1200, 675)))

# Export PDFs
pdf_4k = io.BytesIO()
front_4k.convert("RGB").save(pdf_4k, format="PDF", save_all=True, append_images=[back_4k.convert("RGB")])
st.download_button("⬇️ تحميل PDF دقة 4K", pdf_4k.getvalue(), "tray_card_4K.pdf", "application/pdf")

pdf_print = io.BytesIO()
front_print.convert("RGB").save(pdf_print, format="PDF", save_all=True, append_images=[back_print.convert("RGB")])
st.download_button("⬇️ تحميل PDF للطباعة (9×5سم)", pdf_print.getvalue(), "tray_card_print.pdf", "application/pdf")
