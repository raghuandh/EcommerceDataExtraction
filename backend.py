# Importing Modules
import requests
import seaborn as sns 
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import streamlit as st
import pandas as pd
from IPython.core.display import HTML, display
from time import sleep
from selenium import webdriver
import pyshorteners as sh
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
option = Options()
option.add_argument('--headless')
# Initializing variable to shorten URL's
s = sh.Shortener()
# Creating Front end using StreamLit
st.title("E-commerce website Data Extraction")
st.write("See all the products of websites like Amazon, Flipkart in one click")
platform=st.selectbox('Choose Platform',['','Flipkart','Amazon'])
product_name = st.text_input("Enter Product Name")
button = st.button("Submit")

def flipkart():
    from bs4 import BeautifulSoup
    feature_list = []
    price_list = []
    rating_list = []
    links = []
    prod_links = []
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=option)
    def func(link):
        driver.get(link)
        soup = BeautifulSoup(driver.page_source,'html.parser')
        features = soup.find_all('div','_4rR01T')
        for i in features:
            feature_list.append(i.text.strip())
        prices = soup.find_all('div','_30jeq3 _1_WHN1')
        for i in prices:
            price_list.append(i.text.strip())
        ratings = soup.find_all('div', class_ = '_3LWZlK')
        for i in ratings:
            rating_list.append(i.text.strip())
        images = soup.find_all('div',class_='CXW8mj')
        for image in images:
            img_tag = image.find('img')
            img_src = img_tag['src']
            links.append(img_src)
        prod_link = soup.find_all('a', class_='_1fQZEK')
        for link in prod_link:
            l = "https://www.flipkart.com"+link.get('href')
            prod_links.append(l)
    for i in range(0,1):
        url = f"https://www.flipkart.com/search?q={product_name}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off={i}"
        func(url)
    for i in range(len(prod_links)):
        prod_links[i] = s.tinyurl.short(prod_links[i])
    return feature_list, price_list, rating_list, prod_links,links

def amazon():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=option)
    driver.get(f"https://www.amazon.in/s?k={product_name}&crid=1BELPFOAVWWE5&sprefix=laptops%2Caps%2C210&ref=nb_sb_noss_1")
    soup = BeautifulSoup(driver.page_source,'html.parser')
    container = soup.select('.s-card-container')
    name_list = []
    prices = []
    links = []
    prod_links = []
    for i in container:
        name = i.find('span','a-size-medium a-color-base a-text-normal')
        price = i.find('span','a-price-whole')
        imgs = i.find('div',"a-section aok-relative s-image-fixed-height")
        prod_link = i.find('a',"a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")
        name_list.append(name)
        prices.append(price)
        links.append(imgs)
        prod_links.append(prod_link)
    def remove_none(lst):
        lsts = []
        for i in lst:
            if i is None:
                continue
            else:
                lsts.append(i.text.strip())
        return lsts
    prod_names = remove_none(name_list)
    prices_list = remove_none(prices)
    links_list = []
    for i in links:
        if i is None:
            continue
        else:
            img_tag = i.find('img')
            img_src = img_tag['src']
            links_list.append(img_src)
    products_link = []
    for i in prod_links:
        if i is None:
            continue
        else:
            x = "https://www.amazon.in" + i.get('href')
            products_link.append(x)
    for i in range(len(products_link)):
        products_link[i] = s.tinyurl.short(products_link[i])   
    return prod_names, prices_list, links_list,products_link
def main():
    if button:
        if platform=="Flipkart":
        
            features, price, rating, link, links = flipkart()
            mini = min(len(features), len(price), len(rating), len(links))
            items = {'Product Details':features[:mini], 'Price':price[:mini], 'Rating':rating[:mini],\
                'Link':link[:mini]}
            def pri(price_list, rating_list):
                #rating_list = rating[:len(price_list)]
                rating_list = [float(rating) for rating in rating_list]
                price_list = [float(value.replace('₹', '').replace(',', '')) for value in price]
                return price_list,rating_list
            price_list = price
            rating_list = rating[:len(price_list)]
            price, rating_list = pri(price_list, rating_list)
            df = pd.DataFrame({'price_list': price, 'rating_list': rating_list})
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
            ax1.set_xlabel('Prices')
            ax1.set_ylabel('Prices for each bar')
            ax1.set_title('Analysis of prices')
            sns.histplot(price,kde=True, ax=ax1, color='red')
            sns.histplot(rating_list,kde=True, ax=ax2, color='green')
            ax2.set_xlabel('Ratings')
            ax2.set_ylabel('Ratings for each bar')
            ax2.set_title('Analysis of ratings')
            plt.tight_layout()
            
            st.pyplot(fig)
            print(len(price_list),len(rating_list))
            df = pd.DataFrame(items)
            df['Product_Image'] = links[:mini]
            def to_img_tag(path):
                return '<img src="'+ path + '" width="100" >'
            st.write(HTML(df.to_html(escape=False,formatters=dict(Product_Image=to_img_tag))))
        elif platform=='Amazon':
            l1,l2,l3,l4 = amazon()
            items = {'Product Name':l1[:15],'Price':l2[:15],'ProductLink':l4[:15]}
            df = pd.DataFrame(items)
            df['Product_Image'] = l3[:15]
            def to_img_tag(path):
                return '<img src="'+path+'" width="100">'
            st.write(HTML(df.to_html(escape=False, formatters=dict(Product_Image=to_img_tag))))
if __name__ == "__main__":
    main()
