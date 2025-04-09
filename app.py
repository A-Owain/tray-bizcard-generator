import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import time
import arabic_reshaper
from bidi.algorithm import get_display

# Streamlit config
st.set_page_config(layout="centered", page_title="TRAY Business Card Generator")

# Arabic text fix
def reshape_arabic(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

# Load logo with transparency and cache busting
try:
    logo_path = "assets/Tray_logo.png"
    logo = Image.open(logo_path).convert("RGBA")
    logo = ImageOps.contain(logo, (120, 120))
except FileNotFoundError:
    st.warning("⚠️ Transparent TRAY logo not found in /assets/tray_logo.png.")
    logo = Image.new("RGBA", (120, 120), "gray")

# Load fonts (Arabic and English)
try:
    font_ar_regular = "fonts/NotoSansArabic-Regular.ttf"
    font_ar_bold = "fonts/NotoSansArabic-SemiBold.ttf"
    font_en = "fonts/DejaVuSans.ttf"  # Make sure to include it in /fonts/

    font_name_ar = ImageFont.truetype(font_ar_bold, 34)
    font_title_ar = ImageFont.truetype(font_ar_regular, 28)
    font_info_ar = ImageFont.truetype(font_ar_regular, 24)

    font_name_en = ImageFont.truetype(font_en, 34)
    font_title_en = ImageFont.truetype(font_en, 28)
    font_info_en = ImageFont.truetype(font_en, 24)
except Exception as e:
    st.error("❌ One or more fonts are missing. Please make sure they're in the /fonts folder.")
    st.stop()

# Sidebar input
with st.sidebar:
    st.title("🪪 معلومات البطاقة")
    name_ar = st.text_input("الاسم بالعربية", "عبدالله رجب")
    title_ar = st.text_input("المسمى بالعربية", "مدير تطوير الأعمال")
    name_en = st.text_input("Full Name", "Abdullah Rajab")
    title_en = st.text_input("Job Title", "Business Development Manager")
    email = st.text_input("Email", "abdullah.rajab@alraedahdigital.sa")
    phone = st.text_input("Phone", "+966 59 294 8994")

# Business card design
W, H = 1000, 600
bg_color = "white"
text_color = "#002C5F"

def generate_card():
    card = Image.new("RGB", (W, H), color=bg_color)
    draw = ImageDraw.Draw(card)

    # Arabic info (right aligned)
    draw.text((950, 80), reshape_arabic(name_ar), font=font_name_ar, fill=text_color, anchor="ra")
    draw.text((950, 130), reshape_arabic(title_ar), font=font_title_ar, fill=text_color, anchor="ra")

    # English info (left aligned)
    draw.text((50, 80), name_en, font=font_name_en, fill=text_color)
    draw.text((50, 130), title_en, font=font_title_en, fill=text_color)

    # Contact info
    draw.text((50, 400), f"📧 {email}", font=font_info_en, fill=text_color)
    draw.text((50, 450), f"📞 {phone}", font=font_info_en, fill=text_color)

    # Center logo with transparency
    card.paste(logo, (440, 240), mask=logo)

    return card

# Generate and display card
st.subheader("🔍 Preview")
card_img = generate_card()
st.image(card_img)

# Export as CMYK for printing
cmyk_card = card_img.convert("CMYK")
cmyk_buf = io.BytesIO()
cmyk_card.save(cmyk_buf, format="TIFF")
st.download_button("⬇️ للطباعة تحميل بطاقة CMYK", cmyk_buf.getvalue(), "tray_card.tiff", "image/tiff")

# Export as RGB for screen
rgb_buf = io.BytesIO()
card_img.save(rgb_buf, format="PNG")
st.download_button("⬇️ تحميل بطاقة الشاشة (RGB)", rgb_buf.getvalue(), "tray_card.png", "image/png")
