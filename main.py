import os
import functions_framework
import feedparser
import datetime
from flask import render_template, make_response
from time import mktime

URL=os.environ.get("PARSE_URL")
if URL is None:
    print('bad URL')
    feed=None
else:
    try:
        feed=feedparser.parse(URL)
    except:
        feed=None

def time_to_release(release):
    if not 'updated_parsed' in release:
        return None
    d0=datetime.datetime.fromtimestamp(mktime(release.updated_parsed)) #datetime.datetime.strptime(release['updated'],'%Y-%m-%dT%H:%M:%SZ') #
    dt=d0-datetime.datetime.now()
    return dt.days

def name_of_release(release):
    return release.title

# Register an HTTP function with the Functions Framework
@functions_framework.http
def main(request):
    tidy_entries=[]
    if feed is None:
        # This is considered a successful execution and WILL NOT be reported
        # to Error Reporting, but the status code (500) WILL be logged.
        from flask import abort
        return abort(500)

    for release in feed.entries:
        ttr=time_to_release(release)
        if ttr is not None and -3<ttr<11:
            tidy_entries.append(release)

    template =  render_template('base.xml', entries=tidy_entries) # , baseUrl=podcasts['baseUrl']
    response = make_response(template)
    response.headers['Content-Type'] = 'application/atom+xml'
    return response
