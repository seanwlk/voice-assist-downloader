#!/usr/bin/env python3

import json
import datetime
import time
import urllib
import requests
import os
import transmissionrpc
from flask import Flask,request,jsonify
from utils import *

with open('config.json', 'r') as f:
  config = json.load(f)

ifttt = IFTTTNotifications(config['ifttt']['applet'], config['ifttt']['key'], config['ifttt']['resultNotification'])
tc = transmissionrpc.Client(config['rpc']['host'], port=config['rpc']['port'], user=config['rpc']['user'], password=config['rpc']['password'])

api = Flask(__name__)

@api.route(f'/{config["app"]["routeName"]}', methods=['GET'])
def app():
  title = request.args.get('title',default = "")
  key = request.args.get('key',default = "")
  if key != config["app"]['privateKey']:
    return jsonify({'error': '403'})
  DOWNLOADED = {
    "title" : "",
    "image" : "",
    "file_name" : "",
    "size" : "",
    "downloaded" : False
  }
  # IMDB ID SEARCHER
  r = requests.get(f"http://www.omdbapi.com/?t={urllib.parse.quote(title)}&apikey={config['OMDb']['key']}").json()
  if r['Response'] == "True":
    DOWNLOADED['title'] = r['Title']
    DOWNLOADED['image'] = r['Poster']
  if 'imdbID' in r:
    if r['Type'] == "series":
      # EZTV search
      imdbID = r['imdbID'].replace("tt","")
      print ("imdb: ",imdbID)
      s = requests.get(f"https://eztv.io/api/get-torrents?imdb_id={imdbID}").json()
      currTimeDelta = int(time.time()) - int(config['downloads']['series']['lifespanDays'] * 24 * 60 * 60) # Lifespan in seconds
      print("delta",currTimeDelta)
      temp = []
      if s['torrents_count'] != 0:
        for t in s['torrents']:
          if t['date_released_unix'] > currTimeDelta:
            temp.append(t)
        if len(temp)>0:
          toDownload = sorted(temp, key = lambda i: int(i['size_bytes']),reverse=True)[0]
          DOWNLOADED['size'] = convert_bytes(toDownload['size_bytes'])
          DOWNLOADED['file_name'] = f"{DOWNLOADED['title']} - S{toDownload['season']}E{toDownload['episode']} - {DOWNLOADED['size']}"
          DOWNLOADED['downloaded'] = True
          tc.add_torrent(toDownload['magnet_url'],download_dir=config['downloads']['series']['folder'])
          ifttt.notify({"status":"success","message":f"{DOWNLOADED['file_name']} is being added to the download queue","image":DOWNLOADED['image']})
        else:
          ifttt.notify({"status":"failed","message":f"No new episodes of {DOWNLOADED['title']} were found","image":DOWNLOADED['image']})
        return jsonify(DOWNLOADED)
      else:
        ifttt.notify({"status":"failed","message":"Nothing was found for that series name"})
        return jsonify({'error': 'No torrents found for that IMDb ID on EZTV'})
    elif r['Type'] == "movie":
      g = requests.get(f"https://yts.mx/api/v2/list_movies.json?query_term={r['imdbID']}").json()
      if g['data']['movie_count'] != 1:
        ifttt.notify({"status":"failed","message":f"No downloads availeble for {r['Title']}"},image=r['Poster'])
        return jsonify({'error': 'No torrents found for that IMDb ID on YTS'})
      temp = []
      if len(g['data']['movies'][0]['torrents']) != 0:
        for t in g['data']['movies'][0]['torrents']:
          if config['downloads']['movies']['quality']['2160p'] and t['quality'] == "2160p":
            temp.append(t)
        if len(temp) == 0:
          for t in g['data']['movies'][0]['torrents']:
            if config['downloads']['movies']['quality']['1080p'] and t['quality'] == "1080p":
              temp.append(t)
        if len(temp) == 0:
          for t in g['data']['movies'][0]['torrents']:
            if config['downloads']['movies']['quality']['720p'] and t['quality'] == "720p":
              temp.append(t)
        if len(temp)>0:
          toDownload = sorted(temp, key = lambda i: int(i['size_bytes']),reverse=True)[0] # pick heaviest
          toDownload['magnet_url'] = "magnet:?xt=urn:btih:"+toDownload['hash']+"&dn="+urllib.parse.quote(g['data']['movies'][0]['title_long'])+"&tr=http://track.one:1234/announce&tr=udp://track.two:80"
          tc.add_torrent(toDownload['magnet_url'],download_dir=config['downloads']['movies']['folder'])
          ifttt.notify({"status":"success","message":f"{DOWNLOADED['title']} is being added to the download queue","image":DOWNLOADED['image']})
        else:
          toDownload = {'error': f'There are no decent quality torrents available for {title}'}
          ifttt.notify({"status":"failed","message":f"No decent quality downloads available for {DOWNLOADED['title']}"})
        return jsonify(toDownload)
      else:
        return jsonify({'error': 'No torrents available for this movie'})
        ifttt.notify({"status":"failed","message":f"No downloads available for {r['Title']}"})
      return jsonify(g)
  else:
    ifttt.notify({"status":"failed","message":"Nothing was found for that movie name"})
    return jsonify({'error': 'IMDb ID not found'})

@api.route('/', methods=['GET'])
def home():
  return "These are private APIs."

if __name__ == '__main__':
  api.run(host=config['app']["host"],port=config['app']["port"],debug=False)