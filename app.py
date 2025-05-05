import sys
from urllib.request import Request, urlopen
import os.path
from os import listdir
from bs4 import BeautifulSoup
import time


class find_not_friends:
    cache_folder = "cache"
    def __init__(self, url):
        self.url = url
        if os.path.isdir(self.cache_folder) is False:
            os.mkdir(self.cache_folder)

    def get_html(self,page, url):
        """
        Fetches the HTML content of a webpage, either from a local cache or by making an HTTP request.
        Args:
            page (int): The page number used to name the cached HTML file.
            url (str): The URL of the webpage to fetch.
        Returns:
            str: The HTML content of the webpage.
        Behavior:
            - If a cached HTML file exists for the given page, it reads and returns the content from the file.
            - If no cached file exists, it makes an HTTP request to fetch the HTML content, saves it to the cache, and then returns the content.
            - Introduces a delay of 2 seconds after making an HTTP request to avoid overwhelming the server.
        Note:
            - The method assumes `self.cache_folder` is a valid directory path where cached files are stored.
            - The `save_html` method is expected to handle saving the HTML content to the cache.
        """

        file_name = self.cache_folder + "/" + str(page) + ".html"
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
        """
        Saves the provided HTML content to a file.

        Args:
            file_name (str): The name of the file where the HTML content will be saved.
            html (bytes): The HTML content in bytes to be decoded and written to the file.

        Raises:
            UnicodeDecodeError: If the HTML content cannot be decoded using UTF-8.

        Prints:
            A confirmation message indicating the file has been saved successfully.
        """
        with open(file_name, "w") as f:
            f.write(html.decode("utf-8"))
        print("File saved as " + file_name)

    def find_pages(self,type,page):
        """
        Recursively finds and processes pages of a specific type starting from a given page number.
        Args:
            type (str): The type of pages to search for (used in the URL and query parameters).
            page (int): The current page number to process.
        Returns:
            None: This function does not return a value. It processes pages recursively
            by calling itself if a "Next" link is found in the pagination container.
        Notes:
            - This function uses BeautifulSoup to parse HTML and locate the pagination container.
            - If a "Next" link is found, the function calls itself with the next page number.
            - Ensure that `self.get_html` is implemented to fetch the HTML content of the page.
        """
        html = self.get_html(type+str(page), self.url + "?page=" + str(page) + "&tab=" + type)
        soup = BeautifulSoup(html, features="html.parser")
        padding_container=soup.find('div', class_='paginate-container')
        link_next=padding_container.find('a', string="Next")

        if link_next!=None:
            self.find_pages(type, page + 1)

    def extract_members_from_files(self, type):
        """
        Extracts member names from HTML files in the specified cache folder.
        This method scans through HTML files in the cache folder that match the
        specified type, parses their content, and extracts member names from
        specific HTML elements.
        Args:
            type (str): The prefix of the file names to filter (e.g., "friends", "followers").
        Returns:
            list: A list of member names extracted from the HTML files.
        Raises:
            FileNotFoundError: If the specified files cannot be found in the cache folder.
            Exception: For any issues encountered while parsing the HTML files.
        Notes:
            - The method assumes that the HTML files contain a <turbo-frame> element
              with the id "user-profile-frame".
            - Member names are extracted from <span> elements with the class "Link--secondary".
        """
        mypath = self.cache_folder + "/"
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
        """
        Compares two lists of social media members (followers and following)
        and identifies the members that are being followed but do not follow back.

        Args:
            followers (list): A list of members who follow the user.
            following (list): A list of members the user is following.

        Returns:
            set: A set of members that the user is following but who are not following the user back.
        """
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
if len(not_following) == 0:
    print("All your following in followers list")
else:
    print("You are follow users that not following you")
    for user in not_following:
        print(user)
