"""
Waitress Server for Shahebaz Motors
====================================
Production-grade server for Windows.
Better than Flask's development server.

Run with:
    python run_server.py
"""

from waitress import serve
from app import app

# =========================================================
# CONFIGURATION
# =========================================================

HOST = "0.0.0.0"
PORT = 5000

# Number of threads (for concurrent requests)
# 4 threads = 4 concurrent users can be served
THREADS = 8

# Connection limit
CONNECTION_LIMIT = 100

# Channel timeout
CHANNEL_TIMEOUT = 120


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print("     SHAHEBAZ MOTORS - PRODUCTION SERVER")
    print("     (Powered by Waitress)")
    print("==========================================")
    print(f"Server:      http://{HOST}:{PORT}")
    print(f"Threads:     {THREADS}")
    print(f"Max Conns:   {CONNECTION_LIMIT}")
    print("------------------------------------------")
    print("⚠️  This is a PRODUCTION server")
    print("⚠️  NOT for development")
    print("⚠️  Press Ctrl+C to stop")
    print("==========================================")
    print()

    serve(
        app,
        host=HOST,
        port=PORT,
        threads=THREADS,
        connection_limit=CONNECTION_LIMIT,
        channel_timeout=CHANNEL_TIMEOUT,
        ident="Shahebaz Motors"
    )