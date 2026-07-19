#!/bin/bash
# Serve the pre-built pygbag output
cd build/web
python -m http.server 5000
