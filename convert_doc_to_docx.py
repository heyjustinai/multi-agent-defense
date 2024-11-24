import os
import comtypes.client

def convert_doc_to_docx(input_folder, output_folder):
    """
    Convert all .doc files in the input folder to .docx format and save them in the output folder.

    :param input_folder: Path to the folder containing .doc files.
    :param output_folder: Path to the folder where .docx files will be saved.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Initialize Word application
    word = comtypes.client.CreateObject("Word.Application")
    word.Visible = False

    for filename in os.listdir(input_folder):
        if filename.endswith(".doc"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename.replace(".doc", ".docx"))
            try:
                doc = word.Documents.Open(input_path)
                doc.SaveAs(output_path, FileFormat=16)  # 16 corresponds to wdFormatXMLDocument (.docx)
                doc.Close()
                print(f"Converted: {input_path} -> {output_path}")
            except Exception as e:
                print(f"Error converting {input_path}: {e}")

    word.Quit()
    print("Conversion complete!")

# Specify input and output folders
input_folder = r"path\to\input\folder"  # Replace with the folder containing .doc files
output_folder = r"path\to\output\folder"  # Replace with the folder to save .docx files

# Convert .doc to .docx
convert_doc_to_docx(input_folder, output_folder)