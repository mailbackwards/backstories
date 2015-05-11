#!/usr/bin/env python
import os
import sys
from flask import Flask, render_template, request, jsonify
from flask.ext.cors import CORS

from spider import LinkSpider, CustomStoryDatabase
from stupeflix import StupeflixApi

app = Flask(__name__)
cors = CORS(app)

DBS = ['recap', 'recap-nigeria', 'recap-smuggle', 'recap-thailand', 
       'bs-climate-treaty', 'bs-shell-arctic', 'bs-yemen', 'bs-california-water']
CURRENT_DB = 'bs-yemen'
DEFAULT_AUDIO = None

@app.route("/")
def home():
    args = {'stories': [], 'errors': []}
    if not 'query-url' in request.args:
        # Just visiting the homepage, not entering a form
        pass
    elif not request.args['query-url']:
        # The form has bad input
        args['errors'].append('No URL entered above.')
    else:
        query_url = request.args['query-url']
        spider_limit = request.args.get('spider-level', 'all')
        args['stories'] = CustomStoryDatabase(CURRENT_DB).getSpiderRows(query_url, inlinks_only=False, spider_limit=spider_limit)
        # Sort by publish date, puts the stories without dates at the top
        args['stories'] = filter(lambda s: s.get('headline'), args['stories'])
        args['stories'] = sorted(args['stories'], key=lambda s: s.get('publish_date'))
    return render_template('index.html', **args)

@app.route("/stupefy.json", methods=["POST"])
def stupefy():
    data = request.get_json(force=True)
    if not data.get('stories'):
        return jsonify({'status': 'failed', 'message': 'No stories in POST data.'})
    audio = data.get('audio') or DEFAULT_AUDIO
    stories = filter(lambda s: s.get('img') is not None and s.get('headline') is not None, data['stories'])
    api = StupeflixApi(audio=audio)
    print 'Creating video...'
    video = api.create_video(stories)
    key = video[0]['key']
    print '\tKey is %s' % key
    return jsonify(video[0])

@app.route("/stupestatus.json", methods=["GET"])
def stupestatus():
    if 'key' in request.args:
        key = request.args.get('key')
        resp = StupeflixApi().status(key)
        return jsonify(resp[0])
    return jsonify({'success': False})

if __name__ == "__main__":
    app.run(debug=True)
