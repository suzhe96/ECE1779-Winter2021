import os
import tempfile
import cv2
import requests
import validators
from urllib.request import urlopen
from PIL import Image as PILImage
from wand.image import Image
from flask import render_template, request, session, redirect, url_for
from app import a1_webapp
from FaceMaskDetection import pytorch_infer

'''TODO: TRY TO REMOVE THE LINE AFTER DEPLOY TO EC2
'''
os.environ['KMP_DUPLICATE_LIB_OK']='True'


# https://stackoverflow.com/questions/10543940/check-if-a-url-to-an-image-is-up-and-exists-in-python
def __is_url_image(image_url):
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    r = requests.head(image_url)
    if r.headers["content-type"] in image_formats:
        return True
    print("Not a image URL")
    return False


@a1_webapp.route('/detector_upload_route', methods=['GET', 'POST'])
def detector_upload():
    if request.method == 'POST':
        image_url = request.form['upload_url']
        image_file = request.files['upload_image']
        if image_url != '' and image_file.filename != '':
            return render_template("detector_upload.html", title="Upload Image", error="Error: Mutiple input sources")
        if image_url == '' and image_file.filename == '':
            return render_template("detector_upload.html", title="Upload Image", error="Error: Empty input sources")

        file_handle, path = tempfile.mkstemp()
        filename_original = path+"_original.jpeg"
        filename_detected = path+"_detected.png" 
        if image_url != '' and image_file.filename == '':
            if not validators.url(image_url) or not __is_url_image(image_url):
                return render_template("detector_upload.html", title="Upload Image", error="Error: Invalid Image URL")
            im = PILImage.open(urlopen(image_url))
            im.save(filename_original) 
        if image_url == '' and image_file.filename != '':
            with Image(file=image_file) as img:
                img.save(filename=filename_original)

        total_detected, total_masked, image = pytorch_infer.entry(filename_original)
        cv2.imwrite(filename_detected, image)
        display_dict = {"img_path": filename_detected, "total_detected": total_detected, "total_masked": total_masked}
        os.remove(path)

        # TODO: DETECTED IMAGE QUERY FROM DB
        return render_template("detector_display.html", title="Display Model Image", display_dict=display_dict)
    return render_template("detector_upload.html", title="Upload Image", error='')
