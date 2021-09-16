from sqlalchemy.orm import sessionmaker
from os import environ as env
from dotenv import load_dotenv
from JobOffers_API.database.PostgreSQL_connection_functions import connection2db

load_dotenv()

#  make connection with PostgreSQL
postgre_connection = connection2db(env['PostgreSQL_host2'], env['PostgreSQL_port2'], env['PostgreSQL_user2'],
                                   env['PostgreSQL_password2'], env['PostgreSQL_db_name2'])
postgre_session = sessionmaker(bind=postgre_connection)
