#!/usr/bin/env python3
"""
DAG generate_events_dag.py

Airflow DAG, который каждые 30 минут запускается и эмулирует
5-секционные сессии (play→pause→resume→finish) для одного
пользователя и одного фильма.
"""
from datetime import datetime, timedelta
import random
import time
import logging

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

# Логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Диапазоны генерации (не используются для каждого шага, а только для выбора сессии)
USER_ID_RANGE = (1, 100)
MOVIE_ID_RANGE = (1, 50)

# SQL

INSERT_SQL = text("""
    INSERT INTO raw.events (user_id, movie_id, event_type, event_time)
    VALUES (:user_id, :movie_id, :event_type, :event_time)
""")

def generate_events_batch(postgres_conn_id, **kwargs):
    pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    engine = pg_hook.get_sqlalchemy_engine()
    session = Session(bind=engine)

    # выбираем одного user и один movie для ВСЕХ 5 итераций
    user_id  = random.randint(*USER_ID_RANGE)
    movie_id = random.randint(*MOVIE_ID_RANGE)
    logger.info(f"Начинаем 5-сессионную генерацию для user={user_id}, movie={movie_id}")

    for session_num in range(1, 6):
        base_time = datetime.utcnow()

        # 1) PLAY
        session.execute(INSERT_SQL, {
            'user_id': user_id,
            'movie_id': movie_id,
            'event_type': 'play',
            'event_time': base_time
        })
        session.commit()
        logger.info(f"#{session_num} [play]   at {base_time.isoformat()}")

        # 2) PAUSE (5–15 сек)
        pause_time = base_time + timedelta(seconds=random.randint(5, 15))
        time.sleep(max((pause_time - datetime.utcnow()).total_seconds(), 0))
        session.execute(INSERT_SQL, {
            'user_id': user_id,
            'movie_id': movie_id,
            'event_type': 'pause',
            'event_time': pause_time
        })
        session.commit()
        logger.info(f"#{session_num} [pause]  at {pause_time.isoformat()}")

        # 3) RESUME (3–10 сек)
        resume_time = pause_time + timedelta(seconds=random.randint(3, 10))
        time.sleep(max((resume_time - datetime.utcnow()).total_seconds(), 0))
        session.execute(INSERT_SQL, {
            'user_id': user_id,
            'movie_id': movie_id,
            'event_type': 'resume',
            'event_time': resume_time
        })
        session.commit()
        logger.info(f"#{session_num} [resume] at {resume_time.isoformat()}")

        # 4) FINISH (10–30 сек)
        finish_time = resume_time + timedelta(seconds=random.randint(10, 30))
        time.sleep(max((finish_time - datetime.utcnow()).total_seconds(), 0))
        session.execute(INSERT_SQL, {
            'user_id': user_id,
            'movie_id': movie_id,
            'event_type': 'finish',
            'event_time': finish_time
        })
        session.commit()
        logger.info(f"#{session_num} [finish] at {finish_time.isoformat()}")

        # небольшая пауза перед следующей сессией
        if session_num < 5:
            time.sleep(1)

    logger.info("Генерация событий завершена после 5 итераций.")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 7, 8),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='generate_events',
    default_args=default_args,
    # вот он — каждые 30 минут
    schedule_interval='*/30 * * * *',
    catchup=False,
    tags=['example', 'generate_events'],
) as dag:

    generate_events = PythonOperator(
        task_id='generate_events_batch',
        python_callable=generate_events_batch,
        op_kwargs={'postgres_conn_id': 'server_publicist'},
    )

    generate_events
