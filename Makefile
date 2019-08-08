
build:
		docker build -t python_repl $(CURDIR)

start-server:
		docker run -it --rm -p 9000:9000 python_repl
