import os
import pytest
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_service_running_and_enabled(host):
    assert host.service('nginx').is_running
    assert host.service('nginx').is_enabled


@pytest.mark.parametrize("uri,expecturi,expectcode", [
    ('/map?search=abc1', '/redirectmap?query=def2', 302),
    ('/map?search=other', '/redirectmap', 302),
    ('/direct/', '/redirect', 301),
    ('/redirect/', '/default', 302),
    ('/map', '/redirectmap', 302),
    ('/default', '/default/', 301),
])
def test_redirects(host, uri, expecturi, expectcode):
    out = host.check_output("curl -I http://localhost%s" % uri)
    assert ('HTTP/1.1 %d' % expectcode) in out
    assert ('Location: http://localhost%s' % expecturi) in out


def test_get_alias(host):
    out = host.check_output("curl http://localhost/default/")
    assert '<title>Welcome to nginx!</title>' in out


@pytest.mark.parametrize("method,expectcode", [
    ('GET', 200),
    ('POST', 403),
])
def test_proxy_limit_method(host, method, expectcode):
    out = host.check_output(
        "curl -I -X %s -H 'Host: other' http://localhost/limitget/" % method)
    assert ('HTTP/1.1 %d' % expectcode) in out


@pytest.mark.parametrize("path", [
    'nginx.conf',
    'conf.d',
    'stream-conf.d',
])
def test_compare_config(host, path):
    # Check the exit code separately so that the diff is printed out first
    c = host.run('diff -Nur /root/etc-nginx/%s /etc/nginx/%s' % (
        path, path))
    assert c.stdout == ''
    assert c.rc == 0


def test_maintenance_page(host):
    flag = '/srv/maintenance-test.flag'
    host.check_output('rm -f %s', flag)
    out1 = host.check_output('curl -I http://localhost/maintenance-test/')
    assert 'HTTP/1.1 404' in out1
    host.check_output('touch %s', flag)
    out2 = host.check_output('curl -i http://localhost/maintenance-test/')
    assert 'HTTP/1.1 503' in out2
    assert '<title>Maintenance</title>' in out2
    host.check_output('rm -f %s', flag)
