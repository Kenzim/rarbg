from flask import Flask, request
import json
from rarbg import Rarbg


app = Flask(__name__)
rg = Rarbg()#proxies="proxies.txt")


def rg_search(search="", limit=25, sort="last", categories=[]):
    torrents = rg.search_all(search=search, limit=limit, categories=categories)
    data = {"torrent_results": []}
    for torrent in torrents:
        print(torrent.date)
        data["torrent_results"].append({"title": torrent.name,
                                        "download": torrent.get_magnet(),
                                        "seeders": torrent.seeders,
                                        "leechers": torrent.leechers,
                                        "size": torrent.size,
                                        "pubdate":"2023-04-12 10:14:09 +0000",
                                        "ranked":1,
                                        "info_page": ""})

@app.route("/pubapi_v2.php")
def hello_world():
    if request.args.get("get_token"):
        return json.dumps({"token": "b0f4eiaroc"})
    limit = request.args.get("limit", 25, type=int)
    sort = request.args.get("sort", "last")
    category = request.args.get("category", "").split(";")
    cgs = []
    for c in category:
        try:
            cgs.append(int(c))
        except ValueError:
            pass
        if c == "movies":
            cgs = [47, 42, 17, 50, 44, 51, 54, 45, 52]
        elif c == "tv":
            cgs = [18, 41, 49]
    

    
    if request.args.get("mode", 
                        ) == "list":
        return rg_search(limit=limit, sort=sort, categories=cgs)
    elif request.args.get("mode") == "search":
        return rg_search(search=request.args.get("search_string", "", type=str), limit=limit, sort=sort, categories=cgs)

