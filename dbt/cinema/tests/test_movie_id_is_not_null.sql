--singular test 

SELECT
    *
FROM
    {{ ref('staging_events') }}
WHERE
    movie_id IS NULL