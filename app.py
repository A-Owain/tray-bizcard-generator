import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(layout="centered", page_title="TRAY Business Card Generator")

# --- CONFIG ---
MARGIN = 150
BG_COLOR = "white"
TEXT_COLOR = "#002C5F"
RED_COLOR = "#ea2f2f"
QR_SIZE = 600
LINE_SPACING = 180
ICON_GAP = 60
CONTACT_LINE_GAP = 60

# --- LOADERS ---
def reshape_arabic(text):
    return get_display(arabic_reshaper.reshape(text))

def load_img(path, size=None):
    try:
        img = Image.open(path).convert("RGBA")
        if size:
            img = img.resize(size, Image.ANTIALIAS)
        return img
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        return Image.new("RGBA", size or (40, 40), "gray")

def load_font(path, size):
    return ImageFont.truetype(path, size)

# --- ASSETS ---
icon_email = load_img("assets/icons/email.png", (96, 96))
icon_phone = load_img("assets/icons/phone.png", (96, 96))
qr_code = load_img("assets/qr_code.png")
logo_back = load_img("assets/Tray_logo_white.png")

font_ar_bold = "fonts/NotoSansArabic-SemiBold.ttf"
font_ar_reg = "fonts/NotoSansArabic-Regular.ttf"
font_en_bold = "fonts/PlusJakartaSans-Bold.ttf"
font_en_med = "fonts/PlusJakartaSans-Medium.ttf"

def load_fonts(scale=1.0):
    return {
        "ar_name": load_font(font_ar_bold, int(110 * scale)),
        "ar_title": load_font(font_ar_reg, int(70 * scale)),
        "en_name": load_font(font_en_bold, int(110 * scale)),
        "en_title": load_font(font_en_med, int(70 * scale)),
        "en_info": load_font(font_en_med, int(80 * scale)),
    }

# --- SIDEBAR ---
with st.sidebar:
    st.title("🪪 معلومات البطاقة")
    name_ar = st.text_input("الاسم بالعربية", "عبدالله رجب")
    title_ar = st.text_input("المسمى بالعربية", "مدير تطوير الأعمال")
    name_en = st.text_input("Full Name", "Abdullah Rajab")
    title_en = st.text_input("Job Title", "Business Development Manager")
    email = st.text_input("Email", "abdullah.rajab@alraedahdigital.sa")
    phone = st.text_input("Phone", "+966 59 294 8994")

# --- GENERATOR ---
def generate_front(width, height, fonts):
    card = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(card)

    # Top Left (EN)
    draw.text((MARGIN, MARGIN), name_en, font=fonts["en_name"], fill=TEXT_COLOR)
    draw.text((MARGIN, MARGIN + LINE_SPACING), title_en, font=fonts["en_title"], fill=TEXT_COLOR)

    # Top Right (AR)
    draw.text((width - MARGIN, MARGIN), reshape_arabic(name_ar), font=fonts["ar_name"], fill=TEXT_COLOR, anchor="ra")
    draw.text((width - MARGIN, MARGIN + LINE_SPACING), reshape_arabic(title_ar), font=fonts["ar_title"], fill=TEXT_COLOR, anchor="ra")

    # Bottom Left (Contact Info)
    contact_y = height - MARGIN - 180
    dummy_img = Image.new("RGB", (10, 10))
    dummy_draw = ImageDraw.Draw(dummy_img)
    email_bbox = dummy_draw.textbbox((0, 0), email, font=fonts["en_info"])
    text_height = email_bbox[3] - email_bbox[1]
    text_offset = (icon_email.size[1] - text_height) // 2

    draw.text((MARGIN + 96 + ICON_GAP, contact_y + text_offset), email, font=fonts["en_info"], fill=TEXT_COLOR)
    draw.text((MARGIN + 96 + ICON_GAP, contact_y + CONTACT_LINE_GAP + text_offset), phone, font=fonts["en_info"], fill=TEXT_COLOR)
    card.paste(icon_email, (MARGIN, contact_y), mask=icon_email)
    card.paste(icon_phone, (MARGIN, contact_y + CONTACT_LINE_GAP), mask=icon_phone)

    # Bottom Right (QR)
    qr_scaled = ImageOps.contain(qr_code, (QR_SIZE, QR_SIZE))
    card.paste(qr_scaled, (width - MARGIN - qr_scaled.width, height - MARGIN - qr_scaled.height), mask=qr_scaled)
    return card

def generate_back(width, height):
    card = Image.new("RGB", (width, height), RED_COLOR)
    logo = ImageOps.contain(logo_back, (1000, 1000))
    card.paste(logo, ((width - logo.width)//2, (height - logo.height)//2), mask=logo)
    return card

# --- SIZES ---
W_4K, H_4K = 3840, 2160
W_PRINT, H_PRINT = 1062, 591

fonts_4k = load_fonts(1.0)
fonts_print = load_fonts(1.5)

front_4k = generate_front(W_4K, H_4K, fonts_4k)
back_4k = generate_back(W_4K, H_4K)

front_print = generate_front(W_PRINT, H_PRINT, fonts_print)
back_print = generate_back(W_PRINT, H_PRINT)

# --- DISPLAY + EXPORT ---
st.subheader("🔍 Preview (Front)")
st.image(front_4k.resize((1200, 675)))

def export_pdf(front, back, name):
    buf = io.BytesIO()
    front.convert("RGB").save(buf, format="PDF", save_all=True, append_images=[back.convert("RGB")])
    st.download_button(f"⬇️ {name}", buf.getvalue(), file_name=name, mime="application/pdf")

export_pdf(front_4k, back_4k, "tray_card_4K.pdf")
export_pdf(front_print, back_print, "tray_card_print.pdf")
