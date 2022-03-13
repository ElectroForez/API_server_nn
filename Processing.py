import time

from TextFilesInstruments import TextFilesFunctional
from Video_nn import use_realsr
import threading
from config_nn import REALSR_PATH


class Processing(TextFilesFunctional):
    def process_picture(self, pictures_path, upd_pictures_path, *args_realsr):
        self.processing_thread = threading.Thread(target=use_realsr,
                                                  args=(pictures_path,
                                                        upd_pictures_path,
                                                        *args_realsr,),
                                                  kwargs={
                                                      'realsr_path': REALSR_PATH},
                                                  name='processing')
        self.processing_thread.start()
        time.sleep(0.3)
        if not self.processing_thread.is_alive():  # if the thread dies quickly, then an error has occurred
            return -1
        return 0

    def after_processing(self, picture_filename):
        while self.processing_thread.is_alive():
            pass
        self.add_information(picture_filename, 'all_updated.txt')
        self.add_information(picture_filename, 'new_updated.txt')
        self.delete_information('order.txt')
