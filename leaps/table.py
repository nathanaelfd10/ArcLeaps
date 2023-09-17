from bs4 import BeautifulSoup, ResultSet

class TableEngine:

    def __init__(self, html_source, table_selector: str):
        self.__html_source = html_source
        self.__table_selector = table_selector
        self.th_selector: str = "thead th" # Default "thead th
        self.tr_selector: str = "tbody tr" # Default "tbody tr"
        self.td_selector: str = "td" # Default td

        self.__soup = BeautifulSoup(self.__html_source, "html.parser")
        self.table = self.__soup.select_one(self.__table_selector)
        self.headers = self.get_headers()

    def __remove_escaped_characters_and_strip(self, str: str):
        # Should've been using regex but whev
        str = str.replace("\t", " ").replace("\n", "").replace("\r", "").strip()
        return " ".join(str.split())

    def get_headers(self):
        headers = self.table.select(self.th_selector)
        return [header.text for header in headers]

    def __get_all_rows(self):
        rows = self.table.select(self.tr_selector)
        return rows
    
    def __get_index_of_col(self, col_name: str):
        return self.headers.index(col_name.lower())
    
    def __get_field_value(self, row_element: ResultSet, col_name: str):
        result = []

        col_index = self.__get_index_of_col(col_name.lower())

        field_selector = "td:nth-child({field_index})".format(field_index = str(col_index + 1))
        cell = row_element.select_one(field_selector)
        if cell.find("a"):
            tlm_el = cell.select_one("a")
            tlm_url = tlm_el["href"]
            tlm_name = self.__remove_escaped_characters_and_strip(tlm_el.text)

            curr_tlm = {
                "id": "id",
                "tlm_name": tlm_name,
                "tlm_url": tlm_url
            }
            
            result.append(curr_tlm)
        
        if cell.text:
            tlm_name = cell.text
            curr_tlm = {
                "id": "id",
                "tlm_name": tlm_name,
                "tlm_url": None
            }
            result.append(curr_tlm)
            
        return result
    
    def __get_urls_inside_cell(self, cell_element: ResultSet):
        results = []

        for url in cell_element.find_all("a"):
            cell_content = {
                "content": None,
                "url": None
            }

            cell_content["content"] = self.__remove_escaped_characters_and_strip(url.text)
            cell_content["url"] = self.__remove_escaped_characters_and_strip(url["href"])

            if cell_content["content"] or cell_content["url"]:
               results.append(cell_content)

        return results

    def __get_texts_in_cell(self, cell_element: ResultSet):
        results = []

        for txt in cell_element.strings:
            cell_content = {
                "content": None,
                "url": None
            }

            cell_content["content"] = self.__remove_escaped_characters_and_strip(txt)

            if cell_content["content"] or cell_content["url"]:
                results.append(cell_content)
        
        return results

    def __get_cell_value(self, cell_element):
        urls = self.__get_urls_inside_cell(cell_element)
        texts = self.__get_texts_in_cell(cell_element)

        for text in texts:
            url_contents = [url["content"] for url in urls]
            url_urls = [url["content"] for url in urls]

            if text["content"] in url_contents:
                # print("MATCH!")
                matching_url_index = url_urls.index(text["content"])
                text["url"] = urls[matching_url_index]["url"]

        for url in urls:
            text_contents = [text["content"] for text in texts]
            text_urls = [text["content"] for text in texts]

            if url["content"] in text_contents:
                continue

            if url["url"] in text_urls:
                continue

            cell_content = {
                "content": self.__remove_escaped_characters_and_strip(url["content"]),
                "url": self.__remove_escaped_characters_and_strip(url["url"])
            }

            texts.append(cell_content)
        
        return texts

    def get_table(self):
        # Step 1: Get all rows
        rows = self.__get_all_rows()

        results = []
        # Step 2: Get all field values in row
        for index, row in enumerate(rows):
            columns = row.select(self.td_selector)
            row_content = {
                "fields": []
            }

            for index, col in enumerate(columns):
                col_name = self.headers[index]
                result = self.__get_cell_value(col)

                cell_value = {
                    "name": col_name,
                    "contents": result
                }
                
                row_content["fields"].append(cell_value)    

            if row_content:        
                results.append(row_content)

        return results