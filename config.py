
import os

class Config:
    DB_NAME = "QaAcebank"
    DB_SERVER = r'ALBERT\MSSQLSERVER_FULL'
    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc://@{DB_SERVER}/{DB_NAME}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '1'


