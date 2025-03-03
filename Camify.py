
import customtkinter as ctk
from CameraManager import CameraManager
from DocumentProcessor import DocumentProcessor
from PDFManager import PDFManager
from DocumentScannerUI import DocumentScannerUI

class Camify:
    
    def __init__(self):
        
        self.root = ctk.CTk()
        
        
        self.camera_manager = CameraManager()
        self.document_processor = DocumentProcessor()
        self.pdf_manager = PDFManager()
        
        
        self.ui = DocumentScannerUI(self.root, self.camera_manager, self.document_processor,self.pdf_manager)
    
    def run(self):
        self.root.mainloop()


def main():
    app = Camify()
    app.run()


if __name__ == "__main__":
    main()
