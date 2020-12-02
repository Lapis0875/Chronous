from typing import Callable, Coroutine, Any, Dict

CoroutineFunction = Callable[..., Coroutine]    # coroutinefunction type hint


class Event:
    """
    Event class
    """
    name: str
    # 1.(2) : Event instance as a parameter of listener
    attrs: Dict[str, Any]   # Keyword-arguments of additional attributes assigned to the context.


# 1.(1) : Context object as a parameter of listener
class Context:
    """
    Context class for listener
    """
    e: Event                # Instance of event relevant with the listener.
    attrs: Dict[str, Any]   # Keyword-arguments of additional attributes assigned to the context.


# 2.(1) coroutine function as a listener
# Advantage: simple structure
def subscribeEvent(subscriberCoro: CoroutineFunction, name: str) -> CoroutineFunction:
    """Subscribe coroutine function with listener structure as listener of the event with given name.

    Parameters
    ----------
        subscriberCoro: CoroutineFunciton (async def ~)
            coroutine function object to register as listener.
        name: str
            name of event to register this as a listener.

    Returns
    -------
        subscriberCoro: coroutine function object
            return original coroutine function object.
    """
    pass


# 2.(1) Example.
@subscribeEvent(name="Event")
async def onEvent(ctx: Context):
    pass


class Class:
    def Method(self):
        pass


ClassType = type(Class) # type, as a metaclass.
# classmethod type is a class 'classmethod'
# staticmethod type is a class 'staticmethod'
instance = Class()
MethodType = type(instance.Method)


# 2.(2) : class as a event subscriber
# Advantages : Can listen to multiple events in a single subscriber class,
# can have variables and methods to support listeners.
def SubscribeEvent(subscriberClass: ClassType) -> ClassType:
    """Subscribe class with event subscriber structure as subscriber of events (can be multiple).

    Parameters
    ----------
        subscriberClass: class
            class object which defines event listeners named "on~" / decorated with @listen.

    Returns
    -------
        subscriberClass: class object
            return original class object.
    """
    pass


def listen(m: MethodType, name: str) -> MethodType:
    """Register given method as a listener of given event.

    Parameters
    ----------
        m: MethodType
            method object which defines listener structure.
        name: str
            name of the event to register this listener at.

    Returns
    -------
        subscriberClass: class object
            return original class object
    """
    instance = m.__self__   # instance of subscriber bound in the given method.
    func = m.__func__       # function object inside the given method.
    pass


# 2.(2) example
@SubscribeEvent
class EventSubscriber:
    memberChanged: list = []

    @listen(name="MemberJoinEvent")
    async def onMemberJoin(self, e: Event):
        pass

    @listen(name="MemberLeaveEvent")
    async def onMemberLeave(self, e: Event):
        if e.member in self.memberChanged:
            print("Changed member has left the server!")
        pass

    @listen(name="MemberUpdateEvent")
    async def onMemberUpdate(self, e: Event):
        self.memberChanged.append(e.member)