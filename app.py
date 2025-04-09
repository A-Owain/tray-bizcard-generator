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

def load_logo(size=(120, 120)):
    try:
        logo = Image.open("assets/tray_logo.png").convert("RGBA")
        return ImageOps.contain(logo, size)
    except FileNotFoundError:
        st.warning("⚠️ tray_logo.png not found in /assets")
        return Image.new("RGBA", size, "gray")

def load_icon(path):
    try:
        return Image.open(path).convert("RGBA").resize((28, 28))
    except FileNotFoundError:
        st.warning(f"⚠️ Missing icon: {path}")
        return Image.new("RGBA", (28, 28), "gray")

icon_email = load_icon("assets/icons/email.png")
icon_phone = load_icon("assets/icons/phone.png")

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

with st.sidebar:
    st.title("🪪 معلومات البطاقة")
    name_ar = st.text_input("الاسم بالعربية", "عبدالله رجب")
    title_ar = st.text_input("المسمى بالعربية", "مدير تطوير الأعمال")
    name_en = st.text_input("Full Name", "Abdullah Rajab")
    title_en = st.text_input("Job Title", "Business Development Manager")
    email = st.text_input("Email", "abdullah.rajab@alraedahdigital.sa")
    phone = st.text_input("Phone", "+966 59 294 8994")

# Shared data
text_color = "#002C5F"
red_color = "#ea2f2f"

# ================= FRONT & BACK GENERATORS ===================

def generate_card(width, height, fonts, logo_size):
    logo = load_logo(logo_size)
    card = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(card)

    name_y_ar = int(0.15 * height)
    title_y_ar = name_y_ar + int(0.1 * height)
    name_y_en = name_y_ar + 5
    title_y_en = title_y_ar + 5
    logo_y = int(0.4 * height)

    draw.text((width - 80, name_y_ar), reshape_arabic(name_ar), font=fonts["ar_name"], fill=text_color, anchor="ra")
    draw.text((width - 80, title_y_ar), reshape_arabic(title_ar), font=fonts["ar_title"], fill=text_color, anchor="ra")

    draw.text((80, name_y_en), name_en, font=fonts["en_name"], fill=text_color)
    draw.text((80, title_y_en), title_en, font=fonts["en_title"], fill=text_color)

    icon_x = 80
    text_x = 130
    email_y = int(0.7 * height)
    phone_y = email_y + 70

    card.paste(icon_email.resize((40, 40)), (icon_x, email_y), mask=icon_email)
    card.paste(icon_phone.resize((40, 40)), (icon_x, phone_y), mask=icon_phone)
    draw.text((text_x, email_y), email, font=fonts["en_info"], fill=text_color)
    draw.text((text_x, phone_y), phone, font=fonts["en_info"], fill=text_color)

    card.paste(logo, ((width - logo.width) // 2, logo_y), mask=logo)
    return card

def generate_back(width, height, logo_size):
    logo = load_logo(logo_size)
    back = Image.new("RGB", (width, height), color=red_color)
    back.paste(logo, ((width - logo.width) // 2, (height - logo.height) // 2), mask=logo)
    return back

# ================= 4K VERSION ===================

W_4K, H_4K = 3840, 2160
fonts_4k = load_fonts(scale=2.5)
front_4k = generate_card(W_4K, H_4K, fonts_4k, logo_size=(300, 300))
back_4k = generate_back(W_4K, H_4K, logo_size=(300, 300))

# ================= BUSINESS CARD SIZE ===================

W_BC, H_BC = 1062, 591  # 9x5cm @ 300DPI
fonts_bc = load_fonts(scale=1.0)
front_bc = generate_card(W_BC, H_BC, fonts_bc, logo_size=(120, 120))
back_bc = generate_back(W_BC, H_BC, logo_size=(120, 120))

# ================= STREAMLIT UI ===================

st.subheader("🔍 Preview (Front in 4K)")
st.image(front_4k.resize((1200, 675)))

# PDF (4K)
pdf_4k = io.BytesIO()
front_4k.convert("RGB").save(pdf_4k, format="PDF", save_all=True, append_images=[back_4k.convert("RGB")])
st.download_button("⬇️ تحميل PDF دقة 4K", pdf_4k.getvalue(), "tray_card_4K.pdf", "application/pdf")

# PDF (9x5cm)
pdf_bc = io.BytesIO()
front_bc.convert("RGB").save(pdf_bc, format="PDF", save_all=True, append_images=[back_bc.convert("RGB")])
st.download_button("⬇️ تحميل PDF للطباعة (9×5سم)", pdf_bc.getvalue(), "tray_card_print.pdf", "application/pdf")
