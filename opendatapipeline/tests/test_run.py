import unittest

import pytest
from src.api import app

class TestApp(unittest.TestCase):
    def test_make_shell_context_returns_app(self):
        context = app.make_shell_context()
        self.assertIn('app', context)
        self.assertEqual(context['app'], app)

if __name__ == '__main__':
    unittest.main()
