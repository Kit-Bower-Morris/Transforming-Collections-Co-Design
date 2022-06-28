import requests
import io
from PIL import Image
import pandas as pd
import re

def download_image(url, file_name):
    try:
        image_content = requests.get(url).content
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)
        
        with open(file_name, 'wb') as f:
            image.save(f, 'JPEG')
    except Exception as e:
        print('Failed', file_name, '\n', e)


df = pd.read_csv('British Artists.csv')

bad = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
file_names = []
number = 2
for (title, artist, source) in zip(df['Title'], df['Artist'], df['Image Source']): 
    if number >= 105874:
    
        file_name = title + ', ' + artist + '.jpg'
        file_name = re.sub(r'[\<\>\:\"\/\\\|\?\*] *', '',  file_name)

        if source == 'https://artuk.org/skins/artuk/img/placeholder-w250.png' or source == 'https://artuk.org/skins/artuk/img/placeholder-artwork-listing.png':
            continue
        else:
            download_image(source, file_name)
            print(file_name)
    number += 1
    print(number)

    
105874
