from flask import Flask, request, flash, redirect, session
from flask.helpers import url_for
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy

import secrets
import re
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secrets.secret_key
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32))
    color = db.Column(db.String(6)) #hex code
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text)

@app.route("/")
@app.route("/posts")
@app.route("/posts/<page>")
def posts(page = 1):
    try:
        page = int(page)
    except:
        flash("Page"+page+"does not exist.")
        return redirect(url_for("posts"))
    if page < 1:
        flash("Page"+page+"does not exist.")
        return redirect(url_for("posts"))

    lastPage = (Post.query.count()/postsPerPage())+1
    firstPost = (page-1)*postsPerPage()
    lastPost = firstPost+postsPerPage()

    postList = Post.query.order_by(Post.id.desc())[firstPost:lastPost]
    return render_template("posts.html", post_list = postList, page = page, lastPage = lastPage)

@app.route("/newpost", methods = ['GET','POST'])
def newpost():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        color = request.form["color"]
        correct = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)
        if correct:
            post = Post(title = title, color = color[1:7], content = content)
            db.session.add(post)
            db.session.commit()
            flash("Made new post.")
            return redirect(url_for("posts"))
        else:
            flash("INVALID COLOR CODE RETAD.")
            return redirect(url_for("newpost", title = title, content = content))
            
    else:
        title = request.args.get('title')
        content = request.args.get('content')
        return render_template("newpost.html", title = title, content = content)

@app.route("/settings", methods = ['GET','POST'])
def settings():
    if request.method == "POST":
        posts_per_page = request.form["posts_per_page"]
        if posts_per_page:
            session['posts_per_page'] = posts_per_page
        flash("Saved settings.")
        return redirect(url_for("settings"))
    else:

        return render_template("settings.html", posts_per_page = postsPerPage())

def postsPerPage() -> int:
    posts_per_page = session.get('posts_per_page')
    if posts_per_page == None:
        posts_per_page = 10
    try:
        posts_per_page = int(posts_per_page)
    except:
        posts_per_page = 10
    return posts_per_page

if __name__ == "__main__":
    db.create_all()
    app.run(host = '0.0.0.0', port=8050)