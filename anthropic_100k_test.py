# Unit tests for anthropic_100k.py
import unittest
import anthropic_100k


class TestAnthropic100k(unittest.TestCase):
    """Unit tests for anthropic_100k.py"""
    def test_messages_to_string(self):
        """Test message string conversion."""
        messages = [
            anthropic_100k.Message(role=anthropic_100k.Role.HUMAN, content="Hello"),
            anthropic_100k.Message(role=anthropic_100k.Role.ASSISTANT, content="Hi"),
            anthropic_100k.Message(role=anthropic_100k.Role.HUMAN, content="How are you?"),
            anthropic_100k.Message(role=anthropic_100k.Role.ASSISTANT, content="Good, thanks!"),
        ]
        expected = """

Human: Hello

Assistant: Hi

Human: How are you?

Assistant: Good, thanks!"""
        actual = anthropic_100k.messages_to_string(messages)
        self.assertEqual(expected, actual)
