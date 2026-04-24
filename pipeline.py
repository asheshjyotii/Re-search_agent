import logging
import time
from typing import Callable, Literal

from agents import (
    build_search_agent,
    build_scrape_agent,
    writer_chain,
    critic_chain,
)

logger = logging.getLogger(__name__)

StepId = Literal["search", "scrape", "write", "critic"]
StepPhase = Literal["start", "end"]

# Build agents ONCE globally for better performance
SEARCH_AGENT = build_search_agent()
SCRAPE_AGENT = build_scrape_agent()


def run_research_pipeline(
    topic: str,
    *,
    on_step: Callable[[StepId, StepPhase, dict | None], None] | None = None,
) -> dict:
    """
    Runs the complete research workflow:
    Search → Scrape → Write → Critic

    Optional on_step(step, phase, meta) is called with phase \"start\" before
    each step and \"end\" after, with meta {\"seconds\": float} on end.
    """
    state: dict = {}
    timings: dict[str, float] = {}
    total_start = time.time()

    logger.info("research pipeline started topic=%r", topic)

    # STEP 1: SEARCH
    if on_step:
        on_step("search", "start", None)
    start = time.time()
    search_result = SEARCH_AGENT.invoke({
        "messages": [{
            "role": "user",
            "content": f"Find detailed, recent and reliable information about {topic}",
        }],
    })
    elapsed = time.time() - start
    timings["search"] = elapsed
    state["search_results"] = search_result["messages"][-1].content
    logger.info("search completed in %.2fs", elapsed)
    if on_step:
        on_step("search", "end", {"seconds": elapsed})

    # STEP 2: SCRAPE
    if on_step:
        on_step("scrape", "start", None)
    start = time.time()
    scrape_result = SCRAPE_AGENT.invoke({
        "messages": [{
            "role": "user",
            "content": (
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{state['search_results'][:1000]}"
            ),
        }],
    })
    elapsed = time.time() - start
    timings["scrape"] = elapsed
    state["scraped_content"] = scrape_result["messages"][-1].content
    logger.info("scrape completed in %.2fs", elapsed)
    if on_step:
        on_step("scrape", "end", {"seconds": elapsed})

    # STEP 3: WRITE REPORT
    if on_step:
        on_step("write", "start", None)
    start = time.time()
    writer_report = writer_chain.invoke({
        "topic": topic,
        "research": (
            f"Search Results:\n{state['search_results']}\n\n"
            f"Deep Scraped Content:\n{state['scraped_content']}"
        ),
    })
    elapsed = time.time() - start
    timings["write"] = elapsed
    state["writer_report"] = writer_report
    logger.info("write completed in %.2fs", elapsed)
    if on_step:
        on_step("write", "end", {"seconds": elapsed})

    # STEP 4: CRITIC REVIEW
    if on_step:
        on_step("critic", "start", None)
    start = time.time()
    critic_result = critic_chain.invoke({"report": state["writer_report"]})
    elapsed = time.time() - start
    timings["critic"] = elapsed
    state["critic_result"] = critic_result
    logger.info("critic completed in %.2fs", elapsed)
    if on_step:
        on_step("critic", "end", {"seconds": elapsed})

    total_time = time.time() - total_start
    state["timings"] = timings
    state["total_seconds"] = total_time
    logger.info("pipeline completed in %.2fs total", total_time)

    return state
