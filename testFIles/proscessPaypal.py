import re
import json

from flask import request, render_template, redirect, Flask
from werkzeug.datastructures import ImmutableOrderedMultiDict
import requests



import config

app = Flask(__name__)

@app.route('/ipn', methods=['POST'])
def ipn():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = (json.dumps(request.form))
    print(rsp)
    return (" ",200)




if __name__ == '__main__':
    app.debug = True
    app.run("127.0.0.1", 5000)