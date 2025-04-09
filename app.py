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

    def load_fonts(scale=1.0):
        return {
            "ar_name": ImageFont.truetype(font_ar_bold, int(96 * scale)),
            "ar_title": ImageFont.truetype(font_ar_regular, int(72 * scale)),
            "ar_info": ImageFont.truetype(font_ar_regular, int(60 * scale)),
            "en_name": ImageFont.truetype(font_en_bold, int(96 * scale)),
            "en_title": ImageFont.truetype(font_en_medium, int(72 * scale)),
            "en_info": ImageFont.truetype(font_en_medium, int(60 * scale)),
        }
except:
    st.error("Font loading error.")
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

text_color = "#002C5F"
red_color = "#ea2f2f"

# ===================== LAYOUT =====================

def draw_card(width, height, fonts, logo, contact_icon_size=(48, 48)):
    card = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(card)

    margin = int(width * 0.07)
    name_top = int(height * 0.18)
    spacing = int(height * 0.08)
    contact_top = int(height * 0.7)

    # Draw name/title
    draw.text((width - margin, name_top), reshape_arabic(name_ar), font=fonts["ar_name"], fill=text_color, anchor="ra")
    draw.text((width - margin, name_top + spacing), reshape_arabic(title_ar), font=fonts["ar_title"], fill=text_color, anchor="ra")
    draw.text((margin, name_top + 5), name_en, font=fonts["en_name"], fill=text_color)
    draw.text((margin, name_top + spacing + 5), title_en, font=fonts["en_title"], fill=text_color)

    # Contact info
    icon_offset = int(contact_icon_size[1] / 8)
    draw.text((margin + 60, contact_top + icon_offset), email, font=fonts["en_info"], fill=text_color)
    draw.text((margin + 60, contact_top + spacing + icon_offset), phone, font=fonts["en_info"], fill=text_color)

    email_icon = icon_email.resize(contact_icon_size)
    phone_icon = icon_phone.resize(contact_icon_size)
    card.paste(email_icon, (margin, contact_top), mask=email_icon)
    card.paste(phone_icon, (margin, contact_top + spacing), mask=phone_icon)

    # Logo
    logo_size = int(height * 0.25)
    logo_resized = ImageOps.contain(logo, (logo_size, logo_size))
    logo_pos = ((width - logo_resized.width) // 2, int(height * 0.43))
    card.paste(logo_resized, logo_pos, mask=logo_resized)

    return card

def draw_back(width, height, logo):
    card = Image.new("RGB", (width, height), color=red_color)
    logo_size = int(height * 0.25)
    logo_resized = ImageOps.contain(logo, (logo_size, logo_size))
    logo_pos = ((width - logo_resized.width) // 2, (height - logo_resized.height) // 2)
    card.paste(logo_resized, logo_pos, mask=logo_resized)
    return card

# ===================== CANVAS SIZES =====================

W_4K, H_4K = 3840, 2160
W_PRINT, H_PRINT = 1062, 591  # 9x5cm @ 300 DPI

fonts_4k = load_fonts(scale=1.0)
fonts_print = load_fonts(scale=1.5)  # Bump up for print

# ===================== GENERATE =====================

front_4k = draw_card(W_4K, H_4K, fonts_4k, logo_front)
back_4k = draw_back(W_4K, H_4K, logo_back)

front_print = draw_card(W_PRINT, H_PRINT, fonts_print, logo_front)
back_print = draw_back(W_PRINT, H_PRINT, logo_back)

# ===================== PREVIEW + EXPORT =====================

st.subheader("🔍 Preview (Front in 4K)")
st.image(front_4k.resize((1200, 675)))

def export_pdf(front, back, filename):
    buf = io.BytesIO()
    front.convert("RGB").save(buf, format="PDF", save_all=True, append_images=[back.convert("RGB")])
    st.download_button(f"⬇️ {filename}", buf.getvalue(), file_name=filename, mime="application/pdf")

export_pdf(front_4k, back_4k, "tray_card_4K.pdf")
export_pdf(front_print, back_print, "tray_card_print.pdf")
