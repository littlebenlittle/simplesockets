from python:3.7

workdir /app
copy server.py server.py
copy __init__.py __init__.py
copy conf.py conf.py
run touch docker-lock
cmd [ "./server.py" ]
