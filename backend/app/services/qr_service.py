import io
import qrcode
from app.core.config import settings

def build_clinic_qr_png(slug: str) -> bytes:
    """Generates PNG image bytes for a clinic's intake URL QR code."""
    target_url = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/q/{slug}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(target_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()
