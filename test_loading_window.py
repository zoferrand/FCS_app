import webview
from webview import FileDialog
import os

opening_file_window = webview.create_window(
    " ",
    "opening_file_window.html",
    width=800,
    height=480,
)

webview.start(gui="qt")
        