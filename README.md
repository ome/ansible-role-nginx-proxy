Nginx Proxy
===========

[![Actions Status](https://github.com/ome/ansible-role-nginx-proxy/workflows/Molecule/badge.svg)](https://github.com/ome/ansible-role-nginx-proxy/actions)
[![Ansible Role](https://img.shields.io/badge/ansible--galaxy-nginx_proxy-blue.svg)](https://galaxy.ansible.com/ui/standalone/roles/ome/nginx_proxy/)

Install Nginx for use as a front-end proxy.


Dependencies
------------

Requires the `nginx` role (automatically included).


Role Variables: Main Nginx configuration
----------------------------------------

- `nginx_proxy_worker_processes`: Number of worker processes, default 1
- `nginx_proxy_worker_connections`: Number of worker connections, default 1024
- `nginx_proxy_buffers`: Number and size of proxy buffers (optional)
- `nginx_dynamic_proxy_resolvers`: If the proxied servers are referred to by hostname instead of IP addresses you must provide at least one DNS server


Role Variables: Main site
-------------------------

- `nginx_proxy_server_name`: The server name, default `$hostname`.
  Set this if you are configuring a virtualhost.
- `nginx_proxy_listen_http`: Listen on this port, default `80`.
- `nginx_proxy_cachebuster_port`: An alternative port which can be used to force a cache refresh, disabled by default.
  You should ensure this is firewalled.
  You must also set `nginx_proxy_cachebuster_enabled` to enable this for individual sites.
- `nginx_proxy_404`: The URI to show for 404 errors, default ''.
- `nginx_proxy_log_format_custom`: Additional Nginx log format, will be named `custom`. This only adds the format, to use it as the default log format you should set `nginx_proxy_log_format: custom`.

SSL variables:

- `nginx_proxy_ssl`: If `True` enable SSL on port `443`, default `False`
- `nginx_proxy_hsts_age`: The max-age in seconds for a HSTS (HTTP Strict Transport Security) header, default is to omit this header
- `nginx_proxy_http2`: If `True` enable HTTP2, default `False`
- `nginx_proxy_force_ssl`: If `True` permanently redirect all `http` requests to `https`, default `False`

If SSL is enabled you should install the certificates on the server and set the following two variables:

- `nginx_proxy_ssl_certificate`: Server path to SSL certificate
- `nginx_proxy_ssl_certificate_key`: Server path to SSL certificate key

Optionally this role can handle the certificate installation for you, if you specify the local source paths (default empty, you must handle the installation yourself):

- `nginx_proxy_ssl_certificate_source_path`: Local path to SSL certificate
- `nginx_proxy_ssl_certificate_key_source_path`: Local path to SSL certificate key

Backend servers:

- `nginx_proxy_backends`: List of dictionaries of backend servers with fields
  - `name`: A variable name for proxies using dynamic IP (ignored for static IPs)
  - `location`: The URL location
  - `limit_methods`: Limit to these HTTP methods only, default all
  - `server`: The backend server including scheme
  - `dynamic`: If `True` lookup IP on every request, default `False` (only lookup at startup).
  - `cache_validity`: The time that an object should be cached for, if omitted caching is disabled for this backend
  - `websockets`: If `True` enable proxying of websockets, default `False`
  - `websocketsonly`: If `True` and `websockets: True` only allow websocket requests, otherwise return HTTP status 400, default `False`
  - `read_timeout`: The proxy read timeout, optional
  - `host_header`: Optionally set the Host header, you shouldn't need to set this unless you're trying to work around bugs in applications
  - `maintenance_flag`: Name of an optional local flag file used to indicate the backend is undergoing maintenance, if this file exists `maintenance_uri` will be returned for this location with a `503` error
  - `maintenance_uri`: URI to a maintenance page that will be returned if the `maintenance_flag` file exists

- `nginx_proxy_upstream_servers`: List of dictionaries of backend servers used for load-balancing with fields:
  - `name`: The name of the load-balancing group (can be referenced in `nginx_proxy_backends.[].server`)
  - `balance`: Load balancing algorithm
  - `servers`: List of backend servers to be load-balanced
  - `additional`: List of additional directives

- `nginx_proxy_streams`: List of dictionaries of backend streaming servers
  - `name`: A variable name used for grouping multiple upstream servers
  - `port`: The port Nginx should listen on
  - `servers`: A list of backend servers, each item may include server specific parameters
  - `timeout`: Timeout between successive reads/writes
  - `connect_timeout`: Backend connection timeout

Warning: Using non-standard http ports in `nginx_proxy_streams` may lead to SELinux failures. This role will attempt to configure SELinux but may fail.

Redirection:

- `nginx_proxy_redirect_map`: List of dictionaries of URL redirects with fields:
  - `match`: The request uri to match (operators such as ~ are allowed, matching can include query arguments)
  - `dest`: The new uri
- `nginx_proxy_redirect_map_locations`: List of dictionaries of locations to be mapped using `nginx_proxy_redirect_map`
  - `location`: An nginx location to be mapped
  - `code`: Optional HTTP redirect status code, default `302` (use `301` for a permanent redirect)
- `nginx_proxy_direct_locations`: List of dictionaries of locations to be handled directly with the following fields. `location` is required, along with at least one of the other fields:
  - `location`: An nginx location to be mapped (required)
  - `redirect301`: The new uri to redirect to with code 301
  - `redirect302`: The new uri to redirect to with code 302
  - `index`: Nginx index locations
  - `root`: Root directory for requests
  - `alias`: Alias this directory to location
  - `custom`: List of additional configuration directives

- `nginx_proxy_block_locations`: List of locations which should be blocked (404)

Use `nginx_proxy_direct_locations` with `redirect*` if you need to redirect based on Nginx `location` only, use `nginx_proxy_redirect_map` with `nginx_proxy_redirect_map_locations` if you also want to redirect based on query arguments.

Websockets:

- `nginx_proxy_websockets_enable`: This must be `True` if any proxies require proxying of websockets, default `False`

Caching:

- `nginx_proxy_cache_parent_path`: The parent directory for the nginx caches (optional)
- `nginx_proxy_caches`: List of dictionaries of cache specifications with fields:
  - `name`: Name of the cache
  - `keysize`: Amount of shared memory to use for storing cache keys
  - `maxsize`: Upper limit of the size of the cache
  - `inactive`: Time that items should be cached for
  - `match`: List of patterns to be stored in this cache, you probably want one item with the value `default` somewhere
- `nginx_proxy_cache_skip_uri`: List of URI patterns that shouldn't be cached (default: everything that doesn't match `nginx_proxy_cache_match_uri`)
- `nginx_proxy_cache_match_uri`: List of URI patterns that should be cached
- `nginx_proxy_cache_skip_arg`: List of query patterns that shouldn't be cached (default for this is always the result of `nginx_proxy_cache_*_url`)
- `nginx_proxy_cache_match_arg`: List of query patterns that should be cached (default for this is always the result of `nginx_proxy_cache_*_url`)

- `nginx_proxy_set_header_host`: Override the hostname seen by the backend proxy, default is to use the Nginx `$host` variable (recommended for most cases)
- `nginx_proxy_forward_scheme_header`: A header to be set containing the scheme (e.g. `http`, `https`) that will be passed to the backend
- `nginx_proxy_debug_cache_headers`: If `True` add extra headers for debugging (not for production), default `False`
- `nginx_proxy_cache_ignore_headers`: Headers to be ignored, e.g. `'"Set-Cookie" "Vary" "Expires"'`
- `nginx_proxy_cache_hide_headers`: Headers to be hidden from clients in cached responses, must be a list e.g. `[Set-Cookie]`
- `nginx_proxy_cache_key`: Override the default Nginx cache key, for example `"$host$request_uri"` to ignore session cookies
- `nginx_proxy_cache_key_map`: Optionally map `nginx_proxy_cache_key` to the desired cache key, for instance if you want to ignore part of the url. This should be a list of dictionaries with fields:
  - `match`: Match in nginx_proxy_cache_key
  - `key`: The cache key
`nginx_proxy_cache_key` is always included as the default.
- `nginx_proxy_cache_use_stale`: Situations in which stale cache results should be returned, see `defaults/main.yml` for default, if enabled this will also turn on background updates.
- `nginx_proxy_cache_lock_time`: Prevent multiple backend requests to the same object (subsequent requests will wait for the first to either return or time-out), default 1 minute
- `nginx_proxy_cachebuster_enabled`: Set to `True` to enable cache-busting on port `nginx_proxy_cachebuster_port`

Warning: for convenience, put `nginx_proxy_cache_parent_path` on a separate partition (calculate size of the partition based on `max_size` set on disk caches).

Warning: If SELinux is enabled you may need to update your policy yourself to allow Nginx to bind to a non-standard port (typically 80, 81, 443, 488, 8008, 8009, 8443, 9000 are allowed).

Additional custom configuration:

- `nginx_proxy_conf_http`: Additional directives to be added to top-level `http` context
- `nginx_proxy_additional_maps`: List of custom Nginx maps for use in other custom configuration
- `nginx_proxy_additional_directives`: List of additional directives to be added to the proxy `server` context
- `nginx_proxy_systemd_setup`: Start/restart nginx using systemd, default `true`, if you want to manage Nginx yourself set this to `false`


Role Variables: Multiple sites
------------------------------

- `nginx_proxy_sites`: Additional sites can be configured by creating an array of dictionaries overriding the above "Main site" parameters.
  The default: `nginx_proxy_sites: { nginx_proxy_is_default: True }` mean a single site will be created using the parameters defined above.
  Most parameters are supported in site specific configurations with the exception of those named `nginx_proxy_*cache*`, and `nginx_proxy_redirect_map`.
  One site-specific additional parameter is supported:
  - `nginx_proxy_is_default`: If `True` this is the default Nginx site, default `False`.


Example Playbooks
-----------------

Proxy:
- http://localhost/ to http://a.internal/ statically, make a single DNS request for `a.internal` at the start
- http://localhost/b to http://b.internal/subdir dynamically, making a DNS request for `b.internal` on every request

```yml
- hosts: localhost
  roles:
  - role: ome.nginx_proxy
    nginx_proxy_backends:
    - location: /
      server: http://a.internal
    - name: testb
      location: /b
      server: http://b.internal/subdir
      dynamic: True
```

Advanced configuration: force https, use HSTS, enable HTTP2

```yml
- hosts: localhost
  roles:
  - role: ome.nginx_proxy
    nginx_proxy_backends:
    - location: /
      server: http://a.internal
      cache_validity: 1h
    nginx_proxy_worker_processes: 4
    nginx_proxy_404: '/404.html'
    nginx_proxy_ssl: True
    nginx_proxy_ssl_certificate: /etc/nginx/ssl/website.crt
    nginx_proxy_ssl_certificate_key: /etc/nginx/ssl/website.key
    nginx_proxy_http2: True
    nginx_proxy_force_ssl: True
    nginx_proxy_hsts_age: 31536000
    nginx_proxy_conf_http:
      - "client_max_body_size 500m"
      - "server_tokens off"
```



Author Information
------------------

ome-devel@lists.openmicroscopy.org.uk
