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

    def update_object_ids(self, object_ids):
        """
          This method updates the REPOSITORY.DRS_OBJECT_UPDATE_STATUS table
          for a given list of object ids in the database. DRS automatically
          deletes the rows from the table when the row is updated.
        """

        sql = "merge into repository.drs_object_update_status a using " + \
              "(select id from repository.drs_object where id = :1) b " + \
              "on (a.id = b.id) " + \
              "when matched then update " + \
              "set a.write_to_queue=0, a.desc_needs_update=1, " + \
              "a.index_needs_update=1, a.mongo_needs_update=1 " + \
              "when not matched then " + \
              "insert (a.id, a.desc_needs_update, a.index_needs_update, " + \
              "a.in_process, a.concurrent_update, a.mongo_needs_update, " + \
              "a.write_to_queue) values (b.id, 1, 1, 0, 0, 1, 0)"
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
        sql = "SELECT DISTINCT(DRS_OBJECT_ID) FROM REPOSITORY.DRS_FILE " \
              "WHERE ID in (%s) " % (",".join(bind_file_ids))
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

    def get_descriptor_path(self, object_id):
        path = None
        storage_class = None
        object_id_tuple = (object_id,)
        sql = "SELECT df.FILE_PATH, sc.code FROM REPOSITORY.DRS_FILE df, " + \
              "REPOSITORY.STORAGE_CLASS sc WHERE " + \
              "df.storage_class_id = sc.id and df.DRS_OBJECT_ID = :1 " + \
              "AND df.USAGE_CLASS = 'DESCRIPTOR'"
        cursor = self.db.cursor()
        cursor.execute(sql, object_id_tuple)
        row = cursor.fetchone()
        if row:
            path = row[0]
            storage_class = row[1]
        return path, storage_class

    def check_object_in_update_queue(self, object_id):
        """
        This method checks if the object is in the update queue
        """
        object_id_tuple = (object_id,)
        in_queue = False
        sql = "SELECT ID FROM REPOSITORY.DRS_OBJECT_UPDATE_STATUS " + \
              "WHERE ID = :1"
        cursor = self.db.cursor()
        cursor.execute(sql, object_id_tuple)
        row = cursor.fetchone()
        if row:
            in_queue = True
        return in_queue
