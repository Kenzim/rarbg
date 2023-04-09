import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from pytesseract import pytesseract
import cv2
import numpy as np
from typing import Optional
from dateutil.parser import parse
import random
import torrent_parser as tp
import unicodedata
import pickle


class Rarbg:
    def __init__(self,
                 useragent: str = '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                 max_retries: int = 10,
                 proxies: Optional[str] = None
                ):
        self.url: str = "https://rarbgto.org"
        self.headers: dict = {"sec-ch-ua": useragent,
                        "sec-ch-ua-mobile":"?0",
                        "sec-ch-ua-platform":"Windows",
                        "Upgrade-Insecure-Requests":"1",
                        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
                        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "Sec-Fetch-Site":"same-origin",
                        "Sec-Fetch-Mode":"navigate",
                        "Sec-Fetch-Dest":"document",
                        "host":"rarbgto.org"
                       }
        self.retries = max_retries
        self.s = requests.Session()
        self.s.headers.update(self.headers)
        self.cookie_file = "./cookies.txt"
        self.proxies = []
        self.proxy_index = 0
        self.delay = 0.1
        if proxies:
            self.delay = 0
            with open(proxies, "r") as f:
                for line in f.readlines():
                    data = line.rstrip().split(":")
                    self.proxies.append(f"{data[2]}:{data[3]}@{data[0]}:{data[1]}")
        random.shuffle(self.proxies)
        self.next_proxy()
    
    def next_proxy(self):
        if self.delay != 0:
            return
        if self.proxy_index >= len(self.proxies):
            self.proxy_index = 0
        proxy = self.proxies[self.proxy_index]
        self.proxy_index += 1
        self.s.proxies = {
            'http': 'http://'+proxy,
            'https': 'http://'+proxy,
            }


    def renew_session(self):
        """
        Renew session
        """
        print("Renewing session")
        self.s = requests.Session()
        self.s.headers.update(self.headers)
        self.next_proxy()
        date = datetime.now() + timedelta(days=7) # Wed, 30 Nov 2022 20:38:54 GMT
        date = date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        r1 = self.s.get('https://rarbgto.org/threat_defence.php')
        soup1 = BeautifulSoup(r1.text, 'html.parser')
        scripts = soup1.findAll("script")
        data: str = ""
        for script in scripts:
            script = script.text
            if "value_sk" in script:
                data = script
        value_sk  = data.split("value_sk = '")[1].split("'")[0]
        value_c   = data.split("value_c = '")[1].split("'")[0]
        value_i   = data.split("value_i = '")[1].split("'")[0]
        value_r_1 = data.split("value_i+'&r=")[1].split("'")[0]
        value_r_2 = data.split("""&ref_cookie="+ref_cookie+"&r=""")[1].split('"')[0]
        cookies = { "sk": ";expires=" + date +";path=/;domain=.rarbgto.org" }
        self.s.cookies.update(cookies)
        requests.get(self.url + f"/threat_defence_ajax.php?sk={value_sk}&cid={value_c}&i={value_i}&r={value_r_1}", headers={'Content-type': 'text/plain'})
        time.sleep(4)
        r2 = self.s.get(self.url + "/threat_defence.php?defence=2&sk="+value_sk+"&cid="+value_c+"&i="+value_i+"&ref_cookie=rarbgto.org&r="+value_r_2)
        soup2 = BeautifulSoup(r2.text, 'html.parser')
        captcha_id = soup2.find('input', {'name': 'captcha_id'})["value"]
        captcha_r  = soup2.find('input', {'name': 'r'})["value"]

        captcha_img = ""
        imgs = soup2.findAll('img')
        for img in imgs:
            if "captcha" in img["src"]:
                captcha_img = self.url + img["src"]
                break
        r3 = self.s.get(captcha_img)
        arr = np.asarray(bytearray(r3.content), dtype=np.uint8)
    
        # Providing the tesseract executable
        # location to pytesseract library
        pytesseract.tesseract_cmd = "/usr/bin/tesseract"
        
        # Passing the image object to image_to_string() function
        # This function will extract the text from the image
        image = cv2.imdecode(arr, -1)
        results = pytesseract.image_to_string(image).rstrip()
        self.s.get(self.url + "/threat_defence.php?defence=2&sk="+value_sk+"&cid="+value_c+"&i="+value_i+"&ref_cookie=rarbgto.org&r="+captcha_r+"&solve_string="+results+"&captcha_id="+captcha_id+"&submitted_bot_captcha=1")
        try: #Try to save the cookies we got back so we don't have to renew again until they expire.
            with open(self.cookie_file, 'wb') as f:
                pickle.dump(self.s.cookies, f)
        except Exception as e:
            print("Could not save cookies to file")

    def get(self, *args, **kwargs) -> str:
        return self.get_resp(*args, **kwargs).text

    def get_resp(self, url: str, params: dict = {}, attempts: int = 0) -> requests.Response:
        if attempts == self.retries:
            raise LookupError("Maximum Retries Reached")
        try: # Let's see if we have valid cookies from a previous session that we can re-use.
            with open(self.cookie_file, 'rb') as f:
                self.s.cookies.update(pickle.load(f))
        except Exception as e:
            print("No cookiee file yet")
        resp = self.s.get(self.url + url, params=params)
        # print(resp.status_code)
        if "Please wait while we try to verify your browser..." in resp.text \
          or "pure flooding so you are limited to downloading only using magnets" in resp.text:
            self.renew_session()
            return self.get_resp(url, params, attempts+1)
        else:
            return resp

    def get_content(self, *args, **kwargs) -> bytes:
        return self.get_resp(*args, **kwargs).content

    def convert_size(self, size) -> float:
        if "kb" in size.lower():
            return float(size.split(" ")[0]) * 1000
        elif "mb" in size.lower():
            return float(size.split(" ")[0]) * 1000000
        elif "gb" in size.lower():
            return float(size.split(" ")[0]) * 1000000000
        else:
            return float(0)
    
    def search(self, search: str, categories: list[int] = [], page: int = 1, attempts: int = 0) -> list["Torrent"]:
        """
        Search torrents on RARBG
        Returns list of Torrent objects
        """
        torrents: list[Torrent] = []
        params = {"search": search, "category[]": categories, "page": page}
        data = self.get("/torrents.php", params=params)
        soup = BeautifulSoup(data, "html.parser")
        rows = soup.findAll('tr', {'class': "lista2"})
        for row in rows:
            items = row.findAll('td')
            torrents.append(Torrent(
                indexer=self,
                name=items[1].find('a').text,
                size=self.convert_size(items[3].text),
                seeders=int(items[4].text),
                leechers=int(items[5].text),
                date=parse(items[2].text),
                id=items[1].find('a')['href'].split("/")[-1]
            ))
        time.sleep(self.delay)
        return torrents

    def search_all(self, search: str, categories: list[int] = [], before: Optional[datetime] = None, after: Optional[datetime] = None, limit: int = 9999999) -> list["Torrent"]:
        """
        Search all pages for torrents
        """
        if not before:
            before = datetime.now()
        if not after:
            after = datetime(1970, 1, 1)
        torrents: list[Torrent] = []
        page = 1
        while True:
            results = self.search(search, categories, page)
            if len(results) == 0:
                break
            
            for torrent in results:
                if len(torrents) >= limit:
                    return torrents
                if torrent.date > before:
                    continue
                if torrent.date < after:
                    return torrents
                torrents.append(torrent)

            if len(results) < 25:
                break
            page += 1
        return torrents

class Torrent:
    def __init__(self,
                 indexer: "Rarbg",
                 name: str,
                 size: float,
                 seeders: int,
                 leechers: int,
                 date: datetime,
                 id: str):
        self.indexer = indexer
        self.name: str = name
        self.size: float = size # Size in bytes
        self.seeders: int = seeders
        self.leechers: int  = leechers
        self.date: datetime = date
        self.id: str = id
        self.page = None
    
    def __getattr__(self, name):
        if name == "magnet":
            self.magnet = self.get_magnet()
            return self.magnet
        elif name == "torrent":
            self.torrent = self.get_torrent_file()
            return self.torrent
        elif name == "data":
            self.data = tp.BDecoder(self.torrent).hash_field('pieces').decode()
            return self.data
        elif name == "files":
            self.files = self.get_files()
            return self.files
        else:
            try:
                return self[name]
            except KeyError:
                raise AttributeError(f"'Torrent' object has no attribute '{name}'")
    
    def get_magnet(self) -> str:
        """
        Get magnet link for torrent
        """
        if not self.page:
            self.page = self.indexer.get("/torrent/"+self.id)
        soup = BeautifulSoup(self.page, "html.parser")
        magnet = soup.select_one("a[href^=magnet]")
        return magnet["href"]

    def get_torrent_url(self, full: bool = True) -> str:
        """
        Get torrent url for torrent
        """
        if not self.page:
            self.page = self.indexer.get("/torrent/"+self.id)
        soup = BeautifulSoup(self.page, "html.parser")
        torrent_url = soup.select_one('a[href^="/download.php"]')
        if full:
            return self.indexer.url + torrent_url["href"]
        else:
            return torrent_url["href"]

    def get_torrent_file(self) -> bytes:
        """
        Get torrent
        """
        return self.indexer.get_content(self.get_torrent_url(full=False))

    def get_files(self) -> list[str]:
        """
        Get files in torrent
        """
        if not self.page:
            self.page = self.indexer.get("/torrent/"+self.id)
        soup = BeautifulSoup(self.page, "html.parser")
        rows = soup.select("div#files table.lista tr")
        files = []
        for row in rows:
            items = row.findAll('td')
            if "File Name" in items[0]:
                continue
            files.append({
                "path": unicodedata.normalize("NFKD", items[0].text).strip().split("/"),
                "size": self.indexer.convert_size(items[1].text.strip())
            })
        if len(files) == 0:
            try:
                files = [ {"path": x["path"], "size": x["length"]} for x in self.data["info"]["files"] ]
            except KeyError:
                files = [ {"path": [self.data["info"]["name"]], "size": self.data["info"]["length"]} ]
        return sorted(files, key=lambda d: d['size'], reverse=True)

    def __getitem__(self, key):
        return self.data[key]

    def __str__(self):
        return f"Name: {self.name} Size: {self.size} Seeders: {self.seeders} Leechers: {self.leechers} Date: {self.date} ID: {self.id}"
