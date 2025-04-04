from enum import Enum

import requests
from bs4 import BeautifulSoup


class ContentPullType(Enum):
    HTML = "html"
    JSON = "json"
    XML = "xml"
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"


class Content:
    def __init__(self, name: str, content_pull_type: ContentPullType, data_loc: str):
        self.name = name
        self.content_pull_type = content_pull_type
        self.data_loc_path = data_loc + '/' + name + '/'

    def load(self, **kwargs):
        # Logic to load content based on content_pull_type by implementers
        pass

    def extract(self, **kwargs):
        # Logic to extract content from the URL based on content_pull_type by implementers
        pass

    def safe_close(self):
        # Logic to close any resources if needed
        pass


class HtmlContent(Content):
    def __init__(self, name: str, data_loc: str = '../../data'):
        super().__init__(name, ContentPullType.HTML, data_loc)

    def load(self, url: str, headers: dict = None, params: dict = None, timeout: int = 3):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            response.encoding = 'utf-8'
            response.raise_for_status()  # Raise an error for bad responses
            # Optionally parse the HTML content with BeautifulSoup
            return response.text, response.status_code
        except requests.RequestException as e:
            print(f"Error loading HTML content: {e}")
            return None, e.response.status_code if e.response else 404

    def get_soup(self, html_content: str):
        return BeautifulSoup(html_content, 'html.parser', from_encoding='utf-8')

    def save(self, content: str, file_name: str):
        # save file to the data_loc_path
        with open(self.data_loc_path + file_name, 'w', encoding='utf-8') as file:
            file.write(content + '\n')
