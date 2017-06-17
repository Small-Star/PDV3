#!PDV3/bin/python
import sys
sys.path.insert(0, './app')
from app import app
app.run(debug=True)
