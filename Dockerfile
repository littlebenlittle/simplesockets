from python:3.7

workdir /app
copy server.py server.py
run touch docker-lock
cmd [ "./server.py" ]
