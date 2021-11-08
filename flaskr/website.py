from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('website', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, created, note, tip, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('website/index.html', posts=posts)

@bp.route('/create()', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        note = request.form['note']
        tip = request.form['tip']
        error = None

        if not tip:
            erorr = 'Tip is required.'

        if error is not None:
            flash(error)     
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (note, tip, author_id)'
                ' VALUES (?, ?, ?)',
                (note, tip, g.user['id'])
            )        
            db.commit()
            return redirect(url_for('website.index'))

    return render_template('website/create.html')    

def get_post(id, check_author=True):
    post =  get_db().execute(
        'SELECT p.id, author_id, created, note, tip, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403) 

    return post    

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        tip = request.form['tip']
        note = request.form['note']   
        error = None

        if not tip:
            error = 'Tip is required'

        if error is not None:
            flash(error)
        else:
            db =  get_db()
            db.execute(
                'UPDATE post SET tip = ?, note = ?'
                ' WHERE id = ?',
                (tip,note,id)
            )
            db.commit()
            return redirect(url_for('website.index'))

    return render_template('website/update.html', post=post)     

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))    
    db.commit()
    return redirect(url_for('website.index'))             

