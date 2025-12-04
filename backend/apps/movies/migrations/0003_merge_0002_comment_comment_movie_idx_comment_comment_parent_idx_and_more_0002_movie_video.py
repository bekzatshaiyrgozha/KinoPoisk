from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "movies",
            "0002_comment_comment_movie_idx_comment_comment_parent_idx_and_more",
        ),
        ("movies", "0002_movie_video"),
    ]

    operations = []
