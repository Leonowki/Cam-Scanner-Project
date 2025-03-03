import cv2
from PIL import Image
import os

class PDFManager:
    
    def __init__(self):
        self.captured_images = []
    
    def add_image(self, image):
        
        if image is not None:
            self.captured_images.append(image.copy())
            return True
        return False
    
    def clear_all_images(self):
        
        self.captured_images.clear()
    
    def remove_last_image(self):
        
        if self.captured_images:
            self.captured_images.pop()
            return True
        return False
    
    def get_image_count(self):
        return len(self.captured_images)
    
    def create_pdf(self, filename):
        
        if not self.captured_images:
            return False
        
        try:
            # Convert all images to PIL format
            pil_images = []
            for img in self.captured_images:
                # Convert from BGR to RGB
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_img)
                pil_images.append(pil_img)
            
            # Save the first image as PDF and append the rest
            if pil_images:
                pil_images[0].save(
                    filename, 
                    "PDF", 
                    resolution=100.0, 
                    save_all=True,
                    append_images=pil_images[1:] if len(pil_images) > 1 else []
                )
                
                # Clear captured images after successful PDF creation
                self.captured_images = []
                return True
            
        except Exception as e:
            print(f"Error creating PDF:{e}")
            return False