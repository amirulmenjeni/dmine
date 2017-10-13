import facebook
import time
import sys
import configparser
from spiders import facebook_spider_post
from dmine import Spider, ComponentLoader
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

#Deploy multithreading

class FBspider(Spider):
    name = "facebook"

    def __init__(self):
        config = configparser.ConfigParser()
        config.read("c:/Users/User/Desktop/CS/sem5/Task/config.ini")
        user = config.get('Facebook', 'Email')
        passw = config.get('Facebook', 'Password')
        self.driver = self.init_driver()
        self.login(self.driver, user, passw)
        access_token=self.generate_token(self.driver)
        self.graph=facebook.GraphAPI(access_token)

    def init_driver(self):
        driver = webdriver.PhantomJS(executable_path=r'C:\PhantomJs\bin\phantomjs\bin\phantomjs.exe')
        driver.wait = WebDriverWait(driver, 5)
        return driver

    def generate_token(self, driver):
        driver.get("https://developers.facebook.com/tools/explorer")
        time.sleep(2)
        token=driver.find_element_by_xpath("//div[@class='_371-']/div/label/input")
        return token.get_attribute("value")

    def login(self, driver, username, passw):
        self.driver.get("https://www.facebook.com/login")
        a = driver.find_element_by_id('email')
        a.send_keys(username)
        b = driver.find_element_by_id('pass')
        b.send_keys(passw)
        button = driver.find_element_by_id('loginbutton')
        button.click()

    def setup_filter(self, sf):
        sf.add_com('event', info="An event posted on Facebook")
        sf.add_com('group', info="a facebook group")

        sf_event = sf.get('event')
        sf_event.add('author', info='author of the event post')
        sf_event.add('event_name', info='name of the event')
        sf_event.add('schedule', info='schedule of the event')
        sf_event.add('attending_count', info='')
        sf_event.add('declined_count', info='')

        sf_group = sf.get('group')
        sf_group.add('owner', info='owner of the facebook group')
        sf_group.add('privacy_type', info='Privacy setting of this group')
        sf_group.add('member_request_count', info='No. of members request to join the group')
        sf_group.add('last_updated', info='Time last updated')
        sf_group.add('desc', info='description of group')


        sf.add_var('search_type', type=list, default=['event', 'group', 'place'], info= "Determine the search type i.e groups, events, people ")
        sf.add_var('keyword', default="", info='keyword query')
        sf.add_var('limit', default="5", info='limit of results')


    def start(self, sf):
        types_list=sf.ret('search_type')

        if 'event' in types_list:
            for x in self.search_by_event(sf):
                yield x

        if 'group' in types_list:
            for x in self.search_by_group(sf):
                yield x


    def unicode_decode(self, text):
        try:
            non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
            return text.translate(non_bmp_map)
        except UnicodeDecodeError:
            return text.encode('utf-8')

    def search_by_event(self, sf):
        limit=sf.ret('limit')
        keyword=sf.ret('keyword')
        events = self.graph.request("/search?q={}&type=event&limit={}".format(keyword,limit))
        data_dict = events['data']
        sf_event=sf.get('event')
        for e in data_dict:
            fields=self.graph.get_object(id=e['id'],fields='attending_count, declined_count, owner, maybe_count, noreply_count')
            event_name=self.unicode_decode(e['name'])
            start_time= e['start_time'].split('T')

            end_time=e['end_time'].split('T')
            owner=fields['owner']['name']
            attending_count = fields['attending_count']
            declined_count=fields['declined_count']
            maybe_count=fields['maybe_count']
            no_reply_count=fields['noreply_count']
            location= e['place']

            sf_event.set_attr_values(
                    author= owner,
                    event_name=event_name,
                    schedule = start_time,
                    attending_count= attending_count,
                    declined_count= declined_count
            )

            if sf_event.should_scrape():
                data_dict =  {
                                'Event id' : e['id'],
                                'author' : owner,
                                'Name' : event_name,
                                'start time' : start_time,
                                'end time' : end_time,
                                'attending' : attending_count,
                                'declined' :  declined_count,
                                'maybe' : maybe_count,
                                'no reply' : no_reply_count,
                                'place name' : location['name']
                            }
                data_dict.update(location['location'])

                yield ComponentLoader('event', data_dict)


    def search_by_group(self, sf):
        limit=sf.ret('limit')
        keyword=sf.ret('keyword')
        sf_group=sf.get('group')
        groups = self.graph.request("/search?q={}&type=group&limit={}".format(keyword,limit))
        data_dict = groups['data']

        for e in data_dict:
            fields=self.graph.get_object(id=e['id'],
                             fields='updated_time, member_request_count, owner, description')

            owner=fields['owner']['name'] if 'owner' in fields else "None specified"
            last_updated=fields['updated_time'] if 'updated_time' in fields else "None"

            sf_group.set_attr_values(
                    owner= owner,
                    privacy_type=e['privacy'],
                    member_request_count = fields['member_request_count'],
                    last_updated= last_updated,
                    desc= fields['description']
            )

            if sf_group.should_scrape():
                yield ComponentLoader('group', {
                                'Group id' : e['id'],
                                'owner' : owner,
                                'privacy type' : e['privacy'],
                                'member requestcount' : fields['member_request_count'],
                                'last updated' : last_updated,
                                'description' : fields['description'].replace("\n", " ")
                    })

    #wip
    def search_by_place(self, keyword, limit):
        places = self.graph.request("/search?q={}&type=place&limit={}".format(keyword,limit))
        data_dict = places['data']
        for e in data_dict:
            city_name=e['location'].get('city')
            country=e['location'].get('country')
            state=e['location'].get('state')
            street=e['location'].get('street')
            category_list= [x['name'] for x in e['category_list']]
            name=e['name']
            print("Category: {}".format(category_list))
            print("Name: {} \nCity name: {}\nCountry: {}\nstate: {}\nstreet: {}\n".format(name, city_name,country, state, street))


    def search_by_people(self, keyword, limit):
        groups = self.graph.request("/search?q={}&type=place&limit={}".format(keyword,limit))
        data_dict = groups['data']
        for e in data_dict:
            print(self.unicode_decode(e['name']))

    def search_by_page(self, keyword, limit):
        groups = self.graph.request("/search?q={}&type=page&limit={}".format(keyword,limit))
        data_dict = groups['data']

        for e in data_dict:
            fields=self.graph.get_object(id=e['id'], fields='category, checkins ,current_location, rating_count')
            e.update(fields)
            del e['id'] #Remove Page ID from dict
            yield e

    def search_by_post(self, keyword, limit):
        fb_post = fbpost.FBspider_post(self.driver, keyword, limit)
