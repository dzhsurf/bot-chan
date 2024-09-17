import unittest
from unittest.mock import MagicMock, patch

from botchan.agents.expert.data_mode import TaskConfig, TaskEntity
from botchan.agents.expert.task_node import TaskNode
from botchan.constants import GTP_4O_WITH_STRUCT
from botchan.settings import OPENAI_GPT_MODEL_ID
from botchan.slack.data_model.message_event import MessageEvent
from tests.data.messages import MESSAGE_EVENT_SIMPLE_1


class Te1(TaskEntity):
    value: str


class Te2(TaskEntity):
    value: int


class TestTaskNode(unittest.TestCase):
    def setUp(self) -> None:
        self.secret_word = "Hello World"
        message_data = MESSAGE_EVENT_SIMPLE_1.copy()
        message_data["text"] = self.secret_word
        self.message_event = MessageEvent(**message_data)
        return super().setUp()

    @patch("botchan.agents.expert.task_node.simple_assistant_with_struct_ouput")
    def test_process_with_root_struct_output(self, mock_assistant):
        config = TaskConfig(
            task_key="task1",
            instruction="Test instruction: {text}",
            input_schema={"message_event": MessageEvent},
            output_schema=Te1,
        )
        task_node = TaskNode(config=config)
        self.assertTrue(config.is_root)
        self.assertTrue(config.is_structure_output)

        # Test with root config and message_event in kwargs
        expect_result = Te1(value=self.secret_word)
        mock_assistant.return_value = expect_result
        result = task_node(message_event=self.message_event)

        mock_assistant.assert_called_once_with(
            model_id=GTP_4O_WITH_STRUCT,
            prompt=f"Test instruction: {self.secret_word}",
            output_schema=Te1,
        )
        self.assertEqual(result, expect_result)

    @patch("botchan.agents.expert.task_node.simple_assistant")
    def test_process_root_with_text_output(self, mock_simple_assistant):
        mock_simple_assistant.return_value = "Mocked structured response"

        config = TaskConfig(
            task_key="task1",
            instruction="Test instruction: {text}",
            input_schema={"message_event": MessageEvent},
            output_schema=str,
        )
        self.assertTrue(config.is_root)
        self.assertFalse(config.is_structure_output)
        task_node = TaskNode(config=config)

        result = task_node(message_event=self.message_event)
        mock_simple_assistant.assert_called_once_with(
            model_id=OPENAI_GPT_MODEL_ID,
            prompt=f"Test instruction: {self.secret_word}",
        )
        self.assertEqual(result, "Mocked structured response")

    @patch("botchan.agents.expert.task_node.simple_assistant")
    def test_process_with_non_root(self, mock_simple_assistant):
        mock_simple_assistant.return_value = "Processed data"

        config = TaskConfig(
            task_key="task3",
            instruction="Process data: {input1}, {input2}",
            input_schema={"input1": Te1, "input2": Te2},
            output_schema=str,
            upstream=["i1,", "i2"],
        )
        self.assertFalse(config.is_root)
        self.assertFalse(config.is_structure_output)
        task_node = TaskNode(config=config)
        input1 = Te1(value="test")
        input2 = Te2(value=123)
        result = task_node(input1=input1, input2=input2)

        mock_simple_assistant.assert_called_once_with(
            model_id=OPENAI_GPT_MODEL_ID,
            prompt=f"Process data: {input1}, {input2}",
        )
        self.assertEqual(result, "Processed data")