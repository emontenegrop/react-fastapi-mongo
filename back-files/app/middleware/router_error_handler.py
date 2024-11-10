import time
import traceback
from copy import deepcopy
from typing import Callable

from app.config.messages import Messages
from app.logger import logger
from app.utils.exceptions import DetailHttpException
from app.utils.log_data import create_log_error, data_headers
from fastapi import HTTPException, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import ValidationError


class RouteErrorHandler(APIRoute):

    def get_route_handler(self) -> Callable:  # type: ignore
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            start_time = time.time()
            try:
                logger.debug(request.url.path)
                logger.debug(request.headers)
                return await original_route_handler(request)
            except ValidationError as exc:  # type: ignore
                data_log = data_headers(request)
                create_log_error(
                    data_log,
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    jsonable_encoder(exc),
                    jsonable_encoder(traceback.format_exc()),
                    format(time.time() - start_time),
                )
                tmpl = deepcopy(Messages.API_UNEXPECTED_ERROR)
                tmpl.message = f"{tmpl.message}: {exc.errors()}"  # type: ignore
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content=jsonable_encoder(tmpl),  # type: ignore
                )

            except DetailHttpException as exc:
                data_log = data_headers(request)
                create_log_error(
                    data_log,
                    exc.status_code,
                    exc.detail,
                    jsonable_encoder(traceback.format_exc()),
                    format(time.time() - start_time),
                )

                raise HTTPException(status_code=exc.status_code, detail=exc.detail)

            except Exception as exc:
                data_log = data_headers(request)
                logger.debug(traceback.format_exc)
                create_log_error(
                    data_log,
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    jsonable_encoder(exc),
                    jsonable_encoder(traceback.format_exc()),
                    format(time.time() - start_time),
                )

                if isinstance(exc, HTTPException):
                    raise exc
                # wrap error into pretty 500 exception
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(exc),
                )

        return custom_route_handler
