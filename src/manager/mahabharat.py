from manager import HtmlContent


class Mahabharat(HtmlContent):
    CRAWL_URL_BASE = f'https://sacred-texts.com/hin/mbs/'

    def __init__(self):
        super().__init__(name="mahabharat")

    def download(self):
        for book_number in range(1, 2):
            for chapter_number in range(1, 100):
                url = self.CRAWL_URL_BASE + f'mbs{book_number:02}{chapter_number:03}.htm'
                html_content, status_code = super().load(url)
                if status_code == 404:
                    # break to outer loop
                    break
                if html_content:
                    print(f"Loaded content from: {url}")
                    soup = super().get_soup(html_content)
                    rows = soup.find_all('td')[0]
                    text = rows.get_text()
                    text = text.replace('\u00A0', ' ')
                    text = ''.join(filter(lambda x: not x.isdigit(), text))
                    lines = text.splitlines()
                    cleaned_lines = [line for line in lines if line.strip()]
                    text = '\n'.join(cleaned_lines)
                    if text:
                        file_name = f'mbs{book_number:02}{chapter_number:03}.txt'
                        super().save(text, file_name)
                        print(f"Saved content to: {file_name}")
                else:
                    print(f"Failed to load content from: {url}")
                    continue


if __name__ == '__main__':
    mahabharat = Mahabharat()
    mahabharat.download()
