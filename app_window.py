import os
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from img_manipulator import ImgManipulator
from interface import Ui_MainWindow
from PyQt5.QtGui import QPixmap, QImage, QResizeEvent

import shutil
from datetime import datetime

from skimage.io import imread, imsave

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from multipledispatch import dispatch
from skimage import img_as_ubyte, color, data


class AppWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super(AppWindow, self).__init__()
        self.original_img = None
        self.edited_img = None
        self.ui_setup()

    def ui_setup(self) -> None:
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.bind_menubar()
        self.bind_buttons()

        self.show()

    def bind_menubar(self) -> None:
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionSave.triggered.connect(self.save_file)
        self.ui.actionQuit.triggered.connect(self.close)

        self.ui.actionAstronaut.triggered.connect(
            lambda: self.set_image(data.astronaut()))
        self.ui.actionBrick.triggered.connect(
            lambda: self.set_image(color.gray2rgb(data.brick())))
        self.ui.actionCat.triggered.connect(
            lambda: self.set_image(data.cat()))
        self.ui.actionCoins.triggered.connect(
            lambda: self.set_image(color.gray2rgb(data.coins())))

        self.ui.actionBlur_Image.triggered.connect(self.blur_image)

        self.ui.actionGaussian.triggered.connect(
            lambda: self.add_noise(mode="gaussian"))
        self.ui.actionLocalvar.triggered.connect(
            lambda: self.add_noise(mode="localvar"))
        self.ui.actionPoisson.triggered.connect(
            lambda: self.add_noise(mode="poisson"))
        self.ui.actionSalt.triggered.connect(
            lambda: self.add_noise(mode="salt"))
        self.ui.actionPepper.triggered.connect(
            lambda: self.add_noise(mode="pepper"))
        self.ui.actionS_P.triggered.connect(
            lambda: self.add_noise(mode="s&p"))
        self.ui.actionSpeckle.triggered.connect(
            lambda: self.add_noise(mode="speckle"))

        self.ui.actionAbout_creator.triggered.connect(self.info_creator)
        self.ui.actionAbout_program.triggered.connect(self.info_program)

    def bind_buttons(self) -> None:
        self.ui.id_button.clicked.connect(self.deconv)
        self.ui.nc_button.clicked.connect(self.noise_canceling)
        self.ui.us_button.clicked.connect(self.upscale)

    def deconv(self) -> None:
        try:
            if type(self.edited_img) == str:
                self.edited_img = imread(self.edited_img)
                if len(self.edited_img.shape) == 2:
                    self.edited_img = color.gray2rgb(self.edited_img)
            self.edited_img = color.gray2rgb(ImgManipulator.deconv(
                color.rgb2gray(self.edited_img), self.get_deconv_mode()))
            self.update_image()
            QMessageBox.about(self, "Ok", "Done")
        except:
            QMessageBox.warning(self, "Error", "No File")

    def noise_canceling(self) -> None:
        try:
            if type(self.edited_img) == str:
                self.edited_img = imread(self.edited_img)
                if len(self.edited_img.shape) == 2:
                    self.edited_img = color.gray2rgb(self.edited_img)
            self.edited_img = color.gray2rgb(ImgManipulator.noise_canceling(
                color.rgb2gray(self.edited_img), *self.get_nc_mode()))
            self.update_image()
            QMessageBox.about(self, "Ok", "Done")
        except:
            QMessageBox.warning(self, "Error", "No File")

    def upscale(self) -> None:
        try:
            if type(self.edited_img) == str:
                self.edited_img = imread(self.edited_img)
                if len(self.edited_img.shape) == 2:
                    self.edited_img = color.gray2rgb(self.edited_img)
            self.edited_img = ImgManipulator.upscale(
                self.edited_img, *self.get_upscale_info())
            self.update_image()
            QMessageBox.about(self, "Ok", "Done")
        except:
            QMessageBox.warning(self, "Error", "No File")

    def get_nc_mode(self) -> tuple[str, str, int]:
        fp_text = self.ui.nc_footprint_cb.currentText().split(" ")
        return self.ui.nc_method_cb.currentText(), fp_text[0], int(fp_text[1])

    def get_upscale_info(self) -> tuple[str, str, int]:
        text = self.ui.us_method_cb.currentText()
        return text, text.split("_")[0].lower(), int(text[-1])

    def get_deconv_mode(self) -> str:
        return self.ui.id_method_cb.currentText()

    def add_noise(self, mode: str) -> None:
        try:
            if type(self.edited_img) == str:
                self.edited_img = imread(self.edited_img)
                if len(self.edited_img.shape) == 2:
                    self.edited_img = color.gray2rgb(self.edited_img)
            self.edited_img = ImgManipulator.add_noise(self.edited_img, mode)
            self.update_image()
            QMessageBox.about(self, "Ok", "Done")
        except:
            QMessageBox.warning(self, "Error", "No File")

    def img2file(self, img, time: str,  filename: str) -> None:
        path = "{}".format(os.getcwd()) + "\\files\\" + time
        if not os.path.exists(path):
            os.makedirs(path)
        if type(img) == str:
            shutil.copy(img, path + filename)
        else:
            imsave(path+filename, img)

    def save_file(self) -> None:
        try:
            curr_time = str(datetime.utcnow())
            for char in " -.:":
                curr_time = curr_time.replace(char, "")
            self.img2file(self.original_img, curr_time, "\\original.jpg")
            self.img2file(self.edited_img, curr_time,  "\\edited.jpg")
        except:
            QMessageBox.warning(self, "Error", "No File")

    def blur_image(self) -> None:
        try:
            if type(self.edited_img) == str:
                self.edited_img = imread(self.edited_img)
                if len(self.edited_img.shape) == 2:
                    self.edited_img = color.gray2rgb(self.edited_img)
            self.edited_img = ImgManipulator.blur_image(self.edited_img)
            self.update_image()
            QMessageBox.about(self, "Ok", "Done")
        except:
            QMessageBox.warning(self, "Error", "No File")

    def open_file(self) -> None:
        try:
            filename = QFileDialog.getOpenFileName(self, 'Open file',
                                                   'C:\\', "Image files (*.jpg *.png)")[0]
            img = imread(filename)
            self.set_image(filename)
        except:
            self.original_img = None
            self.edited_img = None
            self.clear_image()
            QMessageBox.warning(self, "Error", "Incorrect File")

    def info_creator(self) -> None:
        title = "About creator"
        msg = '''The programm was created by Leonov Vladislav

vk.com/leerycorsair
t.me/leerycorsair
        '''
        QMessageBox.about(self, title, msg)

    def info_program(self) -> None:
        title = "About program"
        msg = '''Version:1.0.0
PyQt:5.15.7
Scikit-image:0.19.3
NumPy:1.22.3

(c) BMSTU License v1.1
        '''
        QMessageBox.about(self, title, msg)

    def set_image(self, img) -> None:
        self.original_img = img
        self.edited_img = img
        self.img2label(self.ui.original_img_label, self.original_img)
        self.img2label(self.ui.preview_img_label, self.edited_img)

    def update_image(self) -> None:
        if self.original_img is not None:
            self.img2label(self.ui.original_img_label, self.original_img)
            self.img2label(self.ui.preview_img_label, self.edited_img)

    def clear_image(self) -> None:
        self.ui.original_img_label.clear()
        self.ui.preview_img_label.clear()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.update_image()
        return super().resizeEvent(event)

    @dispatch(QtWidgets.QLabel, str)
    def img2label(self, label: QtWidgets.QLabel, img: str) -> None:
        h = label.height()
        w = label.width()
        label.setPixmap(QPixmap(img).scaled(
            w, h, aspectRatioMode=Qt.KeepAspectRatio))

    @dispatch(QtWidgets.QLabel, object)
    def img2label(self, label: QtWidgets.QLabel, img: object) -> None:
        h = label.height()
        w = label.width()
        img = img_as_ubyte(img)
        img = QImage(img.data, img.shape[1], img.shape[0],
                     img.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        label.setPixmap(pixmap.scaled(
            w, h, aspectRatioMode=Qt.KeepAspectRatio))
