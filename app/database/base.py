from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """All ORM models inherit from this base — gives them the shared metadata registry."""
    pass
