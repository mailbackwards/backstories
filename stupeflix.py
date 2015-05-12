import requests
import json
import time

from conf import STUPEFLIX_API_KEY, STUPEFLIX_API_SECRET

class StupeflixApi(object):
	base_url = 'https://dragon.stupeflix.com/v2/'
	pre_boiler = None
	post_boiler = None

	def __init__(self, api_key=None, api_secret=None, theme='tiles', audio=None):
		self.api_key = api_key or STUPEFLIX_API_KEY
		self.api_secret = api_secret or STUPEFLIX_API_SECRET
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

	def create_video(self, stories, print_only=False):
		definition = ""
		for story in stories:
			# Display the text at a variable rate: 2 words per second
			headline_duration = float(len(story['headline'].split(' '))) / 2.2
			definition += "<text duration='0.1'>%s</text><transition type='crossfade' duration='0.1'/>" % story['date']
			definition += "<image filename='%s' duration='%.1f'><track type='caption'><text>%s</text></track></image><transition type='crossfade' duration='0.1'/>" % (
							story['img'], headline_duration, story['headline'])
			# lede_duration = float(len(story['lede'].split(' '))) / 2.5
			# definition += "<image filename='%s' duration='%.1f'><track type='caption'><text>%s</text></track></image><transition type='crossfade' duration='0.1'/>" % (
			# 				story['img'], lede_duration, story['lede'])
		full_definition = self.pre_boiler + definition + self.post_boiler

		if print_only:
			print full_definition
			return

		endpoint = 'create'
		tasks = {
			'tasks': {
				'task_name': 'video.create',
				'definition': full_definition
			}
		}
		return self._call('POST', endpoint, tasks)

	def status(self, key):
		endpoint = 'status'
		tasks = {'tasks': key}
		return self._call('GET', endpoint, tasks)
