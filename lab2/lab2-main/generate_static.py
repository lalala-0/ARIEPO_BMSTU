from PIL import Image, ImageDraw, ImageFont
import qrcode
import os
import sys

def generate_qr(commit_hash, commit_time):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"Commit: {commit_hash}\nTime: {commit_time}")
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_image.save("static/qr_code2.png")

def generate_html(commit_hash, commit_time, message_file="message.txt"):
    message = "Default message"
    if os.path.exists(message_file):
        with open(message_file, 'r') as f:
            message = f.read().strip()

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Static Content Demo</title>
    </head>
    <body>
        <h1>Generated Static Content</h1>
        <p>Commit Hash: {commit_hash}</p>
        <p>Commit Time: {commit_time}</p>
        <p>Message: {message}</p>
        <img src="qr_code.png" alt="QR Code">
        <img src="qr_code2.png" alt="QR Code">
    </body>
    </html>
    """

    os.makedirs("static", exist_ok=True)
    with open("static/index.html", "w") as f:
        f.write(html_content)

if __name__ == "__main__":
    commit_hash = sys.argv[1] if len(sys.argv) > 1 else "test"
    commit_time = sys.argv[2] if len(sys.argv) > 2 else "Unknown Time"  # Changed from sys.argv[3]
    generate_qr(commit_hash, commit_time)
    generate_html(commit_hash, commit_time)