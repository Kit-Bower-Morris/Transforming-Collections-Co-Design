from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import requests
import csv
import re
import pandas as pd 
import math


class Chrome():

    def __init__(self) -> None:
        pass

    def open_sel(self, url):
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--igcognito')
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(url)
        return 

    def scroll_down(self):
        self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        time.sleep(2)
        return

    def close_popup(self):
        time.sleep(45)
        popup = self.driver.find_element(by=By.CLASS_NAME, value = 'modal-content')
        close_popup = popup.find_element(by=By.CLASS_NAME, value = 'close')
        close_popup.click()
        return

    def load_more(self):
        load_more = self.driver.find_element(by=By.LINK_TEXT, value = 'Load more')
        load_more.click()
        return

    def create_soup(self):
        page_source = self.driver.page_source  
        self.soup = BeautifulSoup(page_source, 'html.parser') 
        return     

    def make_soup(self, url):
        page = requests.get(url)  
        soup = BeautifulSoup(page.text, 'html.parser') 
        return soup

    def find_next_artwork_label(self):
        return self.artwork.find_next_sibling()

    def find_next_artist_label(self):
        return self.artist.find_next_sibling()

    def search_artwork_page(self):
        find_main = self.soup.find(class_ = 'results-grid')
        find_artworks = find_main.find('ul')
        artwork = find_artworks.find('li')
        return artwork

    def search_artist_page(self):
        find_main = self.soup.find(class_ = 'results-grid')
        find_artist = find_main.find('ul')
        artist = find_artist.find('li')
        return artist

    def find_artwork_link(self):
        link = self.artwork.find('a')
        link = link.get('href')
        return link

    def find_artist_link(self):
        link = self.artist.find('a')
        link = link.get('href')
        return link

    def find_title(self):
        title = self.artwork_info.find(class_ = 'artwork-title')
        title = title.contents[0]
        return title
            
    def find_artist_name(self):
        find_artist = self.artwork_info.find(class_ = 'artist')
        artist = []
        single_artist = find_artist
        all_artists = find_artist.find_all('a')
        for single_artist in all_artists:
            artist_name = single_artist.contents[0]
            artist_name = re.sub(r'[\n\t]*', '',  artist_name)
            artist_name = re.sub('â', '-', artist_name)
            artist.append(artist_name)
        return artist

    def find_venue(self):
        venue = self.artwork_info.find(class_ = 'venue')
        venue = venue.contents[1]
        venue = venue.contents[0]
        venue = re.sub(r'[\n\t]*', '',  venue)
        return venue

    def find_description(self):
        main = self.artwork_info.find('main') 
        desc = main.find(class_ = 'module artwork-desc single-artwork') 
        if desc != None: 
            description = desc.find(class_ = 'desc') 
            if description != None: 
                description = description.contents[0] 
                description = re.sub(r'[\n\t]*', '', description)
            else: 
                description = None 
        return description

    def find_artwork_info(self, link):  #return artwork varibles to make a dict -> link:{artwork varibles}
        #make a set of info_types
        info_types_set = set(self.info_types)
        #artwork_variables is a dict -> label:value
        artwork_variables = {}
        #make soup for artwork page
        self.artwork_info = self.make_soup(link)
        
        #find title
        artwork_variables['Title'] = self.find_title()
        
        #find artist
        artwork_variables['Artist'] = self.find_artist_name()
        
        #find venue
        artwork_variables['Venue'] = self.find_venue()            

        #find description
        artwork_variables['Description'] = self.find_description()

        #find image source
        image_search = self.artwork.find('img')
        image_source = image_search.get('src')
        artwork_variables['Image Source'] = image_source

        #find other details
        artwork_details = self.artwork_info.find(class_ = 'artwork-details')
        artwork_details = artwork_details.find_all(class_ = 'masonry-item')
        for detail in artwork_details:
            further_detail = detail.contents[1]
            info = further_detail.contents[0]
            value_detail = detail.contents[3]
            value = value_detail.contents[0]
            if info in info_types_set:
                None
            else:
                self.info_types.append(info)
                info_types_set.add(info)
            artwork_variables[str(info)] = value
        
        return artwork_variables

    def find_last_id(self):
        self.id = self.artist.get('id')
        print('id = ', self.id)
        return

    def find_next_entry(self):
        self.artist = self.soup.find('li', id = self.id)
        print('here')
        print(self.artist)
        self.artist = self.find_next_artist_label()
        print(self.artist)
        return 

    def open_csv(self):
        f = open('practice2.csv', 'w', encoding= 'utf8', newline='') 
        self.writer = csv.writer(f) 
        self.writer.writerow(self.info_types)
        return
    
    def write_row(self, data):
        self.writer.writerow(data)
        return

    def order_info(self, artwork_variables):
        all_data = []
        for info in self.info_types:
            if info in artwork_variables.keys():
                all_data.append(artwork_variables[info])
            else:
                all_data.append(None)
        return all_data

    def count_artwork(self):
        amount = self.artist.find(class_ = 'count')
        count = amount.contents[0] 
        temp_count = '' 
        for i in count: 
            if i.isdigit(): 
                temp_count += i 
        count = int(temp_count) 
        return count

    def find_artworks(self, num, artist_link):
        soup = self.make_soup(artist_link)
        if num > 7:
            #make soup for the artist profile page
            more_item = soup.find(class_ = 'item more')
            more_item = more_item.find('a')
            all_art_by_artist_link = more_item.get('href')
            page = str(math.ceil(num/20))
            all_art_by_artist_link = all_art_by_artist_link + '/page/' + page
            soup = self.make_soup(all_art_by_artist_link)
            whole = soup.find(class_ = 'listing-grid')
            self.artwork = whole.find('li')
            for i in range(num):
                link = self.find_artwork_link()
                print(link)
                artwork_variables = self.find_artwork_info(link)
                all_data = self.order_info(artwork_variables)
                self.write_row(all_data)
                if i != (num-1):
                    self.artwork = self.find_next_artwork_label()

        elif num != 0:
            soup = self.make_soup(artist_link) 
            whole = soup.find(class_="module related-artworks related-masonry module-bottom-spacing")
            whole = whole.find(class_ = 'wrap') 
            self.artwork = whole.find('li')
            for i in range(num): 
                link = self.find_artwork_link()
                print(link)
                artwork_variables = self.find_artwork_info(link)
                all_data = self.order_info(artwork_variables)
                self.write_row(all_data)
                if i != (num-1):
                    self.artwork = self.find_next_artwork_label()
        else:
            return

    def run(self, url):
        self.info_types = ['Title','Artist','Image Source','Venue','Description','Date','Medium','Measurements','Accession number','Acquisition method','Work type','Owner','Custodian','Work status',
        'Unveiling date','Access','Access note','Signature/marks description','Inscription description','Listing status','Listing date','Installation start date','Installation end date']
        self.open_csv()
        self.open_sel(url)
        self.create_soup()
        self.artist = self.search_artist_page()
        #self.artwork = self.search_artwork_page()
        self.close_popup()
        total = 9999
        next_pages = 20
        for _ in range(50):
            for _ in range(10):
                links = []
                for row in range(next_pages):
                    total -= 1
                    artist_link = self.find_artist_link()
                    links.append(artist_link)
                    amount_art = self.count_artwork()
                    self.find_artworks(amount_art, artist_link)
                    if row != (19):
                        self.artist = self.find_next_artist_label()
                    print(total)
                self.find_last_id()
                self.scroll_down()
                self.create_soup()
                self.find_next_entry()
                print(links)            
            self.scroll_down()
            self.load_more()
        self.driver.close()








env = Chrome()
env.run('https://artuk.org/discover/artists/view_as/grid/sort_by/name.keyword/order/asc/page/1')

'https://artuk.org/discover/artworks/view_as/grid/search/date-from:1970/sort_by/date_earliest/order/desc/page/1'
'https://artuk.org/discover/artworks/view_as/grid/search/date-to:1969--date-from:1915/sort_by/date_earliest/order/desc/page/1'
'https://artuk.org/discover/artworks/view_as/grid/search/date-from:1850--date-to:1914/sort_by/date_earliest/order/desc/page/1'
'https://artuk.org/discover/artworks/view_as/grid/search/date-from:1750--date-to:1849/sort_by/date_earliest/order/desc/page/1'
'https://artuk.org/discover/artworks/view_as/grid/search/date-to:1750/sort_by/date_earliest/order/desc/page/1'