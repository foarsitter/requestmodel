"""In the future it may be possible to implement our own params,
but for now we use the ones from FastAPI"""
from fastapi.params import Body as Body  # noqa
from fastapi.params import Cookie as Cookie  # noqa
from fastapi.params import File as File  # noqa
from fastapi.params import Header as Header  # noqa
from fastapi.params import Path as Path  # noqa
from fastapi.params import Query as Query  # noqa
