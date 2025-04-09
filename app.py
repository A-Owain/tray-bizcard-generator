import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
import arabic_reshaper
from bidi.algorithm import get_display

# Config
st.set_page_config(layout="centered", page_title="TRAY Business Card Generator")

# Try loading logo
try:
    logo = Image.open("assets/Tray_logo.png").resize((120, 120))
except FileNotFoundError:
    st.warning("⚠️ TRAY logo not found in /assets. Please add tray_logo.png to that folder.")
    logo = Image.new("RGB", (120, 120), "gray")  # placeholder

# Load fonts
try:
    font_path_regular = "fonts/NotoSansArabic-Regular.ttf"
    font_path_bold = "fonts/NotoSansArabic-SemiBold.ttf"
    font_name = ImageFont.truetype(font_path_bold, 34)
    font_title = ImageFont.truetype(font_path_regular, 28)
    font_info = ImageFont.truetype(font_path_regular, 24)
except Exception as e:
    st.error("❌ Could not load font files. Make sure both are in /fonts.")
    st.stop()

# Function to fix Arabic rendering
def reshape_arabic(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

# Sidebar input
with st.sidebar:
    st.title("🪪 معلومات البطاقة")
    name_ar = st.text_input("الاسم بالعربية", "عبدالله رجب")
    title_ar = st.text_input("المسمى بالعربية", "مدير تطوير الأعمال")
    name_en = st.text_input("Full Name", "Abdullah Rajab")
    title_en = st.text_input("Job Title", "Business Development Manager")
    email = st.text_input("Email", "abdullah.rajab@alraedahdigital.sa")
    phone = st.text_input("Phone", "+966 59 294 8994")

# Constants
W, H = 1000, 600
bg_color = "white"
text_color = "#002C5F"

# Card generator
def generate_card():
    card = Image.new("RGB", (W, H), color=bg_color)
    draw = ImageDraw.Draw(card)

    # Arabic text (right)
    draw.text((950, 80), reshape_arabic(name_ar), font=font_name, fill=text_color, anchor="ra")
    draw.text((950, 130), reshape_arabic(title_ar), font=font_title, fill=text_color, anchor="ra")

    # English text (left)
    draw.text((50, 80), name_en, font=font_name, fill=text_color)
    draw.text((50, 130), title_en, font=font_title, fill=text_color)

    # Contact info
    draw.text((50, 400), f"📧 {email}", font=font_info, fill=text_color)
    draw.text((50, 450), f"📞 {phone}", font=font_info, fill=text_color)

    # Logo
    card.paste(logo, (440, 240))

    return card

# Preview
st.subheader("🔍 Preview")
card_img = generate_card()
st.image(card_img)

# CMYK export
cmyk_card = card_img.convert("CMYK")
cmyk_buf = io.BytesIO()
cmyk_card.save(cmyk_buf, format="TIFF")
st.download_button("⬇️ تحميل بطاقة CMYK للطباعة", cmyk_buf.getvalue(), "tray_card.tiff", "image/tiff")

# RGB export
rgb_buf = io.BytesIO()
card_img.save(rgb_buf, format="PNG")
st.download_button("⬇️ تحميل بطاقة للشاشة (RGB)", rgb_buf.getvalue(), "tray_card.png", "image/png")
