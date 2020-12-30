__all__ = (
    'isEarlyMethod'
)


def isMethodFunction(o) -> bool:
    return o.__qualname__ != o.__name__


def notMethodFunction(o) -> bool:
    return not isMethodFunction(o)
