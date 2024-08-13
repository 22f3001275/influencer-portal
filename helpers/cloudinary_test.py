import cloudinary
import cloudinary.uploader

# Configuration
cloudinary.config(
    cloud_name="dxboktgpn",
    api_key="164964595358237",
    api_secret="-CVO4rSwDH41TrpAc7S9NkcW830",
    secure=True
)

# Upload an image
upload_result = cloudinary.uploader.upload("https://res.cloudinary.com/demo/image/upload/getting-started/shoes.jpg",
                                           public_id="shoes")
print(upload_result["secure_url"])

