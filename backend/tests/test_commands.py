from unittest import TestCase
from unittest import mock

from app import create_app
from app.commands import launch_parser


class TestCommands(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('test')
        cls.test_client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    def setUp(self):
        self.runner = self.app.test_cli_runner()

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def test_launch_parser_invalid_params(self):
        for param in ['', 5, True, {}, 'invalid_param']:
            result = self.runner.invoke(launch_parser, ['--parse', param])
            self.assertTrue('Invalid --parse type' in result.output)

    @mock.patch('app.parser.Parser')
    def test_launch_parser_get_parent_categories(self, mock_parser):
        self.runner.invoke(launch_parser, ['--parse', 'categories'])
        self.assertTrue(
            mock_parser.get_parent_categories.called_with())

    @mock.patch('app.parser.Parser')
    def test_launch_parser_get_subcategories(self, mock_parser):
        self.runner.invoke(launch_parser, ['--parse', 'subcategories'])
        self.assertTrue(
            mock_parser.get_subcategories.called_with())

    @mock.patch('app.parser.Parser')
    def test_launch_parser_get_items(self, mock_parser):
        self.runner.invoke(launch_parser, ['--parse', 'items'])
        self.assertTrue(
            mock_parser.get_items.called_with())
