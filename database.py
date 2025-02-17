from sqlalchemy import create_engine, text

engine = create_engine('mysql+pymysql://admineduconnectlms:password.2109@educonnectlms.mysql.database.azure.com/educonnect')

# def get_studygroups():
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT * FROM studygroups"))
#         studygroups = []
#         for row in result.all():
#             studygroups.append(dict(row))
#         return studygroups

with engine.connect() as conn:
      result = conn.execute(text("SELECT * FROM studygroups"))
      print(result.all())