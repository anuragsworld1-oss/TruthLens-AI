"""
TruthLens AI - Backend Server Entrypoint
"""

import os
import sys

# Ensure backend directory is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] TruthLens AI Backend Server listening on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)
