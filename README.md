# 🍿 Аналитический конвейер для Домашнего Кинотеатра

Этот проект представляет собой полноценный ELT-конвейер для сбора, обработки и анализа событий просмотра фильмов в домашнем кинотеатре. Данные генерируются, загружаются в хранилище, трансформируются и визуализируются с использованием современного стека технологий.

## 🛠️ Стек технологий

* [Docker v4.22.1](https://www.docker.com/)
* [Postgres v13](https://www.postgresql.org/)
* [ClickHouse v23.8](https://clickhouse.com/)
* [Python v3.8](https://www.python.org/)
* [AirFlow v2.8.2](https://airflow.apache.org/)
* [DBT v1.8.0](https://www.getdbt.com/)
* [MetaBase v0.49.8](https://www.metabase.com/)
* [super-linter v5.7.2](https://github.com/super-linter/super-linter)

## 🏗️ Архитектура

Данные проходят через несколько этапов, от генерации до визуализации. Весь процесс оркеструется с помощью Apache Airflow.

Поток данных

    Producer: Python-скрипт (generate_events.py), запущенный как задача в Airflow, эмулирует события (старт, пауза, просмотр) и записывает их в PostgreSQL.

    Ingestion & Replication: "Сырые" события сохраняются в PostgreSQL. С помощью логической репликации (Publication/Subscription) изменения передаются дальше.

    Loading to DWH: Отдельный Python-сервис (ClickHouse Loader) подхватывает новые записи и батчами загружает их в аналитическое хранилище ClickHouse.

    Transformation: Airflow запускает dbt для трансформации сырых данных в ClickHouse. В результате создаются очищенные, готовые к анализу витрины данных (например, сессии просмотров).

    Visualization: Metabase подключается к ClickHouse, откуда забирает данные из витрин для построения дашбордов.

## Используемые библиотеки Python

* dbt-core
* dbt-clickhouse
* python-decouple
* requests
* sqlalchemy
* datetime
* logging
* json

## Настройка сети

Как можно увидеть, в Docker Compose выделено 4 основных сетевых сегмента:

* data_postgres - сеть управления БД PostgreSQL (предполагается, что в данной сети будет работать только администратор и разработчик баз данных)
* replication_network (192.168.1.0/24) - предназначена исключительно для трансляции трафика логической репликацией
* click_net (192.168.2.0/24) - сеть подключения ClickHouse к PostgreSQL. Именно по данной сети CH будет выкачивать данные из PostgreSQL
* metanet (192.168.3.0/24) - сеть, по которой BI-система обращается к хранилищу данных (предполагается, что в данной сети работают аналитики)

Структурно сеть выглядит следующим образом:

![Схема подключения маршрутизаторов](./pictures/network.png)

## Запуск

Для запуска необходимо сделать следующие действия:

1. Выгрузить проект с помощью команды
    ```
    git clone git@github.com:horror-04/cinema-analize.git
    ```
2. В каталоге проекта переименовать файл .env_template в .env, в котором необходимо указать следующие атрибуты (не меняйте имена переменных, так как на них есть ссылки в проекте):
    ```
    AIRFLOW_UID=50000
    POSTGRES_PUBLICIST_USER=postgres
    POSTGRES_PUBLICIST_PASSWORD=postgres
    POSTGRES_PUBLICIST_DB=postgres_publicist
    
    POSTGRES_SUBSCRIPTION_USER=postgres
    POSTGRES_SUBSCRIPTION_PASSWORD=postgres
    POSTGRES_SUBSCRIPTION_DB=postgres_subscriber
    
    CLICKHOUSE_USER=username
    CLICKHOUSE_PASSWORD=username
    CLICKHOUSE_DB=my_database
    ```
    (выше указан пример заполения, вы можете вставить свои данные)

3. Запустить Docker и командную оболочку (так как я работаю на ОС Windows, командная оболочка у меня WSL)
4. Перейти в корень проекта, где находится файл docker-compose.yaml
5. Выполнить следующую команду:
    ```
        docker compose up -d
    ```
6. После скачивания всех образов и поднятия всех контейнеров открыть браузер и прописать в поисковой строке:
    ```
        localhost:8080
    ```
7. Зайти в airflow (по умолчанию логин и пароль - airflow)

8. Запустить DAG
9. Перейти на новую вкладку и прописать:
    ```
        localhost:3000
    ```
10. Зарегистрироваться и создать свой дашборд на основе данных из таблиц и представлений.

