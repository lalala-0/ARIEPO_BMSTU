# group_vars/web.yml

# 🌐 Основные настройки
nginx_user: nginx
nginx_worker_processes: auto
nginx_worker_connections: 2048
nginx_client_max_body_size: 100m
nginx_remove_default_vhost: true
nginx_listen_ipv6: true

# 📜 Глобальные директивы конфигурации
nginx_extra_conf_options: |
  user nginx;
  pid /run/nginx.pid;

nginx_extra_http_options: |
  server_tokens off;
  sendfile on;
  tcp_nopush on;
  tcp_nodelay on;
  keepalive_timeout 75;
  types_hash_max_size 2048;

# 📜 Пути к логам
nginx_access_log: "/var/log/nginx/access.log"
nginx_error_log: "/var/log/nginx/error.log"

# 🔁 Балансировка нагрузки
nginx_upstreams:
  - name: myapp_backend
    strategy: least_conn
    servers:
      - "192.168.0.10"
      - "192.168.0.11"

# 🌐 Виртуальные хосты
nginx_vhosts:
  - listen: "443 ssl http2"
    server_name: "myapp.example.com"
    root: "/var/www/myapp"
    index: "index.html index.htm"
    access_log: "/var/log/nginx/myapp_access.log"
    error_log: "/var/log/nginx/myapp_error.log"
    extra_parameters: |
      location / {
        try_files $uri $uri/ =404;
      }
      # SSL настройки
      ssl_certificate     /etc/ssl/certs/myapp.crt;
      ssl_certificate_key /etc/ssl/private/myapp.key;
      ssl_protocols       TLSv1.2 TLSv1.3;
      ssl_ciphers         HIGH:!aNULL:!MD5;

  - listen: "80"
    server_name: "myapp.example.com www.myapp.example.com"
    return: "301 https://myapp.example.com$request_uri"
    filename: "myapp-redirect.conf"

  - listen: "80"
    server_name: "loadbalanced.example.com"
    extra_parameters: |
      location / {
        proxy_pass http://myapp_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
      }

# ⚙️ Управление сервисом
nginx_service_state: started
nginx_service_enabled: true
