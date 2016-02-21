bind = '127.0.0.1:60000'
workers = 16
threads = 16
pidfile = 'gunicorn.pid'
errorlog = 'errorlog'
# debug = True


# nohup gunicorn wordseer:app -b 127.0.0.1:60000 -w 16 >> /projects/wordseer/flask_demo/wordseer_demo.out 2>&1 &