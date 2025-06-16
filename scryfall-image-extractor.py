import json
import requests
from PIL import Image
from io import BytesIO
import re
from pathlib import Path
import shutil
import time

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", str(filename))

def load_json_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in file: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error loading JSON: {e}")
        return None

def get_image_size_choice():
    print("\nChoose image size for all cards:")
    print("1 - Small")
    print("2 - Normal")
    print("3 - Large")
    print("4 - PNG (recomended)")
    print("5 - Art Crop")
    print("6 - Border Crop")
    
    size_mapping = {
        '1': 'small',
        '2': 'normal',
        '3': 'large',
        '4': 'png',
        '5': 'art_crop',
        '6': 'border_crop'
    }
    
    while True:
        choice = input("Enter choice (1-6): ").strip()
        if choice in size_mapping:
            return size_mapping[choice]
        print("Invalid choice")

def get_target_directory():
    while True:  
        dir_input = input("\nEnter target directory (or drag & drop): ").strip(' "\'')
        if not dir_input:
            print("Error: Please enter a directory path.")
            continue
            
        base_dir = Path(dir_input)
        if not base_dir.exists():
            print(f"Error: Directory '{base_dir}' doesn't exist.")
            continue
        
        while True:
            create_new = input("\nDo you want to create a new subfolder? (Y/N): ").strip().upper()
            if create_new in ('Y', 'N'):
                break
            print("Invalid input")

        if create_new != 'Y':
            print(f"Using existing directory: {base_dir}")
            return base_dir
            
        while True:
            folder_name = input("\nEnter new folder name: ").strip()
            if not folder_name:
                print("Error: Folder name cannot be empty.")
                continue
                
            invalid_chars = re.findall(r'[\\/*?:"<>|]', folder_name)
            if invalid_chars:
                print(f"Error: Invalid characters detected: {', '.join(set(invalid_chars))}")
                continue
            break
            
        target_dir = base_dir / folder_name
        
        if target_dir.exists():
            print(f"\nFolder '{folder_name}' already exists in:\n{base_dir}")
            while True:  
                print("\nChoose action:")
                print("1 - Overwrite existing folder")
                print("2 - Create with automatic unique name")
                print("3 - Select different parent directory")
                print("0 - Cancel operation")
                
                choice = input("Your choice: ").strip()
                
                if choice == '1':  
                    try:
                        shutil.rmtree(target_dir)
                        target_dir.mkdir()
                        print(f"\nSuccess: Overwritten existing folder\n{target_dir}")
                        return target_dir
                    except Exception as e:
                        print(f"\nError: Failed to overwrite folder\nReason: {e}")
                        break  
                        
                elif choice == '2': 
                    counter = 1
                    while True:
                        new_dir = base_dir / f"{folder_name}_{counter}"
                        if not new_dir.exists():
                            try:
                                new_dir.mkdir()
                                print(f"\nSuccess: Created new folder\n{new_dir}")
                                return new_dir
                            except Exception as e:
                                print(f"\nError: Failed to create folder\nReason: {e}")
                                break  
                        counter += 1
                elif choice == '3':  
                    break  
                elif choice == '0':  
                    return None
                else:
                    print("\nInvalid choice. Please enter 0-3.")
                    continue  
        else:  
            try:
                target_dir.mkdir()
                print(f"\nSuccess: Created new folder\n{target_dir}")
                return target_dir
            except Exception as e:
                print(f"\nError: Failed to create folder\nReason: {e}")
                continue

def get_resize_preference():
    while True:
        choice = input("\nDo you want to resize images? (Y/N): ").strip().upper()
        if choice == 'Y':
            while True:
                try:
                    width = int(input("Enter width in pixels: "))
                    height = int(input("Enter height in pixels: "))
                    if width <= 0 or height <= 0:
                        print("Dimensions can not be negative")
                        continue
                    return (width, height)
                except ValueError:
                    print("Please enter valid numbers!")
        elif choice == 'N':
            return None
        else:
            print("Invalid choice")

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
        
        print(f"Downloaded {filename.name}")
        return True
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return False

def main():
    downloaded = 0
    skipped = 0
    
    try:
        while True:
            json_path = input("\nEnter path to JSON file (or drag & drop): ").strip(' "\'')
            if not json_path:
                print("Error: Please enter a file path.")
                continue
                
            json_path = Path(json_path)
            if not json_path.exists():
                print(f"Error: File '{json_path}' doesn't exist.")
                continue
                
            data = load_json_data(json_path)
            if data is not None:
                break

        size_key = get_image_size_choice()
        resize_dimensions = get_resize_preference()
        
        output_dir = get_target_directory()
        if not output_dir:
            print("Operation canceled by user.")
            return

        total_cards = len(data)
        print(f"\nStarting download of {total_cards} cards to: {output_dir}")
        
        for i, card in enumerate(data, 1):
            try:
                card_name = card.get('name', 'unnamed')
                image_uris = card.get('image_uris', {})
                
                if not image_uris:
                    print(f"[{i}/{total_cards}] No images for card: {card_name}")
                    skipped += 1
                    continue
                
                url = image_uris.get(size_key)
                if not url:
                    print(f"[{i}/{total_cards}] No {size_key} size for card: {card_name}")
                    skipped += 1
                    continue
                
                filename = output_dir / f"{sanitize_filename(card_name)}"
                
                base_name = sanitize_filename(card_name)
                extension = '.png' if size_key == 'png' else '.jpg'
                filename = output_dir / f"{base_name}{extension}"

                counter = 1
                while filename.exists():
                    filename = output_dir / f"{base_name}_{counter}{extension}"
                    counter += 1
                
                success = download_image(url, filename, resize_dimensions)
                if success:
                    downloaded += 1
                    status = "Downloaded" + (" and resized" if resize_dimensions else "")
                    print(f"[{i}/{total_cards}] {status}: {filename.name}")
                
                time.sleep(0.1) # you can delete this but is not recomended the program may crash or worse
                
            except Exception as e:
                print(f"[{i}/{total_cards}] Error processing card: {e}")
                continue

    except KeyboardInterrupt:
        print("\nOperation canceled by user.")
    except Exception as e:
        print(f"\nCritical error: {e}")
    finally:
        if downloaded > 0 or skipped > 0:
            print(f"\nDownload complete! Downloaded: {downloaded}, Skipped: {skipped}")
            if resize_dimensions: 
                print(f"Resized to: {resize_dimensions[0]}x{resize_dimensions[1]}px")
            print(f"Location: {output_dir}")

if __name__ == "__main__":
    main()