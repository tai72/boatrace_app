from sqlalchemy import create_engine


def load_cloud_sql(db_settings):
    return create_engine('mysql+pymysql://{user}:{password}@/{database}?unix_socket=/cloudsql/{db_name}'.format(**db_settings))

def load_local_db(db_settings):
    return create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={encoding}'.format(**db_settings))