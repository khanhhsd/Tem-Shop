import math
import re


class RankingService:
    def rank_text(self, products, query):
        terms = [term for term in re.findall(r"[\w'-]+", (query or "").lower()) if term]
        ranked = []
        for product in products:
            name = product["name"].lower()
            category = product["category"].lower()
            color = product.get("color", "").lower()
            searchable = " ".join(
                (name, category, color, product.get("description", "").lower())
            )
            score = sum(
                3 if term in name else 2 if term in category or term in color else 1 if term in searchable else 0
                for term in terms
            )
            if score:
                ranked.append((product, score))
        return sorted(
            ranked,
            key=lambda match: (
                match[0]["id"] > 20,
                -match[1],
                match[0]["id"],
            ),
        )

    @staticmethod
    def cosine_similarity(left, right):
        if not left or not right or len(left) != len(right):
            return 0.0
        numerator = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if not left_norm or not right_norm:
            return 0.0
        return numerator / (left_norm * right_norm)
