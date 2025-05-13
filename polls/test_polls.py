from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from polls.models import Poll, Choice, Vote
from django.contrib.auth.models import Permission
from django.core.exceptions import ObjectDoesNotExist

class PollAppAdditionalTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="alice", password="password")
        perm = Permission.objects.get(codename='add_poll')
        self.user.user_permissions.add(perm)
        self.client.login(username="alice", password="password")
        self.poll = Poll.objects.create(text="Your favorite language?", owner=self.user)
        self.choice1 = Choice.objects.create(poll=self.poll, choice_text="Python")
        self.choice2 = Choice.objects.create(poll=self.poll, choice_text="JavaScript")

    # Valid Input 1: vote with valid choice
    def test_vote_valid_choice(self):
        response = self.client.post(reverse('polls:vote', args=[self.poll.id]), {
            'choice': self.choice1.id
        })
        self.assertContains(response, "Python")


    # Valid Input 2: search polls by keyword
    def test_search_poll_by_keyword(self):
        response = self.client.get(reverse('polls:list'), {'search': 'language'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your favorite language?")

    # Invalid Input 1: submit poll with missing question text
    def test_create_poll_missing_question(self):
        response = self.client.post(reverse('polls:add'), {
            'text': '',
            'choice1': 'Option A',
            'choice2': 'Option B'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')


    # Invalid Input 2: create poll with empty choices
    def test_create_poll_with_empty_choices(self):
        response = self.client.post(reverse('polls:add'), {
        'text': 'What is your favorite?',
        'choice1': '',
        'choice2': ''
    })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')  

    # Boundary Case 1: exactly 7 polls for pagination
    def test_pagination_exact_limit(self):
        for i in range(6): 
            Poll.objects.create(text=f"Poll {i}", owner=self.user)

        response = self.client.get(reverse('polls:list'))
        self.assertEqual(response.status_code, 200)

        self.assertIn('polls', response.context)
        page_obj = response.context['polls']
        
        self.assertGreater(page_obj.paginator.num_pages, 1)


    # Boundary Case 2: search with one character
    def test_search_one_letter(self):
        Poll.objects.create(text="Zebra poll", owner=self.user)
        response = self.client.get(reverse('polls:list'), {'search': 'z'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Zebra')

    # Exception Handling 1: vote with invalid choice ID
    def test_vote_with_invalid_choice_id(self):
        with self.assertRaises(ObjectDoesNotExist):
            self.client.post(reverse('polls:vote', args=[self.poll.id]), {
                'choice': 9999
            })

    # Exception Handling 2: access edit view for non-existent poll
    def test_edit_nonexistent_poll(self):
        response = self.client.get(reverse('polls:edit', args=[9999]))
        self.assertEqual(response.status_code, 404)

    # Business Logic 1: user cannot vote twice on same poll
    def test_prevent_double_vote(self):
        Vote.objects.create(user=self.user, poll=self.poll, choice=self.choice1)
        response = self.client.post(
            reverse('polls:vote', args=[self.poll.id]),
            {'choice': self.choice2.id},
            follow=True 
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You already voted this poll!")

    # Business Logic 2: only poll owner can access edit page
    def test_edit_poll_access_by_non_owner(self):
        other_user = User.objects.create_user(username="bob", password="123456")
        self.client.logout()
        self.client.login(username="bob", password="123456")
        response = self.client.get(reverse('polls:edit', args=[self.poll.id]))
        self.assertEqual(response.status_code, 403)
