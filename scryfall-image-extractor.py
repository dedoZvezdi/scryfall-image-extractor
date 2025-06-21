import json
import requests
from PIL import Image
from io import BytesIO
import re
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

def select_json_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select JSON File",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    return Path(file_path) if file_path else None

def select_target_directory():
    root = tk.Tk()
    root.withdraw()
    dir_path = filedialog.askdirectory(title="Select Target Directory")
    return Path(dir_path) if dir_path else None

def ask_image_size():
    options = [
        "1 - Small",
        "2 - Normal",
        "3 - Large",
        "4 - PNG (recommended)",
        "5 - Art Crop",
        "6 - Border Crop"
    ]
    size_mapping = {
        1: 'small',
        2: 'normal',
        3: 'large',
        4: 'png',
        5: 'art_crop',
        6: 'border_crop'
    }
    root = tk.Tk()
    root.withdraw()
    choice = simpledialog.askinteger(
        "Image Size",
        "Choose image size for all cards:\n" + "\n".join(options),
        minvalue=1,
        maxvalue=6
    )
    return size_mapping.get(choice)

def ask_resize():
    root = tk.Tk()
    root.withdraw()
    resize = messagebox.askyesno("Resize Images", "Do you want to resize images?")
    if not resize:
        return None
    try:
        width = simpledialog.askinteger("Resize Width", "Enter width in pixels:", minvalue=1)
        height = simpledialog.askinteger("Resize Height", "Enter height in pixels:", minvalue=1)
        if width and height:
            return (width, height)
    except Exception:
        return None
    return None

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", str(filename))

def load_json_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        messagebox.showerror("Error", f"Error loading JSON: {e}")
        return None

def download_image(url, filename, size=None):
    try:
        response = requests.get(url)
        response.raise_for_status()

        with Image.open(BytesIO(response.content)) as img:
            if size:
                img = img.resize(size, Image.Resampling.LANCZOS)

            if img.mode == 'RGBA':
                filename = filename.with_suffix('.png')
                img.save(filename, format='PNG', optimize=True)
            else:
                filename = filename.with_suffix('.jpg')
                img.save(filename, format='JPEG', quality=90)

        return True
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False

def main():
    json_path = select_json_file()
    if not json_path or not json_path.exists():
        messagebox.showinfo("Cancelled", "No file selected or file not found.")
        return

    target_dir = select_target_directory()
    if not target_dir or not target_dir.exists():
        messagebox.showinfo("Cancelled", "No directory selected or does not exist.")
        return

    data = load_json_data(json_path)
    if not data:
        return

    size_key = ask_image_size()
    if not size_key:
        messagebox.showinfo("Cancelled", "Image size not selected.")
        return

    resize_dimensions = ask_resize()

    downloaded, skipped = 0, 0
    total_cards = len(data)
    print(f"\nStarting download of {total_cards} cards to: {target_dir}")

    for i, card in enumerate(data, 1):
        try:
            image_uris = card.get("image_uris")
            if not image_uris and "card_faces" in card:
                image_uris = card["card_faces"][0].get("image_uris")

            if not image_uris:
                print(f"[{i}/{total_cards}] No image found.")
                skipped += 1
                continue

            url = image_uris.get(size_key)
            if not url:
                print(f"[{i}/{total_cards}] No {size_key} image.")
                skipped += 1
                continue

            card_id = card.get("id", f"card_{i}")
            base_name = sanitize_filename(card_id)
            extension = '.png' if size_key == 'png' else '.jpg'
            filename = target_dir / f"{base_name}{extension}"

            counter = 1
            while filename.exists():
                filename = target_dir / f"{base_name}_{counter}{extension}"
                counter += 1

            success = download_image(url, filename, resize_dimensions)
            if success:
                downloaded += 1
                print(f"[{i}/{total_cards}] Downloaded: {filename.name}")
            else:
                skipped += 1

        except Exception as e:
            print(f"[{i}/{total_cards}] Error: {e}")
            skipped += 1
            continue

    summary = (
        f"\u2705 Done!\nDownloaded: {downloaded}\nSkipped: {skipped}"
        + (f"\nResized to: {resize_dimensions[0]}x{resize_dimensions[1]}px" if resize_dimensions else "")
        + f"\nSaved to: {target_dir}"
    )
    messagebox.showinfo("Download Summary", summary)

if __name__ == "__main__":
    main()