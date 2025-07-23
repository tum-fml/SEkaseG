import pytesseract
from PIL import Image
import cv2
import numpy as np
from tkinter import filedialog
from tkinter import *
import fitz
import csv

class ExtractInfo:
    # adjust the location of installed tool tesseract.exe
    pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    def __init__(self, filename):
        self.results = None
        # Open the file dialog
        self.filename = filename

        self.file_type = self.filename.split('.')[-1]

        if self.file_type == 'png' or self.file_type == 'jpg':
            self.extract_image()

        elif self.file_type == 'pdf':
            self.extract_pdf()

        elif self.file_type == 'csv':
            self.extract_csv()
        
        with open('extract_info.txt', 'w') as f:
            f.write(self.results)


    def extract_image(self):
        # Read image with opencv
        img = cv2.imread(self.filename)

        # convert to gray
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply dilation and erosion to remove some noise
        kernel = np.ones((1,1), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)

        # Apply threshold to get image with only black and white
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

        self.results = pytesseract.image_to_string(img)
        
    def extract_pdf(self):
        '''
        with open(self.filename, 'rb') as pdf_file:
            # Create a PdfFileReader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Get the number of pages in the PDF file
            num_pages = pdf_reader.pages
            print(num_pages)

            # Loop through all the pages in the PDF file
            for page_num in range(num_pages):
                # Get the page object for the current page
                page_obj = pdf_reader.getPage(page_num)

                # Extract the text content of the page
                self.results.append(page_obj.extractText())
        '''
        
        with fitz.open(self.filename) as pdf:
            num_pages = pdf.page_count
            for i in range(num_pages):
                page = pdf.load_page(i)
                text = page.get_text()


    def extract_csv(self):
        self.results = []
        # Open the CSV file
        with open(self.filename, 'r') as file:
            # Create a CSV reader object
            csv_reader = csv.reader(file)

            # Iterate over each row in the CSV file
            for row in csv_reader:
                # Extract information from the row
                self.results.append(row)  
        self.results = str(self.results)

if __name__ == "__main__":
    filename = filedialog.askopenfilename()
    ExtractInfo(filename)

    