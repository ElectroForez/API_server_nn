from flask import Flask, request, send_file, jsonify
from flask_restful import Api, Resource, reqparse
import werkzeug
import os
import time
import threading
from config import PASSWORD
from TextFilesInstruments import TextFilesFunctional
from Processing import Processing
from functools import wraps
from shutil import rmtree
app = Flask(__name__)
api = Api(app)


parser = reqparse.RequestParser()
parser.add_argument('picture', type=werkzeug.datastructures.FileStorage, location='files')
parser.add_argument('realsr', type='string', location='args')

#parser.add_argument('password', type='string', location='headers')



def password_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        password_field = 'X-PASSWORD'
        headers = request.headers

        if password_field in headers:
            password = headers[password_field]
        else:
            return {'status': 'You need a password'}
        if password != PASSWORD:
            return {'status': 'You send invalid password'}
        return func(*args, **kwargs)
    return wrapper


class Content(Resource, Processing):
    def __init__(self):
        super().__init__()
        self.content_path = 'content/'
       

    @password_required
    def post(self, pictures_folder):
        args = parser.parse_args()
        picture = args['picture']
        if not picture:
            return {"status": "No picture in request"}

        if pictures_folder.startswith('Updated_'):
            return {'status': 'You cannot post picture to folder with updated pictures'}

        if self.is_processing:
            return {'status': 'Wait some times. Computer is busy now by other picture'}

        cur_picture_path = pictures_folder + '/' + picture.filename #Path to current picture
        pictures_path = self.content_path + pictures_folder#Directory with pictures
        upd_pictures_path = self.content_path + 'Updated_' + pictures_folder #Directory with updated pictures
        if self.is_path_in_infoFile(cur_picture_path, 'order.txt'):
            return {'status': 'You already send this picture to order'}

        if os.path.exists(self.content_path + cur_picture_path):
            return {'status': 'This picture already exists'}

        if not os.path.exists(pictures_path):
            os.mkdir(pictures_path)
        if not os.path.exists(upd_pictures_path):
            os.mkdir(upd_pictures_path)
        
        args_realsr = ''
        if args['realsr']:
            args_realsr = args['realsr']
        args_realsr = args_realsr.split()

        self.add_information(cur_picture_path, 'order.txt')
        future_filename = 'Updated_' + pictures_folder + '/' \
                          + self.process_picture(picture, pictures_path, upd_pictures_path, *args_realsr)

        self.after_processing_thread = threading.Thread(target=self.after_processing,
                                                        args=(future_filename,),
                                                        name='after_proccessing')
        self.after_processing_thread.start()
        self.is_processing = True

        return {"status": "Picture was uploaded", 'futureName': future_filename}

    @password_required
    def get(self, pictures_folder, picture = None):
        if not picture:
            return {'status':pictures_folder}
        path_to_file = self.content_path + pictures_folder + '/' + picture
        if os.path.exists(path_to_file):
            return send_file(path_to_file)
        else:
            return {'status': 'file is not exists'}

    @password_required
    def delete(self, pictures_folder, picture = None):
        if picture:
            path_to_file = self.content_path + pictures_folder + '/' + picture
            if os.path.exists(path_to_file):
                os.remove(path_to_file)
                return {'status': 'The picture has been deleted'}
            else:
                return {'status': 'This picture does not exist'}
        else:
            path_to_folder = self.content_path + pictures_folder
            if os.path.isdir(path_to_folder):
                rmtree(path_to_folder)
                return {'status': 'The folder has been deleted'}
            else:
                return {'status': 'This folder does not exist'}


class Information(Resource, TextFilesFunctional):
    @password_required
    def get(self, infoFile):
        if not infoFile.endswith('.txt'):
            infoFile += '.txt'
        info = self.read_infoFile(infoFile)
        if info is not None:
            if infoFile == 'new_updated.txt':
                self.clear_file(infoFile)
            return {'File list': info}
        else:
            return {'status': 'File not exists'}

    # def delete(self, pictures_folder):

api.add_resource(Content, '/content/<string:pictures_folder>', '/content/<string:pictures_folder>/<string:picture>')
api.add_resource(Information, '/info/<string:infoFile>')

if __name__ == "__main__":
    app.run(debug=True)