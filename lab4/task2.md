Выбрать список из не менее трех любых пакетов и настроить установку этого списка пакетов отдельно на ВМ1, отдельно на ВМ2 и на группу хостов, состоящую из ВМ1 и ВМ2.
-------------------

Создаем плейбук в любой директории.
```
mkdir ~/ansible_project
mkdir ~/ansible_project/playbooks
cd ~/ansible_project/playbooks
nano install_packages.yml
```

Записываем:

```
---
- name: Установить пакеты на веб-серверы (группа web)
  hosts: web
  become: yes  # Использование прав суперпользователя
  tasks:
    - name: Установить curl
      apt:
        name: curl
        state: present
        update_cache: yes

    - name: Установить git
      apt:
        name: git
        state: present
        update_cache: yes

    - name: Установить htop
      apt:
        name: htop
        state: present
        update_cache: yes
```

Выполнять плебук можно для всех хостов в группе веб:

` ansible-playbook install_packages.yml`

или для определенных:

`ansible-playbook -l vm2 install_packages.yml`




