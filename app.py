import sys
import argparse
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QWidget, QPushButton, QLineEdit, QListWidget, QTextEdit, QMessageBox, QDialog, QScrollArea, QShortcut, QAction, QInputDialog
from PyQt5.QtGui import QImage, QPixmap, QKeySequence, QDesktopServices, QTextCursor, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QUrl
import os
import platform
from PIL import Image  # Add this import at the top of your file

class FileEditorApp(QMainWindow):
    def __init__(self, dark_mode=False):
        super().__init__()
        self.setWindowTitle("Simple Caption Editor")
        self.setGeometry(100, 100, 1200, 800)

        # Status bar for notifications
        self.statusBar = self.statusBar()

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

        # Control panel and file list (Column 1)
        control_panel_widget = QWidget()
        control_panel_widget.setFixedWidth(350)
        self.control_panel_layout = QVBoxLayout()
        
        # Create a container widget for the folder controls
        folder_widget = QWidget()
        folder_layout = QHBoxLayout(folder_widget)
        folder_layout.setContentsMargins(0, 0, 0, 0)

        self.folder_button = self.create_button("Select Folder")
        self.folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_button)

        # Initialize refresh button
        self.refresh_button = self.create_button("🔄")
        self.refresh_button.setFixedSize(30, 30)
        self.refresh_button.clicked.connect(self.refresh_folder)
        self.refresh_button.hide()  # Initially hidden
        folder_layout.addWidget(self.refresh_button)

        # Add the folder widget to the control panel layout
        self.control_panel_layout.addWidget(folder_widget)

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

        # Add spacer
        self.control_panel_layout.addSpacerItem(QSpacerItem(15, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Filter input
        self.filter_entry = QLineEdit()
        self.filter_entry.setPlaceholderText("Search Captions")
        self.filter_entry.textChanged.connect(self.filter_file_list)
        self.control_panel_layout.addWidget(self.filter_entry)

        # File list
        self.file_list = QListWidget()
        self.file_list.itemSelectionChanged.connect(self.on_file_select)
        self.control_panel_layout.addWidget(self.file_list, stretch=1)
        
        # Set the layout for the control panel widget
        control_panel_widget.setLayout(self.control_panel_layout)
        
        # Add the control panel widget to the main layout
        self.main_layout.addWidget(control_panel_widget)

        # Image preview (Column 2)
        self.image_layout = QVBoxLayout()
        self.image_layout.setContentsMargins(10, 10, 10, 10)
        self.image_layout.setSpacing(10)

        self.image_scroll_area = QScrollArea()
        self.image_scroll_area.setFrameStyle(QScrollArea.NoFrame)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.mousePressEvent = self.show_full_image
        self.image_scroll_area.setWidget(self.image_label)
        self.image_scroll_area.setWidgetResizable(True)
        self.image_layout.addWidget(self.image_scroll_area, stretch=1)

        self.main_layout.addLayout(self.image_layout)

        # Text editor (Column 3)
        self.editor_layout = QVBoxLayout()
        self.editor_layout.setContentsMargins(10, 10, 10, 10)
        self.editor_layout.setSpacing(10)

        self.editor = QTextEdit()
        self.editor.textChanged.connect(self.mark_unsaved_changes)
        self.editor_layout.addWidget(self.editor)

        self.save_button = self.create_button("Save")
        self.save_button.clicked.connect(self.save_file)
        self.editor_layout.addWidget(self.save_button)

        self.main_layout.addLayout(self.editor_layout)

        self.current_file = None
        self.unsaved_changes = False

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
        self.filter_entry.setFont(text_field_font)

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
        # Only set up font size shortcuts
        increase_font_shortcut = QShortcut(QKeySequence("Ctrl+="), self)
        decrease_font_shortcut = QShortcut(QKeySequence("Ctrl+_"), self)

        increase_font_shortcut.activated.connect(self.increase_font_size)
        decrease_font_shortcut.activated.connect(self.decrease_font_size)

        # Switch focus between file list and editor
        switch_focus = QShortcut(QKeySequence("Ctrl+E"), self)
        switch_focus.activated.connect(self.toggle_focus)

    def toggle_focus(self):
        if self.editor.hasFocus():
            self.file_list.setFocus()
        else:
            self.editor.setFocus()
            # Move the cursor to the end of the text
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.editor.setTextCursor(cursor)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_label.setText(folder_path)
            self.create_missing_text_files(folder_path)
            self.check_and_offer_image_conversion(folder_path)
            self.populate_file_list(folder_path)

            # Show refresh button when a folder is selected
            self.refresh_button.show()

            # Enable buttons when a folder is selected
            self.rename_button.setEnabled(True)
            self.trigger_all_button.setEnabled(True)
            self.trigger_selected_button.setEnabled(True)
            self.replace_all_button.setEnabled(True)
            self.replace_selected_button.setEnabled(True)
            self.save_button.setEnabled(True)
        else:
            # Hide refresh button if no folder is selected
            self.refresh_button.hide()

            # Disable buttons if no folder is selected
            self.rename_button.setEnabled(False)
            self.trigger_all_button.setEnabled(False)
            self.trigger_selected_button.setEnabled(False)
            self.replace_all_button.setEnabled(False)
            self.replace_selected_button.setEnabled(False)
            self.save_button.setEnabled(False)

    def create_missing_text_files(self, folder_path):
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        text_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.txt')]

        for image_file in image_files:
            base_name, _ = os.path.splitext(image_file)
            corresponding_text_file = f"{base_name}.txt"
            if corresponding_text_file not in text_files:
                text_file_path = os.path.join(folder_path, corresponding_text_file)
                with open(text_file_path, 'w') as file:
                    file.write("")  # Create an empty text file
                self.statusBar.showMessage(f"Created missing text file: {corresponding_text_file}", 3000)

    def check_and_offer_image_conversion(self, folder_path):
        unsupported_formats = ['.bmp', '.webp']
        found_formats = {ext for ext in unsupported_formats if any(f.lower().endswith(ext) for f in os.listdir(folder_path))}

        if found_formats:
            found_formats_str = ', '.join(found_formats)
            supported_formats_str = ', '.join(['.jpeg', '.png'])
            message = (f"Found unsupported image formats: {found_formats_str}\n"
                       f"This app only supports .jpeg and .png\n"
                       f"Would you like to convert to {supported_formats_str}?")
            
            reply = QMessageBox.question(self, 'Convert Images', message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.convert_images(folder_path, [f for f in os.listdir(folder_path) if any(f.lower().endswith(ext) for ext in found_formats)])

    def convert_images(self, folder_path, image_files):
        format_choice, ok = QInputDialog.getItem(self, "Select Format", "Convert images to:", [".jpeg", ".png"], 0, False)
        if ok:
            successful_conversions = []
            for image_file in image_files:
                image_path = os.path.join(folder_path, image_file)
                base_name, _ = os.path.splitext(image_file)
                new_image_path = os.path.join(folder_path, base_name + format_choice.lower())

                try:
                    print(f"Attempting to convert {image_path} to {new_image_path}")  # Debugging line
                    # Use Pillow to open and convert the image
                    with Image.open(image_path) as img:
                        img = img.convert("RGB")  # Ensure the image is in RGB mode
                        save_format = 'JPEG' if format_choice.lower() == '.jpeg' else 'PNG'
                        img.save(new_image_path, save_format)
                    
                    os.remove(image_path)  # Remove the original file if conversion is successful
                    successful_conversions.append(new_image_path)
                    self.statusBar.showMessage(f"Converted {image_file} to {format_choice.lower()}", 3000)
                except FileNotFoundError:
                    QMessageBox.critical(self, "Error", f"File not found: {image_file}")
                except OSError as e:
                    QMessageBox.critical(self, "Error", f"OS error: {e}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to convert {image_file}: {e}")
                    print(f"Failed to convert {image_file}: {e}")  # Print detailed error

            # Only update the file list if there were successful conversions
            if successful_conversions:
                self.populate_file_list(folder_path)
                self.create_missing_text_files(folder_path)  # Ensure text files are created for new images

    def populate_file_list(self, folder_path):
        self.file_list.clear()
        files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
        
        # Sort files alphabetically
        files.sort()  # This will sort the files in alphabetical order
        
        self.file_list.addItems(files)

        # Automatically select the first file in the list
        if files:
            self.file_list.setCurrentRow(0)
            self.on_file_select()  # Load the content of the first file

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

        # Store the pixmap for click detection
        self.current_pixmap = pixmap

    def show_full_image(self, event):
        if hasattr(self, 'current_pixmap') and self.current_pixmap:
            # Get the actual size of the displayed image
            pixmap_rect = self.image_label.pixmap().rect()
            pixmap_rect.moveCenter(self.image_label.rect().center())

            # Check if the click is within the image bounds
            if pixmap_rect.contains(event.pos()):
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

    def mark_unsaved_changes(self):
        self.unsaved_changes = True

    def save_file(self):
        if self.current_file:
            content = self.editor.toPlainText()
            try:
                with open(self.current_file, "w") as file:
                    file.write(content)
                self.statusBar.showMessage("File saved successfully.", 3000)
                self.unsaved_changes = False
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
        else:
            QMessageBox.warning(self, "Warning", "No file is currently open.")

    def load_file_content(self):
        if self.current_file:
            with open(self.current_file, "r") as file:
                content = file.read()
                self.editor.setText(content)
            
            # Reset unsaved changes flag after loading content
            self.unsaved_changes = False

            # Show image preview
            base_name, _ = os.path.splitext(os.path.basename(self.current_file))
            image_path = self.find_associated_image(base_name)
            if image_path:
                self.show_image_preview(image_path)

    def rename_files(self):
        folder_path = self.folder_label.text()
        name_structure = self.rename_entry.text().strip()

        if not folder_path or not os.path.isdir(folder_path):
            self.statusBar.showMessage("Please select a valid folder.", 3000)
            return

        if not name_structure:
            self.statusBar.showMessage("Please enter a naming structure.", 3000)
            return

        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        text_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.txt')]

        if not image_files:
            self.statusBar.showMessage("No image files found in the specified folder.", 3000)
            return

        image_files.sort()

        if not name_structure.endswith('_'):
            name_structure += '_'

        total_files = len(image_files)
        index_format = f"{{:0{len(str(total_files))}d}}"

        # Step 1: Rename to temporary names
        temp_mappings = []  # Store original and temp names
        for index, image_name in enumerate(image_files, start=1):
            base_name, image_ext = os.path.splitext(image_name)
            temp_image_name = f"temp_{index_format.format(index)}{image_ext}"
            
            old_image_path = os.path.join(folder_path, image_name)
            temp_image_path = os.path.join(folder_path, temp_image_name)
            os.rename(old_image_path, temp_image_path)
            
            corresponding_text_file = f"{base_name}.txt"
            if corresponding_text_file in text_files:
                temp_text_name = f"temp_{index_format.format(index)}.txt"
                old_text_path = os.path.join(folder_path, corresponding_text_file)
                temp_text_path = os.path.join(folder_path, temp_text_name)
                os.rename(old_text_path, temp_text_path)
                
                # Store the mapping for both image and text files
                temp_mappings.append((temp_image_name, temp_text_name, index))

        # Step 2: Rename from temporary names to final names
        for temp_image_name, temp_text_name, index in temp_mappings:
            # Rename image file
            final_image_name = f"{name_structure}{index_format.format(index)}{os.path.splitext(temp_image_name)[1]}"
            temp_image_path = os.path.join(folder_path, temp_image_name)
            final_image_path = os.path.join(folder_path, final_image_name)
            os.rename(temp_image_path, final_image_path)

            # Rename text file
            final_text_name = f"{name_structure}{index_format.format(index)}.txt"
            temp_text_path = os.path.join(folder_path, temp_text_name)
            final_text_path = os.path.join(folder_path, final_text_name)
            os.rename(temp_text_path, final_text_path)

            # Update current file if it was renamed
            if self.current_file == temp_text_path:
                self.current_file = final_text_path

        self.statusBar.showMessage(f"Renamed {total_files} image files and their associated text files.", 3000)
        self.populate_file_list(folder_path)
        self.load_file_content()

    def apply_trigger_to_all(self):
        self.unsaved_changes = False  # Temporarily disable unsaved changes check
        trigger = self.trigger_entry.text().strip()
        if not trigger:
            self.statusBar.showMessage("Please enter a trigger word.", 3000)
            return

        folder_path = self.folder_label.text()
        if not folder_path or folder_path == "No folder selected" or not os.path.isdir(folder_path):
            self.statusBar.showMessage("Please select a valid folder.", 3000)
            return

        text_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.txt')]

        for file_name in text_files:
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r+") as file:
                content = file.read()
                file.seek(0, 0)
                file.write(f"{trigger} {content}")
                file.truncate()

        self.statusBar.showMessage(f"Applied trigger '{trigger}' to all text files.", 3000)
        self.populate_file_list(folder_path)
        self.load_file_content()  # Refresh editor

    def apply_trigger_to_selected(self):
        self.unsaved_changes = False  # Temporarily disable unsaved changes check
        trigger = self.trigger_entry.text().strip()
        if not trigger:
            self.statusBar.showMessage("Please enter a trigger word.", 3000)
            return

        if not self.current_file:
            self.statusBar.showMessage("No file selected.", 3000)
            return

        with open(self.current_file, "r+") as file:
            content = file.read()
            file.seek(0, 0)
            file.write(f"{trigger} {content}")
            file.truncate()

        self.statusBar.showMessage(f"Applied trigger '{trigger}' to the selected text file.", 3000)
        self.load_file_content()  # Refresh editor

    def replace_in_selected(self):
        self.unsaved_changes = False  # Temporarily disable unsaved changes check
        find_text = self.find_entry.text()
        replace_text = self.replace_entry.text()

        if not self.current_file:
            self.statusBar.showMessage("No file selected.", 3000)
            return

        with open(self.current_file, "r+") as file:
            content = file.read()
            new_content = content.replace(find_text, replace_text)
            file.seek(0)
            file.write(new_content)
            file.truncate()

        self.statusBar.showMessage(f"Replaced '{find_text}' with '{replace_text}' in the selected file.", 3000)
        self.load_file_content()  # Refresh editor

    def replace_in_all(self):
        self.unsaved_changes = False  # Temporarily disable unsaved changes check
        find_text = self.find_entry.text()
        replace_text = self.replace_entry.text()

        folder_path = self.folder_label.text().strip()
        if not folder_path or folder_path == "No folder selected" or not os.path.isdir(folder_path):
            self.statusBar.showMessage("Please select a valid folder.", 2000)
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
                self.statusBar.showMessage(f"Failed to replace text in {file_name}: {e}", 3000)
                return  # Exit the method if an error occurs

        self.statusBar.showMessage(f"Replaced '{find_text}' with '{replace_text}' in all files.", 3000)
        self.populate_file_list(folder_path)
        self.load_file_content()  # Refresh editor

    def filter_file_list(self):
        filter_text = self.filter_entry.text().lower()
        folder_path = self.folder_label.text()

        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            file_name = item.text()
            file_path = os.path.join(folder_path, file_name)

            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    content = file.read().lower()
                    item.setHidden(filter_text not in content)

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

        # Create save action
        self.save_action = file_menu.addAction('Save Edit to Selected File')
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.triggered.connect(self.save_file)

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

        # Add 'Shortcuts' action
        shortcuts_action = help_menu.addAction('Shortcuts')
        shortcuts_action.triggered.connect(self.show_shortcuts)

        # Add 'Developer Website' link
        dev_website_action = help_menu.addAction('Developer')
        dev_website_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://renderartist.com")))

        # Add 'GitHub' link
        github_action = help_menu.addAction('GitHub')
        github_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/rickrender/Simple-Caption-Editor")))

    def show_shortcuts(self):
        os_name = platform.system()
        if os_name == 'Darwin':  # macOS
            save_shortcut = "Cmd+S"
            increase_font = "Cmd++"
            decrease_font = "Cmd+-"
            toggle_focus = "Cmd+E"
        else:  # Windows and Linux
            save_shortcut = "Ctrl+S"
            increase_font = "Ctrl++"
            decrease_font = "Ctrl+-"
            toggle_focus = "Ctrl+E"

        shortcuts_text = f"""
        <b>Keyboard Shortcuts:</b><br>
        <ul style="list-style-type:none;">
            <li style="margin-bottom: 8px;">🔄 <b>Toggle (File List/Editor):</b> {toggle_focus}</li>
            <li style="margin-bottom: 8px;">🔍 <b>Increase Font Size:</b> {increase_font}</li>
            <li style="margin-bottom: 8px;">🔎 <b>Decrease Font Size:</b> {decrease_font}</li>
            <li style="margin-bottom: 8px;">💾 <b>Save:</b> {save_shortcut}</li>
        </ul>
        """
        QMessageBox.information(self, "Shortcuts", shortcuts_text)

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

    def on_file_select(self):
        if self.unsaved_changes:
            reply = QMessageBox.question(self, 'Unsaved Changes',
                                         "You have unsaved changes. Are you sure you want to switch files?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        selected_items = self.file_list.selectedItems()
        if selected_items:
            file_name = selected_items[0].text()
            self.current_file = os.path.join(self.folder_label.text(), file_name)
            self.load_file_content()

    def refresh_folder(self):
        folder_path = self.folder_label.text()
        if folder_path and os.path.isdir(folder_path):
            self.check_and_offer_image_conversion(folder_path)  # Check for unsupported formats
            self.populate_file_list(folder_path)  # Refresh the file list after conversion
            self.statusBar.showMessage("Folder refreshed.", 3000)

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
