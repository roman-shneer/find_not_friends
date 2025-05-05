import sys
from urllib.request import Request, urlopen
import os.path
from os import listdir
from bs4 import BeautifulSoup
import time


class find_not_friends:
    def __init__(self, url):
        self.url = url

    def get_html(self,page, url):

        file_name="cache/"+str(page)+".html"
        if os.path.isfile(file_name) is True:    
            print(file_name+" skipped")
            with open(file_name, "r") as f:
                return f.read()
        print("Requesting "+url)
        req = Request(
            url=url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        html=urlopen(req).read()
        time.sleep(2)
        self.save_html(file_name, html)
        return html

    def save_html(self,file_name, html):        
        with open(file_name, "w") as f:
            f.write(html.decode("utf-8"))
        print("File saved as " + file_name)

    def find_pages(self,type,page):
        html = self.get_html(type+str(page), self.url + "?page=" + str(page) + "&tab=" + type)
        soup = BeautifulSoup(html, features="html.parser")
        padding_container=soup.find('div', class_='paginate-container')
        link_next=padding_container.find('a', string="Next")

        if link_next!=None:
            self.find_pages(type, page + 1)

    def extract_members_from_files(self, type):
        mypath = "cache/"
        files = [
            mypath+f
            for f in listdir(mypath)
            if f.startswith(type) and f.endswith(".html")
        ]
        members=[]
        for file in files:
            with open(file, "r") as f:
                soup= BeautifulSoup(f, features="html.parser")
                frame=soup.find("turbo-frame", id="user-profile-frame")

                page_members = frame.find_all("span", class_="Link--secondary")
                page_members = [member.get_text() for member in page_members]
                members = members + page_members
        return members

    def compare_members(self, followers, following):
        followers=set(followers)
        following=set(following)
        not_following = following - followers
        return not_following


FU = find_not_friends(sys.argv[1])
FU.find_pages("followers", 1)
FU.find_pages("following", 1)
followers = FU.extract_members_from_files("followers")
following = FU.extract_members_from_files("following")
not_following=FU.compare_members(followers, following)
print("You are follow users that not following you")
for user in not_following:
    print(user)
