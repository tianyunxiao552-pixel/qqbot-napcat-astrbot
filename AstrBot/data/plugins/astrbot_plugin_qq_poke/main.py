"""Route QQ pokes through AstrBot's normal persona and conversation pipeline."""

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.message_components import Poke
from astrbot.api.star import Star


class PokeToSelf(filter.CustomFilter):
    def filter(self, event: AstrMessageEvent, cfg) -> bool:
        return (
            event.get_platform_name() == "aiocqhttp"
            and event.get_sender_id() != event.get_self_id()
            and any(
                isinstance(part, Poke) and part.target_id() == event.get_self_id()
                for part in event.get_messages()
            )
        )


class QQPoke(Star):
    @filter.custom_filter(PokeToSelf)
    async def respond_to_poke(self, event: AstrMessageEvent):
        # Native whitelist/rate-limit stages run before this handler.
        # Let ProcessStage build the usual request with its persona and history.
        event.message_str = "（戳了戳你）"
        event.is_at_or_wake_command = True
        logger.info("[qq_poke] Accepted poke; using the normal persona conversation.")
