# from multiprocessing import Pool
# import requests
# import datetime
# import threading
# def get(url, container):
#     print("getting url {}".format(url))
#     res = requests.get(url)
#     print("response got from {}".format(url))
#
#     container.append(res)
#
# urls = ["https://www.google.com","https://bloomberg.com","https://www.wsj.com","https://yahoo.com","https://msn.com","https://nytimes.com"]
#
# if __name__ == "__main__":
#     start = datetime.datetime.now()
#     threads = []
#     container = []
#     for url in urls:
#         t = threading.Thread(target = get,args=(url,container))
#         t.start()
#         threads.append(t)
#     for t in threads:
#         t.join()
#     print("container has {} elements".format(len(container)))
#     done = datetime.datetime.now()
#     print(done-start)
#     start = datetime.datetime.now()
#     pool = Pool(len(urls))
#     pool.starmap(get,[(url, container) for url in urls])
#     print("container has {} elements".format(len(container)))
#     done = datetime.datetime.now()
#     print(done-start)
#     start = datetime.datetime.now()
#     for url in urls:
#         get(url, container)
#     print("container has {} elements".format(len(container)))
#     done = datetime.datetime.now()
#
#     print(done-start)


from requests_threads import AsyncSession

session = AsyncSession(n=100)
def run(i):
    print("running {}".format(i))
    return await session.get('http://httpbin.org/get')
async def _main():
    rs = []
    for i in range(100):
        rs.append( run(i))
    print(rs)

if __name__ == '__main__':
    session.run(_main)
