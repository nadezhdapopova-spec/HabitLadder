from unittest.mock import MagicMock, patch

from django.test import TestCase

from habits.tasks import send_telegram_message


class SendTelegramMessageTests(TestCase):

    @patch("habits.tasks.requests.post")
    def test_send_telegram_message_success(self, mock_post):
        """Проверяет, что сообщение успешно отправлено"""
        mock_post.return_value.status_code = 200

        send_telegram_message(chat_id=123, message="Hello")

        mock_post.assert_called_once()
        params_called = mock_post.call_args.kwargs["params"]

        self.assertEqual(params_called["chat_id"], 123)
        self.assertEqual(params_called["text"], "Hello")

    @patch("habits.tasks.requests.post")
    def test_send_telegram_message_error(self, mock_post):
        """Проверяет, что Telegram вернул ошибку"""
        mock_response = MagicMock(status_code=400, text="Bad Request")
        mock_post.return_value = mock_response

        send_telegram_message(chat_id=999, message="Error test")

        mock_post.assert_called_once()
