from secrets import token_bytes


key = token_bytes(32).hex()
print(key)
