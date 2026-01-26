from flask import (
    Blueprint, abort, flash, g, redirect, render_template, request, url_for
)

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('author', __name__)

@bp.route('/author/<int:id>')
def index(id):
    db = get_db()
    author = db.execute(
        'SELECT * FROM author WHERE author_id = ? ',(id,)
    ).fetchone()
    books = db.execute(
        'SELECT * FROM books b WHERE b.author_id = ? ',(id,)
    ).fetchall()
    return render_template('author/index.html', author=author, books=books)

def get_author(id, check_author=True):
    author = get_db().execute(
        'SELECT * FROM author WHERE author_id = ? ',(id,)
    ).fetchone()

    if author is None:
        abort(404, f"Author id {id} doesn't exist.")

    if check_author and author['author_id'] != g.user['id']:
        abort(403)

    return author

@bp.route('/author/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    db = get_db()
    author = get_author(id)
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'Please tell us something about you'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE author SET about = ?'
                ' WHERE author_id = ?',(body, id)
            )
            db.commit()
            return redirect(url_for('author.index', id=id))

    return render_template('author/update.html', author=author)

