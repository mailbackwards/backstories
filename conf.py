import os

STUPEFLIX_API_KEY = os.environ.get('STUPEFLIX_API_KEY')
STUPEFLIX_API_SECRET = os.environ.get('STUPEFLIX_API_SECRET')

# For fallback checking whether something's an inlink while crawling
DEFAULT_SOURCE_URL = 'http://america.aljazeera.com'

DEFAULT_AUDIO = None

# These are key, value pairs that correspond to {<DB_NAME>: <START_URL>}
DBS = {
    #'recap':                'http://america.aljazeera.com/articles/2015/5/3/Baltimore-protests-curfew.html',
    'recap-nigeria':        'http://america.aljazeera.com/articles/2015/5/2/nigeria-says-234-more-females-rescued-from-Boko-Haram.html',
    'recap-thailand':       'http://america.aljazeera.com/articles/2015/5/2/26-bodies-at-suspected-thailand-trafficking-camp.html',
    'bs-climate-theory':    'http://america.aljazeera.com/articles/2015/4/2/UN-climate-change-emissions.html',
    'bs-shell-arctic':      'http://america.aljazeera.com/articles/2015/5/5/shells-arctic-return-faces-hurdle-at-seattle-port.html',
    'bs-yemen':             'http://america.aljazeera.com/articles/2015/5/10/houthis-agree-to-five-day-cease-fire.html',
    'bs-california-water':  'http://america.aljazeera.com/articles/2015/5/6/california-adopts-unprecedented-water-cuts.html',
    'bs-nepal':				'http://america.aljazeera.com/articles/2015/5/12/74-magnitude-quake-hits-nepal.html'
}