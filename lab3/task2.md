# Графана для отображения метрик прометеуса на **ВМ2**

## Ставим Grafana вручную (через .deb пакет)
Перейди в домашнюю директорию (или временную):

`cd /tmp`

Скачай .deb пакет Grafana (например, последнюю версию 10.4.2):

`wget https://dl.grafana.com/oss/release/grafana_10.4.2_amd64.deb`

Можно проверить последнюю версию на официальном сайте.

Установи пакет:

`sudo dpkg -i grafana_10.4.2_amd64.deb`

Если будут ошибки зависимостей — исправим их:

`sudo apt-get install -f`

Запусти Grafana и добавь в автозагрузку:

```
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

Проверь, что работает:

`sudo systemctl status grafana-server`

🌐 Шаг 3: Проброс порта с ВМ2 на ВМ1
Если ты уже находишься на ВМ2, и хочешь, чтобы Grafana была доступна снаружи через ВМ1, то на ВМ1 добавь строчки в iptables:

```
sudo iptables -t nat -A PREROUTING -p tcp --dport 3000 -j DNAT --to-destination 172.16.0.10:3000
sudo netfilter-persistent save
```

Теперь Grafana будет доступна по http://<IP_ВМ1>:3000

🌐 Шаг 4: Доступ к интерфейсу Grafana
Теперь можно открыть в браузере:

http://<глобальный IP ВМ1>:3000

По умолчанию:

Логин: admin

Пароль: admin

Тебя попросят сменить пароль при первом входе.

🌉 Шаг 4: Добавляем источник данных Prometheus
Зайди в Grafana → ⚙️ "Configuration" → "Data Sources" → "Add data source".

Выбери Prometheus.

В поле URL укажи IP-адрес VM1, где крутится Prometheus:

http://<IP_VM1_local>:9090
Нажми Save & test — должна появиться надпись "Data source is working".

## Делаем дашборды

Создайте директорию для дашбордов:

sudo mkdir -p /etc/grafana/provisioning/dashboards

sudo nano /etc/grafana/provisioning/dashboards/default.yaml
```
apiVersion: 1
providers:
  - name: 'Default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: /var/lib/grafana/dashboards
```

`sudo mkdir -p /var/lib/grafana/dashboards`

Качаем dashboard для метрик системы + для папки и nginx

```
wget https://grafana.com/api/dashboards/1860/revisions/37/download
wget https://raw.githubusercontent.com/zhuk0vskiy/bmstu-devops/refs/heads/lab_03/my_dashboard.json
sudo mv download /var/lib/grafana/dashboards/node_exporter.json
sudo mv my_dashboard.json /var/lib/grafana/dashboards/my_dashboard.json 
sudo chown root:grafana /var/lib/grafana/dashboards/node_exporter.json
sudo chown root:grafana /var/lib/grafana/dashboards/my_dashboard.json
sudo systemctl restart grafana-server
wget https://grafana.com/api/dashboards/13659/revisions/1/download
sudo systemctl restart grafana-server
```
