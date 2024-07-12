from src.login import LoginManager
from instaloader.structures import Profile
import pdb


def test_issue():
    login_manager = LoginManager()

    with login_manager.session() as insta_loader:
        context = insta_loader.context
        profile = Profile.from_username(insta_loader.context, "destroyasalad")

        usernames = []
        for post in profile.get_posts():
            pdb.set_trace(header="Entering debugging with pdb.")
            post_likes = post.get_likes()
            for likee in post_likes:
                usernames.append(likee.username)

        return usernames


if __name__ == "__main__":
    test_issue()
