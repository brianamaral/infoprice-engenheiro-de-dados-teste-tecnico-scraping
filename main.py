import re
import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
from multiprocessing import Pool

url = 'https://www.supermuffato.com.br/'
user_agent = {'User-agent': 'Mozilla/5.0'}

request = requests.get(url=url,headers=user_agent)

html_code = request.text

soup = BeautifulSoup(html_code,'html.parser')

soup = soup.find('div',attrs={'class':'home_departments-bullets'})
links = []
for element in soup.find_all('a'):
    req = requests.get(element['href'],headers=user_agent)
    
    soup = BeautifulSoup(req.text,'html.parser')

    for ele in tqdm(soup.find_all('div',attrs={'class':'col-xs-7 col-sm-12 prd-list-item-desc'})):
        
        links.append(ele.a['href'])

        #req = requests.get(ele.a['href'],headers=user_agent)
    
        #soup = BeautifulSoup(req.text,'html.parser')

        #print(soup.find('h2',attrs={'class':'prd-name-header'}).div.text)
    

def get_name_of_product(url: str) -> str:
    time.sleep(0.5)
    req = requests.get(url=url,headers=user_agent)

    soup = BeautifulSoup(req.text,'html.parser')
    response = soup.find('h2',attrs={'class':'prd-name-header'}).div.text
    print(response)
    return response

with Pool() as p:
    print(p.map(get_name_of_product,links))
'''
soup = soup.find('div',attrs={'class':'src__View-sc-1h87wse-0 src__WrapperItems-sc-1h87wse-10 iTIKNF'})
print(soup.prettify())
for ele in soup.find_all('a',attrs={'aria-current':'page'}):
    print(ele['href'])


def get_website_map_url(soup: BeautifulSoup) -> str:
    element = soup.find('a',{'class':'mmn-link'})
    return element['href']

url_map = get_website_map_url(soup)

request_map = requests.get(url=url_map,headers=user_agent)

website_map_html = request_map.text

soup = BeautifulSoup(website_map_html,'html.parser')

for i,element in enumerate(soup.find_all('h3',attrs={'class':'sitemap-item-title'})):
    req = requests.get(url=f"{url}{element.a['href']}",headers=user_agent)
    print(req)
'''