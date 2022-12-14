# rarbg
RarBG Scraper w/ Captcha bypass


Example usage:

```py
rarbg = Rarbg(proxies="/media/scripts/proxies.txt")
torrents = rarbg.search_all("something" + " 1080 ", categories=[10, 12])

for torrent in torrents:
    if len("something" in torrent.name):
        torrents.remove(torrent)

for torrent in torrents:
    if torrent.files[0]["path"][-1] not in files:
        with open(os.path.join(Blackhole, torrent.name + ".torrent"), "wb") as fp:
            fp.write(torrent.torrent)
```
