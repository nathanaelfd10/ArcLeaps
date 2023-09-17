import requests
from bs4 import BeautifulSoup
from leaps.base_page import LeapsPage
import os
import re

class TLMDetail(LeapsPage):

    # Stateful version of TLM Detail

    def __init__(self, tlm_id, cookie):
        self.tlm_id = str(tlm_id) 
        self.cookie = cookie

    def __get_extension(self, str: str):
        regexp = "\.\w{3,4}($|\?)"
        match = re.search(regexp, str)
        return match.group() if match else ""
        
    def __get_file_type(self, str: str):
        extension = self.__get_extension(str)
        return extension[1:len(extension)] if extension.startswith(".") else extension

    @staticmethod
    def get_tlm_id(url):
        regexp = "\d+$"
        match = re.search(regexp, url)
        return match.group()
    
    @staticmethod
    def get_tlm_url(course_id: int | str):
        return "http://leaps.kalbis.ac.id/LMS/lectures/detail/{course_id}/teaching-learning-materials".format(course_id=str(course_id))

    def save_to(self, file_type, course_title, tlm_title, content):

        course_title = course_title.strip()
        tlm_title = tlm_title.strip()

        if file_type.startswith("."):
            file_type = file_type.replace(".", "")

        if "/" in course_title or tlm_title or file_type:
            course_title = course_title.replace("/", "-")
            tlm_title = tlm_title.replace("/", "-")
            file_type = file_type.replace("/", "-")

        path = os.path.join("output", "tlm_content", course_title)

        if not os.path.exists(path):
            os.makedirs(path)

        with open(path + "/"+tlm_title+"."+file_type, "wb") as fp:
            fp.write(content)

    def get_tlm_resource_file(self):
        url = "http://leaps.kalbis.ac.id/LMS/lectures/detail/8394/teaching-learning-materials/detail/{tlm_id}".format(tlm_id = self.tlm_id)
        source = self.get_source(url, self.cookie)
        soup = BeautifulSoup(source, "html.parser")

        # Detect content type
        pdf = soup.select_one("input[id='pdf_source']")
        youtube_url = soup.select_one(".box .box-body .row > div > a")
        external_link = soup.select_one("p a[target='_blank']")
        img = soup.select_one(".box-body img")

        tlm_title_tag = ".content .row .box-body > h4"
        tlm_title = soup.select_one(tlm_title_tag).text

        output = {
            "title": tlm_title,
            "file_type": None,
            "content": None
        }

        if pdf:
            pdf_url = pdf["value"]
            response = requests.get(pdf_url)
            output["file_type"] = self.__get_file_type(pdf_url)
            output["content"] = response.content
        elif youtube_url:
            print("Detected youtube embed")
            output["file_type"] = "txt"
            output["content"] = bytes(youtube_url["href"], "utf-8")
        elif img:
            url = img["src"]
            response = requests.get(url)
            output["file_type"] = self.__get_file_type(url)
            output["content"] = response.content
        elif external_link:
            print("Detected external link")
            output["file_type"] = "txt"
            output["content"] = bytes(external_link["href"], "utf-8")
        else:        
            print("Detected non-pdf content")
            non_pdf_url_el = soup.select_one("center a")
            url = non_pdf_url_el["href"] # Actual URL to the file
            response = requests.get(url)
            output["file_type"] = self.__get_file_type(url)
            output["content"] = response.content
            # self.save_to(self.__get_extension(url), course_title, tlm_title, response.content)

        return output

    def get_discussion(self, url):
        # otw
        return