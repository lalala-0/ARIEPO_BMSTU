# alert manager

Качаем alertManager, создаем юзера для него, выдаем права, создаем службу, запускаем ее при включении вм:

```
wget https://github.com/prometheus/alertmanager/releases/download/v0.27.0/alertmanager-0.27.0.linux-amd64.tar.gz
tar -xvf alertmanager-0.27.0.linux-amd64.tar.gz
cd alertmanager-0.27.0.linux-amd64
sudo cp alertmanager amtool /usr/local/bin/
sudo useradd --no-create-home --shell /bin/false alertmanagersudo mkdir -p /etc/alertmanager /var/lib/alertmanager
sudo chown alertmanager:alertmanager /etc/alertmanager /var/lib/alertmanager
sudo nano /etc/systemd/system/alertmanager.service
```
```
[Unit]
Description=Alertmanager
After=network.target

[Service]
User=alertmanager
Group=alertmanager
ExecStart=/usr/local/bin/alertmanager --config.file=/etc/alertmanager/alertmanager.yml --storage.path=/var/lib/alertmanager
Restart=always

[Install]
WantedBy=multi-user.target
```


Создаем правило:
 `sudo nano /etc/prometheus/alert.rules.yml`

```                                          
groups:
- name: nginx-alerts
  rules:
  - alert: NginxDown
    expr: nginx_up == 0
    for: 10s
    labels:
      severity: critical
    annotations:
      summary: "Nginx is DOWN on {{ $labels.instance }}"
      description: |
        Nginx failed health checks.
```

Дополняем прометеус алертом и файлом с правилом:
`sudo nano /etc/prometheus/prometheus.yml`

```
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']  # Alertmanager слушает на 9093

.....

rule_files:
  - 'alert.rules.yml'
```


Создаем бота

Делаем эту часть в Телеге

Откройте Telegram, найдите @BotFather.

Отправьте команду /newbot.

Укажите имя бота.

Получите токен (сохраните его!).

Напишите боту /start.

Отправьте GET-запрос c хоста (подставьте токен):

curl https://api.telegram.org/bot8187103353:AAEcujfiHpdX07tnuU_Gv9jE0UcxkdX9l80/getUpdates

В ответе найдите chat.id (например, 0123456789).


`sudo nano /etc/alertmanager/alertmanager.yml`

```
global:
  resolve_timeout: 5m

route:
  receiver: telegram
  group_wait: 10s
  group_interval: 30s
  repeat_interval: 1h

receivers:
  - name: 'telegram'
    telegram_configs:
      - send_resolved: true
        bot_token: '8187103353:AAEcujfiHpdX07tnuU_Gv9jE0UcxkdX9l80'
        chat_id: 1744656443
        parse_mode: 'Markdown'
        message: |
          🚨 *{{ .Status | toUpper }} alert!* 🚨
          *Alert name:* {{ .CommonLabels.alertname }}
          *Instance:* {{ .CommonLabels.instance }}
          *Summary:* {{ .CommonAnnotations.summary }}
          *Description:* {{ .CommonAnnotations.description }}
          *Severity:* {{ .CommonLabels.severity }}
```

