from flask import render_template

from .. import wordseer

@wordseer.route('/app/')
def ext_app():
    return render_template('app.html')
