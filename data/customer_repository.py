from data.database import use_connection


class CustomerRepository:
    def __init__(self, database):
        self.database = database

    def create(self, name, email, password_hash, phone="", address=""):
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO customers (name, email, password_hash, phone, address)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, email, password_hash, phone, address),
            )
            customer_id = cursor.lastrowid
            connection.execute(
                "INSERT INTO carts (customer_id) VALUES (?)", (customer_id,)
            )
            connection.commit()
            return self.get_by_id(customer_id, connection)

    def get_by_email(self, email, connection=None):
        with use_connection(self.database, connection) as conn:
            row = conn.execute(
                "SELECT * FROM customers WHERE email = ? COLLATE NOCASE", (email,)
            ).fetchone()
            return dict(row) if row else None

    def get_by_id(self, customer_id, connection=None):
        with use_connection(self.database, connection) as conn:
            row = conn.execute(
                """
                SELECT customer_id, name, email, phone, address, customer_type,
                       vip_level, discount_rate, welcome_coupon_code, trial_period_end,
                       is_admin
                FROM customers WHERE customer_id = ?
                """,
                (customer_id,),
            ).fetchone()
            return dict(row) if row else None
