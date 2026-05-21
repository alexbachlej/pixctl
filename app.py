from src.config import HOST, PORT, init_dirs
from src.ui import build_ui

if __name__ == "__main__":
    init_dirs()
    demo = build_ui()
    demo.launch(server_name=HOST, server_port=PORT)
