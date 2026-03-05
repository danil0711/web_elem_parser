from bs4 import BeautifulSoup


class ParserService:
    """
    Извлекает данные из HTML по CSS-селектору.
    """

    def extract_text(self, html: str, selector: str) -> str | None:
        """
        Возвращает текст найденного элемента.
        """
        soup = BeautifulSoup(html, "html.parser")
        element = soup.select_one(selector)

        if not element:
            raise ValueError(f"Selector {selector} не нашёл элемент.")

        return element.get_text(strip=True)
