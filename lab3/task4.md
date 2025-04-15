# blackbox_exporter

Делаем эту часть на ВМ1

Опять смотрим на архитектуру (amd / arm)

```
wget https://github.com/prometheus/blackbox_exporter/releases/download/v0.24.0/blackbox_exporter-0.24.0.linux-amd64.tar.gz
tar xvf blackbox_exporter-*.tar.gz
cd blackbox_exporter-*/
sudo cp blackbox_exporter /usr/local/bin/
sudo mkdir /etc/blackbox_exporter
sudo cp blackbox.yml /etc/blackbox_exporter/
sudo useradd --no-create-home --shell /bin/false blackbox_exporter
sudo chown blackbox_exporter:blackbox_exporter /usr/local/bin/blackbox_exporter /etc/blackbox_exporter
sudo nano /etc/systemd/system/blackbox_exporter.service
```

```
[Unit]
Description=Blackbox Exporter
After=network.target

[Service]
User=blackbox_exporter
Group=blackbox_exporter
ExecStart=/usr/local/bin/blackbox_exporter --config.file=/etc/blackbox_exporter/blackbox.yml --web.listen-address=:9115
Restart=always

[Install]
WantedBy=multi-user.target
```

`sudo nano /etc/prometheus/prometheus.yml`

Добавляем в scrape_configs новый job

```
  - job_name: 'blackbox-http'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - 'https://google.com'   # Пример дополнительного таргета
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9115  # Адрес blackbox_exporter
```

```
sudo systemctl daemon-reload
sudo systemctl start blackbox_exporter
sudo systemctl enable blackbox_exporter
sudo systemctl status blackbox_exporter
```