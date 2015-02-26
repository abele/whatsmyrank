import pytest
import py

@pytest.fixture(scope='session')
def database_url():
    return str(py.path.local('test.shelve'))

