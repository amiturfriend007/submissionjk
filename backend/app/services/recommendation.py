from typing import List

from app.db import models


def get_recommendations_for_user(user: models.User) -> List[models.Book]:
    # placeholder: implement content-based or collaborative filtering
    return []