from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.author import get_author
from flaskr.db import get_db

bp = Blueprint('books', __name__, url_prefix='/books')

@bp.route('/')
def index():
    db = get_db()
    books = db.execute(
        'SELECT b.id, title, description, created, author_id, username'
        ' FROM books b JOIN user u ON b.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('books/index.html', books=books)

@bp.route('/<int:id>')
def book(id):
    db = get_db()
    book = db.execute(
        'SELECT b.id, title, description, created, author_id, username'
        ' FROM books b JOIN user u ON b.author_id = u.id'
        ' WHERE b.id = ?', (id,)
    ).fetchone()
    author = db.execute(
        'SELECT * FROM author WHERE author.author_id = ?', (book['author_id'],)
    ).fetchone()
    return render_template('books/book.html', book=book, author=author)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO books (title, description, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('books.index'))

    return render_template('books/create.html')

def get_post(id, check_author=True):
    book = get_db().execute(
        'SELECT b.id, title, description, created, author_id, username'
        ' FROM books b JOIN user u ON b.author_id = u.id'
        ' WHERE b.id = ?',
        (id,)
    ).fetchone()

    if book is None:
        abort(404, f"Book id {id} doesn't exist.")

    if check_author and book['author_id'] != g.user['id']:
        abort(403)

    return book


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    book = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE books SET title = ?, description = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('books.book', id=id))

    return render_template('books/update.html', book=book)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM books WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('books.index'))