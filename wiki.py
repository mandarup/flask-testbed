from flask import Flask, redirect, render_template, request, url_for
from flask_pymongo import PyMongo
import markdown2
import re
import flask
from datetime import datetime


app = Flask(__name__)
app.config.from_mapping(
        SECRET_KEY='dev',
    )
mongo = PyMongo(app, "mongodb://localhost/wiki")
db = mongo.db

WIKIPART = re.compile(r"([A-Z][a-z0-9_]+)")
WIKIWORD = re.compile(r"([A-Z][a-z0-9_]+(?:[A-Z][a-z0-9_]+)+)")

@app.route("/HomePage", methods=["GET"])
def redirect_to_homepage():
    return redirect(url_for("show_page", pagepath="HomePage"))


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        if request.form['submit'] == 'DeleteOne':
            delete_one_page()
    posts = mongo.db.pages.find()
    return render_template('index.html', posts=posts)

@app.template_filter()
def totitle(value):
    return " ".join(WIKIPART.findall(value))

@app.template_filter()
def wikify(value):
    parts = WIKIWORD.split(value)
    for i, part in enumerate(parts):
        if WIKIWORD.match(part):
            name = totitle(part)
            parts[i] = "[%s](%s)" % (name, url_for("show_page", pagepath=part))
    return markdown2.markdown("".join(parts))


@app.route("/<path:pagepath>")
def show_page(pagepath):
    page = mongo.db.pages.find_one_or_404({"_id": pagepath})
    return render_template("page.html",
        page=page,
        pagepath=pagepath)

@app.route("/create", methods=('GET', 'POST'))
def create_page():
    error = None
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        timestamp = datetime.utcnow()

        if not title:
            error = 'Title is required.'

        if request.form['submit'] == 'Save':
            if error is not None:
                flask.flash(error, 'error')
            else:
                mongo.db.pages.update(
                    {"_id": title},
                    {"$set": {"body": body,
                                "title": title,
                                "timestamp": timestamp}},
                    w=1, upsert=True)
                return redirect(url_for("show_page", pagepath=title))
        elif request.form["submit"] == 'Cancel':
            return redirect(url_for('index'))
        else:
            raise NotImplementedError
    return render_template("create.html", error=error)



@app.route("/edit/<path:pagepath>", methods=["GET"])
def edit_page(pagepath):
    page = mongo.db.pages.find_one_or_404({"_id": pagepath})
    return render_template("edit.html",
        page=page,
        pagepath=pagepath)

@app.route("/edit/<path:pagepath>", methods=["POST"])
def save_page(pagepath):
    if "cancel" not in request.form:
        title = request.form['title']
        body = request.form['body']
        timestamp = datetime.utcnow()
        mongo.db.pages.update(
            {"_id": pagepath},
            {"$set": {"body": body,
                        "title": title,
                        "timestamp": timestamp}},
            w=1, upsert=True)
    return redirect(url_for("show_page", pagepath=pagepath))


def delete_one_page():
    mongo.db.pages.delete_one({})



@app.errorhandler(404)
def new_page(error):
    pagepath = request.path.lstrip("/")
    if pagepath.startswith("uploads"):
        filename = pagepath[len("uploads"):].lstrip("/")
        return render_template("upload.html", filename=filename)
    else:
        return render_template("edit.html", page=None, pagepath=pagepath)




@app.route("/uploads/<path:filename>")
def get_upload(filename):
    return mongo.send_file(filename)

@app.route("/uploads/<path:filename>", methods=["POST"])
def save_upload(filename):
    if request.files.get("file"):
        mongo.save_file(filename, request.files["file"])
        return redirect(url_for("get_upload", filename=filename))
    return render_template("upload.html", filename=filename)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    app.run(debug=True)
