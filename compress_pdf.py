import os
import sys
from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import tempfile
import shutil
from datetime import datetime


class PDFCompressor:
    def __init__(self, input_folder="files_input", output_folder="files_output"):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)

    def get_file_size_mb(self, file_path):
        """Get file size in MB"""
        return os.path.getsize(file_path) / (1024 * 1024)

    def get_first_pdf_file(self):
        """Get the first PDF file from input folder"""
        pdf_files = [f for f in self.input_folder.glob("*.pdf") if f.is_file()]
        pdf_files.sort()  # Sort to get consistent "first" file

        if not pdf_files:
            raise FileNotFoundError("No PDF files found in input folder")

        return pdf_files[0]

    def compress_pdf_basic(self, input_path, output_path):
        """Basic PDF optimization without aggressive compression"""
        doc = fitz.open(input_path)
        # Basic optimization - garbage collection and deflation
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()

    def compress_pdf_pymupdf(self, input_path, output_path, quality=50):
        """Compress PDF using PyMuPDF with image compression"""
        doc = fitz.open(input_path)

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Get image list from page
            image_list = page.get_images(full=True)

            for img_index, img in enumerate(image_list):
                # Get image data
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)

                # Convert to PIL Image for compression
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    img_data = pix.tobytes("png")
                    pil_img = Image.open(tempfile.BytesIO(img_data))

                    # Compress image
                    output_buffer = tempfile.BytesIO()
                    if pil_img.mode == "RGBA":
                        pil_img = pil_img.convert("RGB")

                    pil_img.save(output_buffer, format="JPEG", quality=quality, optimize=True)
                    output_buffer.seek(0)

                    # Replace image in PDF
                    doc.update_stream(xref, output_buffer.read())

                pix = None

        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()

    def compress_pdf_images(self, input_path, output_path, max_width=1200, quality=75):
        """Compress PDF by converting to images and back with reduced quality"""
        try:
            # Convert PDF to images
            images = convert_from_path(input_path, dpi=150)

            # Compress images
            compressed_images = []
            for img in images:
                # Resize if too large
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

                # Convert to RGB if needed
                if img.mode != "RGB":
                    img = img.convert("RGB")

                compressed_images.append(img)

            # Save as PDF
            if compressed_images:
                compressed_images[0].save(
                    output_path,
                    save_all=True,
                    append_images=compressed_images[1:],
                    format="PDF",
                    quality=quality,
                    optimize=True,
                )

            return True
        except Exception as e:
            print(f"Error in image compression method: {e}")
            return False

    def compress_to_target_size(self, input_path, target_size_mb, max_attempts=5):
        """Compress PDF to target size with iterative approach"""
        input_size = self.get_file_size_mb(input_path)

        if input_size <= target_size_mb:
            print(f"File is already smaller than target size ({input_size:.2f} MB <= {target_size_mb} MB)")
            return input_path

        print(f"Original file size: {input_size:.2f} MB")
        print(f"Target size: {target_size_mb} MB")
        print(f"Compression needed: {((input_size - target_size_mb) / input_size * 100):.1f}%")

        # Generate output filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = f"compressed_{target_size_mb}MB_{timestamp}.pdf"
        output_path = self.output_folder / output_filename

        # Try different compression strategies in order of preference (least to most aggressive)
        strategies = [
            ("Basic PDF Optimization", lambda: self.compress_pdf_basic(input_path, output_path)),
            ("PyMuPDF Minimal Compression", lambda: self.compress_pdf_pymupdf(input_path, output_path, quality=95)),
            ("PyMuPDF Very Light Compression", lambda: self.compress_pdf_pymupdf(input_path, output_path, quality=90)),
            ("PyMuPDF Light Compression", lambda: self.compress_pdf_pymupdf(input_path, output_path, quality=85)),
            ("PyMuPDF Low Compression", lambda: self.compress_pdf_pymupdf(input_path, output_path, quality=80)),
            (
                "Image Conversion Minimal",
                lambda: self.compress_pdf_images(input_path, output_path, max_width=1600, quality=95),
            ),
            ("PyMuPDF Medium-Low Compression", lambda: self.compress_pdf_pymupdf(input_path, output_path, quality=75)),
            (
                "Image Conversion Light",
                lambda: self.compress_pdf_images(input_path, output_path, max_width=1400, quality=90),
            ),
            ("PyMuPDF Medium Compression", lambda: self.compress_pdf_pymupdf(input_path, output_path, quality=70)),
            (
                "Image Conversion Medium",
                lambda: self.compress_pdf_images(input_path, output_path, max_width=1200, quality=85),
            ),
            (
                "PyMuPDF Medium-High Compression",
                lambda: self.compress_pdf_pymupdf(input_path, output_path, quality=60),
            ),
            ("PyMuPDF High Compression", lambda: self.compress_pdf_pymupdf(input_path, output_path, quality=50)),
            (
                "Image Conversion High",
                lambda: self.compress_pdf_images(input_path, output_path, max_width=1000, quality=80),
            ),
            ("PyMuPDF Very High Compression", lambda: self.compress_pdf_pymupdf(input_path, output_path, quality=40)),
            ("PyMuPDF Maximum Compression", lambda: self.compress_pdf_pymupdf(input_path, output_path, quality=30)),
        ]

        best_result = None
        best_size = float("inf")
        target_tolerance = target_size_mb * 0.05  # 5% tolerance

        for strategy_name, compress_func in strategies:
            try:
                print(f"\nTrying {strategy_name}...")

                # Create temporary output file
                temp_output = output_path.with_suffix(".tmp.pdf")

                # Apply compression strategy
                compress_func()

                # Check if file was created and get size
                if temp_output.exists():
                    current_size = self.get_file_size_mb(temp_output)
                    print(f"Result: {current_size:.2f} MB")

                    # Check if this is within acceptable range (target ± 5%)
                    if current_size <= target_size_mb and current_size >= (target_size_mb - target_tolerance):
                        # Perfect! We're in the target range
                        shutil.move(temp_output, output_path)
                        print(f"✅ Successfully compressed to {current_size:.2f} MB (target: {target_size_mb} MB)")
                        return output_path
                    elif current_size < best_size:
                        # Better than previous attempts
                        if best_result and best_result.exists():
                            best_result.unlink()
                        best_result = output_path.with_suffix(f'.best_{strategy_name.replace(" ", "_").lower()}.pdf')
                        shutil.move(temp_output, best_result)
                        best_size = current_size
                        print(f"📈 New best result: {current_size:.2f} MB")

                        # If we're very close to target, stop trying more aggressive compression
                        if current_size <= target_size_mb * 1.1:  # Within 10% above target
                            print(f"🎯 Close enough to target, stopping here")
                            break
                    else:
                        # Clean up temp file
                        temp_output.unlink()

            except Exception as e:
                print(f"❌ {strategy_name} failed: {e}")
                if "temp_output" in locals() and temp_output.exists():
                    temp_output.unlink()

        # Use the best result we found
        if best_result and best_result.exists():
            shutil.move(best_result, output_path)
            print(f"\n🎯 Best compression achieved: {best_size:.2f} MB")
            print(f"Compression ratio: {(input_size - best_size) / input_size * 100:.1f}%")

            if best_size > target_size_mb:
                print(f"⚠️  Could not reach target size. Closest: {best_size:.2f} MB (target: {target_size_mb} MB)")

            return output_path

        raise Exception("All compression strategies failed")

    def compress_first_file(self, target_size_mb):
        """Main method to compress the first PDF file to target size"""
        try:
            # Get first PDF file
            input_file = self.get_first_pdf_file()
            print(f"📁 Processing file: {input_file.name}")

            # Compress to target size
            output_file = self.compress_to_target_size(input_file, target_size_mb)

            # Final report
            original_size = self.get_file_size_mb(input_file)
            final_size = self.get_file_size_mb(output_file)

            print(f"\n📊 Final Report:")
            print(f"Original file: {input_file.name}")
            print(f"Original size: {original_size:.2f} MB")
            print(f"Compressed file: {output_file.name}")
            print(f"Final size: {final_size:.2f} MB")
            print(f"Size reduction: {(original_size - final_size) / original_size * 100:.1f}%")
            print(f"Output saved to: {output_file}")

            return output_file

        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def compress_with_multiple_attempts_image_only(self, input_path, target_size_mb):
        """Create multiple compressed files using image compression and keep only the best one below target size"""
        input_size = self.get_file_size_mb(input_path)

        if input_size <= target_size_mb:
            print(f"File is already smaller than target size ({input_size:.2f} MB <= {target_size_mb} MB)")
            return input_path

        print(f"Original file size: {input_size:.2f} MB")
        print(f"Target size: {target_size_mb} MB")
        print(f"Compression needed: {((input_size - target_size_mb) / input_size * 100):.1f}%")

        # Generate base output filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_filename = f"compressed_{target_size_mb}MB_{timestamp}"

        # Define multiple compression parameters (max_width, quality)
        # Start with lighter compression to find the optimal balance
        compression_params = [
            (2000, 100),  # no compression
            (2000, 95),  # Very light compression
            (1900, 90),  # Light compression
            (1800, 85),  # Light compression
            (1700, 80),  # Light-medium compression
            (1600, 95),  # Alternative light compression
            (1600, 90),  # Alternative light compression
            (1600, 85),  # Alternative light compression
            (1600, 80),  # Alternative light compression
            (1500, 95),  # Medium compression
            (1500, 90),  # Medium compression
            (1500, 85),  # Medium compression
            (1500, 80),  # Medium compression
            (1400, 95),  # Medium compression
            (1400, 90),  # Medium compression
            (1400, 85),  # Medium compression
            (1400, 80),  # Medium compression
            (1300, 85),  # Medium-high compression
            (1300, 80),  # Medium-high compression
            (1200, 90),  # High compression alternative
            (1200, 85),  # High compression alternative
            (1200, 80),  # High compression
            (1200, 75),  # High compression
            (1100, 85),  # High compression alternative
            (1100, 80),  # High compression alternative
            (1000, 90),  # Very high compression alternative
            (1000, 85),  # Very high compression alternative
            (1000, 80),  # Very high compression
            (1000, 75),  # Very high compression
            (900, 85),  # Very high compression alternative
            (900, 80),  # Very high compression alternative
            (800, 85),  # Maximum compression alternative
            (800, 80),  # Maximum compression alternative
            (700, 80),  # Extreme compression
            (600, 75),  # Extreme compression
            (500, 70),  # Ultra compression
        ]

        created_files = []
        best_file = None
        best_size = 0  # Start with 0 since we want the largest file under target
        target_tolerance = target_size_mb * 0.02  # 2% tolerance

        print("\n🔄 Creating multiple compressed versions...")
        print(f"Will test {len(compression_params)} different compression settings\n")

        for i, (max_width, quality) in enumerate(compression_params, 1):
            try:
                # Create unique filename for this attempt
                temp_filename = f"{base_filename}_attempt_{i:02d}_w{max_width}_q{quality}.pdf"
                temp_output_path = self.output_folder / temp_filename

                print(
                    f"[{i:2d}/{len(compression_params)}] Testing: width={max_width}, quality={quality}%", end=" ... "
                )

                # Apply compression
                success = self.compress_pdf_images(input_path, temp_output_path, max_width=max_width, quality=quality)

                if success and temp_output_path.exists():
                    current_size = self.get_file_size_mb(temp_output_path)
                    print(f"Result: {current_size:.2f} MB")

                    created_files.append((temp_output_path, current_size, max_width, quality))

                    # Check if this is the best result below target size
                    # We want the LARGEST file that's still under the target size (best quality)
                    if current_size <= target_size_mb and current_size > best_size:
                        best_file = temp_output_path
                        best_size = current_size
                        print(f"    🎯 New best result: {current_size:.2f} MB (closer to target)")

                        # If we're very close to target, we might want to continue to find even better
                        if current_size >= (target_size_mb - target_tolerance):
                            print("    ✨ Very close to target! Continuing to find optimal...")

                else:
                    print("❌ Failed")

            except Exception as e:
                print(f"❌ Error: {e}")

        # Sort all created files by size (descending - largest first)
        created_files.sort(key=lambda x: x[1], reverse=True)

        print(f"\n📊 Summary of all {len(created_files)} compressed files:")
        print("=" * 80)
        for i, (file_path, size, width, quality) in enumerate(created_files, 1):
            if file_path == best_file:
                status = "🎯 BEST (largest under target)"
            elif size <= target_size_mb:
                status = "✅ Under target"
            else:
                status = "❌ Over target"

            print(f"{i:2d}. {file_path.name}")
            print(f"    Size: {size:.2f} MB | Width: {width} | Quality: {quality}% | {status}")

        # Clean up: remove all files except the best one
        final_output_path = self.output_folder / f"compressed_{target_size_mb}MB_{timestamp}.pdf"

        if best_file:
            # Rename the best file to the final name
            shutil.move(best_file, final_output_path)
            print(f"\n🎯 Keeping best result: {best_size:.2f} MB (largest file under target)")
            print(f"📁 Final file: {final_output_path.name}")

            # Remove all other files
            deleted_count = 0
            for file_path, _, _, _ in created_files:
                if file_path != best_file and file_path.exists():
                    file_path.unlink()
                    deleted_count += 1

            print(f"🗑️  Deleted {deleted_count} other files")

            # Final report
            print("\n📊 Final Report:")
            print(f"Original size: {input_size:.2f} MB")
            print(f"Target size: {target_size_mb} MB")
            print(f"Final size: {best_size:.2f} MB")
            print(f"Size reduction: {(input_size - best_size) / input_size * 100:.1f}%")

            if best_size > target_size_mb:
                print(f"⚠️  Could not reach target size. Closest: {best_size:.2f} MB (target: {target_size_mb} MB)")
            else:
                print("✅ Successfully compressed below target size with maximum quality!")

            return final_output_path
        else:
            # Clean up all files if no good result
            for file_path, _, _, _ in created_files:
                if file_path.exists():
                    file_path.unlink()

            raise Exception("No successful compression achieved")

    def compress_first_file_image_only(self, target_size_mb):
        """Main method to compress the first PDF file using only image compression with multiple attempts"""
        try:
            # Get first PDF file
            input_file = self.get_first_pdf_file()
            print(f"📁 Processing file: {input_file.name}")

            # Compress to target size using image compression only
            output_file = self.compress_with_multiple_attempts_image_only(input_file, target_size_mb)

            return output_file

        except Exception as e:
            print(f"❌ Error: {e}")
            return None


def main():
    """Main function to run the PDF compressor"""
    print("🔧 PDF Compressor Tool")
    print("=" * 50)

    # Get target size from user
    try:
        target_size = float(input("Enter target size in MB: "))
        if target_size <= 0:
            print("❌ Target size must be positive")
            return
    except ValueError:
        print("❌ Invalid input. Please enter a valid number.")
        return

    # Ask user for compression method
    print("\nChoose compression method:")
    print("1. Standard (tries multiple methods)")
    print("2. Image-only (creates multiple compressed files, keeps best one)")

    try:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice not in ["1", "2"]:
            print("❌ Invalid choice. Please enter 1 or 2.")
            return
    except (ValueError, KeyboardInterrupt):
        print("❌ Invalid input.")
        return

    # Create compressor and run
    compressor = PDFCompressor()

    if choice == "1":
        compressor.compress_first_file(target_size)
    else:
        compressor.compress_first_file_image_only(target_size)


if __name__ == "__main__":
    main()
