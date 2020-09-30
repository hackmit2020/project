from datetime import datetime, date, timedelta
import requests
import pandas as pd
import json
import urllib.parse

from .data import Data, DataFrame

YOUR_API_KEY = '14liwzS25SPuXHLjyNtWTlzFmz5AAe17'


class NYTArticle:
    COLUMNS = ['date', 'headline', 'abstract', 'url']

    def __init__(self, headline, abstract, url, date):
        self.headline = headline
        self.abstract = abstract
        self.url = url
        self.date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")

    def to_dict(self):
        return {
            'date': self.date,
            'headline': self.headline,
            'abstract': self.abstract,
            'url': self.url
        }


class NYTQuery(Data):
    NAME = "nytimes"

    SEARCH_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json?"
    START_DATE = date(2020, 2, 1)
    END_DATE = date.today()
    DATES = pd.date_range(START_DATE, END_DATE-timedelta(days=1), freq='M')

    def query_range(self, begin, end):

        begin_day = begin.strftime("%Y%m%d")
        end_day = end.strftime("%Y%m%d")

        params = {
            'api-key': YOUR_API_KEY, 'begin_date': begin_day, 'end_date': end_day,
            'fq': "covid"
        }

        print(urllib.parse.urlencode(params))
        url = self.SEARCH_URL + urllib.parse.urlencode(params)
        r = requests.get(url)
        data = r.json()

        response = data.get('response', None)

        if response is not None:
            docs = response['docs']

            all_article_data = []

            for article in docs:
                all_article_data.append(
                    NYTArticle(headline=article['headline']['main'], abstract=article['abstract'], url=article['web_url'],
                               date=article['pub_date']).to_dict()
                )

            df = pd.DataFrame(all_article_data, columns=NYTArticle.COLUMNS)
            return df
        else:
            print("NYT loading failure")
            return pd.DataFrame([], columns=NYTArticle.COLUMNS)

    def _remote_load(self) -> DataFrame:
        all_articles = []

        for month_num in range(2,9+1):
            start_day = date(2020, month_num, 1)
            end_day = date(2020, month_num+1, 1) - timedelta(days=1)
            a = self.query_range(start_day, end_day)
            all_articles.append(a)
        return pd.concat(all_articles).reset_index(drop=True)
