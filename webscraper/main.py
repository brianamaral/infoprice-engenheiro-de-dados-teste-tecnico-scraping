from ingestors.data_ingestor import DataIngestor
from scraper.scraper import Scraper
import time
from io import StringIO
import json
import pandas as pd



if __name__ == "__main__":

    start = time.time()
    scraper = Scraper()

    data_ingestor = DataIngestor(scraper)


    print(data_ingestor.urls[0])
    urls = data_ingestor.ingest()


    end = time.time()

    print("Took {} seconds to pull websites.".format(end - start))

    json_string = json.dumps(urls, indent=2)


    df = pd.read_json(StringIO(json_string), orient="records")

    print(df)

    df.to_csv("data/output/saida.tsv", index=False, sep="\t")