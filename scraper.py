import re
import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
from pathos.multiprocessing import ProcessingPool as Pool
"""
with Pool() as p:
    print(p.map(get_name_of_product, links))

"""


class Scraper:
    def __init__(self) -> None:
        self.root_url = "https://www.supermuffato.com.br/"
        self.headers = {"User-agent": "Mozilla/5.0"}
        self.base_soup = self._build_base_soup()
        self.classes = {
            "department-bullet": "home_departments-bullets",
            "item-description": "col-xs-7 col-sm-12 prd-list-item-desc",
        }
        self.departaments_links = self.get_departments_links()

    def _get_response(self, url: str):

        return requests.get(url=url, headers=self.headers)

    def _build_base_soup(self) -> BeautifulSoup:

        base_request = self._get_response(url=self.root_url)

        html_code = base_request.text

        return BeautifulSoup(html_code, "html.parser")

    def _departments_bullet(self):

        return self.base_soup.find(attrs={"class": self.classes["department-bullet"]})

    def get_departments_links(self) -> list:
        department_links = []
        for department_link in self._departments_bullet().find_all("a"):
            department_links.append(department_link["href"])

        return department_links

    def _build_page_number_url(self, url: str, page: int) -> str:

        return f"{url}#{page}"

    def get_products_links_from_page(self, url: str, page: int) -> list:

        products_links = []

        department_request = self._get_response(
            url=self._build_page_number_url(url=url, page=page)
        )
        department_page_html = department_request.text

        soup = BeautifulSoup(department_page_html, "html.parser")

        for product_link in soup.find_all(
            attrs={"class": self.classes["item-description"]}
        ):

            products_links.append(product_link.a["href"])

        return products_links
    
    def _get_image_url(self,soup: BeautifulSoup) -> str:

        return soup.find('a',attrs={'class':'image-zoom'})['href']

    def _get_code(self, soup: BeautifulSoup) -> int:

        return soup.find("span", attrs={"class": "prd-code"}).div.text

    def _get_seller(self, soup: BeautifulSoup) -> str:

        return soup.find("div", attrs={"class": "seller-name"}).a.text

    def _get_product_name(self, soup: BeautifulSoup) -> str:

        header_nome = soup.find("h2", attrs={"class": "prd-name-header"})

        return header_nome.div.text

    def _treat_price(self, price: str) -> float:
        print(price)
        return float(price.strip("R$ ").replace(",", "."))

    def _get_product_price(self, soup: BeautifulSoup) -> float:

        price = soup.find("strong", attrs={"class": "skuBestPrice"}).text

        return self._treat_price(price)

    def _build_json(self, soup: BeautifulSoup, url: str) -> dict:

        return dict(
            url=url,
            url_imagem = self._get_image_url(soup),
            nome=self._get_product_name(soup),
            preco=self._get_product_price(soup),
            vendedor=self._get_seller(soup),
            codigo=self._get_code(soup),

        )

    def get_product_info(self, product_url: str) -> dict:
        product_request = self._get_response(url=product_url)

        product_html = product_request.text

        soup = BeautifulSoup(product_html, "html.parser")
        product_json = self._build_json(soup=soup, url=product_url)
        print(product_json)
        return product_json
    
    def multiprocessing(self):

        links = self.get_products_links_from_page(url=self.departaments_links[0],page=1)

        with Pool() as p:
            print(p.map(self.get_product_info,links))


scraper = Scraper()

scraper.multiprocessing()

