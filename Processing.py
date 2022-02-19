from TextFilesInstruments import TextFilesFunctional
from Video_nn import use_realsr
import threading

class Processing(TextFilesFunctional):
    def __init__(self):
        super().__init__()
        self.is_processing = False

    def process_picture(self, picture, pictures_path, upd_pictures_path, *args_realsr):
        filenameWOE = picture.filename.split('.')[0]
        picture.save('{}/{}'.format(pictures_path, picture.filename))

        self.processing_thread = threading.Thread(target=use_realsr,
                                                  args=(pictures_path + '/' + picture.filename,
                                                        upd_pictures_path + '/' + filenameWOE + '.png',
                                                        *args_realsr,),
                                                  kwargs={
                                                      'realsr_path': '/home/vladt/PycharmProjects/video_nn/realsr-ncnn-vulkan/realsr-ncnn-vulkan'},
                                                  name='processing')

        self.processing_thread.start()
        return filenameWOE + '.png'

    def after_processing(self, picture_filename):
        while self.processing_thread.is_alive():
            pass
        self.add_information(picture_filename, 'all_updated.txt')
        self.add_information(picture_filename, 'new_updated.txt')
        self.delete_information('order.txt')
        self.is_processing = False