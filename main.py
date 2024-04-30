import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTextEdit, QFileDialog, QProgressDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import cv2
import os
import numpy as np
import easyocr
from spellchecker import SpellChecker #pip install pyspellchecker

def feature_extraction(image):
    output_paths = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 75, 200)
    
    #horizontal projection
    horizontal_projection = np.sum(edged, axis=1)
    threshold = np.mean(horizontal_projection) * 0.1  
    peaks = np.where(horizontal_projection < threshold)[0]
    min_peak_distance = 20  
    peaks = peaks[np.concatenate(([True], np.diff(peaks) > min_peak_distance))]
    
    #break into each line of text
    for i in range(len(peaks) - 1):
        start_row = peaks[i]
        end_row = peaks[i + 1]
        
        line_image = image[start_row:end_row, :]

        # check edge effect
        segment_edged = cv2.Canny(line_image, 75, 200)
        segment_edge_output_path = f'images/segment_{i}_edge_detected.png'
        cv2.imwrite(segment_edge_output_path, segment_edged)

        output_path = f'images/line_{i}.png'
        cv2.imwrite(output_path, line_image)
        output_paths.append(output_path)
        
    return output_paths

def recognize_text(processed_images):
    reader = easyocr.Reader(['en'], gpu=False)
    all_texts = []
    for image_path in processed_images:
        results = reader.readtext(image_path)
        text = '\n'.join([item[1] for item in results])
        corrected_text = correct_spelling(text)#Correct spelling avoid that to tkat
        all_texts.append(corrected_text)
        
        # Delete comment to see segment
        #os.remove(image_path)
        
    return all_texts
def correct_spelling(text):#Just fixing spelling
    spell = SpellChecker()
    corrected_text = []
    words = text.split()
    for word in words:
        corrected_word = spell.correction(word)
        if corrected_word is None:
            #Words not in library
            corrected_word = word
        corrected_text.append(corrected_word)
    return ' '.join(corrected_text)


class processing(QThread):
    finished = pyqtSignal(list)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def run(self):
        image = cv2.imread(self.image_path)
        if image is not None:
            try:
                processed_images = feature_extraction(image)
                recognized_texts = recognize_text(processed_images)
                self.finished.emit([recognized_texts, processed_images])
            except Exception as e:
                self.finished.emit([f"Error: {str(e)}"])
        else:
            self.finished.emit(["Failed to load the image"])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        self.setWindowTitle("Handwritten Recognition")
        self.setGeometry(100, 100, 600, 400)


        # Button to load image
        self.load_image_button = QPushButton("Load Image")
        self.load_image_button.clicked.connect(self.load_image)


        # Output1 for displaying segmented image
        self.preprocessed_output = QLabel("No Image Loaded")
        self.preprocessed_output.setAlignment(Qt.AlignCenter)


        # Output2 for displaying recognized text
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)


        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.load_image_button)
        main_layout.addWidget(QLabel("segmented Image:"))
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


    def finshed(self, results):
        self.progress_dialog.close()

        if isinstance(results, list):
            error_messages = [r for r in results if isinstance(r, str) and (r.startswith("Error") or r.startswith("Failed"))]
            if error_messages:
                self.preprocessed_output.setText("\n".join(error_messages))
                self.text_output.clear()
            else:
                if len(results) > 0 and isinstance(results[0], list):
                    all_texts = "\n".join(results[0]) if results[0] else "No results"
                    self.text_output.setPlainText(all_texts)
                if len(results) > 1 and isinstance(results[1], list):
                    image_paths = results[1]
                    if image_paths:
                        for image_path in image_paths:
                            pixmap = QPixmap(image_path)
                            self.display_image(pixmap)
        else:
            self.preprocessed_output.setText("Unexpected result format")
            self.text_output.clear()

    def display_image(self, pixmap):
        # Display the image in a QLabel
        self.preprocessed_output.setPixmap(pixmap)
        self.preprocessed_output.setScaledContents(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
