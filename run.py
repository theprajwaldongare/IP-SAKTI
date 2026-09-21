import uvicorn
import os
import sys

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure backend root directory is in python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# this is nothing
# if __name__ == "__main__":
#     print("------------------------------------------------------------------")
#     print("Starting IP Sakti Backend Server (FastAPI + RAG Engine)...")
#     print("Server URL: http://127.0.0.1:8000")
#     print("Swagger Docs: http://127.0.0.1:8000/docs")
#     print("------------------------------------------------------------------")
#     uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    print("------------------------------------------------------------------")
    print("Starting IP Sakti Backend Server (FastAPI + RAG Engine)...")
    print("------------------------------------------------------------------")
    # Cloud providers require 0.0.0.0 to allow external web traffic
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
