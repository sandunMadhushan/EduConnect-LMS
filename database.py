from sqlalchemy import create_engine, text

engine = create_engine('mysql+pymysql://freedb_sandunmadu:&J29vY$xsVrTc#Z@sql.freedb.tech:3306/freedb_educonnect_lms', pool_size=10, max_overflow=20)
