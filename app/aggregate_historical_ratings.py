from app.models import OldReview

print(OldReview.query.with_entities(OldReview.asin).distinct())