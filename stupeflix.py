import os
import requests
import json
import time

API_KEY = os.environ.get('STUPEFLIX_API_KEY')
API_SECRET = os.environ.get('STUPEFLIX_API_SECRET')

class StupeflixApi(object):
	base_url = 'https://dragon.stupeflix.com/v2/'
	pre_boiler = None
	post_boiler = None

	def __init__(self, api_key=None, api_secret=None, theme='tiles', audio=None):
		self.api_key = api_key or API_KEY
		self.api_secret = api_secret or API_SECRET
		self.session = requests.Session()
		self._set_boiler(theme, audio)

	def _set_boiler(self, theme, audio):
		self.pre_boiler = "<movie service='craftsman-1.0'><body><widget type='director.theme.%s'><track type='video'>" % theme
		post_boiler = "</track>"
		if audio is not None:
			post_boiler += "<track type='audio'><audio filename='%s'/></track>" % audio
		post_boiler += "</widget></body></movie>"
		self.post_boiler = post_boiler

	def _call(self, method, endpoint, params):
		final_endpoint = self.base_url + endpoint
		headers = {'Authorization': 'Secret %s' % self.api_secret}
		if method.upper() == 'GET':
			data = {}
		else:
			data = params
			params = {}
		r = self.session.request(method.lower(), final_endpoint, 
								 params=params, data=json.dumps(data), headers=headers)
		return r.json()

	def create_video(self, stories):
		definition = ""
		for story in stories:
			definition += "<image filename='%s'><track type='caption'><text>%s</text></track></image>" % (story['img'], story['headline'])

		endpoint = 'create'
		tasks = {
			'tasks': {
				'task_name': 'video.create',
				'definition': self.pre_boiler + definition + self.post_boiler
			}
		}
		return self._call('POST', endpoint, tasks)

	def status(self, key):
		endpoint = 'status'
		tasks = {'tasks': key}
		return self._call('GET', endpoint, tasks)


def stupefy(stories):
    stories = filter(lambda s: s.get('img_url') is not None and s.get('headline') is not None, stories)
    api = StupeflixApi()
    print 'Creating video...'
    video = api.create_video(stories)
    key = video[0]['key']
    resp = None
    while True:
        print 'Waiting...'
        time.sleep(8)
        resp = api.status(key)
        if resp[0]['status'] == 'success':
            print 'Done!'
            break
    return resp