Лабораторная работа 3.

«Настройка системы мониторинга»
ЦЕЛЬ:
Получить практические
навыки по развертыванию
и настройке систем
мониторинга на базе
Prometheus и Grafana.
———————————————————

ПОЛЕЗНЫЕ ССЫЛКИ:
https://www.robustperception.io/configuring-prometheus-storage-retention/
https://laurvas.ru/prometheus-p3/#retention

ЗАДАНИЕ:

● На машине ВМ1 (ROUTER) поднять Nginx и Prometheus. Prometheus должен иметь циклическую запись 10-20 дней и/или ограничение по
размеру.
● На машине ВМ2 поднять Grafana.
Все перечисленные сервисы должны управляться через systemd и
стартовать при загрузке системы.
На каждой машине настроить сбор следующих метрик.
Метрики ВМ 1 :
● host metrics (метрики хоста: память, цпу, сеть, диски). В качестве поставщика данных использовать node_exporter или telegraf.
● Метрики status-страницы Nginx. Метрики должны собираться в
перезаписываемый файл (можно по крону). Файл должен
использоваться поставщиком данных node_exporter или telegraf
для сбора и предоставления метрик для Prometheus.
● Размер папки Prometheus на диске. Метрики должны
собираться в перезаписываемый файл (можно по крону). Файл
должен использоваться поставщиком данных node_exporter или
telegraf для сбора и предоставления метрик для Prometheus.
Метрики ВМ 2: 
● host metrics (метрики хоста: память, цпу, сеть, диски).


Все собираемые метрики необходимо отобразить в Grafana в виде
графиков. Графики должны иметь названия, подписанные значения,
таблицу значений (min max current avg).
Для метрик хоста можно использовать готовые дашборды или создать
свой.


Также требуется поднять и настроить Alertmanager, который должен
отслеживать состояние Nginx (запущен/не запущен) и в случае падения  Nginx (нет процесса nginx или systemd – показывает статус Active: inactive / dead) отсылать уведомление в Телеграм через бота (бота зарегистрировать самостоятельно).

● Установить Prometheus blackbox_exporter настроить дашборд 
для мониторинга любого публичного ресурса на ваш выбор.
https://github.com/prometheus/blackbox_exporter


ВНИМАНИЕ
Использовать docker допускается только для Grafana. Все остальные
сервисы должны быть установлены вручную и управляться через systemd.
При сдаче лабораторной работы будут использоваться утилиты stress (для нагрузки на систему) и ab (для нагрузки на Nginx). Сбор индивидуальных метрик (свои бизнес-метрики) и отрисовка в Grafana приветствуется.