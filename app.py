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
ICON_GAP = 60
CONTACT_LINE_HEIGHT = 100
TEXT_LINE_GAP = 60
AUTO_GAP = 60
ICON_SIZE = (96, 96)

# --- LOADERS ---
def reshape_arabic(text):
    return get_display(arabic_reshaper.reshape(text))

def load_img(path, size=None):
    try:
        img = Image.open(path).convert("RGBA")
        if size:
            img = img.resize(size, Image.LANCZOS)
        return img
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        return Image.new("RGBA", size or (40, 40), "gray")

def load_font(path, size):
    return ImageFont.truetype(path, size)

# --- ASSETS ---
icon_email = load_img("assets/icons/email_96.png", ICON_SIZE)
icon_phone = load_img("assets/icons/phone_96.png", ICON_SIZE)
qr_code = load_img("assets/icons/qr_code.png")
logo_back = load_img("assets/icons/Tray_logo_white.png")

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

    # Names and titles
    name_ar_text = reshape_arabic(name_ar)
    title_ar_text = reshape_arabic(title_ar)

    name_en_box = fonts["en_name"].getbbox(name_en)
    name_en_height = name_en_box[3] - name_en_box[1]

    name_ar_box = fonts["ar_name"].getbbox(name_ar_text)
    name_ar_height = name_ar_box[3] - name_ar_box[1]

    title_en_box = fonts["en_title"].getbbox(title_en)
    title_en_height = title_en_box[3] - title_en_box[1]

    title_ar_box = fonts["ar_title"].getbbox(title_ar_text)
    title_ar_height = title_ar_box[3] - title_ar_box[1]

    name_en_y = MARGIN
    name_ar_y = MARGIN
    title_en_y = name_en_y + name_en_height + AUTO_GAP
    title_ar_y = name_ar_y + name_ar_height + AUTO_GAP

    draw.text((MARGIN, name_en_y), name_en, font=fonts["en_name"], fill=TEXT_COLOR)
    draw.text((width - MARGIN, name_ar_y), name_ar_text, font=fonts["ar_name"], fill=TEXT_COLOR, anchor="ra")

    draw.text((MARGIN, title_en_y), title_en, font=fonts["en_title"], fill=TEXT_COLOR)
    draw.text((width - MARGIN, title_ar_y), title_ar_text, font=fonts["ar_title"], fill=TEXT_COLOR, anchor="ra")

    # Bottom Right (QR)
    qr_scaled = ImageOps.contain(qr_code, (QR_SIZE, QR_SIZE))
    qr_bottom_y = height - MARGIN

    # Bottom Left (Contact Info)
    contact_y = qr_bottom_y - 2 * CONTACT_LINE_HEIGHT
    email_box = fonts["en_info"].getbbox(email)
    email_height = email_box[3] - email_box[1]

    email_y = contact_y + (ICON_SIZE[1] - email_height) // 2
    phone_y = email_y + email_height + TEXT_LINE_GAP

    draw.text((MARGIN + ICON_SIZE[0] + ICON_GAP, email_y), email, font=fonts["en_info"], fill=TEXT_COLOR)
    draw.text((MARGIN + ICON_SIZE[0] + ICON_GAP, phone_y), phone, font=fonts["en_info"], fill=TEXT_COLOR)

    icon_email_y = email_y + email_height // 2 - icon_email.height // 2
    icon_phone_y = phone_y + email_height // 2 - icon_phone.height // 2

    card.paste(icon_email, (MARGIN, icon_email_y), mask=icon_email)
    card.paste(icon_phone, (MARGIN, icon_phone_y), mask=icon_phone)

    card.paste(qr_scaled, (width - MARGIN - qr_scaled.width, qr_bottom_y - qr_scaled.height), mask=qr_scaled)
    return card

def generate_back(width, height):
    card = Image.new("RGB", (width, height), RED_COLOR)
    logo = ImageOps.contain(logo_back, (1300, 1300))
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
