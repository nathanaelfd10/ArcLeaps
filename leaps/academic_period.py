import urllib.parse
from leaps.base_page import LeapsPage
from leaps.table import TableEngine
from datetime import datetime


class AcademicPeriod(LeapsPage):

    def __init__(self, academic_year_start: int, academic_year_end: int, semester_type: str, cookie: str):
        LeapsPage.cookie = cookie
        self.academic_year_start = academic_year_start
        self.academic_year_end = academic_year_end
        self.academic_year_id = self.__get_academic_year_id(academic_year_start)
        self.semester_type = semester_type
        self.is_save_raw_data = True

        # Constant received from Leaps
        self.ACADEMIC_YEAR_ID_MIN = 22

    def __semester_type_short(self, semester_type: str):
        return semester_type.lower()[0]

    def __generate_course_list_url(self, academic_year_id: int, semester_type: str):
        params = {
            "academicyears": str(academic_year_id), 
            "semester_option": self.__semester_type_short(semester_type),
            "view_option": "by-course"
        }

        base_url = "http://leaps.kalbis.ac.id/LMS/lectures/course-list?"
        complete_url = base_url + urllib.parse.urlencode(params)

        return complete_url

    def __get_academic_year_id(self, academic_year_start):
        year_start = datetime.strptime(str(academic_year_start), "%Y")
        academic_year_id = year_start.replace(year_start.year + 8).strftime("%y")
        return academic_year_id
    
    def get_course_list(self):
        """Get all course list from this academic period."""
        url = self.__generate_course_list_url(self.academic_year_id, self.semester_type)
        source = self.get_source(url, self.cookie)

        table_tag = "table"
        course_table = TableEngine(source, table_tag)
        raw_table = course_table.get_table()

        course_id_list = []

        for l1_row in raw_table:
            for field in l1_row["fields"]:
                for content in field["contents"]:
                    if "url" in content:
                        if content["url"] and content["url"] != "#":
                            course_id_list.append(content)
        
        return course_id_list