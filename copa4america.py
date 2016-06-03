#!/usr/bin/env python

# Copyright 2016 Google Inc.
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

# [START imports]
import json
import logging
import os
import urllib

from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

# [START scores]
class Score(ndb.Model):
    """A main model for representing an individual Score entry."""
    id = ndb.KeyProperty(indexed=False)
    number = ndb.IntegerProperty(indexed=True)
    scorer = ndb.StringProperty(indexed=False)
    goals1 = ndb.IntegerProperty(indexed=False)
    goals2 = ndb.IntegerProperty(indexed=False)
# [END greeting]


# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):
        scores_query = Score.query().order(Score.number)
        scores = scores_query.fetch(1000)

        template_values = {
            'scores': scores
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
# [END main_page]


# [START Fixture]
class Fixture(webapp2.RequestHandler):

    def post(self):
        scorer = self.request.get('scorer')
        goals1s = self.request.get_all('goals1s[]')
        goals2s = self.request.get_all('goals2s[]')

        for idx in range(len(goals1s)):
            score = Score.get_or_insert(scorer + str(idx));
            score.id = ndb.Key('Score', scorer + str(idx));
            score.number = idx
            score.scorer = scorer
            score.goals1 = int(goals1s[idx])
            score.goals2 = int(goals2s[idx])
            score.put()

        scores_query = Score.query().order(Score.number)
        scores = scores_query.fetch(1000)

        new_scores = {}
        for score in scores:
            new_scores.setdefault(score.scorer, {})
            new_scores[score.scorer][score.number] = [score.goals1, score.goals2]

        self.response.write(json.dumps(new_scores))
# [END Fixture]


# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/save', Fixture),
], debug=True)
# [END app]
