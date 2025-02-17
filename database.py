from sqlalchemy import create_engine, text
import pymysql

# engine = create_engine('mysql+pymysql://admineduconnectlms:password.2109@educonnectlms.mysql.database.azure.com/educonnect')

# def get_studygroups():
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT * FROM studygroups"))
#         studygroups = []
#         for row in result.all():
#             studygroups.append(dict(row))
#         return studygroups


# with engine.connect() as conn:
#       result = conn.execute(text("SELECT * FROM studygroups"))
#       print(result.all())


conn = pymysql.connect(user='admineduconnectlms',
   password='password.2109',
   database='educonnect',
   host='educonnectlms.mysql.database.azure.com',
   ssl={'ca': '/var/www/html/DigiCertGlobalRootCA.crt.pem'})