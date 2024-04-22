
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTextEdit, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

import cv2
import threading

def feature_extraction(image):
    # Placeholder for feature extraction
    # Assuming feature extraction returns an image and then generates text
    # For demonstration purposes, just return the input image itself
    feature = "new image"
    return feature

def recognize_text(feature):
    # Placeholder for text recognition
    # Assuming recognize_text takes the image and generates text
    # For demonstration purposes, just return the input image's text
    return "Text recognized from preprocessed image."

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Handwritten Recognition")
        self.setGeometry(100, 100, 600, 400)

        # Button to load image
        self.load_image_button = QPushButton("Load Image")
        self.load_image_button.clicked.connect(self.load_image)

        # Output box for displaying preprocessed image
        self.preprocessed_output = QLabel("No Image Loaded")
        self.preprocessed_output.setAlignment(Qt.AlignCenter)

        # Output box for displaying recognized text
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.load_image_button)
        main_layout.addWidget(QLabel("Preprocessed Image:"))
        main_layout.addWidget(self.preprocessed_output)
        main_layout.addWidget(QLabel("Recognized Text:"))
        main_layout.addWidget(self.text_output)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def load_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.bmp)")
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                image_path = selected_files[0]
                image = cv2.imread(image_path)#####################################################part1###############
                if image is not None:
                    # Perform feature extraction
                    preprocessed_image= feature_extraction(image)

                    # Display the preprocessed image
                    pixmap = QPixmap()
                    pixmap.loadFromData(preprocessed_image)
                    self.display_image(pixmap)###################part 2#############################################

                    # Recognize text from preprocessed image
                    recognized_text = recognize_text(preprocessed_image)

                    # Display the recognized text
                    self.text_output.setPlainText(recognized_text)###################part 3#############################################
                else:
                    self.preprocessed_output.setText("Failed to load the image")

    def display_image(self, pixmap):
        # Display the image in a QLabel
        self.preprocessed_output.setPixmap(pixmap)
        self.preprocessed_output.setScaledContents(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
