"""Audit logging middleware."""

from __future__ import annotations

import logging
from typing import Callable

from fastapi import Request

logger = logging.getLogger("audit")


def audit_middleware():
    async def middleware(request: Request, call_next: Callable):
        response = await call_next(request)
        logger.info("audit", extra={"path": request.url.path, "status_code": response.status_code})
        return response

    return middleware
