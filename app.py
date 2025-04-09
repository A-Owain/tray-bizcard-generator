import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

# Page settings
st.set_page_config(layout="centered", page_title="TRAY Business Card Generator")

# Load logo
try:
    logo = Image.open("assets/tray_logo.png").resize((120, 120))
except FileNotFoundError:
    st.warning("⚠️ TRAY logo not found in /assets. Please add tray_logo.png to the /assets folder.")
    logo = Image.new("RGB", (120, 120), "gray")

# Load fonts
try:
    font_path_regular = "fonts/NotoSansArabic-Regular.ttf"
    font_path_bold = "fonts/NotoSansArabic-SemiBold.ttf"
    font_name = ImageFont.truetype(font_path_bold, 34)
    font_title = ImageFont.truetype(font_path_regular, 28)
    font_info = ImageFont.truetype(font_path_regular, 24)
except Exception as e:
    st.error("❌ Could not load font files. Make sure they are in the /fonts directory.")
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

# Card dimensions & colors
W, H = 1000, 600
bg_color = "white"
text_color = "#002C5F"

# Business card generator
def generate_card():
    card = Image.new("RGB", (W, H), color=bg_color)
    draw = ImageDraw.Draw(card)

    # Arabic text (right side)
    draw.text((950, 80), name_ar, font=font_name, fill=text_color, anchor="ra")
    draw.text((950, 130), title_ar, font=font_title, fill=text_color, anchor="ra")

    # English text (left side)
    draw.text((50, 80), name_en, font=font_name, fill=text_color)
    draw.text((50, 130), title_en, font=font_title, fill=text_color)

    # Contact info (left bottom)
    draw.text((50, 400), f"📧 {email}", font=font_info, fill=text_color)
    draw.text((50, 450), f"📞 {phone}", font=font_info, fill=text_color)

    # TRAY logo (centered)
    card.paste(logo, (440, 240))

    return card

# Display preview
st.subheader("🔍 Preview")
card_img = generate_card()
st.image(card_img)

# Export - CMYK for printing
cmyk_card = card_img.convert("CMYK")
cmyk_buf = io.BytesIO()
cmyk_card.save(cmyk_buf, format="TIFF")
st.download_button("⬇️ تحميل بطاقة CMYK للطباعة", cmyk_buf.getvalue(), "tray_card.tiff", "image/tiff")

# Export - RGB for screen
rgb_buf = io.BytesIO()
card_img.save(rgb_buf, format="PNG")
st.download_button("⬇️ تحميل بطاقة للشاشة (RGB)", rgb_buf.getvalue(), "tray_card.png", "image/png")
