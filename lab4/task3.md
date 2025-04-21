Настроить установку любой бд. (запуск через systemd, состояние запущена и включена в автозагрузку)

Настроить установку любого web-сервера (запуск через systemd, состояние запущена и включена в автозагрузку).

Установка через роли!

Управление на вм2 нужно уметь осуществлять с вм1:
- Управление nginx (уметь управлять конфигурацией nginx);
- управление БД Postgresql (создание бд, создание пользователей, создание дампа)
------------------

Качаем готовые роли (роли = сценарии). Они добавляют в автозагрузку сами.

```
ansible-galaxy install geerlingguy.nginx
ansible-galaxy install geerlingguy.postgresql
```

Создаем плейбук для nginx:

`sudo nano ~/ansible_project/playbooks/install_nginx.yml`

```
- name: Установка и настройка nginx
  hosts: web
  become: true

  vars:
    # Настройки Nginx
    nginx_vhosts:
      - listen: "80"
        server_name: "localhost"
        root: "/var/www/html"
        index: "index.html"
        state: "present"

    nginx_remove_default_vhost: true

  roles:
    - geerlingguy.nginx
```

Создаем плейбук для nginx:

`sudo nano ~/ansible_project/playbooks/install_postgresql.yml`

```
- name: Установка и настройка postgreSQL
  hosts: db
  become: true

  vars:
    # Настройки PostgreSQL
    postgresql_databases:
      - name: mydb

  roles:
    - geerlingguy.postgresql
```

---------

Далее чухня для настройки бд с помощью ансибль.

## Настравиаем постгрес так, чтобы локальные изменения в б двносились без пароля.

`nano configure_pg_hba.yml`

```
- name: Настройка pg_hba.conf для доверенной аутентификации
  hosts: db
  become: true

  tasks:
    - name: Определение версии PostgreSQL
      shell: "psql -V | awk '{print $3}' | cut -d. -f1,2"
      register: pg_version
      changed_when: false

    - name: Установка пути к pg_hba.conf
      set_fact:
        pg_hba_path: "/etc/postgresql/{{ pg_version.stdout }}/main/pg_hba.conf"

    - name: Заменить peer на trust для postgres
      replace:
        path: "{{ pg_hba_path }}"
        regexp: '^local\s+all\s+postgres\s+peer'
        replace: 'local   all             postgres                                trust'

    - name: Перезапустить PostgreSQL
      service:
        name: postgresql
        state: restarted
```

`ansible-playbook configure_pg_hba.yml`

## Playbook для создания бд:

`nano create_db.yml`

```
# create_db.yml

- name: Создание баз данных
  hosts: db
  become: false  # отключаем привилегии
  vars:
    dbs_to_create:
      - name: db1
      - name: db2
      - name: db3

  tasks:
    - name: Создание баз данных
      community.postgresql.postgresql_db:
        name: "{{ item.name }}"
        state: present
        login_user: postgres
      loop: "{{ dbs_to_create }}"
```

`ansible-playbook create_db.yml`

## Создание пользователей PostgreSQL

`nano create_user.yml`

```
---
- name: Создание пользователей PostgreSQL
  hosts: db
  become: true

  vars:
    postgres_users:
      - name: user1
        password: password1
        db: mydb
        priv: "ALL"
      - name: user2
        password: password2
        db: mydb
        priv: "ALL"

  tasks:
    - name: Создание пользователей PostgreSQL
      community.postgresql.postgresql_user:
        name: "{{ item.name }}"
        password: "{{ item.password }}"
        db: "{{ item.db }}"
        priv: "{{ item.priv }}"
        state: present
        login_user: postgres
        login_password: your_postgres_password
      loop: "{{ postgres_users }}"
```

## Управление nginx (уметь управлять конфигурацией nginx);

```
mkdir ../templates/
nano ../templates/nginx.conf.j2
```

```
server {
    listen 80;
    server_name {{ server_name }};

    location / {
        root {{ document_root }};
        index index.html index.htm;
    }

    error_page 404 /404.html;
    location = /40x.html {
    }

    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
    }
}
```

`nano manage_nginx.yml`

```
---
- name: Управление конфигурацией Nginx
  hosts: web
  become: true
  vars:
    server_name: "example.com"
    document_root: "/var/www/html"

  tasks:
    - name: Убедиться, что Nginx установлен
      ansible.builtin.package:
        name: nginx
        state: present

    - name: Копирование конфигурации Nginx
      ansible.builtin.template:
        src: ../templates/nginx.conf.j2
        dest: /etc/nginx/sites-available/default
        owner: root
        group: root
        mode: '0644'
      notify:
        - Перезапустить Nginx

    - name: Убедиться, что директория для веб-сайта существует
      ansible.builtin.file:
        path: "{{ document_root }}"
        state: directory
        owner: www-data
        group: www-data
        mode: '0755'

    - name: Проверка синтаксиса конфигурации Nginx
      ansible.builtin.command:
        cmd: nginx -t
      register: nginx_syntax_check
      failed_when: nginx_syntax_check.rc != 0
      changed_when: False

  handlers:
    - name: Перезапустить Nginx
      ansible.builtin.service:
        name: nginx
        state: restarted
```

`ansible-playbook  manage_nginx.yml --ask-become-pa
ss`



------------ ИЛИ --------------

🔧 Роль custom_nginx
roles/custom_nginx/defaults/main.yml
yaml
Копировать
Редактировать
nginx_root: /var/www/html
nginx_index: index.html
nginx_port: 80
roles/custom_nginx/tasks/main.yml
yaml
Копировать
Редактировать
- name: Установка Nginx
  apt:
    name: nginx
    state: present
    update_cache: yes

- name: Настройка виртуального хоста
  copy:
    dest: /etc/nginx/sites-available/custom_default
    content: |
      server {
          listen {{ nginx_port }};
          server_name localhost;

          location / {
              root {{ nginx_root }};
              index {{ nginx_index }};
          }
      }

- name: Включение сайта
  file:
    src: /etc/nginx/sites-available/custom_default
    dest: /etc/nginx/sites-enabled/default
    state: link
    force: yes

- name: Убедиться, что Nginx запущен и в автозагрузке
  systemd:
    name: nginx
    state: started
    enabled: true
🔧 Роль custom_postgresql
roles/custom_postgresql/defaults/main.yml
yaml
Копировать
Редактировать
postgresql_version: 14

postgresql_packages:
  - "postgresql-{{ postgresql_version }}"
  - "postgresql-client-{{ postgresql_version }}"
  - "postgresql-contrib-{{ postgresql_version }}"
  - libpq-dev
  - python3-psycopg2

postgresql_service: postgresql
postgresql_service_state: started
postgresql_service_enabled: true

postgresql_databases:
  - name: myapp_db
    encoding: UTF-8
    lc_collate: en_US.UTF-8
    lc_ctype: en_US.UTF-8
roles/custom_postgresql/tasks/main.yml
yaml
Копировать
Редактировать
- name: Установка PostgreSQL
  apt:
    name: "{{ postgresql_packages }}"
    state: present
    update_cache: yes

- name: Убедиться, что PostgreSQL запущен и в автозагрузке
  systemd:
    name: "{{ postgresql_service }}"
    state: "{{ postgresql_service_state }}"
    enabled: "{{ postgresql_service_enabled }}"

- name: Создание баз данных
  become_user: postgres
  postgresql_db:
    name: "{{ item.name }}"
    encoding: "{{ item.encoding }}"
    lc_collate: "{{ item.lc_collate }}"
    lc_ctype: "{{ item.lc_ctype }}"
  loop: "{{ postgresql_databases }}"
▶️ Плейбуки
playbooks/install_nginx.yml
yaml
Копировать
Редактировать
- name: Установка и настройка Nginx
  hosts: web
  become: true
  roles:
    - custom_nginx
playbooks/install_postgresql.yml
yaml
Копировать
Редактировать
- name: Установка и настройка PostgreSQL
  hosts: db
  become: true
  roles:
    - custom_postgresql
🧪 Запуск
bash
Копировать
Редактировать
ansible-playbook -i inventory.ini playbooks/install_nginx.yml
ansible-playbook -i inventory.ini playbooks/install_postgresql.yml