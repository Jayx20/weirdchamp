from flask import Flask, request, flash, redirect
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
def posts():
    postList = Post.query.order_by(Post.id.desc()).limit(100)
    return render_template("posts.html", post_list = postList)

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

if __name__ == "__main__":
    db.create_all()
    app.run()