from curses import panel
import os
from os.path import isfile, join
from re import A
from PySide6.QtWidgets import QMainWindow, QFileDialog, QVBoxLayout, QWidget, QLabel
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtCore import Qt
from PIL import Image
import bdjson
import requests


class MainWindowClass(QMainWindow):
    main_window_wide = None
    main_window_tall = None
    task_bar= None
    task_bar_option = None
    image = None
    image_tag= None
    path = None

    #
    def __init__(self, title, monitor_size):
        super().__init__()

        self.path = os.path.expanduser('~')

        #gets the first size of the window
        self.main_window_wide = monitor_size.width()*.6
        self.main_window_tall = monitor_size.height()*.6
        
        #helps center the image
        axis_x = int((monitor_size.width() - self.main_window_wide)/2)
        axis_y = int((monitor_size.height() - self.main_window_tall)/2)

        self.setWindowTitle(title)

        self.setGeometry(
            axis_x, 
            axis_y,
            self.main_window_wide,
            self.main_window_tall
        )

        self.start_menu() #function of this class

        #allows to draw within the canvas
        disposition = QVBoxLayout()
        self.setLayout(disposition)
        panel = QWidget()
        panel.setStyleSheet("background-color: #d1d1d1;")
        self.setCentralWidget(panel)
        disposition_panel = QVBoxLayout()
        disposition_panel.setAlignment(Qt.AlignHCenter)
        panel.setLayout(disposition_panel)
        
        #Qlabel enables to place text in the main windows
        self.image_tag = QLabel()
        disposition_panel.addWidget(self.image_tag)

    #
    def start_menu(self):
        main_menu = self.menuBar()

        main_menu.setStyleSheet(
            """
            background-color: #213341; 
            color:white; 
            padding:10px;
            font-size:20px
            """
        )

        menu_option = main_menu.addMenu('Opciones')
        open_option = QAction("Abrir base de datos", menu_option)
        open_option.triggered.connect(self.image_downloader)
        menu_option.addAction(open_option)

    # enable pop-up window to select a file, do not takes arguments, does not return values
    def open_file(self): #verify file selected
        image_dict = {}
        selected_file = QFileDialog.getOpenFileName(
            self,
            "Select a bdjson file: ",
            self.path,
            "Archivo bdJson (*.bdjson)"
        )
        selected_file = selected_file[0]

        if not selected_file:
            return
        else:
            ## llamar una funcion que devuelva la imagen o la direccion
            obje = bdjson.BdJson(selected_file)
            image_dict = obje.separate_data_elements()
            # print (image_dict[2]['url'] )
            return image_dict
         
    # obtain images and name of it
    def image_downloader(self):
        image_dict = {}
        image_dict = self.open_file()
        url = ''
        for image_url in image_dict:
            try:
                if image_url['url']:
                    url = image_url['url']
                    parms = {
                        "auto": "compress",
                        "cs": "tinysrgb",
                        "w": 1260,
                        "h": 750,
                        "dpr" : 1
                    }
                    answer = requests.get(url, params=parms)
            except KeyError as e:
                image_name= "./images_downloaded/" + image_url['nombre'] + ".jpg"
                with open(image_name, mode="wb") as imagen:
                    imagen.write(answer.content)
                # print("Error:", e.args ) #I have the feeling that this is not the proper way but I will investigate later
                self.open_image()# loads the image but just one
                continue
            except:
                print("Unhandled error at image_downloader object")
            
    #
    def open_image(self):
        images_path = "./images_downloaded"
        image_list = []

        files_within = [img for img in os.listdir(images_path) if isfile(join(images_path, img))]
        for img in files_within:
            img_route= images_path+ "/" + img
            image_list.append(Image.open(img_route))
            image_show = QPixmap(img_route)
            self.image_tag.setPixmap(image_show)
            
        return image_list
        

    # # borrar
    # def refresh_image(self):
    #     #formula para manipular la imagen que se muestro
    #     image= self.open_image()
    #     imagen_mostrar = QPixmap(image= image) #si envio la imagen original puede destrozar la interfaz
    #     self.etiqueta_imagen.setPixmap(imagen_mostrar)

    #
    # def resizeEvent(self, event):
    #     if self.imagen != None: self.refrescar_imagen()

    #
    def image_resize(self, images):
        tall= images.height
        wide= images.width
        a, b,c,d = ((wide/2)*.5, (tall/2)*.5, wide*.5, tall*.5)
        images = images.transform(size=(100,100), method= Image.EXTENT, data=(a,b,c,d))