import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from backend.data.database.update_tables import UpdateData


class UpdateController:
    def __init__(self) -> None:
        self.update_data = UpdateData()

    def update_data(self) -> dict:
        self.update_data.update_data()

        response = {"status": "updated"}

        return response
