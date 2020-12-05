import ast
import urllib.parse
import requests
from bs4 import BeautifulSoup

IWILLTRAVEL_FRONTPAGE = "https://iwilltravelagain.com"
MAIN_URL = "https://iwilltravelagain.com/edit/wp-admin/admin-ajax.php"


class ParseRegion():
    def __init__(self):
        self.items = []
        self.profiles = []

    def parse_region_items(self, region_id):
        '''
        :param region_id: id from form-data; name="post_id"
        :return:
        '''
        with requests.Session() as s:
            p = s.post(MAIN_URL, files={'action': (None, 'get_activities'), 'post_id': (None, region_id),
                                        'key': (None, 'rows_2_grid_activities')})
            result = ast.literal_eval(p.text)
            if isinstance(result, list):
                self.items = result

    def set_list_profiles_with_url_name_category_location(self):
        if self.items:
            for item in self.items:
                self.profiles.append({"url": urllib.parse.urljoin(IWILLTRAVEL_FRONTPAGE, item.get("link").strip("\\/")),
                                      "name": item.get("title"),
                                      "category": item.get("taxonomies", {}).get('activity_category', {}).get(
                                          'termString',
                                          {}),
                                      "location": item.get("taxonomies", {}).get('location', {}).get('termString', {})})
            print(len(self.items))
        else:
            print("Items not found")

    def get_profiles_info(self):
        '''
        :return: profiles list
        '''
        if self.profiles:
            result = []
            for profile in self.profiles:
                r = requests.get(profile.get("url"))
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, "html.parser")
                    profile["website"] = soup.find('a', {'aria-label': 'Click here to Visit Website'}).get('href')
                    result.append(profile)
                    print(result)
                else:
                    print("Status code failed")
            return result


def main():
    regions_id = ['143', '1637', '65', '1677', '1690']
    for region_id in regions_id:
        region = ParseRegion()
        region.parse_region_items(region_id)
        region.set_list_profiles_with_url_name_category_location()
        profiles = [[item.get('website'), item.get('name'), item.get('category'), item.get('location')] for item in
                    region.get_profiles_info()]
        # load profiles to db
        # write_to_db(profiles, "table_name")


if __name__ == '__main__':
    main()
