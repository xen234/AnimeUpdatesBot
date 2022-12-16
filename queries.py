class SqlQueries:
    create_users_table_if_not_exists = """
    CREATE TABLE IF NOT EXISTS users(
        id integer PRIMARY KEY,
        name TEXT DEFAULT ''
    );
    """,
    create_anime_table_if_not_exists = """
    CREATE TABLE IF NOT EXISTS anime(
        id integer PRIMARY KEY,
        url TEXT NOT NULL,
        title TEXT DEFAULT '',
        broadcast TEXT DEFAULT '',
        last_episode integer DEFAULT 0
    );
    """,
    create_users_table = """
        DROP TABLE IF EXISTS users CASCADE;
        CREATE TABLE users(
            id integer PRIMARY KEY,
            name TEXT DEFAULT ''
        );
        """,
    create_anime_table = """
        DROP TABLE IF EXISTS anime CASCADE;
        CREATE TABLE anime(
            id integer PRIMARY KEY,
            url TEXT NOT NULL,
            title TEXT DEFAULT '',
            broadcast TEXT DEFAULT '',
            last_episode integer DEFAULT 0
        );
        """,
    insert_user = """
    INSERT INTO users
    VALUES({}, '{}');
    """,
    find_user_by_id = """
    SELECT * FROM users
    WHERE id = {};
    """,
    insert_anime = """
    INSERT INTO anime(id, url, title, broadcast, last_episode)
    VALUES({}, '{}', '{}', '{}', {});
    """,
    find_anime_by_id = """
    SELECT * FROM anime
    WHERE id = {};
    """,
    create_link_table_if_not_exists = """
    CREATE TABLE IF NOT EXISTS connections(
        user_id integer,
        anime_id integer,
        CONSTRAINT fk_user
            FOREIGN KEY(user_id)
            REFERENCES users(id)
            ON DELETE CASCADE,
        CONSTRAINT fk_anime
            FOREIGN KEY(anime_id)
            REFERENCES anime(id)
            ON DELETE CASCADE
    );
    """,
    create_link_table = """
       DROP TABLE IF EXISTS connections;
       CREATE TABLE connections(
           user_id integer,
           anime_id integer,
           CONSTRAINT fk_user
               FOREIGN KEY(user_id)
               REFERENCES users(id)
               ON DELETE CASCADE,
           CONSTRAINT fk_anime
               FOREIGN KEY(anime_id)
               REFERENCES anime(id)
               ON DELETE CASCADE
       );
       """,
    add_reference = """
    INSERT INTO connections(user_id, anime_id)
    VALUES({}, '{}');
    """,
    remove_reference = """
        DELETE FROM connections
        WHERE user_id = {} AND anime_id = {};
        """,
    user_links = """
    SELECT * FROM connections 
    WHERE user_id = {};
    """,
    anime_links = """
    SELECT * FROM connections 
    WHERE anime_id = {};
    """,
    user_anime_select = """
    SELECT * FROM connections
    WHERE user_id = {} AND anime_id = {}; 
    """,
    subscriptions = """
    SELECT * FROM anime
    WHERE id IN
        (SELECT anime_id FROM connections
        WHERE user_id = {});
    """,
    subscribers = """
    SELECT * FROM users
    WHERE id IN
        (SELECT user_id FROM connections
        WHERE anime_id = {});
    """,
    select_all_users = """
    SELECT * FROM users;
    """,
    select_all_anime = """
    SELECT * FROM anime;
    """,
