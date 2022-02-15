from flask import Flask, request, send_file
from flask_restful import Api, Resource, reqparse
import werkzeug
import os
import time
import threading

from TextFilesInstruments import TextFilesFunctional
from Processing import Processing
app = Flask(__name__)
api = Api(app)


parser = reqparse.RequestParser()
parser.add_argument('picture', type=werkzeug.datastructures.FileStorage, location='files')


class Content(Resource, Processing):
    def __init__(self):
        self.is_processing = False
        self.information_path = 'information/'
        self.content_path = 'content/'
        self.check_info()

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
        cur_picture_path = pictures_folder + '/' + picture.filename
        if picture:
            if self.is_path_in_infoFile(cur_picture_path, 'order.txt'):
                return {'status': 'You already send this picture to order'}

            if not self.is_processing:
                self.add_information(cur_picture_path, 'order.txt')
                future_filename = 'Updated_' + pictures_folder + '/' \
                                  + self.process_picture(picture, pictures_path, upd_pictures_path, *args_realsr)

                self.after_processing_thread = threading.Thread(target=self.after_processing,
                                                                args=(future_filename,),
                                                                name='after_proccessing')
                self.after_processing_thread.start()
                self.is_processing = True
            else:
                return {'status': 'Wait some times. Computer is busy now by other picture'}
            return {"status": "Picture was uploaded", 'futureName': future_filename}
        else:
            return {"status": "No picture in request"}


    def get(self, pictures_folder, picture):
        path_to_file = self.content_path + pictures_folder + '/' + picture
        if os.path.exists(path_to_file):
            return send_file(path_to_file)
        else:
            return {'status': 'file is not exists'}
    # def delete(self, pictures_folder):

api.add_resource(Content, '/content/<string:pictures_folder>', '/content/<string:pictures_folder>/<string:picture>')
if __name__ == "__main__":
    app.run(debug=True)