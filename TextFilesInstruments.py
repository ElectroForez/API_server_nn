import os
from config_nn import INFORMATION_PATH


class TextFilesFunctional:
    """class for work with text infofiles(files with information about processing)"""

    def __init__(self):
        self.information_path = INFORMATION_PATH
        self.check_infoFiles()

    def check_infoFiles(self):
        if not os.path.isdir(self.information_path):
            os.mkdir(self.information_path)
        info_files = ['all_updated.txt', 'new_updated.txt', 'order.txt']
        for file in info_files:
            if not os.path.exists(self.information_path + file):
                open(self.information_path + file, 'w')

    def add_information(self, picture_filename, infoFile, first=True):
        self.check_infoFiles()
        file_path = self.information_path + infoFile
        picture_filename += '\n'
        with open(file_path, 'r+') as file:
            text = file.readlines()
            if first:
                text = [picture_filename] + text
            else:
                text += [picture_filename]
            file.seek(0)
            for row in text:
                file.write(row)

    def delete_information(self, infoFile):
        self.check_infoFiles()
        file_path = self.information_path + infoFile
        with open(file_path, 'r+') as file:
            text = file.readlines()
            text = text[1:]
            file.seek(0)
            file.truncate(0)
            for row in text:
                file.write(row)

    def clear_infoFile(self, infoFile):
        self.check_infoFiles()
        file_path = self.information_path + infoFile
        open(file_path, 'w')

    def is_path_in_infoFile(self, path, infoFile):
        infoFile = self.information_path + infoFile
        with open(infoFile) as file:
            text = file.readlines()
            if path + '\n' in text:
                return True
            else:
                return False

    def read_infoFile(self, infoFile):
        infoFile = self.information_path + infoFile
        if not os.path.exists(infoFile):
            return None
        with open(infoFile, 'r') as file:
            text = []
            for line in file:
                if line:
                    text += [line.strip()]
        return text

    def is_busy(self):
        if not self.read_infoFile('order.txt') in ([], ['']):
            return True
        else:
            return False
