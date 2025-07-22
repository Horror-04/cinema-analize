{{ 
  config(
    materialized='incremental',
    unique_key='event_id',
    tags=['staging']
  ) 
}}

with raw as (
  select
    event_id,
    user_id,
    movie_id,
    event_type,
    event_time
  from {{ source('my_database', 'events_from_postgres') }}
)

select
  event_id,
  user_id,
  movie_id,
  event_type,
  event_time as event_timestamp
from raw
where
  {% if is_incremental() %}
    event_time >= subtractDays(today(), 7)
  {% else %}
    event_time >= subtractDays(today(), 7)
  {% endif %}
