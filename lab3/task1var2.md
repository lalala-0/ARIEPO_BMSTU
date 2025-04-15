# Установка и настройка сервисов на **ВМ1** (ROUTER):
- Установить и настроить Nginx:

    -  Поднять Nginx для мониторинга через его status страницу.

    - Настройка Nginx для мониторинга через статус-страницу
Nginx предоставляет встроенную страницу статуса для мониторинга состояния сервера. Для этого необходимо активировать stub_status.

Откройте конфигурационный файл для создания нового server блока:

```
sudo nano /etc/nginx/sites-available/status.conf
```
Вставьте следующую конфигурацию для Nginx:

```
server {
    listen 8081;
    server_name localhost;

    location /status {
        stub_status on;
        access_log off;
        allow 127.0.0.1;  # Разрешаем доступ только с локальной машины
        deny all;         # Запрещаем доступ из других источников
    }
}
```
Теперь создайте символическую ссылку на этот конфиг в директорию sites-enabled:

```
sudo ln -s /etc/nginx/sites-available/status.conf /etc/nginx/sites-enabled/
```
Проверьте синтаксис конфигурации и перезагрузите Nginx, чтобы применить изменения:

```
sudo nginx -t
sudo systemctl reload nginx
```

Теперь Nginx будет доступен по адресу http://localhost:8081/status, где будет выводиться информация о текущем состоянии сервера, включая количество активных подключений, обрабатываемые запросы и т. д.

- Установить и настроить Prometheus:

    - Установить Prometheus для сбора метрик.
        🔧 1. Скачай и установи Prometheus вручную

        ```
        wget https://github.com/prometheus/prometheus/releases/download/v2.51.2/prometheus-2.51.2.linux-amd64.tar.gz

        tar xvf prometheus-2.51.2.linux-amd64.tar.gz
        cd prometheus-2.51.2.linux-amd64

        sudo mv prometheus /usr/local/bin/
        sudo mv promtool /usr/local/bin/
        sudo mkdir -p /etc/prometheus
        sudo cp -r consoles console_libraries /etc/prometheus/
        sudo cp prometheus.yml /etc/prometheus/
        sudo mkdir -p /var/lib/prometheus
        sudo chown -R vm1:vm1 /var/lib/prometheus
        sudo nano /etc/systemd/system/prometheus.service
        ```
        Вставить туда 
        ```
            [Unit]
            Description=Prometheus
            Wants=network-online.target
            After=network-online.target

            [Service]
            User=prometheus
            Group=prometheus
            ExecStart=/usr/local/bin/prometheus --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/var/lib/prometheus/ --web.console.templates=/etc/prometheus/consoles --web.console.libraries=/etc/prometheus/console_libraries --storage.tsdb.retention.time=1d --storage.tsdb.retention.size=1GB 

            Restart=always

            [Install]
            WantedBy=multi-user.target

        ```
        И конфиг
        ```
        sudo nano /etc/prometheus/prometheus.yml        
        ```
        Дополнить scrape_config, чтобы получилось
        ```
        scrape_configs:
        # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
        - job_name: "prometheus"

            # metrics_path defaults to '/metrics'
            # scheme defaults to 'http'.

            static_configs:
            - targets: ["localhost:9090"]

        - job_name: "nginx"
            static_configs:
            - targets: ["localhost:9113"]

        - job_name: "nodeVM1"
            static_configs:
            - targets: ["localhost:9100"]

        - job_name: "nodeVM2"
            static_configs:
            - targets: ["172.16.0.10:9100"]
        ```
        Перезапустите Prometheus для применения изменений:

        ```
        sudo systemctl restart prometheus
        ```
        nginx и node пока не работают, потому что мы их не включили, потом должны быть зелененькими в targeets на странице прометеуса. Сам прометеус должен открываться на порту 9090.
- Настроить сбор метрик с Nginx и других системных ресурсов (с использованием node_exporter или telegraf).

    Prometheus использует экс-экспортеры для сбора метрик. В нашем случае, нужно использовать два экспортеры:

    node_exporter для сбора метрик хоста (CPU, память, диски).

    перезаписываемый файл (через cron или скрипт) для сбора метрик с Nginx (например, из /status) и размера папки Prometheus на диске.

    - Собрать метрики хоста **ВМ1** и **ВМ2** (CPU, память, сеть, диски).
                
        Установите node_exporter:

        Выполните следующую команду для скачивания и установки node_exporter:

        ```
        wget https://github.com/prometheus/node_exporter/releases/download/v1.3.1/node_exporter-1.3.1.linux-amd64.tar.gz
        tar -xvzf node_exporter-1.3.1.linux-amd64.tar.gz
        cd node_exporter-1.3.1.linux-amd64
        sudo mv node_exporter /usr/local/bin/
        ```

        Если вы хотите, чтобы node_exporter автоматически запускался при старте системы, создайте systemd-сервис:

        `sudo nano /etc/systemd/system/node_exporter.service`

        Вставьте следующую конфигурацию:

        ```
[Unit]
Description=Prometheus Node Exporter
After=network.target

[Service]
ExecStart=/usr/local/bin/node_exporter
Restart=always

[Install]
WantedBy=multi-user.target
        ```

        После этого выполните команды:

        ```
        sudo systemctl daemon-reload
        sudo systemctl enable node_exporter
        sudo systemctl start node_exporter
        ```


        Проверьте, что node_exporter работает:

        После того как node_exporter запустится, вы можете проверить его работу с помощью команды:

        `curl http://localhost:9100/metrics`

        Вы должны увидеть метрики, такие как использование процессора, памяти, сети и дисков.
      

    - Настроить сбор метрик с Nginx (метрики из страницы /status).
        🔧 Шаг 1: Установка nginx-prometheus-exporter
        Сначала скачаем и установим экспортёр:

        ```
        # Перейди во временную папку
        cd /tmp

        # Скачиваем последнюю стабильную версию (v1.1.0)
        wget https://github.com/nginxinc/nginx-prometheus-exporter/releases/download/v1.1.0/nginx-prometheus-exporter_1.1.0_linux_amd64.tar.gz

        # Распаковываем
        tar -xvzf nginx-prometheus-exporter_1.1.0_linux_amd64.tar.gz

        # Перемещаем бинарник в стандартную директорию
        sudo mv nginx-prometheus-exporter /usr/local/bin/

        # Проверим
        nginx-prometheus-exporter --version
        ```

        🔧 Шаг 2: Настройка systemd-сервиса
        Создадим сервис, чтобы nginx-prometheus-exporter автоматически запускался при загрузке.

        ```
        sudo nano /etc/systemd/system/nginx-exporter.service
        ```
        Вставь туда следующее:

        ```
        [Unit]
        Description=NGINX Prometheus Exporter
        After=network.target

        [Service]
        ExecStart=/usr/local/bin/nginx-prometheus-exporter -nginx.scrape-uri http://localhost:8081/status
        Restart=always

        [Install]
        WantedBy=multi-user.target
        ```
        Сохрани (Ctrl+O, Enter) и выйди (Ctrl+X).

        Запускаем и включаем:

        ```
        sudo systemctl daemon-reexec
        sudo systemctl daemon-reload
        sudo systemctl enable --now nginx-exporter.service
        ```
        Проверь статус:

        ```
        sudo systemctl status nginx-exporter.service
        ```
        Экспортёр по умолчанию будет слушать порт 9113. Проверить:

        ```
        curl http://localhost:9113/metrics
        ```

- Конфигурация systemd:

    - Все сервисы должны управляться через systemd, чтобы они запускались при загрузке системы.

        Убедитесь, что все сервисы настроены на автозапуск:

        Для Prometheus:

        `sudo systemctl enable prometheus`

        Для Nginx:

        `sudo systemctl enable nginx`

        Для node_exporter:

        `sudo systemctl enable node_exporter`


# Когда вы настроите Prometheus для сбора метрик с Nginx, Node и других системных ресурсов, вы должны увидеть следующие метрики в Prometheus:

1. Метрики Nginx
Метрики с экспортером Nginx (nginx-prometheus-exporter) будут собираться с URL /status, который вы настроили в Nginx. Вы будете видеть такие метрики, как:

nginx_http_requests_total: общее количество HTTP-запросов.

nginx_http_requests_current: количество активных HTTP-запросов.

nginx_http_requests_duration_seconds: продолжительность обработки запросов.

nginx_connections_active: количество активных соединений с сервером.

nginx_connections_reading: количество соединений в процессе чтения запроса.

nginx_connections_writing: количество соединений в процессе записи ответа.

Эти метрики можно просмотреть, перейдя на URL http://localhost:9113/metrics.

2. Метрики с Node Exporter
Метрики с node_exporter будут собираться с порта 9100 и содержат информацию о состоянии системы:

node_cpu_seconds_total: количество времени процессора, использованного на различные операции (пользовательский, системный, ожидание и т.д.).

node_memory_MemTotal_bytes: общий объём памяти.

node_memory_MemFree_bytes: свободная память.

node_disk_read_bytes_total: общее количество байт, прочитанных с диска.

node_disk_write_bytes_total: общее количество байт, записанных на диск.

node_filesystem_size_bytes: размер файловой системы.

node_filesystem_free_bytes: свободное место на файловой системе.

node_network_receive_bytes_total: количество байт, полученных по сети.

node_network_transmit_bytes_total: количество байт, отправленных по сети.

Эти метрики можно просматривать через URL http://localhost:9100/metrics.

3. Метрики с Prometheus
Prometheus сам будет отслеживать различные метрики своей работы, такие как:

prometheus_local_storage_disk_size_bytes: размер хранилища Prometheus на диске.

prometheus_tsdb_head_series: количество серий в главной памяти.

prometheus_engine_query_duration_seconds: время выполнения запросов Prometheus.

Эти метрики отображаются по умолчанию в веб-интерфейсе Prometheus на порту 9090.
