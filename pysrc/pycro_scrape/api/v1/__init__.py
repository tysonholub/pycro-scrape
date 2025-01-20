import json
from datetime import datetime, timedelta, timezone
from uuid import uuid1

from fastapi import APIRouter
from playwright._impl._api_structures import SetCookieParam
from playwright.async_api import Page, async_playwright

from pycro_scrape.api.exceptions import APIError
from pycro_scrape.api.v1.models import (
    BrowserSession,
    PostFetchSessionArgs,
    PostFetchSessionResponse,
    PostSessionArgs,
    PostSessionResponse,
)
from pycro_scrape.config import settings

router = APIRouter(prefix=f"{settings.api_prefix}/v1")


async def cache_page(page: Page, uuid: str) -> BrowserSession:
    await page.wait_for_load_state("load")

    existing_cache = await settings.redis.get(f"session:{uuid}")

    cache = json.loads(existing_cache) if existing_cache else {}
    right_meow = int(datetime.now(timezone.utc).timestamp())
    expire_delta = int(timedelta(hours=1).total_seconds())

    cache["id"] = uuid
    cache["url"] = cache.get("url", page.url)
    cache["cookies"] = await page.context.cookies()
    cache["iat"] = cache.get("iat", right_meow)
    cache["expires"] = right_meow + expire_delta

    try:
        # post_fetch_session may not support reading localStorage
        cache["local_storage"] = await page.evaluate("() => Object.entries(window.localStorage)")
    except Exception:  # nosec CWE-703
        pass

    session = BrowserSession(**cache)

    await settings.redis.setex(f"session:{uuid}", expire_delta, session.model_dump_json())

    return session


async def restore_page(page: Page, uuid: str):
    session = await settings.redis.get(f"session:{uuid}")

    if not session:
        raise APIError("Session not found", 404)

    session = BrowserSession(**json.loads(session))

    for cookie in session.cookies:
        c = SetCookieParam(
            name=cookie["name"],
            value=cookie["value"],
            url=cookie["url"],
            domain=cookie["domain"],
            path=cookie["path"],
            expires=cookie["expires"],
            httpOnly=cookie["httpOnly"],
            secure=cookie["secure"],
            sameSite=cookie["sameSite"],
        )
        await page.context.add_cookies(cookies=[c])

    for storage in session.local_storage:
        for key, value in storage.items():
            await page.evaluate(f"localStorage.setItem({key!r}, {value!r})")


@router.get("/sessions", response_model=list[BrowserSession])
async def get_sessions():
    keys = await settings.redis.keys("session:*")
    sessions = await settings.redis.mget(*keys)

    return [BrowserSession(**json.loads(session.decode())) for session in sessions]


@router.post("/sessions", response_model=PostSessionResponse)
async def post_session(args: PostSessionArgs):
    uuid = str(uuid1())

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(args.url)

        html_response = await page.content()

        session = await cache_page(page, uuid)
        await browser.close()

    return PostSessionResponse(
        session=session,
        html_response=html_response,
    )


@router.post("/sessions/{session_uuid}/fetch", response_model=PostFetchSessionResponse)
async def post_fetch_session(session_uuid: str, args: PostFetchSessionArgs):
    if args.post_data is None:
        script = f"""async () => {{
            try {{
                const response = await fetch({args.url!r}, {{
                    method: {args.method!r},
                    headers: {args.headers},
                }});
                return await response.text();
            }} catch (e) {{
                return e.toString();
            }}
        }};"""
    else:
        script = f"""async () => {{
            try {{
                const response = await fetch({args.url!r}, {{
                    method: {args.method!r},
                    headers: {json.dumps(args.headers)},
                    body: {json.dumps(args.post_data)!r},
                }});
                return await response.text();
            }} catch (e) {{
                return e.toString();
            }}
        }};"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-gpu",
                "--disable-setuid-sandbox",
                "--no-sandbox",
                "--no-zygote",
            ],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/115.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()
        await restore_page(page, session_uuid)

        fetch_response = await page.evaluate(script)

        session = await cache_page(page, session_uuid)

        await browser.close()

    return PostFetchSessionResponse(
        session=session,
        fetch_response=fetch_response,
    )
