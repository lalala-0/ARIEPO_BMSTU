Настроить проброс портов. portforwarding.
При обращении на порт 2222 (или любой другой порт на ваш выбор)  wan интерфейса вм1 запрос должен  улететь на 22 порт вм2 и мы должны получить доступ к ssh vm2.

Реализовать используя iptables.


# На вм1
## Нужно настроить проброс порта, команда:
`sudo iptables -t nat -A PREROUTING -p tcp --dport 2222 -j DNAT --to-destination <ip-адрес второй ВМ>:22`

`sudo netfilter-persistent save` - сохраняем

## Потом проверить iptable с помощью команды `sudo iptables -t nat -L -v -n`

Таблица должна выглядеть как-то так:
```
vm1@vm1:~$ sudo iptables -t nat -L -v -n
Chain PREROUTING (policy ACCEPT 707 packets, 89993 bytes)
 pkts bytes target     prot opt in     out     source               destination
    3   156 DNAT       6    --  *      *       0.0.0.0/0            0.0.0.0/0            tcp dpt:2222 to:172.16.0.10:22

Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain OUTPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain POSTROUTING (policy ACCEPT 7 packets, 474 bytes)
 pkts bytes target     prot opt in     out     source               destination
   53  3514 MASQUERADE  0    --  *      enp0s3  0.0.0.0/0            0.0.0.0/0
```
Следует обратить внимание, что для порта 2222 только одно правило, а не 
```
Chain PREROUTING (policy ACCEPT 611 packets, 71462 bytes)
 pkts bytes target     prot opt in     out     source               destination
    0     0 DNAT       6    --  *      *       0.0.0.0/0            0.0.0.0/0            tcp dpt:2222 to:10.0.0.10:22
    0     0 DNAT       6    --  *      *       0.0.0.0/0            0.0.0.0/0            tcp dpt:2222 to:172.16.0.10:22
```
А то ничего работать не будет.

## В случае лишнего правила, удаляем его из таблицы:
`sudo iptables -t nat -D [PREROUTING / POSTROUTING / INPUT / OUTPUT] <НОМЕР СТРОКИ ПРАВИЛА (НУМЕРАЦИЯ С 1)>`

# На вм2
## Устанавливаем ssh
```
sudo apt update 
sudo apt install openssh-server
```
(может и на 1 тоже надо, я не помню, но лишнем не будет)
## Перезапускаем ssh на всякий случай 
`sudo systemctl restart ssh`

Чтобы проверить статус:
`sudo systemctl status ssh`

# На основном хосте
## Для проверки, что порт действительно пробрасывается 
` ssh vm2@<ip-адрес вм1 для внешней сети> -p 2222`


# Если что-то не работает, можно попробовать отключить фаервол на вм:
`sudo systemctl stop ufw`

Если ufw не установлено, то это ложь, надо установить и выключить его.