from unittest import TestCase
from unittest.mock import patch

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

    @patch('app.commands.ParserLaucher.get_and_create_parent_categories')
    def test_launch_parser_parent(self, mock_launcher):
        self.runner.invoke(launch_parser, ['--parse', 'categories'])
        self.assertTrue(mock_launcher.called)

    @patch('app.commands.Parser.get_parent_categories')
    def test_launch_parser_called_parser_parent(self, mock_parser):
        self.runner.invoke(launch_parser, ['--parse', 'categories'])
        self.assertTrue(mock_parser.called)

    @patch('app.commands.ParserLaucher.save_to_jsonfile')
    def test_launch_parser_parent_called_json(self, mock_launcher):
        self.runner.invoke(launch_parser, ['--parse', 'categories'])
        self.assertFalse(mock_launcher.called)

        self.runner.invoke(launch_parser, ['--parse', 'categories', '--json'])
        self.assertTrue(mock_launcher.called)

    @patch('app.commands.ParserLaucher.get_and_create_subcategories')
    def test_launch_parser_subcategories(self, mock_launcher):
        self.runner.invoke(launch_parser, ['--parse', 'subcategories'])
        self.assertTrue(mock_launcher.called)

    @patch('app.commands.ParserLaucher.get_and_create_items')
    def test_launch_parser_items(self, mock_launcher):
        self.runner.invoke(launch_parser, ['--parse', 'items'])
        self.assertTrue(mock_launcher.called)
