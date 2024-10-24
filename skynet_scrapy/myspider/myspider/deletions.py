import psycopg2
import os
from dotenv import load_dotenv

#get env variables from .env
load_dotenv()

class Deletions:
    def __init__(self):
        # hostname = 'localhost'  # this will be universal
        # username = 'skynetapp'  # create a new user with name: 'skynetapp'
        # password = 'skynet'  # make the password 'skynet' when you create the new user
        # # database = 'skynet' # we don't need this for this to work

        hostname = os.getenv('DB_HOST')
        username = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        #database = os.getenv('DB_NAME')
        self.connection = psycopg2.connect(host=hostname, user=username, password=password)
        self.cur = self.connection.cursor()

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS reentry_table(
                         full_name text,
                         official_name text,
                         country text,
                         owner_country text,
                         owner text,
                         users text,
                         purpose text,
                         detail_purpose text,
                         orbit_class text,
                         orbit_type text,
                         in_GEO INT,
                         perigee integer,
                         apogee integer,
                         eccentricity TEXT,
                         inclination double precision,
                         period text,
                         mass double precision,
                         dry_mass double precision,
                         power text,
                         launch_date date,
                         expected_lifetime TEXT,
                         contractor text,
                         contractor_country text,
                         launch_site text,
                         launch_vehicle text,
                         COSPAR text PRIMARY KEY,
                         NORAD integer,
                         source text,
                         additional_source text)""")
        # extra line
        self.connection.commit()

    def MarkDeletions(self):
        sql_query = """
            INSERT INTO reentry_table
            SELECT UCS_table.*
            FROM (
                SELECT o.designation AS COSPAR
                FROM UCS_table u
                JOIN orbitalfocus o ON u.NORAD = o.cat_no AND u.COSPAR = o.designation
                UNION
                SELECT a.cospar_num AS COSPAR
                FROM UCS_table u
                JOIN aero a ON u.NORAD = a.norad_num AND u.COSPAR = a.cospar_num
            ) AS joined_tables
            JOIN UCS_table ON joined_tables.COSPAR = UCS_table.COSPAR;
        """
        self.cur.execute(sql_query)
        self.connection.commit()
