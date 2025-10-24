from app.managers.database_manager import DatabaseManager


def get_database_manager():
    database_manager = DatabaseManager()
    try:
        yield database_manager
    finally:
        database_manager.close()
