# PDF Merger Tool

A Python solution for merging various image files (JPG, PNG) and existing PDF files into a single, consolidated PDF document with consistent A4 formatting.

## Features

- ✅ Merge multiple image formats (JPG, JPEG, PNG) and PDF files
- ✅ Consistent A4 page sizing for all output pages
- ✅ Automatic image scaling while preserving aspect ratio
- ✅ Center-aligned images with white background fill
- ✅ Convert PDF pages to images and merge them seamlessly
- ✅ Comprehensive error handling and validation
- ✅ Clear progress reporting during merge operations
- ✅ Batch processing from folders in alphabetical order

## Installation

### Prerequisites

This tool requires **Poppler** to be installed on your system for PDF processing:

#### macOS

```bash
brew install poppler
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get install poppler-utils
```

#### Windows

1. Download Poppler for Windows from: <https://github.com/oschwartz10612/poppler-windows/releases/>
2. Extract the downloaded archive
3. Add the `bin` folder to your system PATH

### Python Dependencies

#### Using Poetry (Recommended)

```bash
# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

#### Using pip

```bash
pip install Pillow reportlab pdf2image
```

## Usage

### Basic Example

```python
from main import PDFMerger

# Create a PDFMerger instance
merger = PDFMerger()

# Add files to merge
merger.add_file("image1.jpg")
merger.add_file("document.pdf")
merger.add_file("image2.png")

# Merge all files into a single PDF
merger.merge_files("output.pdf")
```

### Complete Example

```python
from main import PDFMerger
import os

def merge_documents():
    # Initialize the merger
    merger = PDFMerger()

    # Add multiple files
    files_to_merge = [
        "photos/vacation1.jpg",
        "photos/vacation2.png",
        "documents/report.pdf",
        "scans/receipt.jpeg"
    ]

    print("Adding files to merge queue...")
    added_count = 0

    for file_path in files_to_merge:
        if merger.add_file(file_path):
            added_count += 1

    print(f"Successfully added {added_count} files")

    # Display current file list
    merger.list_files()

    # Merge files
    output_path = "merged_document.pdf"
    if merger.merge_files(output_path):
        print(f"✅ Success! Merged PDF created: {output_path}")
        print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")
    else:
        print("❌ Merge failed!")

if __name__ == "__main__":
    merge_documents()
```

### Running the Examples

```bash
# Run the built-in example
python main.py

# Or with poetry
poetry run python main.py
```

### Batch Processing

Process all files from a folder in alphabetical order:

```bash
# Run the batch processing script
python run_batch_process.py
```

This will:

1. Look for files in the "files_input" folder
2. Sort them alphabetically
3. Merge them into a single PDF
4. Save the result as "output_file_{current_date}.pdf" in the "files_output" folder

## Class Reference

### PDFMerger

The main class for merging files into a PDF document.

#### Constructor

```python
merger = PDFMerger()
```

Initializes the merger with A4 page dimensions (595.27 × 841.89 points).

#### Methods

##### `add_file(file_path: str) -> bool`

Adds a file to the merge queue after validation.

- **Parameters:** `file_path` - Path to the image or PDF file
- **Returns:** `True` if file was successfully added, `False` otherwise
- **Supported formats:** JPG, JPEG, PNG, PDF

##### `merge_files(output_pdf_path: str) -> bool`

Merges all added files into a single A4 PDF document.

- **Parameters:** `output_pdf_path` - Path where the merged PDF will be saved
- **Returns:** `True` if merge was successful, `False` otherwise

##### `clear_files()`

Clears the list of files in the merge queue.

##### `get_file_count() -> int`

Returns the number of files currently in the merge queue.

##### `list_files()`

Prints the list of files currently queued for merging.

##### `batch_process(input_folder="files_input", output_folder="files_output") -> (bool, str)`

Process all supported files from the input folder in alphabetical order and save to output folder.

- **Parameters:**
  - `input_folder` - Folder containing files to merge (default: 'files_input')
  - `output_folder` - Folder where the output PDF will be saved (default: 'files_output')
- **Returns:**
  - `(success, output_path)` - A tuple with success status (bool) and path to output file (str) if successful
- **Output filename format:** `output_file_{YYYY-MM-DD}.pdf` (uses current date)

## How It Works

### Image Processing

1. **Validation:** Checks if the file exists and has a supported format
2. **Loading:** Opens the image using Pillow (PIL)
3. **Conversion:** Converts to RGB format if necessary
4. **Scaling:** Calculates scaling factor to fit within A4 boundaries while preserving aspect ratio
5. **Positioning:** Centers the scaled image on the A4 page
6. **Background:** Fills remaining space with white background
7. **Integration:** Adds the processed image to the PDF canvas

### PDF Processing

1. **Conversion:** Uses pdf2image to convert each PDF page to a high-resolution image (300 DPI)
2. **Processing:** Applies the same image processing workflow to each converted page
3. **Integration:** Each original PDF page becomes one A4 page in the output PDF

### Output Format

- **Page Size:** A4 (210 × 297 mm, 595.27 × 841.89 points)
- **Margins:** 5% of page dimensions for optimal visual appearance
- **Background:** White fill for areas not occupied by content
- **Quality:** High-quality JPEG compression (95%) for images

## Error Handling

The tool includes comprehensive error handling for:

- File not found errors
- Unsupported file formats
- Image processing errors
- PDF conversion issues
- File I/O problems
- Poppler installation issues

## Troubleshooting

### Common Issues

**"Error processing PDF: PDF file is damaged"**

- Ensure the PDF file is not corrupted
- Try opening the PDF in another application to verify

**"No module named 'pdf2image'"**

- Install the required dependencies: `pip install pdf2image`

**"Unable to get page count"**

- Ensure Poppler is correctly installed on your system
- Check that the PDF file is accessible and not password-protected

**"Image file cannot be opened"**

- Verify the image file is not corrupted
- Ensure the file format is supported (JPG, JPEG, PNG)

### Performance Tips

- For large PDF files, consider splitting them before merging
- Use compressed image formats when possible
- The tool automatically optimizes images for PDF inclusion

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.
