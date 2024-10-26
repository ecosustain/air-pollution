from database.update_tables import UpdateData


class UpdateController:
    def __init__(self) -> None:
        self.update_data = UpdateData()

    def update_data(self) -> dict:
        self.update_data.update_data()

        response = {"status": "updated"}

        return response
