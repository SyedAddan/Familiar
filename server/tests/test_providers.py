import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from utils.llm import generate_chatbot_response


class GroqProviderTests(unittest.TestCase):
    def test_chat_uses_groq_openai_compatible_endpoint(self):
        completion = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Hello!"))]
        )
        create_completion = Mock(return_value=completion)
        client_instance = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=create_completion)
            )
        )
        with (
            patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}),
            patch("utils.llm.OpenAI") as openai_client,
        ):
            openai_client.return_value = client_instance
            response, messages = generate_chatbot_response(
                "Hi", "Alex", "friend", "", []
            )

        openai_client.assert_called_once_with(
            api_key="test-key",
            base_url="https://api.groq.com/openai/v1",
        )
        self.assertEqual(
            create_completion.call_args.kwargs["model"],
            "llama-3.3-70b-versatile",
        )
        self.assertEqual(response, "Hello!")
        self.assertEqual(messages[-1], {"role": "assistant", "content": "Hello!"})

    def test_missing_groq_key_is_reported(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            with self.assertRaisesRegex(RuntimeError, "GROQ_API_KEY"):
                generate_chatbot_response("Hi", "Alex", "friend", "", [])


if __name__ == "__main__":
    unittest.main()
