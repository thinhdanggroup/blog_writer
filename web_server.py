from flask import Flask, render_template, request, jsonify, Response, send_file
import os
import queue
import threading
from blog_writer.core.generate import generate
from blog_writer.utils.file import read_file
import markdown
from datetime import datetime

from flask import Flask, render_template, request, jsonify, Response
import os
import queue
import threading
from blog_writer.core.generate import generate
from blog_writer.utils.file import read_file
import logging
import sys
from io import StringIO

app = Flask(__name__)

# Create a queue for log messages
log_queue = queue.Queue()

# Create a custom log handler that puts messages in our queue
class QueueHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_queue.put(log_entry)

# Configure logging to use our custom handler
queue_handler = QueueHandler()
queue_handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))

# Add handler to root logger to capture all logs
logging.getLogger().addHandler(queue_handler)

@app.route('/')
def index():
    # Get list of existing folders
    folders = get_workspace_folders()
    
    # Get content from input.txt if it exists
    input_content = ""
    if os.path.exists("input.txt"):
        input_content = read_file("input.txt")
    
    return render_template('web_ui.html', 
                         input_content=input_content,
                         last_folder=folders[0] if folders else None,
                         folders=folders)

@app.route('/stream')
def stream():
    def generate_log_stream():
        while True:
            try:
                # Get message from queue, waiting up to 1 second
                message = log_queue.get(timeout=1)
                yield f"data: {message}\n\n"
            except queue.Empty:
                # If no message received after timeout, send a heartbeat
                yield f"data: heartbeat\n\n"
    
    return Response(generate_log_stream(), mimetype='text/event-stream')

@app.route('/generate', methods=['POST'])
def generate_blog():
    data = request.get_json()
    blog_topic = data.get('topic', '')
    use_last_folder = data.get('use_last_folder', False)
    workspace = None
    
    def run_generation(result):
        try:
            # Save topic to input.txt
            with open("input.txt", "w") as f:
                f.write(blog_topic)
            
            subject = f'Write a blog about\n"""{blog_topic}\n"""'
            load_from = ""
            
            if use_last_folder:
                folders = [f for f in os.listdir(".working_space") if f[0].isdigit()]
                folders.sort()
                if folders:
                    load_from = folders[-1]
            
            result['workspace'] = generate(subject, load_from)
            log_queue.put("Blog generation completed successfully")
        except Exception as e:
            log_queue.put(f"Error: {str(e)}")
    
    # Dictionary to store the result
    result = {'workspace': None}
    
    # Run generation in a separate thread
    thread = threading.Thread(target=run_generation, args=(result,))
    thread.start()
    
    return jsonify({
        "status": "success", 
        "message": "Blog generation started",
        "workspace": result['workspace']
    })

def get_workspace_folders():
    working_space = ".working_space"
    if not os.path.exists(working_space):
        return []
    folders = [f for f in os.listdir(working_space) if f[0].isdigit()]
    folders.sort(reverse=True)  # Most recent first
    return folders

def get_markdown_content(workspace):
    worksapce_path = os.path.join(".working_space", workspace)
    final_dir = os.path.join(worksapce_path, "final")
    if not os.path.exists(final_dir):
        return None
        
    # Find any markdown file in the final directory
    md_files = [f for f in os.listdir(final_dir) if f.endswith('.md')]
    if not md_files:
        return None
        
    md_file = os.path.join(final_dir, md_files[0])
    content = read_file(md_file)
    return content

@app.route('/blog/<workspace>')
def view_blog(workspace):
    content = get_markdown_content(workspace)
    if content is None:
        return "Blog not found", 404
    
    # Convert markdown to HTML
    html = markdown.markdown(content, extensions=['extra', 'toc'])
    
    # Get list of all workspace folders
    folders = get_workspace_folders()
    
    return render_template('blog_view.html', 
                         content=html,
                         folders=folders,
                         current_workspace=workspace)

if __name__ == '__main__':
    debug = True if os.getenv('DEBUG', 'false').lower() == 'true' else False
    app.run(debug=debug, port=int(os.getenv('PORT', 5000)))
