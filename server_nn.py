from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import werkzeug
from Video_nn import VideoNN
import os
import time
import threading

app = Flask(__name__)
api = Api(app)


parser = reqparse.RequestParser()
parser.add_argument('picture', type=werkzeug.datastructures.FileStorage, location='files')


def check_info(info_path):
    if not os.path.isdir(info_path):
        os.mkdir(info_path)
    info_files = ['all_updated.txt', 'new_updated.txt', 'order.txt']
    for file in info_files:
        if not os.path.exists(info_path + file):
            open(file, 'w')

class HellowWOrld(Resource):
    def __init__(self):
        self.is_proceccing = False
        self.information_path = 'information/'
        self.content_path = 'content/'
        check_info(self.information_path)

    def post(self, pictures_folder):
        pictures_path = self.content_path + pictures_folder
        upd_pictures_path = self.content_path + 'Updated_' + pictures_folder
        if not os.path.exists(pictures_path):
            os.mkdir(pictures_path)
        if not os.path.exists(upd_pictures_path):
            os.mkdir(upd_pictures_path)

        args = parser.parse_args()
        picture = args['picture']
        args_realsr = ''.split()

        if picture:
            if not self.is_proceccing:
                future_filename = 'Updated_' + pictures_folder + '/' \
                                  + self.process_picture(picture, pictures_path, upd_pictures_path, *args_realsr)

                self.after_processing_thread = threading.Thread(target=self.after_processing,
                                                                args=(self, future_filename,),
                                                                name='after_proccessing')
                self.after_processing_thread.start()
            else:
                return {'status': 'Wait some times. Computer is busy now by other picture'}

            return {"status": "Picture was uploaded", 'futureName': future_filename}
        else:
            return {"status": "No picture in request"}

    def process_picture(self, picture, pictures_path, upd_pictures_path, *args_realsr):
        self.add_information(pictures_path + picture.filename)
        filenameWOE = picture.filename.split('.')[0]
        picture.save('{}/{}'.format(pictures_path, picture.filename))

        self.processing_thread = threading.Thread(target=VideoNN.use_realsr,
                                                  args=(VideoNN, pictures_path + '/' + picture.filename,
                                                           upd_pictures_path + '/' + filenameWOE + '.png',
                                                           *args_realsr,),
                                  kwargs= {
                                      'pathToRealsr': '/home/vladt/PycharmProjects/VideoNN/realsr-ncnn-vulkan/realsr-ncnn-vulkan'},
                                             name='processing')

        self.processing_thread.start()
        return filenameWOE + '.png'

    def after_processing(self, picture_filename):
        while not self.processing_thread.is_alive():
            self.add_information(picture_filename, 'all_updated.txt')
            self.add_information(picture_filename, 'new_updated.txt')
            self.delete_information('order.txt')

    def add_information(self, picture_filename, infofile, first=True):
        check_info(self.information_path)
        file_path = self.information_path + infofile
        with open(file_path, 'r+') as file:
            text = file.readlines()
            if first:
                text = [picture_filename + '\n'] + text
            else:
                if (text[-1] == '\n') or (not text):
                    del text[-1]
                text += [picture_filename]
            file.seek(0)
            for row in text:
                file.write(row)

    def delete_information(self, infofile):
        check_info(self.information_path)
        file_path = self.information_path + infofile
        with open(file_path, 'r+') as file:
            text = file.readlines()
            text = text[1:]
            file.seek(0)
            for row in text:
                file.write(row)
    # def delete(self, pictures_folder):

api.add_resource(HellowWOrld, '/content/<string:pictures_folder>')

if __name__ == "__main__":
    app.run(debug=True)