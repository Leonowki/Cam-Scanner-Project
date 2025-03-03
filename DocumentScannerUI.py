import cv2
import customtkinter as ctk
from tkinter import filedialog
import PIL.Image, PIL.ImageTk
import os

class DocumentScannerUI:
    
    def __init__(self,window,camera_manager,document_processor,pdf_manager):
        self.window = window
        self.window.title("Camify")
        self.window.geometry("1200x800")
        
        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Connect managers
        self.camera_manager = camera_manager
        self.document_processor = document_processor
        self.pdf_manager = pdf_manager
        
        # Create UI components
        self.setup_ui()
        
        # Start video loop
        self.delay = 15
        self.update_video()
        
        # Set up closing behavior
        self.window.protocol("WM_DELETE_WINDOW",self.on_closing)
    
    def setup_ui(self):
        #icon
        self.window.iconbitmap("camify.ico")
        
        #Header
        header_label = ctk.CTkLabel(self.window, text="CAMIFY",font=("Poppins", 20,"bold"))
        header_label.pack(pady=15)
        #Main frame
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both",expand=True,padx=10, pady=10)
        
        #Camera frame
        self.camera_frame = ctk.CTkFrame(self.main_frame)
        self.camera_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.camera_frame.grid_rowconfigure(1, weight=1)
        self.camera_frame.grid_columnconfigure(0, weight=1)
        
        # Camera frame title
        self.camera_title = ctk.CTkLabel(self.camera_frame, text="Camera Feed", font=("Poppins", 14, "bold"))
        self.camera_title.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Camera canvas - using standard tk.Canvas as CustomTkinter doesn't have canvas
        # Using grid instead of pack to fill all available space
        self.canvas = ctk.CTkCanvas(self.camera_frame, highlightthickness=0,bg="#1A1A1A")
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # Preview frame
        self.preview_frame = ctk.CTkFrame(self.main_frame)
        self.preview_frame.grid(row=0, column=1, padx=12, pady=12, sticky="nsew")
        self.preview_frame.grid_rowconfigure(1, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        
        # Preview frame title
        self.preview_title = ctk.CTkLabel(self.preview_frame, text="Document Preview", font=("Poppins", 14, "bold"))
        self.preview_title.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Preview canvas - also using grid for dynamic sizing
        self.preview_canvas = ctk.CTkCanvas(self.preview_frame,highlightthickness=0,bg="white")
        self.preview_canvas.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # Control frame
        self.control_frame = ctk.CTkFrame(self.main_frame)
        self.control_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Buttons
        self.btn_capture = ctk.CTkButton(self.control_frame, text="Capture", command=self.capture_image,fg_color="#2CC985",hover_color="#229660")
        self.btn_capture.pack(side="left", padx=5, pady=5)
        
        self.btn_clear_list = ctk.CTkButton(self.control_frame, text="Clear PDF", command=self.clear_images)
        self.btn_clear_list.pack(side="left",padx=7,pady=7)
        
        self.btn_clear_top = ctk.CTkButton(self.control_frame, text="Remove Latest Page", command=self.remove_top)
        self.btn_clear_top.pack(side="left",padx=9,pady=9)
        
        self.btn_add_to_pdf = ctk.CTkButton(self.control_frame, text="Add to PDF", command=self.add_to_pdf, state="disabled")
        self.btn_add_to_pdf.pack(side="left", padx=5, pady=5)
        
        self.btn_create_pdf = ctk.CTkButton(self.control_frame, text="Create PDF", command=self.create_pdf)
        self.btn_create_pdf.pack(side="left", padx=5, pady=5)
        
        self.btn_add_from_files = ctk.CTkButton(self.control_frame,text="Add From Files",command=self.add_from_local)
        self.btn_add_from_files.pack(side="left", padx=11, pady=11)
        #____________________________________________________________________________________________________________________
        # Status label
        self.status_var = ctk.StringVar(value="Ready. Point camera at a document.")
        self.status_label = ctk.CTkLabel(self.control_frame,textvariable=self.status_var,text_color="#FFFFFF")
        self.status_label.pack(side="right", padx=5, pady=5)
        
        # Document indicator
        self.document_indicator_var = ctk.StringVar(value="No document detected")
        self.document_indicator = ctk.CTkLabel(self.control_frame, textvariable=self.document_indicator_var, text_color="#FF5555")
        self.document_indicator.pack(side="right", padx=5, pady=5)
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
    
    def update_video(self):
        
        frame = self.camera_manager.get_frame()
        
        if frame is not None:
            # Process the frame to detect documents
            processed_frame, original_frame = self.camera_manager.process_frame(frame)
            
            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Skip first few frames until canvas is properly sized
            if canvas_width > 1 and canvas_height > 1:
                # Resize the frame to fit the canvas while maintaining aspect ratio
                img_height, img_width = processed_frame.shape[:2]
                scale = min(canvas_width/img_width, canvas_height/img_height)
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                resized_frame = cv2.resize(processed_frame, (new_width, new_height))
                
                # Convert to RGB for tkinter
                self.photo = PIL.ImageTk.PhotoImage(
                    image=PIL.Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB))
                )
                
                # Center the image in canvas
                x_offset = (canvas_width - new_width) // 2
                y_offset = (canvas_height - new_height) // 2
                
                # Clear canvas and add new image
                self.canvas.delete("all")
                self.canvas.create_image(x_offset, y_offset, image=self.photo, anchor="nw")
            
            # Update document detection indicator
            if self.camera_manager.is_document_detected:
                self.document_indicator_var.set("Document detected")
                self.document_indicator.configure(text_color="#55FF55")
            else:
                self.document_indicator_var.set("No document detected")
                self.document_indicator.configure(text_color="#FF5555")
        
        self.window.after(self.delay, self.update_video)
    
    def capture_image(self):
        
        if self.camera_manager.current_image is not None:
            try:
                self.status_var.set("Processing image...")
                
                # Get the current image regardless of document detection
                captured_image = self.camera_manager.current_image.copy()
                
                # If document is detected, try to process it, but don't require success
                if self.camera_manager.is_document_detected and self.camera_manager.document_corners is not None:
                    try:
                        # Try to process document
                        warped = self.document_processor.process_document(
                            self.camera_manager.current_image,
                            self.camera_manager.document_corners
                        )
                        
                        # If successfully warped, use that
                        if warped is not None:
                            captured_image = warped
                            self.status_var.set("Document captured and processed successfully.")
                        else:
                            # Use original image if warping failed
                            self.status_var.set("Document detected but couldn't be processed. Using original image.")
                    except Exception as e:
                        # Use original image if processing raised an exception
                        self.status_var.set(f"Document processing error:{e}. Using original image.")
                else:
                    # No document detected, just use the original image
                    self.status_var.set("No document detected. Using captured image as-is.")
                    
                # Display the image (either warped or original)
                self.display_preview(captured_image)
                
                # Enable the add to PDF button
                self.btn_add_to_pdf.configure(state="normal")
                
            except Exception as e:
                self.status_var.set(f"Error capturing image:{e}")
    
    def display_preview(self, image):
        
        # Get canvas dimensions
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        # Skip if canvas is not properly sized yet
        if canvas_width <= 1 or canvas_height <= 1:
            # Use default sizes as fallback
            canvas_width = 480
            canvas_height = 678
            
        # Get image dimensions
        h, w = image.shape[:2]
        
        # Calculate A4 aspect ratio (1:√2)
        a4_ratio = 1 / 1.414
        
        # Determine if we should constrain by width or height
        if canvas_width / canvas_height < w / h:
            # Constrain by width
            new_w = canvas_width
            new_h = int(new_w * h / w)
        else:
            # Constrain by height
            new_h = canvas_height
            new_w = int(new_h * w / h)
            
        # Resize image
        resized_img = cv2.resize(image, (new_w, new_h))
        
        # Convert to RGB for tkinter
        self.preview_photo = PIL.ImageTk.PhotoImage(
            image=PIL.Image.fromarray(cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB))
        )

        # Clear canvas
        self.preview_canvas.delete("all")
        
        # Center the image in canvas
        x_offset = (canvas_width - new_w) // 2
        y_offset = (canvas_height - new_h) // 2
        
        # Draw image centered in canvas
        self.preview_canvas.create_image(x_offset, y_offset, image=self.preview_photo, anchor="nw")
    
    def add_to_pdf(self):
        if self.document_processor.processed_image is not None:
            if self.pdf_manager.add_image(self.document_processor.processed_image):
                self.status_var.set(f"Added to PDF. Total pages: {self.pdf_manager.get_image_count()}")
                self.btn_add_to_pdf.configure(state="disabled")
    
    def clear_images(self):
        self.pdf_manager.clear_all_images()
        self.status_var.set(f"Successfully cleared all pages! Total pages: {self.pdf_manager.get_image_count()}")
    
    def remove_top(self):
        if self.pdf_manager.remove_last_image():
            self.status_var.set(f"Image successfully removed. Total pages: {self.pdf_manager.get_image_count()}")
        else:
            self.status_var.set("No images to remove.")
    
    def add_from_local(self):
        file_path = filedialog.askopenfilename(
            initialdir="/",
            title="Select Image",
            filetypes=(("Image files", "*.jpg;*.jpeg;*.png"), ("all files", "*.*"))
        )
        
        if file_path:
            try:
                # Read image
                img = cv2.imread(file_path)
                if img is not None:
                    self.status_var.set("Processing uploaded image...")
                    
                    # Attempt to detect document in the uploaded image
                    # Create a temporary copy in the camera manager to use its detection logic
                    original_image = self.camera_manager.current_image
                    self.camera_manager.current_image = img.copy()
                    
                    # Process the frame to detect documents (reusing camera manager's detection)
                    _, _ = self.camera_manager.process_frame_local(img)
                    
                    # Get the current image regardless of document detection
                    captured_image = img.copy()
                    
                    # If document is detected, try to process it
                    if self.camera_manager.is_document_detected and self.camera_manager.document_corners is not None:
                        try:
                            # Try to process document
                            warped = self.document_processor.process_document(
                                img,
                                self.camera_manager.document_corners
                            )
                            
                            # If successfully warped, use that
                            if warped is not None:
                                captured_image = warped
                                self.status_var.set("Document detected and processed successfully.")
                            else:
                                # Use original image if warping failed
                                self.status_var.set("Document detected but couldn't be processed. Using original image.")
                        except Exception as e:
                            # Use original image if processing raised an exception
                            self.status_var.set(f"Document processing error: {e}. Using original image.")
                    else:
                        # No document detected, just use the original image
                        self.status_var.set("No document detected in uploaded image. Using image as-is.")
                    
                    # Restore the original camera image
                    self.camera_manager.current_image = original_image
                    
                    # Display the processed image and enable the add button
                    self.document_processor.processed_image = captured_image
                    self.display_preview(captured_image)
                    self.btn_add_to_pdf.configure(state="normal")
                else:
                    self.status_var.set("Failed to load image.")
            except Exception as e:
                self.status_var.set(f"Error loading image: {e}")
    
    def create_pdf(self):
        if self.pdf_manager.get_image_count() == 0:
            self.status_var.set("No images captured. Capture some documents first.")
            return
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            initialdir="/",
            title="Save PDF As",
            filetypes=(("PDF files", "*.pdf"), ("all files", "*.*")),
            defaultextension=".pdf"
        )
        
        if not filename:
            return
        
        if self.pdf_manager.create_pdf(filename):
            self.status_var.set(f"PDF created successfully: {os.path.basename(filename)}")
        else:
            self.status_var.set("Error creating PDF.")
    
    def on_closing(self):
        self.camera_manager.release()
        self.window.destroy()