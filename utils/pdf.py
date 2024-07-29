import requests, tempfile

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image

async def photo_to_pdf(photo_url, pdf_bytes):
    response = requests.get(photo_url)
    image_data = response.content
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image_file:
        temp_image_file.write(image_data)
        temp_image_path = temp_image_file.name

    img = Image.open(temp_image_path)
    img_width, img_height = img.size

    pdf_canvas = canvas.Canvas(pdf_bytes, pagesize=letter)
    
    aspect_ratio = img_width / img_height
    new_width = letter[0]
    new_height = new_width / aspect_ratio
    if new_height > letter[1]:
        new_height = letter[1]
        new_width = new_height * aspect_ratio

    pdf_canvas.drawImage(temp_image_path, 0, 0, width=new_width, height=new_height)
    pdf_canvas.save()
