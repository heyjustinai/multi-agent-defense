import os
import subprocess
import re
import logging
import tempfile
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def sanitize_filename(filename):
    """
    Sanitize the filename to be safe for filesystem operations.
    """
    # Remove invalid characters and replace spaces with underscores
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.replace(' ', '_')
    return filename

def validate_markdown_content(file_path):
    """
    Validate the content of a markdown file.
    Returns (is_valid, message)
    """
    try:
        if not os.path.exists(file_path):
            return False, "File does not exist"

        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size < 10:  # Only fail if file is essentially empty
            return False, f"File too small ({file_size} bytes)"

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for critical error messages
        error_patterns = [
            r"pandoc.*error",
            r"fatal error",
            r"conversion failed",
            r"cannot process",
            r"invalid input"
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, content.lower()):
                return False, f"Found critical error: {pattern}"

        # Check for actual content
        lines = content.strip().split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        if len(non_empty_lines) < 1:
            return False, "No content found in file"

        # All checks passed
        return True, f"Valid content ({len(non_empty_lines)} lines, {file_size} bytes)"

    except Exception as e:
        return False, f"Validation error: {str(e)}"

def check_requirements():
    """
    Check if required tools are installed.
    """
    # Check pandoc
    try:
        subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.error("Pandoc is not installed. Please install it using 'brew install pandoc'")
        return False

    # Check LibreOffice
    try:
        subprocess.run(['soffice', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.error("LibreOffice is not installed. Please install it using 'brew install libreoffice'")
        return False

    return True

def convert_doc_to_docx(input_path):
    """
    Convert .doc to .docx using LibreOffice.
    Returns path to the converted file or None if conversion failed.
    """
    # Create a temporary directory for the conversion
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Copy the input file to temp directory
            temp_input = os.path.join(temp_dir, os.path.basename(input_path))
            shutil.copy2(input_path, temp_input)
            
            # Convert to docx using LibreOffice
            subprocess.run([
                'soffice',
                '--headless',
                '--convert-to', 'docx',
                '--outdir', temp_dir,
                temp_input
            ], capture_output=True, check=True)
            
            # Get the converted file path
            docx_filename = os.path.splitext(os.path.basename(input_path))[0] + '.docx'
            docx_path = os.path.join(temp_dir, docx_filename)
            
            if os.path.exists(docx_path):
                # Create a new temporary file for the result
                temp_output = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
                temp_output.close()
                shutil.copy2(docx_path, temp_output.name)
                return temp_output.name
                
        except subprocess.CalledProcessError as e:
            logging.error(f"Error converting {input_path} to docx: {e.stderr}")
        except Exception as e:
            logging.error(f"Unexpected error converting {input_path} to docx: {str(e)}")
    
    return None

def convert_to_markdown(input_path, output_path):
    """
    Convert document to markdown using pandoc.
    
    :param input_path: Path to input document
    :param output_path: Path to output markdown file
    """
    if not os.path.exists(input_path):
        logging.error(f"Input file does not exist: {input_path}")
        return False

    temp_file = None
    try:
        # If it's a .doc file, convert to .docx first
        if input_path.lower().endswith('.doc'):
            temp_file = convert_doc_to_docx(input_path)
            if not temp_file:
                return False
            input_path = temp_file

        # Run pandoc conversion
        result = subprocess.run([
            'pandoc',
            input_path,
            '-f', 'docx',
            '-t', 'markdown',
            '-o', output_path,
            '--wrap=none',  # Don't wrap lines
            '--extract-media=./'  # Extract embedded images if any
        ], capture_output=True, text=True, check=True)
        
        # Validate the output
        is_valid, validation_msg = validate_markdown_content(output_path)
        if not is_valid:
            logging.error(f"Invalid conversion output: {validation_msg}")
            if os.path.exists(output_path):
                os.unlink(output_path)
            return False
            
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting {input_path}: {e.stderr}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error converting {input_path}: {str(e)}")
        return False
    finally:
        # Clean up temporary file if it exists
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)

def convert_docs_to_markdown(input_folder, output_folder):
    """
    Convert all .doc and .docx files in the input folder to .md format.

    :param input_folder: Path to the folder containing .doc/.docx files
    :param output_folder: Path to the folder where .md files will be saved
    """
    # Check if required tools are installed
    if not check_requirements():
        return

    # Check if input folder exists
    if not os.path.exists(input_folder):
        logging.error(f"Input folder does not exist: {input_folder}")
        return

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Track conversion statistics
    total_files = 0
    successful_conversions = 0
    validation_results = []
    
    # Get list of files to convert
    try:
        files = [f for f in os.listdir(input_folder) 
                if f.lower().endswith(('.doc', '.docx'))]
        total_files = len(files)
        
        if total_files == 0:
            logging.warning(f"No .doc or .docx files found in {input_folder}")
            return
            
        logging.info(f"Found {total_files} files to convert")
        
        for filename in files:
            input_path = os.path.join(input_folder, filename)
            base_name = os.path.splitext(filename)[0]
            safe_name = sanitize_filename(base_name)
            output_path = os.path.join(output_folder, f'{safe_name}.md')
            
            logging.info(f"Converting: {filename}")
            if convert_to_markdown(input_path, output_path):
                successful_conversions += 1
                is_valid, validation_msg = validate_markdown_content(output_path)
                validation_results.append((filename, is_valid, validation_msg))
                logging.info(f"Successfully converted: {filename} -> {safe_name}.md")
                logging.info(f"Validation: {validation_msg}")
            else:
                logging.error(f"Failed to convert: {filename}")
                validation_results.append((filename, False, "Conversion failed"))
                
    except Exception as e:
        logging.error(f"Error processing files: {str(e)}")
        return
        
    # Print summary
    logging.info(f"\nConversion Summary:")
    logging.info(f"Total files processed: {total_files}")
    logging.info(f"Successfully converted: {successful_conversions}")
    logging.info(f"Failed conversions: {total_files - successful_conversions}")
    
    # Print validation results
    logging.info(f"\nValidation Results:")
    for filename, is_valid, msg in validation_results:
        status = "" if is_valid else ""
        logging.info(f"{status} {filename}: {msg}")

def main():
    # Specify input and output folders using the correct paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(base_dir, "AAR", "raw", "USSOF")
    output_folder = os.path.join(base_dir, "AAR", "clean", "USSOF")
    
    logging.info(f"Input folder: {input_folder}")
    logging.info(f"Output folder: {output_folder}")
    
    convert_docs_to_markdown(input_folder, output_folder)

if __name__ == '__main__':
    main()