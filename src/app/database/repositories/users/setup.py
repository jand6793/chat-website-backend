schema = """
    CREATE TABLE user (
        full_name text NOT NULL,
        description text,
        username text UNIQUE NOT NULL,
        hashed_password text NOT NULL
    )
"""
