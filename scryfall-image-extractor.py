import json
import requests  # type: ignore | For somereason is giving me warning after I already have it installed but is working perfectly fine
import os
from pathlib import Path


file_path = r'..\path' # Here use the path for the json file

try:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    print("Data loaded successfully")
except FileNotFoundError:
    print("File not found")
except UnicodeDecodeError as e:
    print(f"Error decoding file: {e}")

# All image URLs
def extract_image_urls(card):
    return card.get('image_uris', {})

all_image_urls = []
for card in data:
    urls = extract_image_urls(card)
    if urls:
        for size, url in urls.items():
            all_image_urls.append((size, url))

'''
# Only Normal image URLs | the sizes are small, normal, large, png, art_crop, border_crop change it as you like it
def extract_normal_image_url(card):
    return card['image_uris'].get('normal')

normal_image_urls = []
for card in data:
    if 'image_uris' in card:
        url = extract_normal_image_url(card)
        if url:
            normal_image_urls.append(url)
'''

def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download {filename}")


pictures_path = Path.home() / '..\path' #This is the directory that will be saved the folder
output_dir = pictures_path / 'Name' # This is the folder name
os.makedirs(output_dir, exist_ok=True)


for i, url in enumerate(all_image_urls): # When you want to download only specific size change 'all_image_urls' to corresponding name
    filename = output_dir / f"name_{i}.jpg" #This is the the name of every card followed by number starting from 0
    download_image(url, filename)
