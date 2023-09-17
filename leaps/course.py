import re
from leaps.base_page import LeapsPage
from leaps.table import TableEngine  

class Course(LeapsPage):
    
    def __init__(self, course_id, cookie):
        LeapsPage.cookie = cookie
        self.course_id = course_id
        self.tlm_url = "http://leaps.kalbis.ac.id/LMS/lectures/detail/{course_id}/teaching-learning-materials".format(course_id=self.course_id)

    @staticmethod
    def extract_course_id_from_url(url):
        match = re.search("LMS\/lectures\/detail\/(.*)\/home", url)
        return match.group(1)   
    
    def get_all_tlm(self):
        source = self.get_source(self.tlm_url, self.cookie)
        tlm_table = TableEngine(source, ".table-responsive table")        
        table = tlm_table.get_table()

        tlm_list = []
        for index, l1_row in enumerate(table):
            session_no = index + 1
            for field in l1_row["fields"]:
                for content in field["contents"]:
                    if "url" in content and content["url"] and content["url"] != "#":
                        output = {
                            "session_no": session_no,
                            "field_name": field["name"],
                            "content": content["content"],
                            "url": content["url"]
                        }

                        tlm_list.append(output)

        return tlm_list