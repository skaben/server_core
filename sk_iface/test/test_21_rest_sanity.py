import requests
import pytest
import json

root_url = 'http://192.168.0.200:8000/api'

from sk_iface.models import Terminal

#request = factory.post('/notes/', {'title': 'new idea'})
@pytest.mark.parametrize('url', ('/states', '/terms', '/locks'))
def test_get_200(url):
    try:
        response = requests.get(root_url + url)
        assert response.status_code == 200, response._content
    except requests.exceptions.ConnectionError:
        pytest.fail(f"server on {root_url} seems down")


def test_get_term_list():
    response = requests.get(root_url + '/terms')
    decoded = json.loads(response._content.decode('utf-8'))
    assert 1 == 0, decoded
    assert decoded.get('url'), 'bad response - no url'
