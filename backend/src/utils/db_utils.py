from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from utils.credentials import LOGIN_MYSQL, PASSWORD_MYSQL

DATABASE_URL = f"mysql+pymysql://{LOGIN_MYSQL}:{PASSWORD_MYSQL}@db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def with_session(func):
    """
    Decorator to manage database sessions for non-request operations.
    Ensures proper cleanup and rollback on errors.
    """
    def wrapper(*args, **kwargs):
        session = Session()
        try:
            result = func(*args, session=session, **kwargs)
            session.commit()  # Commit if no errors
            return result
        except SQLAlchemyError as e:
            session.rollback()  # Rollback on error
            print(f"Error: {e}")
            raise e
        finally:
            session.close()
    return wrapper
