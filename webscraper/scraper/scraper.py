from asyncio.events import get_event_loop
import aiohttp
import asyncio
import time
from bs4 import BeautifulSoup
from aiohttp.client import request
import re
import requests
import json
from io import StringIO
import backoff

import concurrent.futures


class Scraper:
    def __init__(self) -> None:
        self.root_url = "https://www.comper.com.br"
        self.headers = {"User-agent": "Mozilla/5.0"}
        self.base_soup = self._build_base_soup()
        self.classes = {
            "department-bullet": "home_departments-bullets",
            "item-description": "col-xs-7 col-sm-12 prd-list-item-desc",
        }
        self.departaments_links = self._get_departments_links()
        self.departaments_endpoints = self._get_department_products_endpoints()

        self.pool = concurrent.futures.ThreadPoolExecutor(8)

    @backoff.on_exception(backoff.expo,aiohttp.ClientError,max_tries=20)
    async def _get_response_async(self, url: str):

        start = time.time()
        connector = aiohttp.TCPConnector(limit=60)
        async with aiohttp.ClientSession(
            headers=self.headers, trust_env=True, connector=connector,raise_for_status=True
        ) as session:
            
            async with session.get(url=url) as response:
                    
                response = await response.read()

            

        end = time.time()

        print(f"url: {url} took {end - start} seconds")
        return response

    def _get_response(self, url: str):

        return requests.get(url=url, headers=self.headers)

    def _build_base_soup(self) -> BeautifulSoup:

        base_request = self._get_response(url=self.root_url)

        html_code = base_request.text

        return BeautifulSoup(html_code, "html.parser")

    def _departments_header(self):

        return self.base_soup.find_all("li", {"data-departament": True})

    def _complete_department_link(self, url: str) -> str:
        return f"{self.root_url}{url}"

    def _get_departments_links(self) -> list:
        department_links = []
        for department_link in self._departments_header():

            department_links.append(
                self._complete_department_link(department_link.a["href"])
            )

        return department_links

    def _endpoint_products_regex(self, soup: BeautifulSoup) -> str:

        for item in soup.find_all("script"):
            pattern = "(?<=')/buscapagina\?.+(?=')"
            match = re.search(pattern, item.text)
            if match != None:

                return match[0]

    def _complete_departments_endpoints(self, url: str) -> str:
        return f"{self.root_url}{url}"

    def _get_department_products_endpoints(self):
        endpoints = []
        for department in self.departaments_links:
            department_request = self._get_response(department)

            department_html = department_request.text

            soup = BeautifulSoup(department_html, "html.parser")

            endpoints.append(
                self._complete_departments_endpoints(
                    self._endpoint_products_regex(soup)
                )
            )

        return endpoints

    def _build_page_number_url(self, url: str, page: int) -> str:

        return f"{url}{page}"

    def _department_total_pages_regex(self, soup: BeautifulSoup) -> int:
        for item in soup.find_all("script"):
            pattern_number_of_pages = "(?<==\ )[0-9]+(?=;)"
            match = re.search(pattern_number_of_pages, item.text)

            if match != None:
                return match[0]

    def get_department_total_pages(self, departaments_url: str) -> int:

        departament_request = self._get_response(url=departaments_url)

        departament_page_html = departament_request.text

        soup = BeautifulSoup(departament_page_html, "html.parser")

        last_page = self._department_total_pages_regex(soup)

        return int(last_page)

    def _parse_products_soup(self, department_page_html: str):

        products_links = []

        soup = BeautifulSoup(department_page_html, "lxml")

        for product_link in soup.find_all(
            "a", attrs={"class": "shelf-item__title-link"}
        ):

            products_links.append(product_link["href"])

        return products_links

    async def get_products_links_from_page(self, url: str, page: int) -> list:

        department_page_html = await self._get_response_async(
            url=self._build_page_number_url(url=url, page=page)
        )

        loop = asyncio.get_event_loop()

        return await loop.run_in_executor(
            self.pool, self._parse_products_soup, department_page_html
        )

    def _get_product_json(self, soup: BeautifulSoup) -> dict:
        json_from_script_pattern = "(?<=\(){.*}(?=\))"
        for script in soup.find_all("script"):
            match = re.search(pattern=json_from_script_pattern, string=script.text)
            if match != None:
                return json.loads(match[0])

    def _get_product_image(self, soup: BeautifulSoup) -> str:

        return soup.find("a", attrs={"class": "image-zoom"})["href"]

    def _build_json(self, soup: BeautifulSoup, url: str) -> dict:

        product_json = self._get_product_json(soup=soup)

        image_url = self._get_product_image(soup=soup)

        try:
            gtin = product_json["productEans"][0]
        except KeyError as e:
            gtin = None

        descricao = product_json["productName"]

        preco = product_json["productPriceTo"]

        product_url = product_json["pageUrl"]
        return dict(
            gtin=gtin,
            descricao=descricao,
            preco=preco,
            product_url=product_url,
            url_photo=image_url,
        )

    async def get_product_info(self, product_url) -> dict:

        product_html = await self._get_response_async(url=product_url)

        soup = BeautifulSoup(product_html, "lxml")
        product_json = self._build_json(soup=soup, url=product_url)

        return product_json






