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
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainPage(Handler):

    def render_front(self, title="", post="", error=""):
        self.render("newpost.html", title=title, post=post, error=error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            p = Post(title = title, post = post)
            p.put()
            
            self.redirect("/blog/%s" % str(p.key().id()))
        else:
            error = "You must enter a title, and a post!"
            self.render_front(title, post, error)

class Blog(Handler):

    def render_blog(self, title="", post=""):
        posts = db.GqlQuery("SELECT * FROM Post "
                            "ORDER BY created DESC "
                            "LIMIT 5")
        self.render("blog.html", title=title, post=post, posts=posts)

    def get(self):
        self.render_blog()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")


class ViewPostHandler(Handler):

    def get(self, id):
        single_post = Post.get_by_id(int(id), parent = None)
        if single_post:
            self.render("perma.html", single_post = single_post)
        else:
            self.response.write("Nah dude")


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', Blog),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
