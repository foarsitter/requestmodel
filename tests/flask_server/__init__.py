from a2wsgi import WSGIMiddleware
from flask import Flask
from flask import Response
from flask import jsonify
from flask import request
from flask_wtf import FlaskForm  # type: ignore
from starlette.testclient import TestClient
from wtforms import StringField  # type: ignore
from wtforms.validators import DataRequired  # type: ignore


class MyForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])


app = Flask(__name__)


@app.route("/submit", methods=["POST"])
def submit() -> Response:
    data = request.form

    print(data)

    form = MyForm(meta={"csrf": False})
    if form.validate_on_submit():
        return jsonify({"errors": {}})
    return jsonify({"errors": form.errors})


client = TestClient(WSGIMiddleware(app))  # type: ignore
