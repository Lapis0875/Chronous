===============
Chronous
===============
|py_ver| |issues|

|pypi_ver| |pypi_license| |pypi_package| |pypi_status|

|discord|

**Chronous** is a asynchronous python library designed to make asynchronous event-driven architectures on discord.py

.. |py_ver| image:: https://img.shields.io/pypi/pyversions/chronous?label=Python%20Version&logo=python&logoColor=yellow
   :target: https://python.org
.. |issues| image:: https://img.shields.io/github/issues/Lapis0875/Chronous?logo=github&logoColor=white
    :target: https://github.com/Lapis0875/Chronous/issues
.. |pypi_ver| image:: https://img.shields.io/pypi/v/chronous?logo=pypi&logoColor=blue
    :target: https://pypi.org/project/chronous/
.. |pypi_license| image:: https://img.shields.io/pypi/l/chronous?logo=pypi&logoColor=blue
    :target: https://github.com/Lapis0875/Chronous/blob/master/LICENSE
.. |pypi_package| image:: https://img.shields.io/pypi/format/chronous?label=package&logo=pypi
   :target: https://pypi.org/project/chronous/
.. |pypi_status| image:: https://img.shields.io/pypi/status/chronous?color=blue&logo=pypi&logoColor=blue
    :target: https://pypi.org/project/chronous/
.. |discord| image:: https://img.shields.io/discord/622434051365535745?color=blue&label=Discord&logo=Discord&logoColor=White
   :target: https://discord.gg/taVq6rw

[Example]

.. code-block:: python

    class SampleArchitecture(BaseArchitecture):

        def __init__(self) -> None:
            super(SampleArchitecture, self).__init__(name="sample")

            # Registering events
            self.registerEvent(event=Setup())
            self.registerEvent(event=Init())
            self.registerEvent(event=Start())
            self.registerEvent(event=Close())

        def run(self) -> None:
            # Registering default lifecycle events
            # Start the game.
            print("Starting process...")
            asyncio.run(self.process())

        async def process(self) -> NoReturn:
            await self.dispatch("setup")
            await self.dispatch("init")
            print('='*20)
            await self.dispatch("start", datetime.datetime.now())
            index: int = 0
            while index < 10:
                print("Looping!")
                index += 1
            await self.dispatch("close")
            print('='*20)


    sample = SampleArchitecture()


    # Multiple listener sample
    @sample.listen()
    async def setup(ec: EventContext):
        print("{ec.name} phase - listener 1".format(ec=ec))


    @sample.listen()
    async def setup(ec: EventContext):
        print("{ec.name} phase - listener 2".format(ec=ec))


    # EventContext  sample
    @sample.listen()
    async def init(ec: EventContext):
        print("Initialization phase")
        print("Event : {event}".format(event=ec.event))


    # Additional arguments sample
    @sample.listen()
    async def start(ec: EventContext, time: datetime):
        print("Starting process...")
        print("Starting at : {time}".format(time=time))


    # Exception sample
    @sample.listen()
    async def close(ec: EventContext):
        print("Closing process...")
        print(f"Make an error : {1/0}")

    sample.run()

