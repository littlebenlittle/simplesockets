
# Super Simple REPL Server

*Because the client is able to execute arbitrary python commands, the server should never be run outside of a sandboxed environment.*

	make build
	make start-server

	echo "x = 1\nx += 1\nprint(x)" | client.py
