import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os

# === Constants ===
CM = 118.11  # pixels per cm for 300 DPI
WIDTH_CM = 9
HEIGHT_CM = 5
W_PRINT = int(WIDTH_CM * CM)
H_PRINT = int(HEIGHT_CM * CM)
W_4K = 3840
H_4K = 2160
MARGIN = 150
QR_SIZE = 600
ICON_SIZE = (96, 96)
ICON_GAP = 40
CONTACT_SPACING = 120

# === Colors ===
COLOR_PRIMARY = "#0f2c5d"
COLOR_ACCENT = "#ea2f2f"
BG_COLOR = "white"

# === Paths ===
FONT_AR_BOLD = "assets/fonts/NotoSansArabic-SemiBold.ttf"
FONT_AR_REGULAR = "assets/fonts/NotoSansArabic-Regular.ttf"
FONT_EN_BOLD = "assets/fonts/PlusJakartaSans-Bold.ttf"
FONT_EN_MEDIUM = "assets/fonts/PlusJakartaSans-Medium.ttf"
LOGO_QR = "assets/icons/qr_code.png"
ICON_EMAIL = "assets/icons/email.png"
ICON_PHONE = "assets/icons/phone.png"

# === Load fonts ===
def load_fonts(scale=1):
    return {
        "ar_name": ImageFont.truetype(FONT_AR_BOLD, int(130 * scale)),
        "ar_title": ImageFont.truetype(FONT_AR_REGULAR, int(72 * scale)),
        "en_name": ImageFont.truetype(FONT_EN_BOLD, int(130 * scale)),
        "en_title": ImageFont.truetype(FONT_EN_REGULAR, int(72 * scale)),
        "en_info": ImageFont.truetype(FONT_EN_REGULAR, int(60 * scale))
    }

# === Load icon ===
def load_img(path, size):
    img = Image.open(path).convert("RGBA")
    return img.resize(size, Image.ANTIALIAS)

# === Generate Front ===
def generate_front(canvas_width, canvas_height, fonts):
    canvas = Image.new("RGB", (canvas_width, canvas_height), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    # Inputs
    ar_name = st.session_state.get("ar_name", "عبدالله رجب")
    ar_title = st.session_state.get("ar_title", "مدير تطوير الأعمال")
    en_name = st.session_state.get("en_name", "Abdullah Rajab")
    en_title = st.session_state.get("en_title", "Business Development Manager")
    email = st.session_state.get("email", "abdullah.rajab@alraedahdigital.sa")
    phone = st.session_state.get("phone", "+966 59 294 8994")

    # --- Top Left ---
    draw.text((MARGIN, MARGIN), en_name, font=fonts["en_name"], fill=COLOR_PRIMARY)
    draw.text((MARGIN, MARGIN + fonts["en_name"].getsize(en_name)[1] + 10), en_title, font=fonts["en_title"], fill=COLOR_PRIMARY)

    # --- Top Right ---
    ar_name_size = fonts["ar_name"].getsize(ar_name)
    ar_title_size = fonts["ar_title"].getsize(ar_title)
    x_ar = canvas_width - MARGIN - max(ar_name_size[0], ar_title_size[0])
    y_ar = MARGIN + 20  # tweak to align with English name
    draw.text((x_ar, y_ar), ar_name, font=fonts["ar_name"], fill=COLOR_PRIMARY)
    draw.text((x_ar, y_ar + ar_name_size[1] + 10), ar_title, font=fonts["ar_title"], fill=COLOR_PRIMARY)

    # --- Bottom Right (QR) ---
    qr = load_img(LOGO_QR, (QR_SIZE, QR_SIZE))
    canvas.paste(qr, (canvas_width - MARGIN - QR_SIZE, canvas_height - MARGIN - QR_SIZE), qr)

    # --- Bottom Left (Contact Info) ---
    icon_email = load_img(ICON_EMAIL, ICON_SIZE)
    icon_phone = load_img(ICON_PHONE, ICON_SIZE)

    email_text_height = fonts["en_info"].getsize(email)[1]
    phone_text_height = fonts["en_info"].getsize(phone)[1]
    email_text_offset = (ICON_SIZE[1] - email_text_height) // 2
    phone_text_offset = (ICON_SIZE[1] - phone_text_height) // 2

    x_contact = MARGIN
    y_email = canvas_height - MARGIN - ICON_SIZE[1] * 2 - CONTACT_SPACING
    y_phone = y_email + ICON_SIZE[1] + CONTACT_SPACING

    # Email line
    canvas.paste(icon_email, (x_contact, y_email), mask=icon_email)
    draw.text((x_contact + ICON_SIZE[0] + ICON_GAP, y_email + email_text_offset), email, font=fonts["en_info"], fill=COLOR_PRIMARY)

    # Phone line
    canvas.paste(icon_phone, (x_contact, y_phone), mask=icon_phone)
    draw.text((x_contact + ICON_SIZE[0] + ICON_GAP, y_phone + phone_text_offset), phone, font=fonts["en_info"], fill=COLOR_PRIMARY)

    return canvas

# === Save to PDF ===
def save_as_pdf(img):
    buf = io.BytesIO()
    img.save(buf, format="PDF", resolution=300.0)
    return buf

# === Streamlit UI ===
st.set_page_config(layout="wide")
st.title("📇 Preview (Front)")

with st.sidebar:
    st.header("📸 معلومات البطاقة")
    st.text_input("الاسم بالعربية", "عبدالله رجب", key="ar_name")
    st.text_input("المسمى بالعربية", "مدير تطوير الأعمال", key="ar_title")
    st.text_input("Full Name", "Abdullah Rajab", key="en_name")
    st.text_input("Job Title", "Business Development Manager", key="en_title")
    st.text_input("Email", "abdullah.rajab@alraedahdigital.sa", key="email")
    st.text_input("Phone", "+966 59 294 8994", key="phone")

fonts_4k = load_fonts(scale=1.0)
front_4k = generate_front(W_4K, H_4K, fonts_4k)
buf_4k = save_as_pdf(front_4k)
st.download_button("📥 tray_card_4K.pdf", data=buf_4k, file_name="tray_card_4K.pdf")

fonts_print = load_fonts(scale=W_PRINT / W_4K)
front_print = generate_front(W_PRINT, H_PRINT, fonts_print)
buf_print = save_as_pdf(front_print)
st.download_button("📥 tray_card_print.pdf", data=buf_print, file_name="tray_card_print.pdf")

st.image(front_4k, caption="Preview", use_column_width=True)
