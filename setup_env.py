from secrets import token_bytes


ENV_TEMPLATE = [
    f"SECRET_KEY={token_bytes(32).hex()}",
    "IP_ADDRESS=localhost",
    "PORT=8000",
    "JSW_ALGORITHM=HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES=240",
    "POSTGRES_PASSWORD=",
    "BACKEND_PASSWORD=",
]

with open(".env", "w") as f:
    f.write("\n".join(ENV_TEMPLATE))
