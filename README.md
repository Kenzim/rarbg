# rarbg
RarBG Scraper using their frontend, not the torrentapi.org API.
Now with a fake torrentapi server utilising this module.


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

Proxies should be in the format of:

```
ip:port:username:password
```

## Api Server

Run api.py to fake a torrentapi server. I find the real torrentapi extremely unreliable, so this is a good alternative.
You don't need to get a key or app id, it just works without any of that.

## To-do list (in no particular order)

- [ ] ASYNCIO VERSION! definitely high priority as proxies block everything so much
- [ ] Testing
- [ ] Better docs, comments, etc
- [ ] Redis cache for api server
- [ ] Sql database cache for api server? Store torrents in db, no expiry like a redis cache might have.


Please open issues if there is some missing functionality/bugs/anything else really.
