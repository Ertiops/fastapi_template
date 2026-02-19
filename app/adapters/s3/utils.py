from aiobotocore.session import AioSession, get_session


def create_session() -> AioSession:
    return get_session()
