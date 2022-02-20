from flask import Flask, request, send_file
from flask_restful import Api, Resource, reqparse
import werkzeug
import os
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


def password_required(func):  # decorator for using methods only with auth
    @wraps(func)
    def wrapper(*args, **kwargs):
        password_field = 'X-PASSWORD'
        headers = request.headers

        if password_field in headers:
            password = headers[password_field]
        else:
            return {'status': 'You need a password'}
        if password != PASSWORD:
            return {'status': 'You send a invalid password'}
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

        if self.read_infoFile('order.txt'):
            return {'status': 'Wait some times. Computer is busy now by other picture'}

        cur_picture_path = pictures_folder + '/' + picture.filename  # Path to current picture
        pictures_path = self.content_path + pictures_folder  # Directory with pictures
        upd_pictures_path = self.content_path + 'Updated_' + pictures_folder  # Directory with updated pictures
        if self.is_path_in_infoFile(cur_picture_path, 'order.txt'):
            return {'status': 'You already send this picture to order'}

        if not os.path.exists(pictures_path):
            os.mkdir(pictures_path)
        if not os.path.exists(upd_pictures_path):
            os.mkdir(upd_pictures_path)

        args_realsr = ''
        if args['realsr']:
            args_realsr = args['realsr']
        args_realsr = args_realsr.split()

        self.add_information(cur_picture_path, 'order.txt')
        # the future name is returned from the process_picture method
        future_filename = 'Updated_' + pictures_folder + '/' \
                          + self.process_picture(picture, pictures_path, upd_pictures_path, *args_realsr)  # called here

        after_processing_thread = threading.Thread(target=self.after_processing,
                                                   args=(future_filename,),
                                                   name='after_processing')
        after_processing_thread.start()

        return {"status": "Picture was uploaded", 'futureName': future_filename}

    @password_required
    def get(self, pictures_folder, picture=None):
        path = self.content_path + pictures_folder
        if not os.path.exists(path):
            return {'status': 'This folder does not exist'}

        if picture:
            path += '/' + picture
            obj = 'picture'
        else:
            obj = 'folder'

        if os.path.exists(path):
            if picture:
                return send_file(path)
            else:
                files = os.listdir(path)
                return {'status': files}
        else:
            return {'status': f'This {obj} does not exist'}

    @password_required
    def delete(self, pictures_folder, picture=None):
        path = self.content_path + pictures_folder
        if not os.path.exists(path):
            return {'status': 'This folder does not exist'}

        if picture:
            path += '/' + picture
            obj = 'picture'
        else:
            obj = 'folder'

        if os.path.exists(path):
            if picture:
                os.remove(path)
            else:
                rmtree(path)
            return {'status': f'The {obj} has been deleted'}
        else:
            return {'status': f'This {obj} does not exist'}


class Information(Resource, TextFilesFunctional):
    @password_required
    def get(self, infoFile):
        if not infoFile.endswith('.txt'):
            infoFile += '.txt'
        info = self.read_infoFile(infoFile)
        if info is not None:
            if infoFile == 'new_updated.txt':
                self.clear_infoFile(infoFile)
            return {'File list': info}
        else:
            return {'status': 'File not exists'}


api.add_resource(Content, '/content/<string:pictures_folder>', '/content/<string:pictures_folder>/<string:picture>')
api.add_resource(Information, '/info/<string:infoFile>')

if __name__ == "__main__":
    app.run(debug=True)
