import oracledb as cx_Oracle
import os


class DrsDB:

  def __init__(self):
    self.db = self._get_db_connection()


  def is_open(self):
    try:
        return self.db.ping() is None
    except:
        return False


  def update_file_ids(self, file_ids):
    """
      This method is a helper for querying the DRS DB for object ois urn
      associated with file-ID
    """
    sql = "UPDATE REPOSITORY.DRS_OBJECT_UPDATE_STATUS f SET f.DESC_NEEDS_UPDATE = 1, f.INDEX_NEEDS_UPDATE = 1, f.CONCURRENT_UPDATE = 0 WHERE f.ID = :1"
    cursor = self.db.cursor()
    cursor.executemany(sql,file_ids)
    self.db.commit()

    if row is None:
      raise Exception("File not found in DRS DB with ID: {}".format(file_id))

    return row




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
