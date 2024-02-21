import oracledb as cx_Oracle
import os
from . import configure_logger
from dotenv import load_dotenv


class DrsDB:

  def __init__(self):
    load_dotenv()
    configure_logger()
    self.db = self._get_db_connection()


  def is_open(self):
    try:
        return self.db.ping() is None
    except:
        return False


  def update_file_ids(self, file_ids, integration_test=False):
    """
      This method is a helper for querying the DRS DB for object ois urn
      associated with file-ID
    """
    if integration_test:
       sql = "UPDATE REPOSITORY.TEST_TABLE f SET f.DESC_NEEDS_UPDATE = 1, f.INDEX_NEEDS_UPDATE = 1, f.CONCURRENT_UPDATE = 0 WHERE f.ID = :1"
    else:
       sql = "UPDATE REPOSITORY.DRS_OBJECT_UPDATE_STATUS f SET f.DESC_NEEDS_UPDATE = 1, f.INDEX_NEEDS_UPDATE = 1, f.CONCURRENT_UPDATE = 0 WHERE f.ID = :1"
    cursor = self.db.cursor()
    cursor.executemany(sql,file_ids, batcherrors=True)
    errors = []
    for error in cursor.getbatcherrors():
        errors.append({'index': error.offset, 'message': error.message})
    self.db.commit()
    cursor.close()
    return errors


  def get_object_id(self, file_id):
    """
      This method is a helper for querying the DRS DB for object ois urn
      associated with file-ID
    """
    sql = "SELECT DRS_OBJECT_ID FROM REPOSITORY.DRS_FILE WHERE ID = {}".format(file_id)
    cursor = self.db.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()

    if row is None:
      raise Exception("File not found in DRS DB with ID: {}".format(file_id))
    
    object_id = row[0][0]
    cursor.close()

    return object_id
  

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
