
blog-gen:
	@echo "Generating blog..."
	@poetry run python main.py 
	@echo "Done."

playground:
	@echo "Starting playground..."
	# set current folder to simple-prompt
	@cd blog_writer/simple-prompt && PYTHONPATH=$(PWD) poetry run python playground.py
	@echo "Done."