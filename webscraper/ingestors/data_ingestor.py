from scraper.scraper import Scraper
import asyncio
import time
import numpy as np

class DataIngestor:
    def __init__(self, scraper: Scraper) -> None:
        self.scraper = scraper
        self.urls = self._matrix_to_list(self.get_urls())

    def _matrix_to_list(self, matrix: list) -> list:

        return list(np.concatenate(matrix))

    async def fetch_department_pages(self, department_endpoint: str, total_pages: int):

        return await asyncio.gather(
            *[
                self.scraper.get_products_links_from_page(
                    url=department_endpoint, page=page + 1
                )
                for page in range(total_pages)
            ]
        )

    def get_urls(self):
        urls = []
        for department_endpoint, department_link in zip(
            self.scraper.departaments_endpoints, self.scraper.departaments_links
        ):
            department_total_pages = self.scraper.get_department_total_pages(department_link)

            urls += asyncio.run(
                self.fetch_department_pages(
                    department_endpoint=department_endpoint,
                    total_pages=department_total_pages,
                )
            )

        return urls

    async def fetch_product_pages(self, pages: list):

        return await asyncio.gather(
            *[self.scraper.get_product_info(url) for url in pages]
        )

    def _list_into_chunks(self, url_list: list, chunk_size: int) -> list:

        return [
            url_list[i : i + chunk_size] for i in range(0, len(url_list), chunk_size)
        ]

    def ingest(self):

        urls_lists = self._list_into_chunks(self.urls, chunk_size=500)

        returns = []

        for url_list in urls_lists:

            products = asyncio.run(self.fetch_product_pages(pages=url_list))

            returns += products
            time.sleep(1)

        return returns