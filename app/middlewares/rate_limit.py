from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from collections import defaultdict
import time



class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, calls: int = 10, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self._clients : dict = defaultdict(list)
    

    async def dispatch(self, request, call_next):
        client_ip = request.client.host
        now = time.time()
        # Nettoyer les vieilles requêtes
        self._clients[client_ip] = [
            t for t in self._clients[client_ip]
            if now - t < self.period
        ]

        if len(self._clients[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={"detail": "Trop de requêtes. Réessayez plus tard."},
                headers={"Retry-After": str(self.period)},
            )
        self._clients[client_ip].append(now)
        return await call_next(request)
