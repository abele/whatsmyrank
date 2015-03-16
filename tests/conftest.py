import py
import pytest
import shelve


@pytest.fixture(scope='session')
def database_url():
    return str(py.path.local('test.shelve'))


@pytest.fixture(scope='function', autouse=True)
def clear_database(database_url):
    with shelve.open(database_url) as db:
        db.clear()
