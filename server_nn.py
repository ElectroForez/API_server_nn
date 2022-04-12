from flask import Flask, request, send_file
from flask_restful import Api, Resource, reqparse
import werkzeug
import os
import threading
from config_nn import PASSWORD, CONTENT_PATH
from infofile import InfofileHandler
from processing import Processing
from functools import wraps
from shutil import rmtree
import sys

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()


def password_required(func):  # decorator for using methods only with auth
    @wraps(func)
    def wrapper(*args, **kwargs):
        password_field = 'X-PASSWORD'
        headers = request.headers

        if password_field in headers:
            password = headers[password_field]
        else:
            return {'status': 'You need a password'}, 401
        if password != PASSWORD:
            return {'status': 'You send a invalid password'}, 401
        return func(*args, **kwargs)

    return wrapper


class Content(Resource, Processing):
    """class with methods to load pictures"""
    def __init__(self):
        super().__init__()
        self.content_path = CONTENT_PATH
        if not os.path.exists(self.content_path):
            os.mkdir(self.content_path)

    @password_required
    def post(self, pictures_folder):
        parser.add_argument('picture', type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('realsr', type=str, location='args')
        parser.add_argument('output_filename', type=str, location='args')
        args = parser.parse_args()
        picture = args['picture']
        if not picture:
            return {"status": "No picture in request"}, 400
        if pictures_folder.startswith('Updated_'):
            return {'status': 'You cannot post picture to folder with updated pictures'}, 403
        if self.is_busy():
            return {'status': 'Wait some times. Computer is busy now by other picture'}, 503
        pictures_path = self.content_path + pictures_folder  # Directory with not updated pictures
        cur_picture_path = pictures_folder + '/' + picture.filename  # Not full path to  current picture
        upd_pictures_path = 'Updated_' + pictures_folder  # Not full path to directory with updated pictures
        if self.is_path_in_infoFile(cur_picture_path, 'order.txt'):
            return {'status': 'You already send this picture to order'}

        if not os.path.exists(pictures_path):
            os.mkdir(pictures_path)
        if not os.path.exists(self.content_path + upd_pictures_path):
            os.mkdir(self.content_path + upd_pictures_path)

        args_realsr = args['realsr']
        if not args_realsr:
            args_realsr = ''
        args_realsr = args_realsr.split()

        picture.save('{}/{}'.format(pictures_path, picture.filename))

        output_filename = args['output_filename']
        if output_filename is None:
            output_filename = picture.filename.split('.')[0] + '.png'
        output_filename = upd_pictures_path + '/' + output_filename

        if self.process_picture(self.content_path + cur_picture_path, self.content_path + output_filename,
                             *args_realsr) == -1:
            return {'status': 'Invalid args realsr or extension of files'}, 400
        after_processing_thread = threading.Thread(target=self.after_processing,
                                                   args=(output_filename,),
                                                   name='after_processing')
        after_processing_thread.start()
        self.add_information(cur_picture_path, 'order.txt')
        return {"status": "Picture was uploaded", 'output_filename': output_filename}, 202

    @password_required
    def get(self, pictures_folder, picture=None):
        path = self.content_path + pictures_folder
        if not os.path.exists(path):
            return {'status': 'This folder does not exist'}, 404

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
                return {'Files list': files}
        else:
            return {'status': f'This {obj} does not exist'}, 404

    @password_required
    def delete(self, pictures_folder, picture=None):
        path = self.content_path + pictures_folder
        if not os.path.exists(path):
            return {'status': 'This folder does not exist'}, 404

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
            return {'status': f'This {obj} does not exist'}, 404


class Information(Resource, InfofileHandler):
    """method to get info about processing"""
    @password_required
    def get(self, infoFile):
        if not infoFile.endswith('.txt'):
            infoFile += '.txt'
        info = self.read_infoFile(infoFile)
        if info is not None:
            return {'Files list': info}
        else:
            return {'status': 'File not exists'}, 404


class Check(Resource, InfofileHandler):
    """method to check some condition"""
    @password_required
    def get(self, condition, pictures_folder=None, picture=None):
        if condition == 'available':
            return {'status': True,
                    'message': 'Hello from API_NN'}
        elif condition == 'busy':
            return {'status': self.is_busy()}
        elif condition == 'content':
            exists = os.path.exists(CONTENT_PATH + pictures_folder + '/' + picture)
            return {'File exists': exists}
        return {'status': 'Not found this condition'}, 404


api.add_resource(Content, '/content/<string:pictures_folder>', '/content/<string:pictures_folder>/<string:picture>', )
api.add_resource(Information, '/info/<string:infoFile>')
api.add_resource(Check, '/check/<string:condition>/',
                 '/check/<string:condition>/<string:pictures_folder>/<string:picture>')

if __name__ == "__main__":
    InfofileHandler().delete_information('order.txt')
    InfofileHandler().delete_information('new_updated.txt')
    app.run(port=int(sys.argv[1]), debug=True)
