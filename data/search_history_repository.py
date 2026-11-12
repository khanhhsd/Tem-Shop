import json

from data.database import use_connection


class SearchHistoryRepository:
    def __init__(self, database):
        self.database = database

    def add(self, customer_id, query_type, query_text, transcript=None, image_path=None, feature_vector=None):
        with self.database.connect() as connection:
            history_id = self.add_with_connection(
                connection,
                customer_id,
                query_type,
                query_text,
                transcript,
                image_path,
                feature_vector,
            )
            connection.commit()
            return history_id

    @staticmethod
    def add_with_connection(
        connection,
        customer_id,
        query_type,
        query_text,
        transcript=None,
        image_path=None,
        feature_vector=None,
    ):
        cursor = connection.execute(
            """
            INSERT INTO search_histories (customer_id, query_type, query_text)
            VALUES (?, ?, ?)
            """,
            (customer_id, query_type, query_text),
        )
        history_id = cursor.lastrowid
        if query_type == "voice":
            connection.execute(
                """
                INSERT INTO voice_search_queries (search_history_id, transcript)
                VALUES (?, ?)
                """,
                (history_id, transcript or query_text),
            )
        elif query_type == "image":
            connection.execute(
                """
                INSERT INTO image_search_queries (search_history_id, image_path, feature_vector)
                VALUES (?, ?, ?)
                """,
                (history_id, image_path or "", json.dumps(feature_vector or [])),
            )
        return history_id

    def recent_for_customer(self, customer_id, limit=10):
        with use_connection(self.database) as connection:
            return [
                dict(row)
                for row in connection.execute(
                    """
                    SELECT query_type, query_text, created_at
                    FROM search_histories WHERE customer_id = ?
                    ORDER BY created_at DESC, search_history_id DESC LIMIT ?
                    """,
                    (customer_id, limit),
                )
            ]
