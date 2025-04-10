import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

# Constants
W, H = 3508, 2480  # 300 DPI for 11.7in x 8.3in (A4 landscape)
MARGIN = 150
QR_SIZE = 300
ICON_SIZE = (48, 48)
ICON_GAP = 30
LINE_SPACING = 60
TEXT_COLOR = (20, 40, 80)

# Paths
FONT_AR_REGULAR = "assets/fonts/NotoSansArabic-Regular.ttf"
FONT_AR_BOLD = "assets/fonts/NotoSansArabic-SemiBold.ttf"
FONT_EN_BOLD = "assets/fonts/PlusJakartaSans-Bold.ttf"
FONT_EN_REGULAR = "assets/fonts/PlusJakartaSans-Regular.ttf"
ICON_EMAIL = "assets/icons/email.png"
ICON_PHONE = "assets/icons/phone.png"
QR_IMAGE = "assets/icons/qr_code.png"

# Loaders
def load_font(path, size):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Font file not found: {path}")
    return ImageFont.truetype(path, size)

def load_img(path, size=None):
    img = Image.open(path).convert("RGBA")
    if size:
        img = img.resize(size, Image.LANCZOS)
    return img

# Generator
def generate_card(ar_name, ar_title, en_name, en_title, email, phone):
    card = Image.new("RGBA", (W, H), "white")
    draw = ImageDraw.Draw(card)

    fonts = {
        "ar_bold": load_font(FONT_AR_BOLD, 60),
        "ar_regular": load_font(FONT_AR_REGULAR, 42),
        "en_bold": load_font(FONT_EN_BOLD, 60),
        "en_regular": load_font(FONT_EN_REGULAR, 42),
    }

    icon_email = load_img(ICON_EMAIL, ICON_SIZE)
    icon_phone = load_img(ICON_PHONE, ICON_SIZE)
    qr = load_img(QR_IMAGE, (QR_SIZE, QR_SIZE))

    # Top Left (EN)
    en_x = MARGIN
    en_y = MARGIN
    draw.text((en_x, en_y), en_name, font=fonts["en_bold"], fill=TEXT_COLOR)
    en_y += fonts["en_bold"].getbbox(en_name)[3] + 10
    draw.text((en_x, en_y), en_title, font=fonts["en_regular"], fill=TEXT_COLOR)

    # Top Right (AR)
    ar_name_bbox = fonts["ar_bold"].getbbox(ar_name)
    ar_title_bbox = fonts["ar_regular"].getbbox(ar_title)
    ar_x = W - MARGIN
    ar_name_y = MARGIN
    ar_title_y = ar_name_y + ar_name_bbox[3] + 10
    draw.text((ar_x, ar_name_y), ar_name, font=fonts["ar_bold"], fill=TEXT_COLOR, anchor="ra")
    draw.text((ar_x, ar_title_y), ar_title, font=fonts["ar_regular"], fill=TEXT_COLOR, anchor="ra")

    # Bottom Left (contact info)
    contact_y = H - MARGIN - ICON_SIZE[1]*2 - LINE_SPACING
    draw.bitmap((MARGIN, contact_y), icon_email, fill=None)
    draw.text((MARGIN + ICON_SIZE[0] + ICON_GAP, contact_y + (ICON_SIZE[1] - fonts["en_regular"].getbbox(email)[3]) // 2),
              email, font=fonts["en_regular"], fill=TEXT_COLOR)

    contact_y += ICON_SIZE[1] + LINE_SPACING
    draw.bitmap((MARGIN, contact_y), icon_phone, fill=None)
    draw.text((MARGIN + ICON_SIZE[0] + ICON_GAP, contact_y + (ICON_SIZE[1] - fonts["en_regular"].getbbox(phone)[3]) // 2),
              phone, font=fonts["en_regular"], fill=TEXT_COLOR)

    # Bottom Right (QR)
    card.paste(qr, (W - MARGIN - QR_SIZE, H - MARGIN - QR_SIZE), mask=qr)
    return card

# Streamlit App
st.title("🔍 Preview (Front)")
ar_name = st.text_input("Arabic Name", "")
ar_title = st.text_input("Arabic Job Title", "")
en_name = st.text_input("English Name", "")
en_title = st.text_input("English Job Title", "")
email = st.text_input("Email", "")
phone = st.text_input("Phone", "")

if ar_name and ar_title and en_name and en_title and email and phone:
    card_image = generate_card(ar_name, ar_title, en_name, en_title, email, phone)
    st.image(card_image)

    from io import BytesIO
    pdf_output = BytesIO()
    card_image.save(pdf_output, format="PDF", resolution=300)
    st.download_button("📥 Download PDF", pdf_output.getvalue(), file_name="tray_card_4K.pdf")
else:
    st.warning("Please fill in all the fields to generate your card.")
