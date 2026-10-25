"""Keep refusal/unknown-answer wording consistent with the QQ persona."""

import re

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageChain, filter
from astrbot.api.star import Star
from astrbot.core.agent.message import TextPart

FALLBACK = "这是和大家幸福无关的事"
FALLBACK_JA = "これは、みんなの幸せとは関係のないことです"
_PATTERNS = tuple(re.compile(pattern) for pattern in (
    r"(?:我|这(?:个|类|些|种)(?:话题|问题|请求|内容|人物评价|评价)).{0,16}(?:不能|无法|没办法|没有办法|不方便|不适合|不宜|不可以).{0,8}(?:回答|回复|讨论|谈论|聊|评价|提供|协助|帮助)",
    r"这(?:个|类|些|种).{0,18}(?:不聊|不谈|不评价|不作评价|不做评价)(?:了|啦|哦|呢|吧|[，。, ]|$)",
    r"(?:我|这(?:个|题|个问题|件事)).{0,10}(?:答不上来|回答不了|不知道(?:该|要|应该)?(?:怎么|如何)(?:回答|回复|答|说)|不知(?:该|要)?(?:怎么|如何)(?:回答|回复|答|说))",
    r"我(?:也|还|真的|确实|暂时)?不(?:知道|清楚|了解).{0,15}(?:答案|怎么回答|如何回答)",
    r"^(?:(?:抱歉|对不起|不好意思|这个|这题|嗯)[，,。\s]*)*(?:我(?:也|还|暂时)?(?:不知道|不清楚|不了解)|不知道|不清楚)(?:了|呢|啦)?[，,。！!\s]*$",
    r"(?:この|その)(?:質問|問い|話題|内容|お願い|リクエスト).{0,24}(?:答えられません|答えることはできません|お答えできません|お話しできません|お手伝いできません)",
    r"(?:お答え|回答|お手伝い|協力)(?:すること)?(?:は|が)?できません",
    r"(?:答え|回答)(?:が|は)(?:わかりません|分かりません|わからない|分からない)",
    r"(?:どう|なんと|何と)(?:お答え|答え|返事|返答|返信)(?:すれば|したら|ていいか).{0,10}(?:わかりません|分かりません|わからない|分からない)",
    r"^(?:(?:ごめんなさい|すみません|申し訳ありません)[、。\s]*)?(?:わたし(?:には|は|も))?(?:わかりません|分かりません|わからない|分からない)[。…\s]*$",
))


def needs_fallback(response) -> bool:
    text = (response.completion_text or "").strip()
    if text.startswith((FALLBACK, FALLBACK_JA)):
        return True
    choices = getattr(response.raw_completion, "choices", None)
    if choices and getattr(choices[0].message, "refusal", None):
        return True
    # Recognize the bot's own refusal/inability wording, not topic keywords.
    opening = text[:180].replace("\n", " ")
    opening = re.sub(r'“[^”]*”|「[^」]*」|‘[^’]*’|"[^"]*"', "", opening)
    return any(pattern.search(opening) for pattern in _PATTERNS)


class QQFallbackPhrase(Star):
    @filter.on_agent_done()
    async def normalize_reply(self, event: AstrMessageEvent, run_context, response):
        if (
            event.get_platform_name() != "aiocqhttp"
            or response is None
            or response.role != "assistant"
            or not needs_fallback(response)
        ):
            return
        text = FALLBACK_JA if event.get_extra("_qq_japanese_primary", False) else FALLBACK
        response.result_chain = MessageChain().message(text)
        response.reasoning_content = None
        event.set_extra("_llm_reasoning_content", None)
        # AstrBot records the assistant turn before this hook. Keep its refusal
        # consistent; Japanese-primary mode stores the original, not the display translation.
        messages = run_context.messages
        if messages and messages[-1].role == "assistant":
            messages[-1].content = [TextPart(text=text)]
        logger.info("[qq_fallback_phrase] Applied the configured fallback wording.")
