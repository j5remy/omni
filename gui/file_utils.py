from PyQt5.QtWidgets import QFileDialog


def save_text_to_file(parent, text):
    """
    Opens a file dialog to choose an output file and saves the provided text.
    """
    if not text.strip():
        print("No notes to save.")
        return

    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    file_path, _ = QFileDialog.getSaveFileName(parent, "Save Notes", "", "Text Files (*.txt)", options=options)
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text.strip())
            print(f"Notes saved to {file_path}")
        except Exception as e:
            print(f"Error saving notes: {e}")
    else:
        print("Save cancelled.")