#!/usr/bin/env python3
"""
Mokuro Local Bookshelf Web Server
---------------------------------
Multi-threaded HTTP server for serving the Mokuro manga library.
Supports automatic browser opening, graceful shutdown, and port conflict resolution.
"""

import os
import sys
import time
import socket
import signal
import subprocess
import threading
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

SCRIPT_DIR = Path(__file__).resolve().parent
LIBRARY_DIR = SCRIPT_DIR / "manga_library"
DEFAULT_PORT = 8080


class QuietHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        # Format clean HTTP request logs
        sys.stderr.write(f"[{self.log_date_time_string()}] {fmt % args}\n")


def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("0.0.0.0", port))
            return True
        except OSError:
            return False


def find_free_port(start_port=DEFAULT_PORT, max_tries=50):
    for p in range(start_port, start_port + max_tries):
        if is_port_free(p):
            return p
    return start_port


def kill_process_on_port(port):
    """Attempt to terminate any process listening on the specified port."""
    try:
        out = subprocess.check_output(["lsof", "-ti", f":{port}"], text=True).strip()
        if out:
            pids = [int(p) for p in out.split() if int(p) != os.getpid()]
            for pid in pids:
                try:
                    os.kill(pid, signal.SIGTERM)
                except OSError:
                    pass
            time.sleep(0.5)
    except Exception:
        pass


def open_browser(port):
    """Wait for server to accept connections, then open browser."""
    url = f"http://localhost:{port}"
    for _ in range(30):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                break
        time.sleep(0.1)

    try:
        subprocess.Popen(
            ["xdg-open", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


def main():
    port = DEFAULT_PORT

    # If port 8080 is already occupied, check if we should free it or increment
    if not is_port_free(port):
        kill_process_on_port(port)

    # If still not free (e.g. non-user process), find the next available port
    if not is_port_free(port):
        free_port = find_free_port(port + 1)
        print(f"⚠️  Port {port} is busy. Switched to port {free_port}.")
        port = free_port

    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    os.chdir(str(LIBRARY_DIR))

    handler = partial(QuietHandler, directory=str(LIBRARY_DIR))

    try:
        server = ThreadingHTTPServer(("0.0.0.0", port), handler)
    except Exception as e:
        print(f"❌ Failed to bind to port {port}: {e}", file=sys.stderr)
        sys.exit(1)

    print("==========================================================")
    print("🌸 Mokuro Manga Library Server")
    print("==========================================================")
    print(f"Serving bookshelf at: http://localhost:{port}")
    print(f"Serving directory:    {LIBRARY_DIR}")
    print("")
    print("Press Ctrl+C to stop the server.")
    print("==========================================================")

    # Launch browser in a background thread
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # Graceful shutdown handler
    def shutdown_signal(sig, frame):
        print("\n🛑 Stopping server...")
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGINT, shutdown_signal)
    signal.signal(signal.SIGTERM, shutdown_signal)

    try:
        server.serve_forever()
    except Exception:
        pass
    finally:
        server.server_close()
        print("🛑 Server stopped cleanly.")


if __name__ == "__main__":
    main()
