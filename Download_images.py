import os
from hashlib import md5


class Download:
    def __init__(self, keyword):
        self.path = os.path.join(os.path.dirname(__file__), keyword)
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def download_images(self, image_title, content):
        file_path = os.path.join(self.path, image_title)
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        images_path = os.path.join(file_path, md5(content).hexdigest()+'.jpg')
        if not os.path.exists(images_path):
            with open(images_path, 'wb') as f:
                f.write(content)
                f.close()