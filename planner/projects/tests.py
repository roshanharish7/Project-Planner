from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date

from .models import AssignedProject, Project
from .serializers import AssignedProjectSerializer


class AssignedProjectSerializerTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title='Project',
            description='Description',
            documentation='project.pdf',
        )
        self.coordinator = get_user_model().objects.create_user(
            username='coordinator',
            password='password',
            role='Project Coordinator',
        )
        self.assigned_project = AssignedProject.objects.create(
            project=self.project,
            coordinator=self.coordinator,
            duration=6,
            start_date=date(2026, 11, 11),
            tentative_end_date=date(2027, 5, 11),
            project_completed=False,
        )

    def test_duplicate_assignment_returns_validation_error(self):
        response = self.client.post(
            '/assigned-projects/',
            {
                'project': self.project.pk,
                'coordinator': self.coordinator.pk,
                'developers': [],
                'duration': 6,
                'start_date': '2026-11-11',
                'tentative_end_date': '2027-05-11',
                'project_completed': False,
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('project', response.json())

    def test_allows_existing_project_when_updating_assignment(self):
        serializer = AssignedProjectSerializer(
            instance=self.assigned_project,
            data={'project': self.project.pk},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)


class TaskListCreateViewTests(TestCase):
    def test_task_list_uses_task_serializer(self):
        response = self.client.get('/tasks/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'], [])

    def test_unknown_assigned_project_uuid_returns_empty_list(self):
        response = self.client.get(
            '/tasks/',
            {'project': 'c1dccc95-876c-4e01-a6fc-0634d868f608'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'], [])
