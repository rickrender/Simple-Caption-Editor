import sys
import argparse
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QWidget, QPushButton, QLineEdit, QListWidget, QTextEdit, QMessageBox, QDialog, QScrollArea, QShortcut
from PyQt5.QtGui import QImage, QPixmap, QKeySequence, QDesktopServices
from PyQt5.QtCore import Qt, QUrl  # Correct import for Qt
import os
import platform

class FileEditorApp(QMainWindow):
    def __init__(self, dark_mode=False):
        super().__init__()
        self.setWindowTitle("Simple Caption Editor")
        self.setGeometry(100, 100, 1200, 800)

        # Apply stylesheets
        if dark_mode:
            self.setStyleSheet(self.dark_mode_stylesheet())
        else:
            self.apply_stylesheet()

        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(5)

        # Control panel and image preview (Column 1)
        self.control_panel_layout = QVBoxLayout()
        self.control_panel_layout.setContentsMargins(10, 10, 10, 10)
        self.control_panel_layout.setSpacing(10)
        self.main_layout.addLayout(self.control_panel_layout)

        # Folder selection
        self.folder_button = self.create_button("Select Folder")
        self.folder_button.clicked.connect(self.select_folder)
        self.control_panel_layout.addWidget(self.folder_button)

        self.folder_label = QLabel("No folder selected")
        self.control_panel_layout.addWidget(self.folder_label)

        # Add spacer
        self.control_panel_layout.addSpacerItem(QSpacerItem(15, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Rename panel
        self.rename_entry = QLineEdit()
        self.rename_entry.setPlaceholderText("Rename Structure")
        self.control_panel_layout.addWidget(self.rename_entry)

        self.rename_button = self.create_button("Rename Files")
        self.rename_button.clicked.connect(self.rename_files)
        self.control_panel_layout.addWidget(self.rename_button)

        # Add spacer
        self.control_panel_layout.addSpacerItem(QSpacerItem(15, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Trigger panel
        self.trigger_entry = QLineEdit()
        self.trigger_entry.setPlaceholderText("Trigger")
        self.control_panel_layout.addWidget(self.trigger_entry)

        trigger_buttons_layout = QHBoxLayout()
        trigger_buttons_layout.setSpacing(15)
        self.trigger_all_button = self.create_button("Apply to All")
        self.trigger_all_button.clicked.connect(self.apply_trigger_to_all)
        trigger_buttons_layout.addWidget(self.trigger_all_button)

        self.trigger_selected_button = self.create_button("Apply to Selected")
        self.trigger_selected_button.clicked.connect(self.apply_trigger_to_selected)
        trigger_buttons_layout.addWidget(self.trigger_selected_button)

        self.control_panel_layout.addLayout(trigger_buttons_layout)

        # Add spacer
        self.control_panel_layout.addSpacerItem(QSpacerItem(15, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Find and Replace
        find_replace_layout = QHBoxLayout()
        find_replace_layout.setSpacing(15)
        self.find_entry = QLineEdit()
        self.find_entry.setPlaceholderText("Find")
        find_replace_layout.addWidget(self.find_entry)

        self.replace_entry = QLineEdit()
        self.replace_entry.setPlaceholderText("Replace")
        find_replace_layout.addWidget(self.replace_entry)

        self.control_panel_layout.addLayout(find_replace_layout)

        replace_buttons_layout = QHBoxLayout()
        replace_buttons_layout.setSpacing(15)
        self.replace_all_button = self.create_button("Replace in All")
        self.replace_all_button.clicked.connect(self.replace_in_all)
        replace_buttons_layout.addWidget(self.replace_all_button)

        self.replace_selected_button = self.create_button("Replace in Selected")
        self.replace_selected_button.clicked.connect(self.replace_in_selected)
        replace_buttons_layout.addWidget(self.replace_selected_button)

        self.control_panel_layout.addLayout(replace_buttons_layout)

        # Spacer to maintain consistent spacing
        self.control_panel_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Image preview with scroll area
        self.image_scroll_area = QScrollArea()
        self.image_scroll_area.setFrameStyle(QScrollArea.NoFrame)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.mousePressEvent = self.show_full_image
        self.image_scroll_area.setWidget(self.image_label)
        self.image_scroll_area.setWidgetResizable(True)
        self.control_panel_layout.addWidget(self.image_scroll_area, stretch=1)

        # File list (Column 2)
        self.file_list = QListWidget()
        self.file_list.itemSelectionChanged.connect(self.on_file_select)

        file_list_layout = QVBoxLayout()
        file_list_layout.setContentsMargins(10, 10, 10, 10)
        file_list_layout.setSpacing(10)
        file_list_layout.addWidget(self.file_list)

        file_list_widget = QWidget()
        file_list_widget.setLayout(file_list_layout)

        self.main_layout.addWidget(file_list_widget)

        # Text editor and save button (Column 3)
        self.editor_layout = QVBoxLayout()
        self.editor_layout.setContentsMargins(10, 10, 10, 10)
        self.editor_layout.setSpacing(10)
        self.editor_widget = QWidget()
        self.editor_widget.setLayout(self.editor_layout)
        self.main_layout.addWidget(self.editor_widget)

        self.editor = QTextEdit()
        self.editor_layout.addWidget(self.editor)

        self.save_button = self.create_button("Save")
        self.save_button.clicked.connect(self.save_file)
        self.editor_layout.addWidget(self.save_button)

        self.current_file = None

        # Set font size for the text editor
        editor_font = self.editor.font()
        editor_font.setPointSize(13)
        self.editor.setFont(editor_font)

        # Set font size for the file list
        file_list_font = self.file_list.font()
        file_list_font.setPointSize(13)
        self.file_list.setFont(file_list_font)

        # Set font size for text fields
        text_field_font = self.rename_entry.font()
        text_field_font.setPointSize(14)
        self.rename_entry.setFont(text_field_font)
        self.trigger_entry.setFont(text_field_font)
        self.find_entry.setFont(text_field_font)
        self.replace_entry.setFont(text_field_font)

        # Keyboard shortcuts
        self.setup_shortcuts()

        # Disable buttons initially
        self.rename_button.setEnabled(False)
        self.trigger_all_button.setEnabled(False)
        self.trigger_selected_button.setEnabled(False)
        self.replace_all_button.setEnabled(False)
        self.replace_selected_button.setEnabled(False)
        self.save_button.setEnabled(False)

        # Create menu bar
        self.create_menu_bar()

    def create_button(self, text):
        button = QPushButton(text)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button.setMinimumHeight(35)
        return button

    def setup_shortcuts(self):
        # Determine the platform
        if platform.system() == 'Darwin':  # macOS
            save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)  # Cmd+S on macOS
        else:  # Windows and others
            save_shortcut = QShortcut(QKeySequence.Save, self)
        
        save_shortcut.activated.connect(self.save_file)

        # Font size shortcuts
        increase_font_shortcut = QShortcut(QKeySequence.ZoomIn, self)
        decrease_font_shortcut = QShortcut(QKeySequence.ZoomOut, self)

        increase_font_shortcut.activated.connect(self.increase_font_size)
        decrease_font_shortcut.activated.connect(self.decrease_font_size)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_label.setText(folder_path)
            self.populate_file_list(folder_path)

            # Enable buttons when a folder is selected
            self.rename_button.setEnabled(True)
            self.trigger_all_button.setEnabled(True)
            self.trigger_selected_button.setEnabled(True)
            self.replace_all_button.setEnabled(True)
            self.replace_selected_button.setEnabled(True)
            self.save_button.setEnabled(True)
        else:
            # Disable buttons if no folder is selected
            self.rename_button.setEnabled(False)
            self.trigger_all_button.setEnabled(False)
            self.trigger_selected_button.setEnabled(False)
            self.replace_all_button.setEnabled(False)
            self.replace_selected_button.setEnabled(False)
            self.save_button.setEnabled(False)

    def populate_file_list(self, folder_path):
        self.file_list.clear()
        files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
        files.sort(key=lambda f: int(''.join(filter(str.isdigit, f)) or 0))
        self.file_list.addItems(files)

        # Automatically select the first file in the list
        if files:
            self.file_list.setCurrentRow(0)
            self.on_file_select()  # Load the content of the first file

    def on_file_select(self):
        selected_items = self.file_list.selectedItems()
        if selected_items:
            file_name = selected_items[0].text()
            self.current_file = os.path.join(self.folder_label.text(), file_name)
            self.load_file_content()

    def load_file_content(self):
        if self.current_file:
            with open(self.current_file, "r") as file:
                content = file.read()
                self.editor.setText(content)

            # Show image preview
            base_name, _ = os.path.splitext(os.path.basename(self.current_file))
            image_path = self.find_associated_image(base_name)
            if image_path:
                self.show_image_preview(image_path)

    def find_associated_image(self, base_name):
        folder_path = self.folder_label.text()
        for ext in ['.png', '.jpg', '.jpeg']:
            image_path = os.path.join(folder_path, base_name + ext)
            if os.path.exists(image_path):
                return image_path
        return None

    def show_image_preview(self, image_path):
        self.current_image_path = image_path  # Store the current image path
        image = QImage(image_path)
        
        # Get the width of the scroll area
        scroll_area_width = self.image_scroll_area.viewport().width()
        
        # Scale the image to fit within the scroll area width, maintaining aspect ratio
        pixmap = QPixmap.fromImage(image.scaled(scroll_area_width, scroll_area_width, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.image_label.setPixmap(pixmap)

    def show_full_image(self, event):
        if hasattr(self, 'current_image_path') and self.current_image_path:
            dialog = QDialog(self)
            dialog.setWindowTitle("Full Image View")
            layout = QVBoxLayout(dialog)

            full_image_label = QLabel(dialog)
            full_image_label.setAlignment(Qt.AlignCenter)  # Center the image

            full_pixmap = QPixmap(self.current_image_path)

            def resize_event(event):
                # Scale the image to fit within the dialog size, maintaining aspect ratio
                scaled_pixmap = full_pixmap.scaled(full_image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                full_image_label.setPixmap(scaled_pixmap)

            dialog.resizeEvent = resize_event  # Connect the resize event

            layout.addWidget(full_image_label)
            dialog.setLayout(layout)
            dialog.setMinimumSize(400, 300)  # Set a minimum size for the dialog
            dialog.showMaximized()  # Open the dialog maximized
            dialog.exec_()

    def save_file(self):
        if self.current_file:
            content = self.editor.toPlainText()
            try:
                with open(self.current_file, "w") as file:
                    file.write(content)
                QMessageBox.information(self, "Success", "File saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
        else:
            QMessageBox.warning(self, "Warning", "No file is currently open.")

    def rename_files(self):
        folder_path = self.folder_label.text()
        name_structure = self.rename_entry.text().strip()

        if not folder_path or not os.path.isdir(folder_path):
            QMessageBox.critical(self, "Error", "Please select a valid folder.")
            return

        if not name_structure:
            QMessageBox.critical(self, "Error", "Please enter a naming structure.")
            return

        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        text_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.txt')]

        if not image_files:
            QMessageBox.information(self, "Info", "No image files found in the specified folder.")
            return

        image_files.sort()

        if not name_structure.endswith('_'):
            name_structure += '_'

        total_files = len(image_files)

        for index, image_name in enumerate(image_files, start=1):
            base_name, image_ext = os.path.splitext(image_name)
            new_image_name = f"{name_structure}{index:02d}{image_ext}" if total_files < 100 else f"{name_structure}{index}{image_ext}"

            old_image_path = os.path.join(folder_path, image_name)
            new_image_path = os.path.join(folder_path, new_image_name)
            os.rename(old_image_path, new_image_path)

            corresponding_text_file = f"{base_name}.txt"
            if corresponding_text_file in text_files:
                new_text_name = f"{name_structure}{index:02d}.txt" if total_files < 100 else f"{name_structure}{index}.txt"
                old_text_path = os.path.join(folder_path, corresponding_text_file)
                new_text_path = os.path.join(folder_path, new_text_name)
                os.rename(old_text_path, new_text_path)

                # Update current file if it was renamed
                if self.current_file == old_text_path:
                    self.current_file = new_text_path

        QMessageBox.information(self, "Success", f"Renamed {total_files} image files and their associated text files.")
        self.populate_file_list(folder_path)
        self.load_file_content()  # Refresh editor

    def apply_trigger_to_all(self):
        trigger = self.trigger_entry.text().strip()
        if not trigger:
            QMessageBox.critical(self, "Error", "Please enter a trigger word.")
            return

        folder_path = self.folder_label.text()
        if not folder_path or folder_path == "No folder selected" or not os.path.isdir(folder_path):
            QMessageBox.critical(self, "Error", "Please select a valid folder.")
            return

        text_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.txt')]

        for file_name in text_files:
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r+") as file:
                content = file.read()
                file.seek(0, 0)
                file.write(f"{trigger} {content}")
                file.truncate()

        QMessageBox.information(self, "Success", "Trigger applied to all text files.")
        self.populate_file_list(folder_path)
        self.load_file_content()  # Refresh editor

    def apply_trigger_to_selected(self):
        trigger = self.trigger_entry.text().strip()
        if not trigger:
            QMessageBox.critical(self, "Error", "Please enter a trigger word.")
            return

        if not self.current_file:
            QMessageBox.critical(self, "Error", "No file selected.")
            return

        with open(self.current_file, "r+") as file:
            content = file.read()
            file.seek(0, 0)
            file.write(f"{trigger} {content}")
            file.truncate()

        QMessageBox.information(self, "Success", "Trigger applied to the selected text file.")
        self.load_file_content()  # Refresh editor

    def replace_in_selected(self):
        find_text = self.find_entry.text()
        replace_text = self.replace_entry.text()

        if not self.current_file:
            QMessageBox.critical(self, "Error", "No file selected.")
            return

        with open(self.current_file, "r+") as file:
            content = file.read()
            new_content = content.replace(find_text, replace_text)
            file.seek(0)
            file.write(new_content)
            file.truncate()

        QMessageBox.information(self, "Success", "Text replaced in the selected file.")
        self.load_file_content()  # Refresh editor

    def replace_in_all(self):
        find_text = self.find_entry.text()
        replace_text = self.replace_entry.text()

        folder_path = self.folder_label.text().strip()
        if not folder_path or folder_path == "No folder selected" or not os.path.isdir(folder_path):
            QMessageBox.critical(self, "Error", "Please select a valid folder.")
            return

        text_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.txt')]

        for file_name in text_files:
            file_path = os.path.join(folder_path, file_name)
            try:
                with open(file_path, "r+") as file:
                    content = file.read()
                    new_content = content.replace(find_text, replace_text)
                    file.seek(0)
                    file.write(new_content)
                    file.truncate()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to replace text in {file_name}: {e}")
                return  # Exit the method if an error occurs

        QMessageBox.information(self, "Success", "Text replaced in all files.")
        self.populate_file_list(folder_path)
        self.load_file_content()  # Refresh editor

    def dark_mode_stylesheet(self):
        return """
        QWidget {
            background-color: #2e2e2e;
            color: #ffffff;
        }
        QMenuBar {
            background-color: #3e3e3e;
            color: #ffffff;
        }
        QMenuBar::item {
            background-color: #3e3e3e;
            color: #ffffff;
        }
        QMenuBar::item:selected {
            background-color: #5a5a5a;  /* Darker color on hover */
            color: #ffffff;  /* Ensure text is visible */
        }
        QMenu {
            background-color: #3e3e3e;
            color: #ffffff;
        }
        QMenu::item:selected {
            background-color: #5a5a5a;  /* Darker color on hover */
            color: #ffffff;
        }
        QPushButton {
            background-color: #4a4a4a;
            color: #ffffff;
            border: none;
            border-radius: 0px;  /* Ensure square corners */
            padding: 5px;  /* Add padding for better appearance */
        }
        QPushButton:hover {
            background-color: #5a5a5a;
        }
        QLineEdit, QTextEdit {
            background-color: #3e3e3e;
            color: #ffffff;
            border: 1px solid #5a5a5a;
            border-radius: 0px;  /* Ensure square corners */
        }
        QListWidget {
            background-color: #3e3e3e;
            color: #ffffff;
        }
        QScrollArea {
            background-color: #2e2e2e;
        }
        """

    def apply_stylesheet(self):
        stylesheet = """
        QWidget {
            background-color: #f0f0f0;  /* Light mode background */
            color: #000000;  /* Light mode text color */
        }
        QMenuBar {
            background-color: #d3d3d3;
            color: #000000;
        }
        QMenuBar::item {
            background-color: #d3d3d3;
            color: #000000;
        }
        QMenuBar::item:selected {
            background-color: #505050;  /* Darker color on hover */
            color: #ffffff;  /* Ensure text is visible */
        }
        QMenu {
            background-color: #d3d3d3;  /* Menu background */
            color: #000000;
        }
        QMenu::item:selected {
            background-color: #505050;  /* Darker color on hover */
            color: #ffffff;
        }
        QPushButton {
            background-color: #d3d3d3;
            color: #000000;
            border: 1px solid #a0a0a0;  /* Add a border for consistency */
            border-radius: 0px;  /* Ensure square corners */
            padding: 5px;  /* Add padding for better appearance */
            min-height: 30px;  /* Ensure consistent height */
        }
        QPushButton:hover {
            background-color: #c0c0c0;
        }
        QLineEdit, QTextEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #c0c0c0;
            border-radius: 0px;  /* Ensure square corners */
        }
        QListWidget {
            background-color: #ffffff;
            color: #000000;
        }
        QScrollArea {
            background-color: #f0f0f0;
        }
        """
        self.setStyleSheet(stylesheet)

    def create_menu_bar(self):
        # Create a menu bar
        menu_bar = self.menuBar()

        # Create a 'File' menu
        file_menu = menu_bar.addMenu('File')

        # Add 'Save Edit to Selected File' action with shortcut
        save_action = file_menu.addAction('Save Edit to Selected File')
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)

        # Create a 'View' menu
        view_menu = menu_bar.addMenu('View')

        # Add 'Increase Font Size' action with shortcut
        increase_font_action = view_menu.addAction('Increase Font Size')
        increase_font_action.setShortcut(QKeySequence.ZoomIn)
        increase_font_action.triggered.connect(self.increase_font_size)

        # Add 'Decrease Font Size' action with shortcut
        decrease_font_action = view_menu.addAction('Decrease Font Size')
        decrease_font_action.setShortcut(QKeySequence.ZoomOut)
        decrease_font_action.triggered.connect(self.decrease_font_size)

        # Create a 'Help' menu
        help_menu = menu_bar.addMenu('Help')

        # Add 'GitHub' link
        github_action = help_menu.addAction('GitHub')
        github_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/url")))

        # Add 'Developer Website' link
        dev_website_action = help_menu.addAction('Developer Website')
        dev_website_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://renderartist.com")))

    def increase_font_size(self):
        # Increase font size for editor and file list
        self.adjust_font_size(1)

    def decrease_font_size(self):
        # Decrease font size for editor and file list
        self.adjust_font_size(-1)

    def adjust_font_size(self, delta):
        # Adjust font size for the text editor
        editor_font = self.editor.font()
        editor_font.setPointSize(editor_font.pointSize() + delta)
        self.editor.setFont(editor_font)

        # Adjust font size for the file list
        file_list_font = self.file_list.font()
        file_list_font.setPointSize(file_list_font.pointSize() + delta)
        self.file_list.setFont(file_list_font)

        # Note: Text fields are no longer adjusted

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quick Caption Editor")
    parser.add_argument('--light-mode', action='store_true', help='Enable light mode')
    args = parser.parse_args()

    # Enable high-DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Enable font antialiasing
    QApplication.setAttribute(Qt.AA_UseStyleSheetPropagationInWidgetStyles, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    window = FileEditorApp(dark_mode=not args.light_mode)  # Default to dark mode
    window.show()
    sys.exit(app.exec_())
