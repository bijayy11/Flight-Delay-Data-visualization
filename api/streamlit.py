import os
import subprocess
from flask import Flask, request

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def streamlit_proxy(path):
    # Start the Streamlit app if it's not already running
    streamlit_port = 8501
    if not os.path.exists(".streamlit/active"):
        subprocess.Popen(["streamlit", "run", "viznew.py", "--server.port", str(streamlit_port)])
        open(".streamlit/active", "w").close()
    
    # Proxy requests to the Streamlit app
    return f"Streamlit app is running at http://localhost:{streamlit_port}/{path}"

if __name__ == "__main__":
    app.run()
