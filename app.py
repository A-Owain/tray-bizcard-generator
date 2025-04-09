import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import arabic_reshaper
from bidi.algorithm import get_display

# App setup
st.set_page_config(layout="centered", page_title="TRAY Business Card Generator")

# Arabic reshaping
def reshape_arabic(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

# Load logo
def load_logo():
    try:
        logo = Image.open("assets/tray_logo.png").convert("RGBA")
        return ImageOps.contain(logo, (300, 300))  # Scaled for back
    except FileNotFoundError:
        st.warning("⚠️ tray_logo.png not found in /assets")
        return Image.new("RGBA", (300, 300), "gray")

# Load icons
def load_icon(path):
    try:
        return Image.open(path).convert("RGBA").resize((28, 28))
    except FileNotFoundError:
        st.warning(f"⚠️ Missing icon: {path}")
        return Image.new("RGBA", (28, 28), "gray")

icon_email = load_icon("assets/icons/email.png")
icon_phone = load_icon("assets/icons/phone.png")
logo = load_logo()

# Load fonts
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
    st.error("❌ Font loading error. Please check the /fonts folder.")
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

# Constants
WIDTH, HEIGHT = 3840, 2160  # 4K resolution
text_color = "#002C5F"

def generate_front():
    card = Image.new("RGB", (WIDTH, HEIGHT), color="white")
    draw = ImageDraw.Draw(card)

    # Name/title alignment fix
    name_y_ar = 300
    title_y_ar = 420
    name_y_en = 305
    title_y_en = 425

    # Arabic
    draw.text((3700, name_y_ar), reshape_arabic(name_ar), font=font_name_ar, fill=text_color, anchor="ra")
    draw.text((3700, title_y_ar), reshape_arabic(title_ar), font=font_title_ar, fill=text_color, anchor="ra")

    # English
    draw.text((140, name_y_en), name_en, font=font_name_en, fill=text_color)
    draw.text((140, title_y_en), title_en, font=font_title_en, fill=text_color)

    # Contact info
    icon_x = 140
    text_x = 200
    email_y = 1400
    phone_y = 1520

    card.paste(icon_email, (icon_x, email_y), mask=icon_email)
    card.paste(icon_phone, (icon_x, phone_y), mask=icon_phone)

    draw.text((text_x, email_y), email, font=font_info_en, fill=text_color)
    draw.text((text_x, phone_y), phone, font=font_info_en, fill=text_color)

    # Center logo
    logo_pos = ((WIDTH - logo.width) // 2, 850)
    card.paste(logo, logo_pos, mask=logo)

    return card

def generate_back():
    card = Image.new("RGB", (WIDTH, HEIGHT), color="#ea2f2f")
    draw = ImageDraw.Draw(card)

    # Center logo
    logo_pos = ((WIDTH - logo.width) // 2, (HEIGHT - logo.height) // 2)
    card.paste(logo, logo_pos, mask=logo)

    return card

# Generate both sides
front_img = generate_front()
back_img = generate_back()

# Show front only for preview
st.subheader("🔍 Preview (Front)")
preview_resized = front_img.resize((1200, 675))
st.image(preview_resized)

# PDF Export
pdf_buf = io.BytesIO()
front_img_rgb = front_img.convert("RGB")
back_img_rgb = back_img.convert("RGB")
front_img_rgb.save(pdf_buf, format="PDF", save_all=True, append_images=[back_img_rgb])
st.download_button("⬇️ تحميل الوجهين PDF (دقة عالية)", pdf_buf.getvalue(), "tray_card_4k.pdf", "application/pdf")

# Optional PNG download
rgb_buf = io.BytesIO()
front_img.save(rgb_buf, format="PNG")
st.download_button("⬇️ تحميل الواجهة الأمامية (RGB)", rgb_buf.getvalue(), "tray_front.png", "image/png")
