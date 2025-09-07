# Basic test for health check
from django.test import TestCase
from django.urls import reverse


class HealthCheckTest(TestCase):
    def test_health_check_endpoint(self):
        """Test the health check endpoint returns 200 OK."""
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'healthy')
