"""Pass image file attachments to AstrBot's existing visual-input pipeline."""

import asyncio
from pathlib import Path

from PIL import Image as PillowImage

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.provider import ProviderRequest
from astrbot.api.star import Star
from astrbot.core.agent.message import TextPart
from astrbot.core.message.components import File, Reply


def is_image(path: str) -> bool:
    """Check content rather than guessing from the attachment's extension."""
    try:
        with PillowImage.open(path) as image:
            image.verify()
        return True
    except (OSError, ValueError):
        return False


class Main(Star):
    @filter.on_llm_request()
    async def promote_image_files(
        self, event: AstrMessageEvent, req: ProviderRequest
    ) -> None:
        if event.get_platform_name() != "aiocqhttp":
            return

        components = []
        for component in event.get_messages():
            components.append((component, False))
            if isinstance(component, Reply) and component.chain:
                components.extend((part, True) for part in component.chain)

        converted_notices = set()
        for component, quoted in components:
            if not isinstance(component, File):
                continue
            # AstrBot already downloads direct/quoted files and caches this path.
            path = await component.get_file()
            if not path or not await asyncio.to_thread(is_image, path):
                continue
            if path not in req.image_urls:
                req.image_urls.append(path)
            name = component.name or Path(path).name
            prefix = "File Attachment in quoted message" if quoted else "File Attachment"
            converted_notices.add(f"[{prefix}: name {name}, path {path}]")

        if not converted_notices:
            return

        # Keep non-image attachments; remove only the replaced path-only notices.
        req.extra_user_content_parts = [
            part
            for part in req.extra_user_content_parts
            if not (
                isinstance(part, TextPart) and part.text in converted_notices
            )
        ]
        if req.prompt == "<attachment>" and not req.extra_user_content_parts:
            req.prompt = ""
        logger.info(
            "[qq_image_files] Promoted %s image file attachment(s) to visual input.",
            len(converted_notices),
        )
