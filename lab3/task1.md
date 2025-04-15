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

Теперь Nginx будет доступен по адресу http://localhost:8081/status, где будет выводиться информация о текущем состоянии сервера, включая количество активных подключений, обрабатываемые запросы и т. д.. Именно localhost!!!! ибо все остальные источники запрещены.

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

        - job_name: "nodeVM1"
            static_configs:
            - targets: ["localhost:9100"]

        - job_name: "nodeVM2"
            static_configs:
            - targets: ["172.16.0.10:9100"]
        ```

        # 1. Создаём пользователя и группу без shell и без домашней директории
        sudo useradd --no-create-home --shell /bin/false prometheus

        # 2. Выдаём права на директории
        sudo chown -R prometheus:prometheus /etc/prometheus
        sudo chown -R prometheus:prometheus /var/lib/prometheus

        Перезапустите Prometheus для применения изменений:

        ```
        sudo systemctl restart prometheus
        ```
        nginx и node пока не работают, потому что мы их не включили, потом должны быть зелененькими в targeets на странице прометеуса. Сам прометеус должен открываться на порту 9090.
- Настроить сбор метрик с Nginx и других системных ресурсов (с использованием node_exporter или telegraf).

    Prometheus использует экс-экспортеры для сбора метрик. В нашем случае, нужно использовать два экспортеры:

    nginx_exporter для сбора метрик с Nginx (например, из /status).

    node_exporter или telegraf для сбора метрик хоста (CPU, память, диски).

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

        ```[Unit]
        Description=Prometheus Node Exporter
        After=network.target

        [Service]
        ExecStart=/usr/local/bin/node_exporter
        Restart=always

        [Install]
        WantedBy=multi-user.target```

        После этого выполните команды:

        ```sudo systemctl daemon-reload
        sudo systemctl enable node_exporter
        sudo systemctl start node_exporter```


        Проверьте, что node_exporter работает:

        После того как node_exporter запустится, вы можете проверить его работу с помощью команды:

        `curl http://localhost:9100/metrics`

        Вы должны увидеть метрики, такие как использование процессора, памяти, сети и дисков.
      

    - Настроить сбор метрик с Nginx. Метрики из страницы /status собираются посредством скрипта, который парсит страничку.
       
        Создам скрипт для складывания метрик
        ```
        sudo mkdir /opt/prometheus_scripts
        sudo nano /opt/prometheus_scripts/nginx_metrics.sh
        ```
        
```
#!/bin/bash

OUTPUT_FILE="/var/lib/node_exporter/nginx_metrics.prom"

# Очистка файла перед началом (перезапись)
> "$OUTPUT_FILE"

# Функция для добавления метрик в вывод (дозапись)
add_metric() {
    echo "$1 $2" >> "$OUTPUT_FILE"
}

# Функция для проверки статуса Nginx
check_nginx_status() {
    STATUS=$(curl -s -m 2 http://localhost:8081/status 2>/dev/null)
    if [ $? -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# Функция для парсинга статуса Nginx
parse_nginx_status() {
    ACTIVE_CONNECTIONS=$(echo "$STATUS" | awk '/Active connections/ {print $3}')
    READING=$(echo "$STATUS" | awk '/Reading/ {print $2}')
    WRITING=$(echo "$STATUS" | awk '/Writing/ {print $4}')
    WAITING=$(echo "$STATUS" | awk '/Waiting/ {print $6}')

    add_metric "nginx_active_connections" "$ACTIVE_CONNECTIONS"
    add_metric "nginx_reading" "$READING"
    add_metric "nginx_writing" "$WRITING"
    add_metric "nginx_waiting" "$WAITING"
}

# Проверка через systemctl
check_nginx_systemd() {
    if systemctl is-active --quiet nginx; then
        add_metric "nginx_systemd_active" 1
    else
        add_metric "nginx_systemd_active" 0
    fi
}

# Проверка, что процесс Nginx запущен
check_nginx_process() {
    if pgrep -x "nginx" >/dev/null; then
        add_metric "nginx_process_running" 1
    else
        add_metric "nginx_process_running" 0
    fi
}

# Проверка доступности Nginx статус-страницы
check_nginx_status_page() {
    if check_nginx_status; then
        add_metric "nginx_status_available" 1
        parse_nginx_status
    else
        add_metric "nginx_status_available" 0
        add_metric "nginx_active_connections" 0
    fi
}

# Проверка агрегированной доступности Nginx
check_nginx_up() {
    if grep -q "nginx_systemd_active 1" "$OUTPUT_FILE" && \
       grep -q "nginx_process_running 1" "$OUTPUT_FILE" && \
       grep -q "nginx_status_available 1" "$OUTPUT_FILE"; then
        add_metric "nginx_up" 1
    else
        add_metric "nginx_up" 0
    fi
}

# Запуск всех проверок
check_nginx_systemd
check_nginx_process
check_nginx_status_page
check_nginx_up
```


        Выдаем скрипту права на выполнение:

        `sudo chmod +x /opt/prometheus_scripts/nginx_metrics.sh`

    - Сбор метрики размера папки прометеус на диске **вм1**
        
        Создаем скрипт для складывания метрик

        sudo nano /opt/prometheus_scripts/prometheus_size.sh

        #!/bin/bash
        OUTPUT_FILE="/var/lib/node_exporter/prometheus_size.prom"
        PROMETHEUS_DIR="/var/lib/prometheus"
        SIZE=$(du -sb "$PROMETHEUS_DIR" | awk '{print $1}')
        echo "prometheus_dir_size_bytes $SIZE" > "$OUTPUT_FILE"
 
 
        sudo chmod +x /opt/prometheus_scripts/prometheus_size.sh


    - Создаем сервис-таймер и запускаем созданные скрипты тоже как службу, обновляем файлы с метриками каждые 10 секунд


`sudo nano /etc/systemd/system/collect-metrics.service`

```
[Unit]
Description=Run both nginx and prometheus metric scripts

[Service]
Type=oneshot
ExecStart=/bin/bash -c '/opt/prometheus_scripts/nginx_metrics.sh && /opt/prometheus_scripts/prometheus_size.sh'
```

`sudo nano /etc/systemd/system/collect-metrics.timer`

```
[Unit]
Description=Run collect-metrics.service every 10 seconds

[Timer]
OnBootSec=10
OnUnitActiveSec=10s
AccuracySec=1s
Unit=collect-metrics.service

[Install]
WantedBy=timers.target

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

nginx_active_connections 1
nginx_requests_total 34

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

vm1@vm1:~$ sudo cat /var/lib/node_exporter/prometheus_size.prom
prometheus_dir_size_bytes 1218011: размер хранилища Prometheus на диске.

prometheus_tsdb_head_series: количество серий в главной памяти.

prometheus_engine_query_duration_seconds: время выполнения запросов Prometheus.

Эти метрики отображаются по умолчанию в веб-интерфейсе Prometheus на порту 9090.
