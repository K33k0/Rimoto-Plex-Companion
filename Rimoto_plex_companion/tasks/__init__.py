import threading
# def daemonize(func):
#     def wrapper():
#         timer_thread = threading.Thread(target=func)
#         timer_thread.daemon = True
#         timer_thread.start()
#     return wrapper

def dameonize(func):
    def wrapper():
        timer_thread = threading.Timer(300, func)
        timer_thread.daemon = True
        timer_thread.start()
    return wrapper