import cv2
import numpy as np

class DocumentProcessor:
    
    def __init__(self):
        self.processed_image = None
        
        
    def enhanced_scanned_look(self, image):
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Remove noise using a lighter Gaussian blur
        blurred = cv2.GaussianBlur(gray, (1, 1), 0)
        
        # Use just adaptive thresholding for better detail preservation
        # Increase blockSize and reduce C for more balanced thresholding
        adaptive = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 15, 5
        )
        
        # Apply minimal cleaning - smaller kernel and less aggressive
        kernel = np.ones((1, 1), np.uint8)
        
        
        # Improve contrast with moderation
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(blurred)  # Apply to blurred image instead of cleaned
        
        sharpened = cv2.addWeighted(enhanced, 1.1, cv2.GaussianBlur(enhanced, (0, 0), 2), -0.1, 0)
        
        # Decide whether to return grayscale or color based on document type
        b, g, r = cv2.split(image)
        diff_bg = cv2.absdiff(b, g)
        diff_br = cv2.absdiff(b, r)
        diff_gr = cv2.absdiff(g, r)
        avg_diff = (np.mean(diff_bg) + np.mean(diff_br) + np.mean(diff_gr)) / 3
        
        if avg_diff < 10:  # Mostly B&W document
        # Check if it's truly B&W or has subtle colors we should enhance
            if avg_diff < 3:
                return sharpened
            else:
                # It has some color - let's enhance it slightly
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                hsv[:,:,1] = np.clip(hsv[:,:,1] * 1.2, 0, 255).astype(np.uint8)  # Boost saturation
                hsv[:,:,2] = sharpened  # Use sharpened grayscale for value channel
                return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        else:
            # For color documents, enhance colors
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Increase saturation to make colors more vibrant (boost by 10%)
            hsv[:,:,1] = np.clip(hsv[:,:,1] * 1.1, 0, 255).astype(np.uint8)
            
            # Use the sharpened grayscale to enhance details in the value channel
            # But blend it with original value to preserve color brightness relationships
            original_v = hsv[:,:,2]
            blended_v = cv2.addWeighted(original_v, 0.4, sharpened, 0.6, 0)
            hsv[:,:,2] = blended_v
            
            # Convert back to BGR
            color_enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
            # Final color boost - slightly increase color contrast
            lab = cv2.cvtColor(color_enhanced, cv2.COLOR_BGR2Lab)
            l, a, b = cv2.split(lab)
            
            # Enhance a and b channels (color channels in Lab color space)
            a = cv2.addWeighted(a, 1.05, a, 0, 0)
            b = cv2.addWeighted(b, 1.05, b, 0, 0)
            
            # Merge channels
            enhanced_lab = cv2.merge([l, a, b])
            enhanced_color = cv2.cvtColor(enhanced_lab, cv2.COLOR_Lab2BGR)
            
            return enhanced_color
        
    def process_document(self, image, corners):
        
        try:
            # Get perspective transform
            image = self.enhanced_scanned_look(image)
            input_pts = np.float32(corners.reshape(4, 2))
            
            # Sort corners: top-left, bottom-left, bottom-right, top-right
            rect = np.zeros((4, 2), dtype="float32")
            # Sum of coordinates - smallest is top-left, largest is bottom-right
            s = input_pts.sum(axis=1)
            rect[0] = input_pts[np.argmin(s)]  # Top-left
            rect[2] = input_pts[np.argmax(s)]  # Bottom-right
            
            # Difference of coordinates - smallest is top-right, largest is bottom-left
            diff = np.diff(input_pts, axis=1)
            rect[1] = input_pts[np.argmax(diff)]  # Bottom-left
            rect[3] = input_pts[np.argmin(diff)]  # Top-right
            
            width, height = 800, 800
            output_pts = np.float32([[0, 0],
                                    [0, height],
                                    [width, height], 
                                    [width, 0]])
            
            # Get transformation matrix
            M = cv2.getPerspectiveTransform(rect, output_pts)
            # Apply transformation
            warped = cv2.warpPerspective(image, M, (width, height))
            
            # Store the processed image
            self.processed_image = warped
            
            return warped
        except Exception as e:
            print(f"Error processing document: {e}")
            return None
    
    