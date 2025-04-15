На ВМ2 развернуть APACHE на порту 80.
На ВМ1 развернуть NGINX на порту 80.
Требуется настроить виртуальные машины так, чтобы при обращении с хостовой (где хостятся ВМ) машины на IP адрес 
ВМ1 1-го сетевого интерфейса должна выводиться дефолтная страница Apache, развернутого на ВМ2. 
nginx как front-end к apache!

# Установка Apache на ВМ2
Установи Apache на ВМ2:
```
sudo apt update
sudo apt install apache2 -y
```

Запусти Apache:
```
sudo systemctl start apache2
sudo systemctl enable apache2
```

Проверь, что Apache работает:
` curl http://127.0.0.1 ` - отдается страница apache2.

# Установка Nginx на ВМ1
Установи Nginx на ВМ1:
```
sudo apt update
sudo apt install nginx -y
```

Настрой Nginx как реверс-прокси для Apache: