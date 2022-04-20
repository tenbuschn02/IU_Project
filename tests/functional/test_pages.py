from tests.conftest import force_login

#access to login and sign-up page should work without logged in user
def test_login_without_login(client):
    """
    GIVEN a Flask application
    WHEN the /login page is requested without login
    THEN check that a '200' status code is returned and the correct template is returned
    """
    response = client.get('/login')
    assert response.status_code == 200
    assert b'<h2 align="center">Login</h2>' in response.data

def test_signup_without_login(client):
    """
    GIVEN a Flask application
    WHEN the /sign-up page is requested without login
    THEN check that a '200' status code is returned and the correct template is returned
    """
    response = client.get('/sign-up')
    assert response.status_code == 200
    assert b'<h2 align="center"> Sign Up</h2>' in response.data

#access should be denied without login --> redirect to login page
def test_home_without_login(client):
    """
    GIVEN a Flask application
    WHEN the / page is requested without login
    THEN check that a '302' status code is returned and it redirects to the login page
    """
    response = client.get('/')
    assert response.status_code == 302
    assert b'href="/login' in response.data


def test_foodcalc_without_login(client):
    """
    GIVEN a Flask application
    WHEN the /foodcalc page is requested without login
    THEN check that a '302' status code is returned and it redirects to the login page
    """
    response = client.get('/foodcalc')
    assert response.status_code == 302
    assert b'href="/login' in response.data

def test_finances_without_login(client):
    """
    GIVEN a Flask application
    WHEN the /finances page is requested without login
    THEN check that a '302' status code is returned and it redirects to the login page
    """
    response = client.get('/finances')
    assert response.status_code == 302
    assert b'href="/login' in response.data

def test_guestlist_withoutlogin(client):
    """
    GIVEN a Flask application
    WHEN the /guest-list page is requested without login
    THEN check that a '302' status code is returned and it redirects to the login page
    """
    response = client.get('/guest-list')
    assert response.status_code == 302
    assert b'href="/login' in response.data

def test_table_without_login(client):
    """
    GIVEN a Flask application
    WHEN the /table-overview page is requested without login
    THEN check that a '302' status code is returned and it redirects to the login page
    """
    response = client.get('/table-overview')
    assert response.status_code == 302
    assert b'href="/login' in response.data


#access possible with login

@force_login(user_id=1)
def test_home_with_login(client):
    """
    GIVEN a Flask application
    WHEN the / page is requested with login
    THEN check that a '200' status code is returned and the correct template is returned
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data

@force_login(user_id=1)
def test_guestlist_with_login(client):
    """
    GIVEN a Flask application
    WHEN the /guest-list page is requested with login
    THEN check that a '200' status code is returned and the correct template is returned
    """
    response = client.get('/guest-list')
    assert response.status_code == 200
    assert b'<h1 align="center">Guest List</h1>' in response.data

@force_login(user_id=1)
def test_finances_with_login(client):
    """
    GIVEN a Flask application
    WHEN the /finances page is requested with login
    THEN check that a '200' status code is returned and the correct template is returned
    """
    response = client.get('/finances')
    assert response.status_code == 200
    assert b'<h1 align="center">Finances</h1>' in response.data

@force_login(user_id=1)
def test_tables_with_login(client):
    """
    GIVEN a Flask application
    WHEN the /table-overview page is requested with login
    THEN check that a '200' status code is returned and the correct template is returned
    """
    response = client.get('/table-overview')
    assert response.status_code == 200
    assert b'<h1 align="center">Table Overview</h1>' in response.data

@force_login(user_id=1)
def test_foodcalc_with_login(client):
    """
    GIVEN a Flask application
    WHEN the /foodcalc page is requested with login
    THEN check that a '200' status code is returned and the correct template is returned
    """
    response = client.get('/foodcalc')
    assert response.status_code == 200
    assert b'<h1 align="center">Food Calculator</h1>' in response.data
