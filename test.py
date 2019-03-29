from requests_threads import AsyncSession

session = AsyncSession(n=100)

async def _main():
    rs = []
    for _ in range(100):
        rs.append(await session.get('http://httpbin.org/get'))
    print(rs)

if __name__ == '__main__':
    session.run(_main)
