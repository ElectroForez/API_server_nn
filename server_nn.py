from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import werkzeug
from Video_nn import Video_nn
import os
import time
import threading

app = Flask(__name__)
api = Api(app)


parser = reqparse.RequestParser()
parser.add_argument('picture', type=werkzeug.datastructures.FileStorage, location='files')


def checkInfo(pathToInfo):
    if not os.path.isdir(pathToInfo):
        os.mkdir(pathToInfo)
    infoFiles = ['info.txt']
    for file in infoFiles:
        if not os.path.exists(pathToInfo + file):
            open(file, 'w')

class HellowWOrld(Resource):
    def __init__(self):
        self.isBusyProceccing = False
        self.informationPath = 'information/'
        checkInfo(self.informationPath)

    def post(self, picturesFolderName):
        contentPath = 'content/'
        pathToPictures = contentPath + picturesFolderName
        pathToUpdatedPictures = contentPath + 'Updated_' + picturesFolderName
        if not os.path.exists(pathToPictures):
            os.mkdir(pathToPictures)
        if not os.path.exists(pathToUpdatedPictures):
            os.mkdir(pathToUpdatedPictures)
        args = parser.parse_args()
        picture = args['picture']
        argsRealsr = []

        if picture:
            if not self.isBusyProceccing:
                self.process_picture(picture, pathToPictures, pathToUpdatedPictures, *argsRealsr)
            else:
                return {'status': 'Wait some times. Computer is busy now by other picture'}
            return {"status": "Picture was uploaded"}
        else:
            return {"status": "No picture in request"}

    def process_picture(self, picture, pathToPictures, pathToUpdatedPictures, *argsRealsr):
        self.addToOrder(picture)
        filenameWOExtension = picture.filename.split('.')[0]
        picture.save('{}/{}'.format(pathToPictures, picture.filename))

        thread = threading.Thread(target=Video_nn.useRealsr, args=(Video_nn, pathToPictures + '/' + picture.filename,
                                                                   pathToUpdatedPictures + '/' + filenameWOExtension + '.png',
                                                                   *argsRealsr,),
                                  kwargs={
                                      'pathToRealsr': '/home/vladt/PycharmProjects/video_nn/realsr-ncnn-vulkan/realsr-ncnn-vulkan'})
        thread.start()


    def addToOrder(self, pictureName, first=True):
        checkInfo(self.informationPath)
        infoFilePath = self.informationPath + 'info.txt'
        with open(infoFilePath, 'r+') as file:
            text = file.readlines()
            if first:
                text = [pictureName + '\n'] + text
            else:
                if (text[-1] == '\n') or (not text):
                    del text[-1]
                text += [pictureName]
            file.seek(0)
            for row in text:
                file.write(row)

    def deleteFromOrder(self):
        checkInfo(self.informationPath)
        infoFilePath = self.informationPath + 'info.txt'
        with open(infoFilePath, 'r+') as file:
            text = file.readlines()
            text = text[1:]
            file.seek(0)
            for row in text:
                file.write(row)
    # def delete(self, picturesFolderName):

api.add_resource(HellowWOrld, '/<string:picturesFolderName>')

if __name__ == "__main__":
    app.run(debug=True)