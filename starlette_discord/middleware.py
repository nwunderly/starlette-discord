import secrets
import typing

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.datastructures import Secret

from .client import DiscordOAuthClient


def setup_login_session_middleware(
    # required args
    app: Starlette,
    client: DiscordOAuthClient,
    *,
    # starlette SessionMiddleware kwargs
    secret_key: typing.Union[str, Secret] = None,
    session_cookie: str = "session",
    max_age: int = 14 * 24 * 60 * 60,  # 14 days, in seconds
    same_site: str = "lax",
    https_only: bool = False,
    # starlette-discord args
    login_path: str = "/login",
    callback_path: str = "/callback",
    redirect_path: str = "/dash",
    generate_state: bool = False,
    login_prompt: str = None
) -> None:
    if not secret_key:
        secret_key = secrets.token_urlsafe(64)

    #########
    # LOGIN #
    #########

    @app.route(login_path)
    async def login_route_handler(request: Request):
        # skip login if there's already a login session
        if 'discord-user' in request.session:
            return RedirectResponse(redirect_path)

        # optionally set a state for the authorization
        if generate_state:
            state = secrets.token_urlsafe(32)
            request.session['state'] = state
        else:
            state = None

        # redirect to Discord authorization
        return client.redirect(state, login_prompt)

    ############
    # CALLBACK #
    ############

    @app.route(callback_path)
    async def callback_route_handler(request: Request):
        # skip login if there's already a login session
        if 'discord-user' in request.session:
            return RedirectResponse(redirect_path)

        if generate_state:
            session_state = request.session.get('state')
            query_state = request.query_params.get('state')

            # if state is invalid, raise 401-Unauthorized
            if not (session_state and query_state and session_state == query_state):
                raise HTTPException(401)

        # identify user, cache user info and token
        code = request.query_params.get('code')
        async with client.session(code) as session:
            user = await session.identify()
            token = session.token
            request.session['discord-user'] = user.json()
            request.session['discord-token'] = token

        return RedirectResponse(redirect_path)

    ##################
    # ADD MIDDLEWARE #
    ##################

    app.add_middleware(
        SessionMiddleware,
        secret_key=secret_key,
        session_cookie=session_cookie,
        max_age=max_age,
        same_site=same_site,
        https_only=https_only
    )


# TODO
# class DiscordSessionMiddleware(SessionMiddleware):
#     """A middleware that handles Discord login and session storage."""
