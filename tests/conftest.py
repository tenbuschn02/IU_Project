from website.models import User, Note, Guest, Food, AcceptedRatio, Table, Costs
from website.auth import login
from website import create_app
import pytest
import os
import tempfile
from flask.testing import FlaskClient
import functools


@pytest.fixture(scope='module')
def flask_app():
    app = create_app()
    with app.app_context():
        yield app


@pytest.fixture(scope='module')
def client(flask_app):
    app = flask_app
    ctx = flask_app.test_request_context()
    ctx.push()
    app.test_client_class = FlaskClient
    return app.test_client()


def force_login(user_id=None):
    def inner(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if user_id:
                for key, val in kwargs.items():
                    if isinstance(val, FlaskClient):
                        with val:
                            with val.session_transaction() as sess:
                                sess['_user_id'] = user_id
                            return f(*args, **kwargs)
            return f(*args, **kwargs)

        return wrapper

    return inner
    

