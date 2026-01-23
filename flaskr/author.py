from flask import (
    Blueprint, render_template
)

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('author', __name__)

@bp.route('/author/<int:id>')
@login_required
def index(id):
    db = get_db()
    author = db.execute(
        'SELECT * FROM author WHERE author_id = ? ',(id,)
    ).fetchone()
    books = db.execute(
        'SELECT * FROM books b WHERE b.author_id = ? ', (id)
    ).fetchall()
    return render_template('author/index.html', author=author, books=books)