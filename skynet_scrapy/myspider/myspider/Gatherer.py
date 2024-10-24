import psycopg2
from dotenv import load_dotenv
import os
from psycopg2.errors import UniqueViolation
from dotenv import load_dotenv
import os

#get env variables from .env
load_dotenv()

load_dotenv()

class Gatherer:

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
        print('creating ucs_new_launches table')

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS ucs_new_launches(
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
                         COSPAR text primary key,
                         NORAD integer,
                         source_used_for_orbital_data text,
                         source text,
                         additional_source text,
                         data_status integer)""")
        self.connection.commit()

    def gather(self):
        #needs to check ucs_master first whether an entry with similar cospar exists
        #if it does then it should not be scraped
        table_exists_sql_query = """
            INSERT INTO ucs_new_launches (
                full_name, 
                official_name, 
                owner_country, 
                owner, 
                users, 
                orbit_class,
                orbit_type,
                in_geo, 
                perigee, 
                apogee, 
                inclination, 
                period, 
                mass, 
                dry_mass, 
                launch_date, 
                contractor, 
                launch_site, 
                launch_vehicle, 
                cospar, 
                norad,
                source_used_for_orbital_data,
                data_status)
            SELECT
                plname,
                name,
                state,
                owner,
                mission_sector,
                oporbit,
                orbit_type,
                CASE 
                    WHEN oporbit LIKE '%GEO%' THEN 1 
                    ELSE 0 
                END,
                perigee,
                apogee,
                inc,
                period,
                mass,
                drymass,
                ldate,
                manufacturer,
                launch_site,
                launch_vehicle,
                piece,
                satcat,
                source_used_for_orbital_data,
                data_status         
            FROM planet4589
            WHERE planet4589.piece NOT IN (SELECT cospar FROM ucs_master)
            AND planet4589.piece NOT IN (SELECT cospar FROM ucs_removed_satellites)
            ON CONFLICT (cospar) DO NOTHING
        """

        sql_query = """
            INSERT INTO ucs_new_launches (
                full_name, 
                official_name, 
                owner_country, 
                owner, 
                users, 
                orbit_class,
                orbit_type,
                in_geo, 
                perigee, 
                apogee, 
                inclination, 
                period, 
                mass, 
                dry_mass, 
                launch_date, 
                contractor, 
                launch_site, 
                launch_vehicle, 
                cospar, 
                norad,
                source_used_for_orbital_data,
                data_status)
            SELECT
                plname,
                name,
                state,
                owner,
                mission_sector,
                oporbit,
                orbit_type,
                CASE 
                    WHEN oporbit LIKE '%GEO%' THEN 1 
                    ELSE 0 
                END,
                perigee,
                apogee,
                inc,
                period,
                mass,
                drymass,
                ldate,
                manufacturer,
                launch_site,
                launch_vehicle,
                piece,
                satcat,
                source_used_for_orbital_data,
                data_status         
            FROM planet4589
            ON CONFLICT (cospar) DO NOTHING
        """
        try:
            table_name = "ucs_master"
            # table_name_remove = "ucs_removed_satellites"
            # table_exist_query = f"""SELECT exists (SELECT 1 FROM "{table_name_remove}")"""
            # self.cur.execute(table_exist_query)
            # table_exists = self.cur.fetchone()[0]
            # print(f'{table_name_remove} exists: {table_exists}')
            # input()
            table_exist_query = f"""SELECT exists (SELECT 1 FROM "{table_name}")"""
            self.cur.execute(table_exist_query)
            table_exists = self.cur.fetchone()[0]
            if table_exists:
                self.cur.execute(table_exists_sql_query)
            else:
                self.cur.execute(sql_query)
            self.connection.commit()
        except UniqueViolation as e:
            self.connection.rollback()
            print(f'Error: {e}')
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f'Error during item processing: {e}')
        finally:
            self.cur.close()
            self.connection.close()