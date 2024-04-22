import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTextEdit, QFileDialog, QProgressDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import cv2
import time
def feature_extraction(image):
    # Placeholder for feature extraction
    time.sleep(2) #2 second
    feature = "new image"
    return feature

def recognize_text(feature):
    time.sleep(2)#2 second
    # Placeholder for text recognition
    return "Recognized text from feature."

class processing(QThread):
    finished = pyqtSignal(str)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def run(self):
        image = cv2.imread(self.image_path)#####################################################part1###############
        if image is not None:
            feature = feature_extraction(image)     ###################part 2#############################################
            recognized_text = recognize_text(feature)###################part 3#############################################
            self.finished.emit(recognized_text)
        else:
            self.finished.emit("Failed to load the image")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Handwritten Recognition")
        self.setGeometry(100, 100, 600, 400)

        # Button to load image
        self.load_image_button = QPushButton("Load Image")
        self.load_image_button.clicked.connect(self.load_image)

        # Output1 for displaying preprocessed image
        self.preprocessed_output = QLabel("No Image Loaded")
        self.preprocessed_output.setAlignment(Qt.AlignCenter)

        # Output2 for displaying recognized text
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

                # Start a thread for image processing
                self.thread = processing(image_path)
                self.thread.finished.connect(self.finshed)
                self.thread.start()

                # Show progress dialog
                self.progress_dialog = QProgressDialog("Processing Image...", None, 0, 0, self)
                self.progress_dialog.setWindowModality(Qt.WindowModal)
                self.progress_dialog.show()

    def finshed(self, result):
        self.progress_dialog.close()

        if result.startswith("Failed"):
            self.preprocessed_output.setText(result)
            self.text_output.clear()
        else:
            self.text_output.setPlainText(result)

    def display_image(self, pixmap):
        # Display the image in a QLabel
        self.preprocessed_output.setPixmap(pixmap)
        self.preprocessed_output.setScaledContents(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
