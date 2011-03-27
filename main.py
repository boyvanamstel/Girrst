#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

from gistapi import Gist, Gists

import os

class MainHandler(webapp.RequestHandler):
  def get(self):
    self.response.headers.add_header('Content-Type', 'text/html')
    path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    self.response.out.write(template.render(path, {}))    
    
class UserHandler(webapp.RequestHandler):
  def get(self, *args):
    self.response.headers.add_header('Content-Type', 'application/xml')
    
    # <?xml version="1.0" encoding="UTF-8" ?>
    # <rss version="2.0">
    # <channel>
    #         <title>RSS Title</title>
    #         <description>This is an example of an RSS feed</description>
    #         <link>http://www.someexamplerssdomain.com/main.html</link>
    #         <lastBuildDate>Mon, 06 Sep 2010 00:01:00 +0000 </lastBuildDate>
    #         <pubDate>Mon, 06 Sep 2009 16:45:00 +0000 </pubDate>
    # 
    #         <item>
    #                 <title>Example entry</title>
    #                 <description>Here is some text containing an interesting description.</description>
    #                 <link>http://www.wikipedia.org/</link>
    #                 <guid>unique string per item</guid>
    #                 <pubDate>Mon, 06 Sep 2009 16:45:00 +0000 </pubDate>
    #         </item>
    # 
    # </channel>
    # </rss>    
    try:
      gists = Gists.fetch_by_user(args[0])
    
      feed = []
      feed.append('<?xml version="1.0" encoding="UTF-8" ?>')
      feed.append('<rss version="2.0">')
      feed.append('<channel>')
      feed.append('<title>Girsst for %s</title>' % args[0])
      feed.append('<description>Girsst converts your gists to RSS</description>')
      
      feed.append('<link>http://girsst.appspot.com</link>')

      for gist in gists:
        feed.append('<item>')
        feed.append('<link>http://gist.github.com/%s</link>' % gist.id)
        feed.append('<title>%s</title>' % gist.description)
        feed.append('<pubDate>%s</pubDate>' % gist.created_at)
        feed.append('<author>%s</author>' % gist.owner)
        
        if len(gist.filenames) == 1:
          feed.append('<description><![CDATA[ %s ]]></description>' % gist.files[gist.filenames[0]].getvalue())
        else:
          feed.append('<description>Snippit in %d files: %s</description>' % (len(gist.filenames), ', '.join(gist.filenames)))
          feed.append('<files>')
          for file in gist.files:
            feed.append('<file><![CDATA[ %s ]]></file>' % gist.files[file].getvalue())
          feed.append('</files>')
        
        feed.append('</item>')

      feed.append('</channel>')
      feed.append('</rss>')
      
      #self.response.out.write(feed.join)
      self.response.out.write(''.join(feed))
    except Exception:
      self.response.out.write('<error>Invalid username, or GitHub is being a bitch.</error>') 

def main():
  application = webapp.WSGIApplication([('/', MainHandler), ('/user/(.*)/?', UserHandler)], debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
