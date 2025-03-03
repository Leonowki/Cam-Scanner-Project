import cv2
import numpy as np

class CameraManager:

    def __init__(self):
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Initialize document detection variables
        self.is_document_detected = False
        self.document_corners = None
        self.current_image = None
    
    def get_frame(self):
        """Capture a frame from the camera"""
        ret, frame = self.cap.read()
        if ret:
            self.current_image = frame.copy()
            return frame
        return None
    
    def process_frame_local(self, frame):
        try:
            # Make a copy of the original frame
            original = frame.copy()
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Apply Gaussian blur with smaller kernel for speed
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)

            # Apply Otsu's thresholding
            _, th2 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours - use CHAIN_APPROX_SIMPLE to reduce points
            contours, _ = cv2.findContours(th2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Reset document detection status
            self.is_document_detected = False
            self.document_corners = None
            
            # Only process if we have contours
            if contours:
                # Find the largest contour first (potential optimization)
                largest_contour = max(contours, key=cv2.contourArea)
                largest_area = cv2.contourArea(largest_contour)
                
                # Only process if the largest contour is big enough
                if largest_area >= 10000:
                    # Approximate the largest contour
                    perimeter = cv2.arcLength(largest_contour, True)
                    approx = cv2.approxPolyDP(largest_contour, 0.05 * perimeter, True)
                    
                    # If it's a quadrilateral, it's likely our document
                    if len(approx) == 4:
                        # Draw the document contour in green
                        # cv2.drawContours(frame, [approx], -1, (0, 255, 0), 2)
                        self.is_document_detected = True
                        self.document_corners = approx
                    else:
                        # If the largest contour isn't a quad, try others in descending order
                        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
                        # Skip the largest one as we already checked it
                        for cnt in sorted_contours[1:]:
                            if cv2.contourArea(cnt) < 10000:
                                break  # Stop early if contours get too small
                            
                            perimeter = cv2.arcLength(cnt, True)
                            approx = cv2.approxPolyDP(cnt, 0.05 * perimeter, True)
                            
                            if len(approx) == 4:
                                # cv2.drawContours(frame, [approx], -1, (0, 255, 0), 2)
                                self.is_document_detected = True
                                self.document_corners = approx
                                break
            
            return frame, original
            
        except Exception as e:
            print(f"Error in processing frame: {e}")
            return frame, frame.copy()
        
    def process_frame(self, frame):
        try:
            # Make a copy of the original frame
            original = frame.copy()
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Apply Gaussian blur with smaller kernel for speed
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)

            # Apply Otsu's thresholding
            _, th2 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours - use CHAIN_APPROX_SIMPLE to reduce points
            contours, _ = cv2.findContours(th2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # Reset document detection status
            self.is_document_detected = False
            self.document_corners = None
            # Only process if we have contours
            if contours:
                # Find the largest contour first (potential optimization)
                largest_contour = max(contours, key=cv2.contourArea)
                largest_area = cv2.contourArea(largest_contour)
                
                # Only process if the largest contour is big enough
                if largest_area >= 10000:
                    # Approximate the largest contour
                    perimeter = cv2.arcLength(largest_contour, True)
                    approx = cv2.approxPolyDP(largest_contour, 0.05 * perimeter, True)
                    
                    # If it's a quadrilateral, it's likely our document
                    if len(approx) == 4:
                        # Draw the document contour in green
                        cv2.drawContours(frame, [approx], -1, (0, 255, 0), 2)
                        self.is_document_detected = True
                        self.document_corners = approx
                    else:
                        # If the largest contour isn't a quad, try others in descending order
                        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
                        # Skip the largest one as we already checked it
                        for cnt in sorted_contours[1:]:
                            if cv2.contourArea(cnt) < 1000:
                                break  # Stop early if contours get too small
                            
                            perimeter = cv2.arcLength(cnt, True)
                            approx = cv2.approxPolyDP(cnt, 0.05 * perimeter, True)
                            
                            # if len(approx) == 4:
                            #     cv2.drawContours(frame, [approx], -1, (0, 255, 0), 2)
                            #     self.is_document_detected = True
                            #     self.document_corners = approx
                            #     break
            
            return frame, original
            
        except Exception as e:
            print(f"Error in processing frame: {e}")
            return frame, frame.copy()
    
    def release(self):
        
        if self.cap.isOpened():
            self.cap.release()