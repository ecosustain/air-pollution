from database.update_tables import UpdateData


class UpdateController:
    def __init__(self) -> None:
        self.update_data_object = UpdateData()

    def update_data(self) -> dict:
        self.update_data_object.update_data()

        response = {"status": "updated"}

        return response
