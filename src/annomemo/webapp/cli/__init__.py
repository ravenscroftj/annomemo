from .users import users
from click import CommandCollection, Group


cli = Group(commands=[users])

if __name__ == "__main__":
    cli()
