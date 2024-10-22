# Simple Caption Editor
Efficiently manage image captions in bulk or individually. Edit captions with structural renaming, find and replace functionality, and prefix trigger word appending. Perfect for streamlining your image caption workflow.

Simple Caption Editor is written in Python using PyQt5, only one dependency. Simple, efficient and straight to the point. This GUI works on both Windows and Mac. 

Although still in active development, v1 delivers core functionality for caption editing and file management. Additional features and improvements are planned for future releases.

![Simple Caption Editor Screenshot](https://raw.githubusercontent.com/rickrender/Simple-Caption-Editor/main/Simple-Caption-Editor-Screenshot.png)

# Installation Instructions

# 1. Clone the repository
```bash
git clone https://github.com/rickrender/Simple-Caption-Editor/
```

# 2. Navigate to the directory
```bash
cd Simple-Caption-Editor
```

# 3. Create a virtual environment
```bash
python -m venv venv
```


# 4. Activate the virtual environment
```bash
venv\Scripts\activate  # Windows
```

```bash
source venv/bin/activate  # macOS
```


# 5. Install requirements
```bash
pip install -r requirements.txt
```

# 6. Run the application
```bash
python app.py
```

```bash
python app.py --light-mode
```
# Quick Tips: 
Customize your viewing experience using keyboard shortcuts or the menu options to adjust the font size in both the file list and editor views. This makes it easier to read and work with your captions at a comfortable size.

Save your changes to the current caption file using CTRL+S on Windows or CMD+S on macOS.

The rename structure feature helps organize your files with a consistent naming pattern. When your working directory contains multiple images with inconsistent names, simply enter a base name (like "Training") in the structure field. All images and their associated caption files will be automatically renamed following this pattern - for example, "Training_01.png" and "Training_01.txt". This is particularly useful when working with tools that require specific naming conventions or when you wish to organize your captioned images more systematically.
