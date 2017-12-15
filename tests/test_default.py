import testinfra.utils.ansible_runner
import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


def test_service_running_and_enabled(Service):
    service = Service('nginx')
    assert service.is_running
    assert service.is_enabled


@pytest.mark.parametrize("uri,expecturi,expectcode", [
    ('/map?search=abc1', '/redirectmap?query=def2', 302),
    ('/map?search=other', '/redirectmap', 302),
    ('/direct/', '/redirect', 301),
    ('/redirect/', '/default', 302),
    ('/map', '/redirectmap', 302),
    ('/default', '/default/', 301),
])
def test_redirects(Command, uri, expecturi, expectcode):
    out = Command.check_output("curl -I http://localhost%s" % uri)
    assert ('HTTP/1.1 %d' % expectcode) in out
    assert ('Location: http://localhost%s' % expecturi) in out


def test_get_alias(Command):
    out = Command.check_output("curl http://localhost/default/")
    assert '<title>Welcome to nginx!</title>' in out


@pytest.mark.parametrize("method,expectcode", [
    ('GET', 200),
    ('POST', 403),
])
def test_proxy_limit_method(Command, method, expectcode):
    out = Command.check_output(
        "curl -I -X %s -H 'Host: other' http://localhost/limitget/" % method)
    assert ('HTTP/1.1 %d' % expectcode) in out


@pytest.mark.parametrize("path", [
    'nginx.conf',
    'conf.d',
    'stream-conf.d',
])
def test_compare_config(Command, path):
    # Check the exit code separately so that the diff is printed out first
    c = Command('diff -Nur /root/etc-nginx/%s /etc/nginx/%s' % (
        path, path))
    assert c.stdout == ''
    assert c.rc == 0
