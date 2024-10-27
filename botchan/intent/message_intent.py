from pydantic import BaseModel, field_validator

_UNKNOWN = "unknown"
_METHOD = "method"
_EMOJI = "emoji"

MessageIntentMetadataType = str | bool | float | int | None


class MessageIntent(BaseModel):
    key: str
    metadata: dict[str, MessageIntentMetadataType] = {}

    @field_validator("key")
    @classmethod
    def uppercase_key(cls, v):
        if not isinstance(v, str):
            raise ValueError("The key must be a string.")
        return v.upper()

    @property
    def unknown(self) -> bool:
        return _UNKNOWN in self.metadata

    def equal_wo_metadata(self, other: "MessageIntent") -> bool:
        return self.key == other.key

    def set_metadata(self, **kwargs: MessageIntentMetadataType):
        """Set multiple metadata key-value pairs at once.

        Args:
            kwargs: Key-value pairs where the key is a string, and the value is of type MessageIntentMetaData.
        """
        for key, value in kwargs.items():
            self.metadata[key] = value

    def get_metadata(self, key: str) -> MessageIntentMetadataType:
        return self.metadata.get(key, None)


def create_intent(key: str | None = None, unknown: bool = False) -> MessageIntent:
    if unknown:
        return MessageIntent(key="", metadata={_UNKNOWN: True})
    assert key, "key must present"
    return MessageIntent(key=key)


_EMOJI_INTENT_MAP = {
    "miao": ["cat"],
}

_INTENT_BY_EMOJI = {
    emoji: intent for intent, emojis in _EMOJI_INTENT_MAP.items() for emoji in emojis
}


def get_message_intent_by_emoji(text: str) -> MessageIntent:
    for emoji in _INTENT_BY_EMOJI:
        if text.startswith(f":{emoji}:"):
            return MessageIntent(
                key=_INTENT_BY_EMOJI[emoji], metadata={_METHOD: _EMOJI, _EMOJI: emoji}
            )
    return MessageIntent(key="", metadata={_UNKNOWN: True, _METHOD: _EMOJI})