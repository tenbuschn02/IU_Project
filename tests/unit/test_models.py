from website.models import User, Note, Guest, Food, AcceptedRatio, Table, Costs
#create groupes and create status is only tested when creating a new database

def test_new_user():
    
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email and the password are defined correctly
    """
    new_user = User(email='test@web.de', first_name='first_name', password='password')
    assert new_user.email == 'test@web.de'
    assert new_user.password == 'password'
    assert new_user.first_name == 'first_name'

def test_new_note():
 
    """
    GIVEN a Note model
    WHEN a new Note is added for user 123
    THEN check note data and the userid is defined correctly
    """
    new_note = Note(data='test', user_id=123)
    assert new_note.data == 'test'
    assert new_note.user_id == 123

def test_new_guest():
    """
    GIVEN a Guest model
    WHEN a new Guest is added for user 123
    THEN check guest name, invatiation status, group, status and the userid is defined correctly
    """
    new_guest = Guest(name='guest', user_id=123, invitation_sent=False, group_id=1, status_id=1)
    assert new_guest.name == 'guest'
    assert new_guest.user_id == 123
    assert new_guest.invitation_sent == False
    assert new_guest.status_id == 1

def test_new_food():
    """
    GIVEN a Food model
    WHEN a new Food is added for user 123
    THEN check guest name, invatiation status, group, status and the userid is defined correctly
    """
    new_food = Food(name='food_name', user_id=123, price=1, amount_1=2, amount_2=3, amount_3=4)
    assert new_food.name == 'food_name'
    assert new_food.user_id == 123
    assert new_food.price == 1
    assert new_food.amount_1 == 2
    assert new_food.amount_2 == 3
    assert new_food.amount_3 == 4

def test_new_ratio():
    """
    GIVEN a Accepted_Ratio model
    WHEN a new ratio is added for user 123
    THEN check ratio and userid is defined correctly
    """
    new_accepted_ratio = AcceptedRatio(ratio=80, user_id=123)
    assert new_accepted_ratio.user_id == 123
    assert new_accepted_ratio.ratio == 80

def test_new_table():
    """
    GIVEN a Table model
    WHEN a new table is added for user 123
    THEN check table_name, max_guests and userid is defined correctly
    """
    new_table = Table(name='table_name', user_id=123, max_guests=10)
    assert new_table.user_id == 123
    assert new_table.max_guests == 10
    assert new_table.name == 'table_name'

def test_new_costs():
    """
    GIVEN a Costs model
    WHEN a new Cost is added for user 123
    THEN check name, price and userid is defined correctly
    """
    new_costs = Costs(name='cost_name', user_id=123, price=10)
    assert new_costs.user_id == 123
    assert new_costs.price == 10
    assert new_costs.name == 'cost_name'
