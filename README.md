# PDF Merger Tool

A Python tool for merging various image files (JPG, JPEG, PNG) and existing PDF files into a single, consolidated PDF document with consistent A4 formatting.

## Features

- ✅ **Multi-format support**: Merge JPG, JPEG, PNG images and PDF files
- ✅ **Consistent A4 output**: All pages standardized to A4 size (595.27 × 841.89 points)
- ✅ **Smart scaling**: Automatic image scaling while preserving aspect ratio
- ✅ **Center alignment**: Images centered on pages with white background fill
- ✅ **PDF conversion**: Convert PDF pages to images and merge seamlessly
- ✅ **Batch processing**: Process entire folders in alphabetical order
- ✅ **Quality preservation**: High-quality JPEG compression (95%) for images
- ✅ **Error handling**: Comprehensive validation and error reporting
- ✅ **Progress tracking**: Clear progress reporting during merge operations

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
# Clone the repository
git clone <repository-url>
cd file-merge-pdf

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

#### Using pip

```bash
pip install Pillow reportlab pdf2image
```

## Quick Start

### Simple Folder Processing

The easiest way to use the tool is to place your files in the `files_input` folder and run:

```bash
python main.py
```

This will:

1. Find all supported files in `files_input/`
2. Sort them alphabetically
3. Merge them into a single PDF
4. Save the result as `output_file_{current_date}.pdf` in `files_output/`

### Programmatic Usage

```python
from main import PDFMerger

# Create a PDFMerger instance
merger = PDFMerger()

# Add files individually
merger.add_file("photo.jpg")
merger.add_file("document.pdf")
merger.add_file("scan.png")

# Merge all files
merger.merge_files("merged_output.pdf")
```

## Usage Examples

### Basic Example

```python
from main import PDFMerger

# Initialize the merger
merger = PDFMerger()

# Add files to merge
merger.add_file("image1.jpg")
merger.add_file("document.pdf")
merger.add_file("image2.png")

# List files in queue
merger.list_files()

# Merge all files into a single PDF
success = merger.merge_files("output.pdf")
if success:
    print("✅ PDF created successfully!")
```

### Batch Processing Example

```python
from main import PDFMerger

# Initialize the merger
merger = PDFMerger()

# Process all files in a folder
success = merger.process_folder(
    input_folder="my_documents",
    output_folder="merged_pdfs"
)

if success:
    print("✅ Batch processing completed!")
```

### Advanced Example with Error Handling

```python
from main import PDFMerger
import os

def merge_documents():
    merger = PDFMerger()

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

    print(f"Successfully added {added_count}/{len(files_to_merge)} files")

    if added_count > 0:
        merger.list_files()

        output_path = "merged_document.pdf"
        if merger.merge_files(output_path):
            file_size = os.path.getsize(output_path) / 1024
            print(f"✅ Success! Merged PDF created: {output_path}")
            print(f"File size: {file_size:.1f} KB")
        else:
            print("❌ Merge failed!")
    else:
        print("❌ No files could be added to merge queue")

if __name__ == "__main__":
    merge_documents()
```

## API Reference

### PDFMerger Class

#### Constructor

```python
merger = PDFMerger()
```

Initializes the merger with A4 page dimensions and empty file queue.

#### Methods

##### `add_file(file_path: str) -> bool`

Adds a file to the merge queue after validation.

- **Parameters:** `file_path` - Path to the image or PDF file
- **Returns:** `True` if file was successfully added, `False` otherwise
- **Supported formats:** `.jpg`, `.jpeg`, `.png`, `.pdf`

##### `merge_files(output_pdf_path: str) -> bool`

Merges all queued files into a single A4 PDF document.

- **Parameters:** `output_pdf_path` - Path where the merged PDF will be saved
- **Returns:** `True` if merge was successful, `False` otherwise

##### `process_folder(input_folder: str = "files_input", output_folder: str = "files_output") -> bool`

Process all supported files from the input folder in alphabetical order.

- **Parameters:**
  - `input_folder` - Folder containing files to merge (default: `"files_input"`)
  - `output_folder` - Folder where the output PDF will be saved (default: `"files_output"`)
- **Returns:** `True` if processing was successful, `False` otherwise
- **Output filename format:** `output_file_{YYYY-MM-DD}.pdf` (uses current date)

##### `clear_files()`

Clears the list of files in the merge queue.

##### `get_file_count() -> int`

Returns the number of files currently in the merge queue.

##### `list_files()`

Prints the list of files currently queued for merging.

##### `find_supported_files(folder_path: str) -> List[str]`

Finds all supported files in the specified folder.

- **Parameters:** `folder_path` - Path to the folder to search
- **Returns:** List of paths to supported files

## How It Works

### Image Processing Pipeline

1. **Validation**: Checks file existence and format support
2. **Loading**: Opens image using Pillow (PIL)
3. **Conversion**: Converts to RGB format if needed (handles RGBA, etc.)
4. **Scaling**: Calculates scaling factor to fit A4 with 5% margins
5. **Positioning**: Centers the scaled image on the A4 page
6. **Background**: Fills page with white background
7. **Integration**: Adds processed image to PDF canvas

### PDF Processing Pipeline

1. **Conversion**: Uses pdf2image to convert pages to 300 DPI images
2. **Processing**: Applies same image processing pipeline to each page
3. **Integration**: Each PDF page becomes one A4 page in output

### Technical Details

- **Page Size**: A4 (210 × 297 mm, 595.27 × 841.89 points)
- **Margins**: 5% of page dimensions for optimal appearance
- **Image Quality**: 95% JPEG compression for optimal size/quality balance
- **PDF Conversion**: 300 DPI for high-quality output
- **Scaling**: Never enlarges images beyond original size (max scale = 1.0)

## Project Structure

```text
file-merge-pdf/
├── main.py              # Main PDFMerger class and CLI
├── files_input/         # Input folder for batch processing
├── files_output/        # Output folder for merged PDFs
├── pyproject.toml       # Poetry configuration
├── README.md           # This file
└── LICENSE             # GNU AGPL v3 license
```

## Error Handling

The tool includes comprehensive error handling for:

- File not found errors
- Unsupported file formats
- Image processing errors (corrupted files, unsupported modes)
- PDF conversion issues
- File I/O problems
- Poppler installation issues
- Memory issues with large files

## Troubleshooting

### Common Issues

#### Error processing PDF: No such file or directory

- Ensure Poppler is correctly installed on your system
- Check that the PDF file is accessible and not password-protected

#### No module named 'pdf2image'

- Install the required dependencies: `pip install pdf2image`

#### Image file cannot be opened

- Verify the image file is not corrupted
- Ensure the file format is supported (JPG, JPEG, PNG)

#### No supported files found in folder

- Check that your files have the correct extensions (.jpg, .jpeg, .png, .pdf)
- Ensure the files are not hidden or in subdirectories

### Performance Tips

- For large PDF files, consider splitting them before merging
- Use compressed image formats when possible
- The tool processes files in order, so organize your input folder accordingly
- Memory usage scales with image size - very large images may cause issues

## Dependencies

- **Python**: ^3.13
- **Pillow**: ^11.3.0 (Image processing)
- **reportlab**: ^4.4.2 (PDF generation)
- **pdf2image**: ^1.17.0 (PDF to image conversion)
- **Poppler**: System dependency for PDF processing

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

### v0.1.0

- Initial release
- Support for JPG, JPEG, PNG, and PDF files
- A4 page standardization
- Batch processing functionality
- Comprehensive error handling
