import requests
import random
import time

class LeapsPage:

    def __init__(self, cookie):
        self.cookie = cookie
        self.throttling_min = 1
        self.throttling_max = 3
        self.is_save_raw_data = True

    def get_source(self, url, cookie):

        timeout = random.uniform(0.1, 1.0)
        time.sleep(timeout)

        print(url)

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,id-ID;q=0.8,id;q=0.7,ja-JP;q=0.6,ja;q=0.5",
            "cache-control": "no-cache",
            "connection": "keep-alive",
            "cookie": cookie,
            "dnt": "1",
            "pragma": "no-cache",
            "referer": "http://leaps.kalbis.ac.id/LMS/lectures/course-list?academicyears=31&semester_option=e&view_option=by-course",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, verify=False)

        if not response.text:
            # Should raise a better suited exception?
            raise FileNotFoundError("Response is empty!")
        
        print(response)

        return response.text
