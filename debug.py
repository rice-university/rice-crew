#! /usr/bin/env python
import sys
from ricecrew.loader import app

if len(sys.argv) > 1:
    app.run(host=sys.argv[1], debug=True)
else:
    app.run(debug=True)

