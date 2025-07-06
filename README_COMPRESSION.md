# PDF Compressor Tool 🔧

A Python tool to compress PDF files to a specified target size in MB. The tool automatically selects the first PDF file from the `files_input` folder and applies various compression strategies to achieve the desired file size.

## Features

- 📁 Automatically processes the first PDF file from `files_input` folder (alphabetically sorted)
- 🎯 Compresses to a specific target size in MB
- 🔄 Two compression modes: Standard (multiple methods) and Image-only (optimized quality)
- 📊 Provides detailed progress reporting and final compression statistics
- ✅ Handles various PDF types and sizes with smart strategy selection
- 🚀 Interactive command-line interface with method selection
- 🎯 Intelligent tolerance system (5% for standard, 2% for image-only)
- 🗑️ Automatic cleanup of temporary files

## Installation

### Prerequisites

- Python 3.13 or higher
- Poetry (for dependency management)

### Dependencies

The tool uses the following Python packages:

- `PyMuPDF` (fitz) - Advanced PDF manipulation and image compression
- `Pillow` (PIL) - Image processing and format conversion
- `pdf2image` - PDF to image conversion for aggressive compression

### Setup

1. Install dependencies:

```bash
poetry install
```

Or manually install:

```bash
pip install pymupdf pillow pdf2image
```

## Usage

### Method 1: Interactive Mode (Recommended)

```bash
python compress_pdf.py
```

The program will prompt you to:

1. Enter the target size in MB
2. Choose compression method:
   - **Standard**: Tries multiple methods sequentially, stops when target is reached
   - **Image-only**: Creates multiple compressed files, keeps the best one under target size

### Method 2: Programmatic Usage

```python
from compress_pdf import PDFCompressor

# Create compressor instance
compressor = PDFCompressor()

# Standard compression (tries multiple methods)
result = compressor.compress_first_file(5.0)

# Image-only compression (creates multiple files, keeps best)
result = compressor.compress_first_file_image_only(5.0)

if result:
    print(f"Success! File saved as: {result}")
```

## File Structure

```text
project/
├── compress_pdf.py          # Main compression class with two methods
├── main.py                  # PDF merger tool (separate functionality)
├── pyproject.toml          # Poetry dependencies configuration
├── files_input/            # Place your PDF files here
│   ├── document1.pdf
│   ├── document2.pdf
│   └── ...
└── files_output/           # Compressed files will be saved here
    ├── compressed_5.0MB_2025-07-06_19-30-31.pdf
    └── ...
```

## Compression Methods

### Standard Compression Mode

The tool uses 16 different compression strategies in order of preference (least to most aggressive):

1. **Basic PDF Optimization** - Garbage collection and deflation
2. **PyMuPDF Minimal** - Quality 95% compression
3. **PyMuPDF Very Light** - Quality 90% compression
4. **PyMuPDF Light** - Quality 85% compression
5. **PyMuPDF Low** - Quality 80% compression
6. **Image Conversion Minimal** - 1600px width, 95% quality
7. **PyMuPDF Medium-Low** - Quality 75% compression
8. **Image Conversion Light** - 1400px width, 90% quality
9. **PyMuPDF Medium** - Quality 70% compression
10. **Image Conversion Medium** - 1200px width, 85% quality
11. **PyMuPDF Medium-High** - Quality 60% compression
12. **PyMuPDF High** - Quality 50% compression
13. **Image Conversion High** - 1000px width, 80% quality
14. **PyMuPDF Very High** - Quality 40% compression
15. **PyMuPDF Maximum** - Quality 30% compression

The tool stops when it finds a result within 5% tolerance of the target size.

### Image-Only Compression Mode

Creates multiple compressed files using 36 different parameter combinations:

- **Width settings**: 2000px down to 500px
- **Quality settings**: 100% down to 70%
- **Strategy**: Tests all combinations, keeps the largest file under target size (best quality)
- **Tolerance**: 2% for optimal results
- **Cleanup**: Automatically deletes all test files except the best one

## Output

The compressed files are saved in the `files_output` folder with descriptive names:

- Format: `compressed_{target_size}MB_{timestamp}.pdf`
- Example: `compressed_5.0MB_2025-07-06_19-30-31.pdf`

## Example Output

### Standard Mode Example

```text
🔧 PDF Compressor Tool
==================================================
Enter target size in MB: 5.0

Choose compression method:
1. Standard (tries multiple methods)
2. Image-only (creates multiple compressed files, keeps best one)
Enter choice (1 or 2): 1

📁 Processing file: Education_SwarajBisane_06072025.pdf
Original file size: 18.29 MB
Target size: 5.0 MB
Compression needed: 72.7%

Trying Basic PDF Optimization...
Result: 17.85 MB
📈 New best result: 17.85 MB

Trying PyMuPDF Minimal Compression...
Result: 16.12 MB
📈 New best result: 16.12 MB

Trying PyMuPDF High Compression...
Result: 4.87 MB
✅ Successfully compressed to 4.87 MB (target: 5.0 MB)

📊 Final Report:
Original file: Education_SwarajBisane_06072025.pdf
Original size: 18.29 MB
Compressed file: compressed_5.0MB_2025-07-06_19-30-31.pdf
Final size: 4.87 MB
Size reduction: 73.4%
Output saved to: files_output/compressed_5.0MB_2025-07-06_19-30-31.pdf
```

### Image-Only Mode Example

```text
🔧 PDF Compressor Tool
==================================================
Enter target size in MB: 10.0

Choose compression method:
1. Standard (tries multiple methods)
2. Image-only (creates multiple compressed files, keeps best one)
Enter choice (1 or 2): 2

📁 Processing file: Education_SwarajBisane_06072025.pdf
Original file size: 18.29 MB
Target size: 10.0 MB
Compression needed: 45.3%

🔄 Creating multiple compressed versions...
Will test 36 different compression settings

[ 1/36] Testing: width=2000, quality=100% ... Result: 15.42 MB
[ 2/36] Testing: width=2000, quality=95% ... Result: 12.85 MB
[ 3/36] Testing: width=1900, quality=90% ... Result: 10.12 MB
    🎯 New best result: 10.12 MB (closer to target)
[ 4/36] Testing: width=1800, quality=85% ... Result: 9.87 MB
    🎯 New best result: 9.87 MB (closer to target)
    ✨ Very close to target! Continuing to find optimal...
[... continues testing ...]

📊 Summary of all 36 compressed files:
================================================================================
 1. compressed_10.0MB_2025-07-06_19-51-18_attempt_04_w1800_q85.pdf
    Size: 9.87 MB | Width: 1800 | Quality: 85% | 🎯 BEST (largest under target)
 2. compressed_10.0MB_2025-07-06_19-51-18_attempt_05_w1700_q80.pdf
    Size: 9.12 MB | Width: 1700 | Quality: 80% | ✅ Under target
[... more files ...]

🎯 Keeping best result: 9.87 MB (largest file under target)
📁 Final file: compressed_10.0MB_2025-07-06_19-51-18.pdf
🗑️ Deleted 35 other files

📊 Final Report:
Original size: 18.29 MB
Target size: 10.0 MB
Final size: 9.87 MB
Size reduction: 46.1%
✅ Successfully compressed below target size with maximum quality!
```

## Notes

- The tool always processes the first PDF file found in `files_input` folder (alphabetically sorted)
- If the original file is already smaller than the target size, no compression is applied
- **Standard mode**: Tries strategies sequentially, stops when target is reached (5% tolerance)
- **Image-only mode**: Tests all 36 combinations, keeps the largest file under target (2% tolerance)
- Some PDFs may not compress to the exact target size due to their content structure
- The tool provides detailed progress information during compression
- All temporary files are automatically cleaned up

## Error Handling

- ❌ **No PDF files found**: No PDF files in input folder
- ❌ **Invalid target size**: Target size must be positive number
- ❌ **Invalid choice**: Must enter 1 or 2 for compression method
- ❌ **Compression failed**: All strategies unsuccessful
- ⚠️ **Target size not achieved**: Shows closest result with warning
- 🗑️ **Automatic cleanup**: Temporary files are automatically deleted

## Compression Method Comparison

| Feature | Standard Mode | Image-Only Mode |
|---------|---------------|-----------------|
| **Strategies** | 15 methods | 36 combinations |
| **Approach** | Sequential, stops when target reached | Tests all, keeps best |
| **Tolerance** | 5% of target size | 2% of target size |
| **Quality Priority** | Speed and efficiency | Maximum quality under target |
| **Temp Files** | Minimal | Creates many, auto-cleanup |
| **Best For** | Quick compression | Optimal quality results |

## Troubleshooting

1. **No PDF files found**: Make sure you have PDF files in the `files_input` folder
2. **Compression failed**: The PDF might be corrupted or have protection
3. **Target size not achieved**: Some PDFs have minimum compression limits
4. **Missing dependencies**: Install required packages using `poetry install`
5. **Permission errors**: Ensure write permissions for `files_output` folder
6. **Large files**: Image-only mode may take longer but provides better quality

## Technical Details

### Standard Mode Strategy Order

The standard mode tries compression strategies from least to most aggressive:

1. Basic optimization (garbage collection, deflation)
2. Minimal PyMuPDF compression (95% quality)
3. Progressive quality reduction (90%, 85%, 80%, 75%, 70%)
4. Image conversion methods (various width/quality combinations)
5. Aggressive PyMuPDF compression (60%, 50%, 40%, 30% quality)

### Image-Only Mode Parameters

Tests all combinations of:

- **Width**: 2000, 1900, 1800, 1700, 1600, 1500, 1400, 1300, 1200, 1100, 1000, 900, 800, 700, 600, 500 pixels
- **Quality**: 100%, 95%, 90%, 85%, 80%, 75%, 70%
- **DPI**: Fixed at 150 for optimal balance
- **Resampling**: Lanczos for best quality

## License

This project is licensed under the MIT License.
