from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в базе данных для проверки сушествующего slug
        cls.post_author = User.objects.create_user(username='post_author')
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="testslug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая запись",
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post_author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""

        post_count = Post.objects.count()
        form_data = {
            "text": "Тестовая запись чезез форму",
            "group": self.group.pk,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile",
                kwargs={"username": self.post_author.username}
            )
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        post = Post.objects.latest("id")
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group_id, form_data["group"])

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""

        post_count = Post.objects.count()
        form_data = {
            "text": "Отредактированный тестовая запись чезез форму",
            "group": self.group.pk,
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": str(self.post.pk)}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail", kwargs={"post_id": str(self.post.pk)}
            ),
        )
        # Проверяем, что не создался новый пост
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                text="Отредактированный тестовая запись чезез форму",
            ).exists()
        )

    def test_nonauthorized_user_create_post(self):
        """Проверка создания записи не авторизированным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Текст поста",
            "group": self.group.id,
        }
        response = self.guest_user.post(
            reverse("posts:create"),
            data=form_data,
            follow=True
        )
        redirect = reverse('login') + '?next=' + reverse('posts:create')
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)
