import qrcode
import io
import base64

def generate_qr_code(offer_id: str, description: str, points_required: int) -> str:
    """Generate a QR code containing offer details and return it as a base64-encoded string."""
    
    # Prepare QR data
    qr_data = f"Offer ID: {offer_id}\nDescription: {description}\nPoints Required: {points_required}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Generate image
    img = qr.make_image(fill="black", back_color="white")
    
    # Convert image to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return qr_base64  # Return base64 image
