"""Method for post message.

All methods return a MessageResponse.
"""

from abc import ABC
from typing import Optional

import structlog
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from botchan.data_model.slack import MessageEvent, MessageResponse
from botchan.slack.exception import SlackResponseError

logger = structlog.getLogger(__name__)


class SlackChat(ABC):
    slack_client: WebClient

    def _post_message(
        self, channel_id: str, text: str, thread_ts: Optional[str] = None
    ) -> MessageResponse:
        """
        Posts a message to a given Slack channel using the provided WebClient.

        Parameters:
            client (WebClient): The WebClient instance to use for posting the message.
            channel_id (str): The ID of the channel to which the message should be posted.
            text (str): The message content.
            thread_ts (Optional[str]): Optional thread timestamp to reply in a thread.

        Returns:
            str: The timestamp of the newly posted message.

        Raises:
            SlackResponseError: If there was an error posting the message to Slack.
        """
        response = self.slack_client.chat_postMessage(
            channel=channel_id, text=text, thread_ts=thread_ts
        )
        if response.status_code == 200 and response["ok"]:
            return MessageResponse.from_api_response(response)
        else:
            raise SlackResponseError(response)

    def send_slack_message(self, channel_id: str, text: str) -> MessageResponse:
        """
        This function sends a Slack message to the specified channel using the given client object.
        """
        try:
            return self._post_message(channel_id=channel_id, text=text)
        except SlackApiError as e:
            logger.error("Error sending message", error=str(e))

    def reply_to_message(self, event: MessageEvent, text: str) -> MessageResponse:
        """
        This function sends a reply message to the channel where the original message was sent.
        """
        try:
            return self._post_message(
                channel_id=event.channel, text=text, thread_ts=event.ts
            )
        except SlackApiError as e:
            logger.error("Error sending message", error=str(e))
