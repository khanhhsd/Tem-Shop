from werkzeug.security import check_password_hash, generate_password_hash


class AuthService:
    def __init__(self, customer_repository):
        self.customer_repository = customer_repository

    def register(self, name, email, password, phone="", address=""):
        name = (name or "").strip()
        password = password or ""
        normalized_email = (email or "").strip().lower()
        if not name or not normalized_email or len(password) < 8:
            raise ValueError("Provide your name, email, and a password of at least 8 characters.")
        if self.customer_repository.get_by_email(normalized_email):
            raise ValueError("An account with that email already exists.")
        return self.customer_repository.create(
            name,
            normalized_email,
            generate_password_hash(password),
            phone.strip(),
            address.strip(),
        )

    def authenticate(self, email, password):
        customer = self.customer_repository.get_by_email((email or "").strip())
        if not customer or not check_password_hash(customer["password_hash"], password or ""):
            return None
        return self.customer_repository.get_by_id(customer["customer_id"])

    def get_customer(self, customer_id):
        return self.customer_repository.get_by_id(customer_id)
