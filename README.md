# Backstori.es

Backstori.es lets you semi-automatically generate a background explainer video for any story, inspired by "Previously On..." recap sequences on TV shows. It uses a story's inline links to generate a network of possible stories; after selecting the headlines and images that matter most, it creates a video of them using [Stupeflix](stupeflix.com).

## Requirements

* [MongoDB](http://docs.mongodb.org/manual/installation/)
* python + pip

## Installation

* `git clone` this repo and cd into it, activate virtualenv if you like
* `pip install -r requirements.txt` installs everything
* set the `STUPEFLIX_API_KEY` and `STUPEFLIX_API_SECRET` environment variables to your Stupeflix keys (or change them in `conf.py`, but don't re-commit!)
* `python app.py` starts the server
* navigate to `localhost:5000`

## Adding Backstories

1. go to `conf.py` and find the `DBS` dictionary
1. add an item to the dictionary where the key is the name of the database you want to create, and the value is the URL to start crawling from, e.g. "'ukraine': 'http://america.aljazeera.com/articles/2015/5/12/nemtsov-report-220-russians-killed-in-ukraine.html'"
1. to start the crawl, run `python spider.py <DB_NAME>`
1. to access the results, find them in the dropdown in `localhost:5000`

## Endpoints

* `/` - leads to homepage
* `/stupefy.json` - takes a list of stories in `POST` data and generates video via Stupeflix API
* `/stupestatus.json` - checks status of a video given its Stupeflix key

## Files

* `templates/index.html` contains all the frontend code
* `app.py` contains the server and endpoints for talking to the frontend
* `extractor.py` extracts and indexes links from articles
* `spider.py` contains the crawler and higher-level interaction with the database
* `storage.py` is for lower-level integration with MongoDB (stolen from [MediaCloud-API-Client](https://github.com/c4fcm/MediaCloud-API-Client))
* `stupeflix.py` integrates with the Stupeflix API
