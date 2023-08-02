from lib.config import *

class Holiday():
    def __init__(self, ABSTRACT_API_KEY):
        self.api_key = ABSTRACT_API_KEY

    def __str__(self):
        return "This is the class for Abstract Holiday API"
    
    def get_holiday_info(self, country_code, year=None, month=None, day=None):
        try:
            params = {
                "api_key": self.api_key,
                "country": country_code,
                "year": year or datetime.now().year,
                "month": month,
                "day": day
            }
            time.sleep(10)
            response = requests.get(ABSTRACT_URL["Holiday"], params=params)
            response.raise_for_status()
            return response.json()
        except Exception as err:
            raise Exception("Failed to get holiday information") from err