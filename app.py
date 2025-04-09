import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(layout="centered", page_title="TRAY Business Card Generator")

def reshape_arabic(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

def load_logo(path):
    try:
        return Image.open(path).convert("RGBA")
    except:
        return Image.new("RGBA", (1, 1), "gray")

def load_icon(path, size=(48, 48)):
    try:
        return Image.open(path).convert("RGBA").resize(size)
    except:
        return Image.new("RGBA", size, "gray")

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

    font_name_ar = ImageFont.truetype(font_ar_bold, 96)
    font_title_ar = ImageFont.truetype(font_ar_regular, 72)
    font_info_ar = ImageFont.truetype(font_ar_regular, 60)

    font_name_en = ImageFont.truetype(font_en_bold, 96)
    font_title_en = ImageFont.truetype(font_en_medium, 72)
    font_info_en = ImageFont.truetype(font_en_medium, 60)
except Exception as e:
    st.error("Font loading error.")
    st.stop()

with st.sidebar:
    st.title("🪪 معلومات البطاقة")
    name_ar = st.text_input("الاسم بالعربية", "عبدالله رجب")
    title_ar = st.text_input("المسمى بالعربية", "مدير تطوير الأعمال")
    name_en = st.text_input("Full Name", "Abdullah Rajab")
    title_en = st.text_input("Job Title", "Business Development Manager")
    email = st.text_input("Email", "abdullah.rajab@alraedahdigital.sa")
    phone = st.text_input("Phone", "+966 59 294 8994")

text_color = "#002C5F"
red_color = "#ea2f2f"

# Generate front and back cards
def generate_front(width, height):
    card = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(card)

    # Layout points
    margin = 160
    name_top = 300
    spacing = 110
    icon_offset = 8

    # Arabic
    draw.text((width - margin, name_top), reshape_arabic(name_ar), font=font_name_ar, fill=text_color, anchor="ra")
    draw.text((width - margin, name_top + spacing), reshape_arabic(title_ar), font=font_title_ar, fill=text_color, anchor="ra")

    # English
    draw.text((margin, name_top + 10), name_en, font=font_name_en, fill=text_color)
    draw.text((margin, name_top + spacing + 10), title_en, font=font_title_en, fill=text_color)

    # Contact
    contact_top = int(height * 0.72)
    icon_size = icon_email.size[1]
    draw.text((margin + 60, contact_top + icon_offset), email, font=font_info_en, fill=text_color)
    draw.text((margin + 60, contact_top + spacing + icon_offset), phone, font=font_info_en, fill=text_color)
    card.paste(icon_email, (margin, contact_top), mask=icon_email)
    card.paste(icon_phone, (margin, contact_top + spacing), mask=icon_phone)

    # Center logo
    logo_resized = ImageOps.contain(logo_front, (200, 200))
    logo_pos = ((width - logo_resized.width) // 2, int(height * 0.43))
    card.paste(logo_resized, logo_pos, mask=logo_resized)

    return card

def generate_back(width, height):
    card = Image.new("RGB", (width, height), red_color)
    logo_resized = ImageOps.contain(logo_back, (200, 200))
    logo_pos = ((width - logo_resized.width) // 2, (height - logo_resized.height) // 2)
    card.paste(logo_resized, logo_pos, mask=logo_resized)
    return card

# Sizes
W_4K, H_4K = 3840, 2160
W_PRINT, H_PRINT = 1062, 591  # 9x5cm @ 300DPI

# Generate both sizes
front_4k = generate_front(W_4K, H_4K)
back_4k = generate_back(W_4K, H_4K)

front_print = generate_front(W_PRINT, H_PRINT)
back_print = generate_back(W_PRINT, H_PRINT)

# Show preview
st.subheader("🔍 Preview (Front)")
st.image(front_4k.resize((1200, 675)))

# Export PDFs
def export_pdf(front_img, back_img, filename):
    buf = io.BytesIO()
    front_img.convert("RGB").save(buf, format="PDF", save_all=True, append_images=[back_img.convert("RGB")])
    st.download_button(f"⬇️ تحميل {filename}", buf.getvalue(), file_name=filename, mime="application/pdf")

export_pdf(front_4k, back_4k, "tray_card_4K.pdf")
export_pdf(front_print, back_print, "tray_card_print.pdf")
