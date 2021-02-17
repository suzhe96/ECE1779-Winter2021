import os
import sys
import json
import tempfile
import cv2
import time
import requests
import validators
import mysql.connector
from urllib.request import urlopen
from PIL import Image as PILImage
from wand.image import Image
from flask import render_template, request, session, redirect, url_for, g
from flask_login import current_user
from app import a1_webapp
from app.dbhandler import get_db
from FaceMaskDetection import pytorch_infer

'''TODO: TRY TO REMOVE THE LINE AFTER DEPLOY TO EC2
'''
os.environ['KMP_DUPLICATE_LIB_OK']='True'


# Ref: https://stackoverflow.com/questions/10543940/check-if-a-url-to-an-image-is-up-and-exists-in-python
def __is_url_image(image_url):
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    r = requests.head(image_url)
    if r.headers["content-type"] in image_formats:
        return True
    print("Not a image URL")
    return False


def __get_render_template(html, title_in, param_in=None, error_in=None):
    return render_template(html, title=title_in, param=param_in, error=error_in)


def __get_image_category(total_detected, total_masked):
    '''
    1: Images with no faces detected
    2: Images with all faces masked
    3: Images with no face masked
    4: Images with some faces masked
    '''
    if total_detected == 0: return 1
    if total_detected == total_masked: return 2
    if total_masked == 0: return 3
    return 4


def __get_timestamp_string():
    timestamp = time.time()
    return str(timestamp).split('.')[0] + str(timestamp).split('.')[1]


@a1_webapp.route('/detector_upload_route', methods=['GET', 'POST'])
def detector_upload():
    if request.method == 'POST':
        image_url = request.form['upload_url']
        image_file = request.files['upload_image']
        if image_url != '' and image_file.filename != '':
            return __get_render_template("detector_upload.html", "Upload Image", error_in = "Error: Mutiple input sources")
        if image_url == '' and image_file.filename == '':
            return __get_render_template("detector_upload.html", "Upload Image", error_in = "Error: Empty input sources")

        file_handle, path = tempfile.mkstemp()
        filename_original = path+"_original.jpeg"
        filename_detected = path+"_detected.png" 
        if image_url != '' and image_file.filename == '':
            if not validators.url(image_url) or not __is_url_image(image_url):
                return __get_render_template("detector_upload.html", "Upload Image", error_in = "Error: Invalid Image URL")
            try:
                im = PILImage.open(urlopen(image_url))
                im.save(filename_original) 
            except:
               return __get_render_template("detector_upload.html", "Upload Image", error_in = "Error: Bad image file from URL") 
        if image_url == '' and image_file.filename != '':
            try:
                with Image(file=image_file) as img:
                    img.save(filename=filename_original)
            except:
                return __get_render_template("detector_upload.html", "Upload Image", error_in = "Error: Bad Image file")
        
        try:
            total_detected, total_masked, image = pytorch_infer.entry(filename_original)
        except:
            return __get_render_template("detector_upload.html", "Upload Image", error_in = "Error: Face detection exception - try another image")
        cv2.imwrite(filename_detected, image)
        param = {"img_path": filename_detected, "total_detected": total_detected, "total_masked": total_masked}
        

        # TODO: DETECTED IMAGE QUERY FROM DB
        __username = current_user.username
        print("__username:{}".format(__username))
        cnx = get_db(Debug=True)
        cursor = cnx.cursor()

        query = '''SELECT id FROM users WHERE username = %s'''
        cursor.execute(query, (__username,))
        __user_id = cursor.fetchone()[0]
        print("__user_id:{}".format(__user_id))
        __category = __get_image_category(total_detected, total_masked)
        print("__category:{}".format(__category))
        __image_key = __get_timestamp_string()
        print("__image_key:{}".format(__image_key))
        query = '''INSERT INTO images (category, user_id, image_key) VALUES (%s,%s,%s)'''
        cursor.execute(query, (__category,__user_id,__image_key))
        cnx.commit()

        os.remove(path)
        os.remove(filename_original)
        os.remove(filename_detected)
        return __get_render_template("detector_display.html", "Display Model Image", param_in = param)
    if request.method == 'GET':
        return __get_render_template("detector_upload.html", "Upload Image", error_in = None)

@a1_webapp.route('/api/upload', methods=['GET','POST'])
def api_upload():
    failure_dict = {"success": "false", "error": {"code": 500, "message" : None}}
    success_dict = {"success": "true", "payload": {"num_faces" : None, "num_masked": None, "num_unmasked" : None}}
    if request.method == 'GET':
        return __get_render_template("api_upload.html", "API upload for testing", error_in = None)
    if request.method == 'POST':
        image_file = request.files['file']
        file_handle, path = tempfile.mkstemp()
        filename_api = path+"_api.jpeg"
        print(path)
        try:
            with Image(file=image_file) as img:
                img.save(filename=filename_api)
        except:
            failure_dict["error"]["message"] = "Open image file error"
            return json.dumps(failure_dict)

        try: 
            total_detected, total_masked, image = pytorch_infer.entry(filename_api)
        except:
            failure_dict["error"]["message"] = "Face Detector Error"
            return json.dumps(failure_dict)
        os.remove(path)
        os.remove(filename_api)
        success_dict["payload"]["num_faces"] = total_detected
        success_dict["payload"]["num_masked"] = total_masked
        success_dict["payload"]["num_unmasked"] = total_detected - total_masked
        return json.dumps(success_dict)
