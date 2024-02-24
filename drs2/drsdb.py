import oracledb as cx_Oracle
import os
from dotenv import load_dotenv


class DrsDB:

    def __init__(self):
        load_dotenv()
        self.db = self._get_db_connection()

    def is_open(self):
        try:
            return self.db.ping() is None
        except cx_Oracle.Error:
            return False

    def update_object_ids(self, object_ids, integration_test=False):
        """
          This method updates the REPOSITORY.DRS_OBJECT_UPDATE_STATUS table
          for a given list of object ids in the database. DRS automatically
          deletes the rows from the table when the row is updated.
        """

        if integration_test:
            sql = "UPDATE REPOSITORY.DRS_OBJECT_UPDATE_STATUS o SET " + \
                  "o.DESC_NEEDS_UPDATE = 1, o.INDEX_NEEDS_UPDATE = 1, " + \
                  "o.MONGO_NEEDS_UPDATE = 1, o.WRITE_TO_QUEUE = 0, " + \
                  "o.CONCURRENT_UPDATE = 0 WHERE o.ID = :1"
        else:
            sql = "INSERT INTO REPOSITORY.DRS_OBJECT_UPDATE_STATUS o " + \
                  "(o.ID, o.DESC_NEEDS_UPDATE, o.INDEX_NEEDS_UPDATE, " + \
                  "o.MONGO_NEEDS_UPDATE, o.WRITE_TO_QUEUE, " + \
                  "o.CONCURRENT_UPDATE, o.IN_PROCESS) VALUES " + \
                  "(:1, 1, 1, 1, 0, 0, 1)"
        cursor = self.db.cursor()
        cursor.executemany(sql, object_ids, batcherrors=True)
        rows_updated = cursor.rowcount
        errors = []
        for error in cursor.getbatcherrors():
            errors.append({'index': error.offset, 'message': error.message})
        self.db.commit()
        cursor.close()
        return rows_updated, errors

    def get_object_ids(self, file_ids):
        """
           This method takes a list of file ids and
           returns a list of associated object ids
        """
        object_ids = []
        bind_file_ids = [":" + str(i + 1) for i in range(len(file_ids))]
        sql = "SELECT DRS_OBJECT_ID FROM REPOSITORY.DRS_FILE WHERE ID in (%s)"\
              % (",".join(bind_file_ids))
        cursor = self.db.cursor()
        cursor.execute(sql, file_ids)

        for row in cursor:
            object_ids.append(row)
        cursor.close()

        return object_ids

    def commit(self):
        self.db.commit()

    def close(self):
        self.db.close()

    def _get_db_connection(self):
        DB_HOST = os.getenv('DB_HOST')
        DB_PORT = os.getenv('DB_PORT')
        DB_NAME = os.getenv('DB_NAME')
        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        dsn_tns = cx_Oracle.makedsn(DB_HOST,
                                    DB_PORT,
                                    DB_NAME)
        db = cx_Oracle.connect(user=DB_USER,
                               password=DB_PASSWORD,
                               dsn=dsn_tns)
        return db
