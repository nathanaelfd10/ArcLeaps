from datetime import datetime
import os
from leaps.academic_period import AcademicPeriod
from leaps.course import Course
from leaps.tlm_detail import TLMDetail
import hashlib

class ArchivalEngine:

    def __init__(self, student_id, cookie):
        self.student_id = student_id
        self.email = "{student_id}@student.kalbis.ac.id".format(student_id=student_id)
        self.cookie = cookie
        self.LEAPS_MIN_ACADEMIC_YEAR_ID = 22
        self.LEAPS_MIN_ACADEMIC_YEAR = 2014
        self.is_save = True

    def get_current_max_academic_year_id(self):
        two_digit_year = datetime.now().strftime("%y")
        academic_year_id = (int(two_digit_year) + 8) + 1
        return academic_year_id

    def year_id_to_academic_year(self, academic_year_id: int):
        lowest_start_year = datetime.strptime("2014", "%Y")

        start_year = lowest_start_year.replace(year=lowest_start_year.year + (academic_year_id - self.LEAPS_MIN_ACADEMIC_YEAR_ID)).strftime("%Y")
        end_year = lowest_start_year.replace(year=lowest_start_year.year + (academic_year_id - (self.LEAPS_MIN_ACADEMIC_YEAR_ID - 1))).strftime("%Y")

        year_formatted = "{start_year}/{end_year}".format(start_year=start_year, end_year=end_year)
        return year_formatted

    def __get_time_dir_partition_name(self, academic_year_start, academic_year_end, semester_type):
        folder_name = "{academic_year_start}-{academic_year_end} - {semester_type}".format(academic_year_start = academic_year_start,
                                                                                         academic_year_end = academic_year_end, 
                                                                                        semester_type=semester_type)
        print(folder_name)
        return folder_name

    def __get_output_dir(self, academic_year_start, academic_year_end, semester_type):
        folder_name = self.__get_time_dir_partition_name(academic_year_start, academic_year_end, semester_type)
        academic_year_partition_path = os.path.join("output", folder_name)
        return academic_year_partition_path

    def __make_output_dir(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def get_all_courses_from_all_academic_period(self):

        current_year = int(datetime.now().strftime("%Y"))

        courses = []

        for iter_year in range(self.LEAPS_MIN_ACADEMIC_YEAR, current_year + 1):
            year_dt = datetime.strptime(str(iter_year), "%Y")
            academic_year_start = int(year_dt.strftime("%Y"))
            academic_year_end = int(year_dt.replace(year = year_dt.year + 1).strftime("%Y"))

            for semester_type in ["Odd", "Even", "Short"]:
                academic_period = AcademicPeriod(academic_year_start, academic_year_end, semester_type, self.cookie)
                output = {
                    "academic_year_start": academic_year_start,
                    "academic_year_end": academic_year_end,
                    "semester_type": semester_type,
                    "course_list": academic_period.get_course_list()
                }
                courses.append(output)

        return courses
    
    def remove_forbidden_characters(self, str):
        forbidden_characters = dict((ord(char), None) for char in '\/*?:"<>|')
        return str.translate(forbidden_characters)

    # Code clean ups?
    def get_all_tlm(self):
        print("Starting to index all course lists from all academic years.")
        partitions = self.get_all_courses_from_all_academic_period()

        print("Starting to index all TLMs from obtained courses.")
        for partition in partitions:
            for course in partition["course_list"]:
                course_name = "Placeholder Course Name" if not course["content"] else course["content"]
                course_id = Course.extract_course_id_from_url(course["url"])
                course_obj = Course(course_id, self.cookie)
                tlm_list = course_obj.get_all_tlm()

                # Fetch TLMs
                for tlm in tlm_list:
                    print("TLM Content:", tlm)

                    attached_file = None
                    if tlm["url"].startswith("http://leaps.kalbis.ac.id/LMS/lectures/detail/"):
                        tlm_id = TLMDetail.get_tlm_id(tlm["url"])
                        tlm_detail = TLMDetail(tlm_id, self.cookie)
                        attached_file = tlm_detail.get_tlm_resource_file()
                    else:
                        attached_file = {
                            "title": "External Link " + hashlib.md5(str(datetime.now()).encode()).hexdigest()[0:6] if not tlm["content"] else tlm["content"],
                            "file_type": "txt",
                            "content": bytes(tlm["url"], encoding="utf-8") # Contents must be in bytes
                        }
                    
                    academic_year_start = partition["academic_year_start"]
                    academic_year_end = partition["academic_year_end"]
                    semester_type = partition["semester_type"]
            
                    session_name = "Session {session_no}".format(session_no = str(tlm["session_no"]))

                    filename = "{filename}.{file_type}".format(filename = str(attached_file["title"]), file_type = str(attached_file["file_type"]))

                    # Replaces all '/' to '-' in order to not confuse the filepaths.
                    partition_dir = self.__get_output_dir(academic_year_start, academic_year_end, semester_type)
                    partition_by_session_dir = os.path.join(partition_dir, self.remove_forbidden_characters(course_name), self.remove_forbidden_characters(session_name), self.remove_forbidden_characters(tlm["field_name"]))
                    output_file_path = os.path.join(partition_by_session_dir, self.remove_forbidden_characters(filename))
            
                    if not os.path.exists(partition_by_session_dir):
                        os.makedirs(partition_by_session_dir)

                    with open(output_file_path, "wb") as fp:
                        fp.write(attached_file["content"])