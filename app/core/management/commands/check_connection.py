import psycopg2
import os
from django.core.management.base import BaseCommand
import time


class Command(BaseCommand):
    """Django command to pause untill databse is ready"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for connection... ')
        db_conn = None
        while not db_conn:
            try:
                conn = psycopg2.connect("host=localhost dbname=postgres", host=os.environ.get('DB_HOST'),
                                           dbname=os.environ.get('DB_NAME'), user=os.environ.get('DB_USER'),
                                           password=os.environ.get('DB_PASS'))
                conn.close()
                db_conn = True
            except psycopg2.OperationalError as ex:
                self.stdout.write("Connection failed: {0}".format(ex))
                time.sleep(5)

        self.stdout.write(self.style.SUCCESS('Connected!'))
