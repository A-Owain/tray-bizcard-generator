import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import arabic_reshaper
from bidi.algorithm import get_display

# Set up Streamlit page
st.set_page_config(layout="centered", page_title="TRAY Business Card Generator")

# Reshape Arabic text
def reshape_arabic(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

# Load logo with transparency
try:
    logo = Image.open("assets/tray_logo.png").convert("RGBA")
    logo = ImageOps.contain(logo, (120, 120))
except FileNotFoundError:
    st.warning("⚠️ tray_logo.png not found in /assets")
    logo = Image.new("RGBA", (120, 120), "gray")

# Load email and phone icons
try:
    icon_email = Image.open("assets/icons/email.png").convert("RGBA").resize((28, 28))
    icon_phone = Image.open("assets/icons/phone.png").convert("RGBA").resize((28, 28))
except FileNotFoundError:
    st.warning("⚠️ Icons not found in /assets/icons. Please add email.png and phone.png.")
    icon_email = Image.new("RGBA", (28, 28), "gray")
    icon_phone = Image.new("RGBA", (28, 28), "gray")

# Load fonts
try:
    font_ar_regular = "fonts/NotoSansArabic-Regular.ttf"
    font_ar_bold = "fonts/NotoSansArabic-SemiBold.ttf"
    font_en = "fonts/DejaVuSans.ttf"

    font_name_ar = ImageFont.truetype(font_ar_bold, 34)
    font_title_ar = ImageFont.truetype(font_ar_regular, 28)
    font_info_ar = ImageFont.truetype(font_ar_regular, 24)

    font_name_en = ImageFont.truetype(font_en, 34)
    font_title_en = ImageFont.truetype(font_en, 28)
    font_info_en = ImageFont.truetype(font_en, 24)
except Exception as e:
    st.error("❌ Could not load one or more fonts. Make sure they exist in /fonts.")
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

# Constants
W, H = 1000, 600
bg_color = "white"
text_color = "#002C5F"

# Generate the card
def generate_card():
    card = Image.new("RGB", (W, H), color=bg_color)
    draw = ImageDraw.Draw(card)

    # Arabic section (right aligned)
    draw.text((950, 80), reshape_arabic(name_ar), font=font_name_ar, fill=text_color, anchor="ra")
    draw.text((950, 130), reshape_arabic(title_ar), font=font_title_ar, fill=text_color, anchor="ra")

    # English section (left aligned)
    draw.text((50, 80), name_en, font=font_name_en, fill=text_color)
    draw.text((50, 130), title_en, font=font_title_en, fill=text_color)

    # Contact info with icons
    card.paste(icon_email, (50, 395), mask=icon_email)
    card.paste(icon_phone, (50, 445), mask=icon_phone)

    draw.text((90, 395), email, font=font_info_en, fill=text_color)
    draw.text((90, 445), phone, font=font_info_en, fill=text_color)

    # Paste logo in center
    card.paste(logo, (440, 240), mask=logo)

    return card

# Preview
st.subheader("🔍 Preview")
card_img = generate_card()
st.image(card_img)

# CMYK export
cmyk_card = card_img.convert("CMYK")
cmyk_buf = io.BytesIO()
cmyk_card.save(cmyk_buf, format="TIFF")
st.download_button("⬇️ للطباعة تحميل بطاقة CMYK", cmyk_buf.getvalue(), "tray_card.tiff", "image/tiff")

# RGB export
rgb_buf = io.BytesIO()
card_img.save(rgb_buf, format="PNG")
st.download_button("⬇️ تحميل بطاقة الشاشة (RGB)", rgb_buf.getvalue(), "tray_card.png", "image/png")
