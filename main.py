"""
PDF Merger Tool - Combines images and PDF files into a single A4 PDF document

This module provides a PDFMerger class that can merge various image files (JPG, PNG)
and existing PDF files into a single, consolidated PDF document with consistent A4 formatting.

Dependencies:
- Pillow (PIL): For image manipulation
- reportlab: For PDF generation
- pdf2image: For converting PDF pages to images (requires Poppler)

Installation Instructions:
1. Install Poppler:
   - macOS: brew install poppler
   - Linux (Ubuntu/Debian): sudo apt-get install poppler-utils
   - Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/

2. Install Python packages:
   pip install Pillow reportlab pdf2image
   or
   poetry add Pillow reportlab pdf2image
"""

import os
from typing import List
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pdf2image import convert_from_path
import tempfile
import datetime
import glob


class PDFMerger:
    """
    A class for merging image files and PDF documents into a single A4 PDF.

    This class handles the conversion of various image formats (JPG, PNG) and
    existing PDF files into a unified PDF document with consistent A4 page sizing.
    All images are scaled to fit within A4 boundaries while preserving aspect ratio.
    """

    def __init__(self):
        """
        Initialize the PDFMerger with A4 page dimensions and empty file list.

        Sets up standard A4 dimensions in points (72 points per inch):
        - Width: 595.27 points (8.27 inches)
        - Height: 841.89 points (11.69 inches)
        """
        # A4 page dimensions in points (72 points per inch)
        self.page_width, self.page_height = A4

        # Internal list to store file paths for processing
        self.files_to_merge: List[str] = []

        # Supported file extensions
        self.supported_image_formats = {".jpg", ".jpeg", ".png"}
        self.supported_pdf_format = {".pdf"}

        print(f"PDFMerger initialized with A4 dimensions: {self.page_width:.2f} x {self.page_height:.2f} points")

    def add_file(self, file_path: str) -> bool:
        """
        Add a file to the merge queue after validation.

        Args:
            file_path (str): Path to the image or PDF file to be added

        Returns:
            bool: True if file was successfully added, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"Error: File does not exist: {file_path}")
                return False

            # Get file extension and normalize to lowercase
            file_extension = os.path.splitext(file_path)[1].lower()

            # Validate file type
            if file_extension in self.supported_image_formats:
                print(f"Added image file: {os.path.basename(file_path)}")
                self.files_to_merge.append(file_path)
                return True
            elif file_extension in self.supported_pdf_format:
                print(f"Added PDF file: {os.path.basename(file_path)}")
                self.files_to_merge.append(file_path)
                return True
            else:
                print(
                    f"Error: Unsupported file format '{file_extension}'. "
                    f"Supported formats: {', '.join(self.supported_image_formats | self.supported_pdf_format)}"
                )
                return False

        except Exception as e:
            print(f"Error adding file {file_path}: {str(e)}")
            return False

    def _calculate_scaling_and_position(self, image_width: int, image_height: int) -> tuple:
        """
        Calculate scaling factor and position to fit image in A4 page while preserving aspect ratio.

        Args:
            image_width (int): Original image width in pixels
            image_height (int): Original image height in pixels

        Returns:
            tuple: (scale_factor, x_position, y_position, scaled_width, scaled_height)
        """
        # Define margins (10% of page dimensions for better visual appearance)
        margin_x = self.page_width * 0.05
        margin_y = self.page_height * 0.05

        # Available space for the image
        available_width = self.page_width - (2 * margin_x)
        available_height = self.page_height - (2 * margin_y)

        # Calculate scaling factors for width and height
        width_scale = available_width / image_width
        height_scale = available_height / image_height

        # Use the smaller scaling factor to ensure the image fits entirely within page
        # Cap scale_factor at 1.0 to prevent scaling up images (only scale down if needed)
        # This ensures images are never enlarged beyond their original size
        scale_factor = min(width_scale, height_scale, 1.0)

        # Calculate scaled dimensions
        scaled_width = image_width * scale_factor
        scaled_height = image_height * scale_factor

        # Calculate position to center the image
        x_position = (self.page_width - scaled_width) / 2
        y_position = (self.page_height - scaled_height) / 2

        return scale_factor, x_position, y_position, scaled_width, scaled_height

    def _add_image_to_pdf(self, canvas_obj: canvas.Canvas, image_path: str) -> bool:
        """
        Add an image to the PDF canvas as a new A4 page.

        Args:
            canvas_obj (canvas.Canvas): ReportLab canvas object
            image_path (str): Path to the image file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Open and process the image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (handles RGBA and other formats)
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Get image dimensions
                img_width, img_height = img.size

                # Calculate scaling and positioning
                scale_factor, x_pos, y_pos, scaled_width, scaled_height = self._calculate_scaling_and_position(
                    img_width, img_height
                )

                # Fill the entire page with white background
                canvas_obj.setFillColorRGB(1, 1, 1)  # White color
                canvas_obj.rect(0, 0, self.page_width, self.page_height, fill=1)

                # Save image to temporary file for ReportLab compatibility
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                    img.save(temp_file.name, "JPEG", quality=95)
                    temp_image_path = temp_file.name

                try:
                    # Add the scaled and positioned image to the canvas
                    canvas_obj.drawImage(
                        temp_image_path,
                        x_pos,
                        y_pos,
                        width=scaled_width,
                        height=scaled_height,
                        preserveAspectRatio=True,
                    )

                    # Move to next page after adding content
                    canvas_obj.showPage()
                    print(f"  Added image: {os.path.basename(image_path)} " f"(scaled by {scale_factor:.2f})")

                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_image_path)
                    except:
                        pass

                return True

        except Exception as e:
            print(f"Error processing image {image_path}: {str(e)}")
            return False

    def _add_pdf_to_pdf(self, canvas_obj: canvas.Canvas, pdf_path: str) -> bool:
        """
        Add all pages from a PDF file to the canvas by converting them to images.

        Args:
            canvas_obj (canvas.Canvas): ReportLab canvas object
            pdf_path (str): Path to the PDF file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert PDF pages to images
            print(f"  Converting PDF pages to images: {os.path.basename(pdf_path)}")

            # Convert PDF to images with high DPI for better quality
            images = convert_from_path(pdf_path, dpi=300)

            # Process each page as an image
            for page_num, img in enumerate(images, 1):
                # Convert PIL Image to RGB if necessary
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Get image dimensions
                img_width, img_height = img.size

                # Calculate scaling and positioning
                scale_factor, x_pos, y_pos, scaled_width, scaled_height = self._calculate_scaling_and_position(
                    img_width, img_height
                )

                # Fill the entire page with white background
                canvas_obj.setFillColorRGB(1, 1, 1)  # White color
                canvas_obj.rect(0, 0, self.page_width, self.page_height, fill=1)

                # Save page image to temporary file
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                    img.save(temp_file.name, "JPEG", quality=95)
                    temp_image_path = temp_file.name

                try:
                    # Add the scaled and positioned page to the canvas
                    canvas_obj.drawImage(
                        temp_image_path,
                        x_pos,
                        y_pos,
                        width=scaled_width,
                        height=scaled_height,
                        preserveAspectRatio=True,
                    )

                    # Move to next page after adding content
                    canvas_obj.showPage()
                    print(f"    Added page {page_num} from PDF " f"(scaled by {scale_factor:.2f})")

                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_image_path)
                    except:
                        pass

            print(f"  Successfully processed {len(images)} pages from PDF")
            return True

        except Exception as e:
            print(f"Error processing PDF {pdf_path}: {str(e)}")
            print("Note: Make sure Poppler is installed on your system for PDF processing")
            return False

    def merge_files(self, output_pdf_path: str) -> bool:
        """
        Merge all added files into a single A4 PDF document.

        Args:
            output_pdf_path (str): Path where the merged PDF will be saved

        Returns:
            bool: True if merge was successful, False otherwise
        """
        if not self.files_to_merge:
            print("Error: No files have been added for merging")
            return False

        try:
            print(f"\nStarting merge process...")
            print(f"Output PDF: {output_pdf_path}")
            print(f"Files to process: {len(self.files_to_merge)}")

            # Create the PDF canvas
            pdf_canvas = canvas.Canvas(output_pdf_path, pagesize=A4)

            successful_files = 0

            # Process each file in the order they were added
            for i, file_path in enumerate(self.files_to_merge, 1):
                print(f"\nProcessing file {i}/{len(self.files_to_merge)}: {os.path.basename(file_path)}")

                # Determine file type and process accordingly
                file_extension = os.path.splitext(file_path)[1].lower()

                if file_extension in self.supported_image_formats:
                    if self._add_image_to_pdf(pdf_canvas, file_path):
                        successful_files += 1
                elif file_extension in self.supported_pdf_format:
                    if self._add_pdf_to_pdf(pdf_canvas, file_path):
                        successful_files += 1

            # Save the final PDF
            pdf_canvas.save()

            print("\n✅ Merge completed successfully!")
            print(f"Successfully processed: {successful_files}/{len(self.files_to_merge)} files")
            print(f"Output saved to: {output_pdf_path}")

            return successful_files > 0

        except Exception as e:
            print(f"Error during merge process: {str(e)}")
            return False

    def clear_files(self):
        """Clear the list of files to merge."""
        self.files_to_merge.clear()
        print("File list cleared")

    def get_file_count(self) -> int:
        """Get the number of files currently in the merge queue."""
        return len(self.files_to_merge)

    def list_files(self):
        """Print the list of files currently queued for merging."""
        if not self.files_to_merge:
            print("No files in merge queue")
        else:
            print(f"\nFiles in merge queue ({len(self.files_to_merge)}):")
            for i, file_path in enumerate(self.files_to_merge, 1):
                file_extension = os.path.splitext(file_path)[1].lower()
                file_type = "Image" if file_extension in self.supported_image_formats else "PDF"
                print(f"  {i}. {file_type}: {os.path.basename(file_path)}")

    def find_supported_files(self, folder_path: str) -> List[str]:
        """
        Find all supported image and PDF files in the specified folder.

        Args:
            folder_path (str): Path to the folder to search for files

        Returns:
            List[str]: List of paths to supported files (case-insensitive extension matching)
        """
        # Find all files in input folder
        all_input_files = glob.glob(os.path.join(folder_path, "*.*"))

        # List to store supported files
        supported_files = []

        # Filter files based on extensions (case-insensitive)
        supported_extensions = list(self.supported_image_formats) + list(self.supported_pdf_format)
        for file_path in all_input_files:
            # Get file extension and convert to lowercase for comparison
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in supported_extensions:
                supported_files.append(file_path)

        return supported_files

    def process_folder(self, input_folder: str = "files_input", output_folder: str = "files_output") -> bool:
        """
        Process all image and PDF files in the input folder and merge them into a single PDF.

        Files are processed in alphabetical order, and the output PDF is saved with today's date.

        Args:
            input_folder (str): Path to the folder containing image and PDF files (default: 'files_input')
            output_folder (str): Path to the folder where the merged PDF will be saved (default: 'files_output')

        Returns:
            bool: True if processing and merge were successful, False otherwise
        """
        try:
            # Create folders if they don't exist
            for folder in [input_folder, output_folder]:
                os.makedirs(folder, exist_ok=True)
                if not os.path.exists(folder):
                    print(f"Error: Could not create folder {folder}")
                    return False

            # Generate output PDF file name with today's date
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            output_pdf_name = f"output_file_{today}.pdf"
            output_pdf_path = os.path.join(output_folder, output_pdf_name)

            print(f"\nProcessing files in folder: {input_folder}")
            print(f"Output PDF will be saved as: {output_pdf_path}")

            # Find all supported files in the input folder
            all_files = self.find_supported_files(input_folder)

            # Check if any files were found
            if not all_files:
                print(f"No supported files found in {input_folder}")
                print(f"Supported formats: {', '.join(self.supported_image_formats | self.supported_pdf_format)}")
                return False

            # Sort files alphabetically
            all_files.sort()

            # Clear any previously added files
            self.clear_files()

            # Add files to the merger
            for file_path in all_files:
                self.add_file(file_path)

            # Display file list
            self.list_files()

            # Start merge
            print(f"Processing {len(all_files)} files in alphabetical order")
            return self.merge_files(output_pdf_path)

        except Exception as e:
            print(f"Error processing folder {input_folder}: {str(e)}")
            return False


def main():
    """
    Example usage of the PDFMerger class.

    This function demonstrates how to:
    1. Create a PDFMerger instance
    2. Add various image and PDF files
    3. Merge them into a single PDF
    4. Handle basic error scenarios
    """
    print("=== PDF Merger Example ===\n")

    # Create an instance of PDFMerger
    merger = PDFMerger()

    merger.process_folder()

    # Example of clearing the file list for a new merge operation
    print("\nClearing file list for demonstration...")
    merger.clear_files()
    merger.list_files()


if __name__ == "__main__":
    main()
