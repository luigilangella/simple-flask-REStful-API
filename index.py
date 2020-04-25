import sqlite3
from contextlib import closing
from flask import Flask, request, g, redirect, url_for, render_template, abort, jsonify

# Config
DATABASE = '/tmp/api.db'
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)


# Add methods and routes here

def connect_db():
    """Connects the app to the database"""
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    """Initialize the database and import the data from the schema.sql file"""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    """ The before_request method will establish the connection
        and stors it in the g object for use through the request
        cycle"""
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    """ The teardown request will make sure to close the database
        if is still open"""
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def get_posts():
    """ This route displays all available posts in the database"""
    cur = g.db.execute('select title, text from posts order by id desc')
    posts = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_posts.html', posts=posts)


@app.route('/api/v1/posts', methods=['GET'])
def show_entries():
    """This route creates an API response and returns the data in a JSON format"""
    cur = g.db.execute('select title, text from posts order by id desc')
    posts = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return jsonify({'count': len(posts), 'posts': posts})


@app.route('/api/v1/posts/<int:post_id>', methods=['GET', 'DELETE'])
def single_post(post_id):
    method = request.method
    if method == 'GET':
        cur = g.db.execute(
            'select title, text from posts where id =?', [post_id])
        posts = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
        return jsonify({'count': len(posts), 'posts': posts})
    elif method == 'DELETE':
        g.db.execute('delete from posts where id = ?', [post_id])
        return jsonify({'status': 'Post Deleted'})


if __name__ == '__main__':
    app.run()
