from typing import Generator
import random
import simpy


def source(env: simpy.Environment, number: int, interval: float, counter: simpy.Resource,
           **kwargs) -> Generator:
    """Source generates customers randomly.

    ``kwargs`` includes keys ``'min_patience'`` and ``'max_patience'``.

    :param env: ``simpy``-environment.
    :param number: The number of customers.
    :param interval: The interval of the customers' arriving.
    :param counter: The ``simpy.Resource``'s counter.
    :return: ``simpy`` generator.
    """
    for i in range(number):
        c = customer(env, f"Customer #{i + 1}", counter, time_in_bank=12., **kwargs)
        env.process(c)
        t = random.expovariate(1 / interval)
        yield env.timeout(t)


def customer(env: simpy.Environment, name: str, counter: simpy.Resource, time_in_bank: float,
             **kwargs) -> Generator:
    """Customer arrives, is served and leaves.

    ``kwargs`` includes keys ``'min_patience'`` and ``'max_patience'``.

    :param env: ``simpy``-environment.
    :param name: Customer's name.
    :param counter: The ``simpy.Resource``'s counter.
    :param time_in_bank: Customer's time in bank.
    :return: ``simpy`` generator.
    """
    min_patience = kwargs['min_patience'] if 'min_patience' in kwargs else 0.
    max_patience = kwargs['max_patience'] if 'max_patience' in kwargs else 1.

    arrive = env.now
    print(f"{arrive:.3f} {name}: Here I'm")

    with counter.request() as req:
        patience = random.uniform(min_patience, max_patience)
        # Wait for the counter or abort at the end of our tether
        results = yield req | env.timeout(patience)

        wait = env.now - arrive

        if req in results:
            # We got to the counter
            print(f"{env.now:.3f} {name}: Waited {wait:.3f}")

            tib = random.expovariate(1 / time_in_bank)
            yield env.timeout(tib)
            print(f"{env.now:.3f} {name}: Finished")
        else:
            # We reneged
            print(f"{env.now:.3f} {name}: RENEGED after {wait:.3f}")


def main():
    # Setup and start the simulation
    print("*** Bank Renege ***")
    new_customers = 5
    interval_customers = 10.
    random.seed(42)
    env = simpy.Environment()

    # Start processes and run
    counter = simpy.Resource(env, capacity=1)
    env.process(source(env, new_customers, interval_customers, counter,
                       min_patience=1., max_patience=3.))
    env.run()

    return 0


if __name__ == '__main__':
    main()
