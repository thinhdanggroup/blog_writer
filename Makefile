
PORT=6123

gen-blog:
	@echo "Generating blog..."
	@poetry run python main.py 
	@echo "Done."

playground:
	@echo "Starting playground..."
	# set current folder to simple-prompt
	@cd blog_writer/simple-prompt && PYTHONPATH=$(PWD) poetry run python playground.py
	@echo "Done."

server-tunnel:
	@echo "Starting server tunnel..."
	@hrzn tunnel http://localhost:$(PORT)
	@echo "Done."

server-up:
	@PORT=$(PORT) poetry run python web_server.py

# Start both server and tunnel
up:
	@echo "Starting server and tunnel..."
	@DEBUG=false PORT=$(PORT) poetry run python web_server.py & \
	hrzn tunnel http://localhost:$(PORT) & \
	echo "Server and tunnel started. Use 'make down' to stop."

# Stop all related processes
down:
	@echo "Stopping server and tunnel..."
	@pkill -f "python web_server.py" || true
	@pkill -f "hrzn tunnel" || true
	@echo "Server and tunnel stopped."
