from functools import wraps


def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Before the function call.")
        result = func(*args, **kwargs)
        print("After the function call.")
        return result
    return wrapper


@decorator
def say_hello(name):
    """Greets the person with the given name."""
    print(f"Hello, {name}!")


if __name__ == "__main__":
    say_hello("Alice")
    print(say_hello.__name__)  # Output: say_hello
    print(say_hello.__doc__)   # Output: Greets the person with the given name.