from django.test import TestCase
from unittest.mock import patch
from polls.models import Poll, Choice
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from unittest.mock import patch
from django.contrib import messages

class FakeVote:
    def __init__(self, user, poll, choice):
        self.user = user
        self.poll = poll
        self.choice = choice

    def save(self):
        print("Fake vote saved.")  # No real DB operation

class VoteWithFakeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password")
        self.client.login(username="alice", password="password")
        self.poll = Poll.objects.create(text="Language?", owner=self.user)
        self.choice = Choice.objects.create(poll=self.poll, choice_text="Python")

    @patch('polls.views.Vote', new=FakeVote)
    def test_vote_with_fake_vote_model(self):
        response = self.client.post(reverse('polls:vote', args=[self.poll.id]), {
            'choice': self.choice.id
        })
        self.assertEqual(response.status_code, 200)


class VoteStubTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bob", password="pw")
        self.client.login(username="bob", password="pw")
        self.poll = Poll.objects.create(text="Color?", owner=self.user)
        self.choice = Choice.objects.create(poll=self.poll, choice_text="Blue")

    @patch('polls.models.Poll.user_can_vote', return_value=False)
    def test_user_already_voted(self, mock_user_can_vote):
        response = self.client.post(reverse('polls:vote', args=[self.poll.id]), {
            'choice': self.choice.id
        })
        self.assertRedirects(response, reverse('polls:list'))


class VoteErrorMockTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="carol", password="pw")
        self.client.login(username="carol", password="pw")
        self.poll = Poll.objects.create(text="Drink?", owner=self.user)

    @patch.object(messages, 'error')
    def test_vote_no_choice_selected(self, mock_error):
        response = self.client.post(reverse('polls:vote', args=[self.poll.id]), {})  # No 'choice'
        mock_error.assert_called_once_with(
            response.wsgi_request,
            "No choice selected!",
            extra_tags='alert alert-warning alert-dismissible fade show'
        )
