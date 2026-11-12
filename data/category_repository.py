class CategoryRepository:
    def __init__(self, database):
        self.database = database

    def all(self):
        with self.database.connect() as connection:
            return [
                dict(row)
                for row in connection.execute(
                    "SELECT category_id, name FROM categories ORDER BY name"
                )
            ]
