# MTG Card Image Downloader

A GUI-based Python tool that downloads Magic: The Gathering (MTG) card images from a JSON file by reading their `image_uris`. It supports selecting image size and optional image resizing.

---

## 🧠 What does this script do?

- Loads a JSON file containing MTG card data.
- Allows the user to choose a target directory to save images.
- Extracts image URLs from the `image_uris` key (or from `card_faces` for double-faced cards).
- Lets the user choose a preferred image size (`small`, `normal`, `large`, `png`, `art_crop`, or `border_crop`).
- Optionally resizes the images to custom dimensions.
- Automatically avoids filename conflicts by appending counters.
- Saves the downloaded images in `.png` or `.jpg` format depending on the original image mode.

---

## 📦 Requirements

Make sure you have the following Python packages installed:

```bash
pip install requests Pillow
```
```bash
pip install tkinter
```
```bash
pip install pathlib
```
*These are required in addition to Python's standard libraries (json, tkinter, re, pathlib, etc.).*

---

## 🚀 Usage

1. Run the script:

```bash
python scryfall-image-extractor.py
```
2. A file dialog will open. Select your JSON file with MTG card data.

3. Select a directory where you want to save the images.

4. Choose the desired image size from a list.

5. Optionally, choose whether to resize images and enter width and height if desired.

6. The script will download the images and show a final summary.

---

## 🛠 Features  

- Friendly GUI using `tkinter`

- Supports multiple image formats and sizes

- Image resizing with anti-aliasing

- Automatic filename sanitization

- Progress reporting and error handling

---

## 🧹Notes

- Filenames are sanitized to avoid invalid characters.

- Duplicate filenames are resolved by appending `_1`, `_2`, etc.

- If the image mode is `RGBA`, it's saved as `.png`; otherwise, `.jpg`.
   
