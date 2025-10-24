from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.database_schemas import (
    AgendaList,
    CategoriesMapping,
    GetByCategoriesInput,
    GetByDateInput,
    SearchInput,
)
from app.utils.dependencies import (
    DatabaseManager,
    get_database_manager,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO replace with Depends equivalent
    database_manager = DatabaseManager()
    database_manager.reload()
    yield
    database_manager.close()


app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return "Pire Agenda Api"


@app.get("/all")
async def get_all(
    database_manager: DatabaseManager = Depends(get_database_manager),
) -> AgendaList:
    return database_manager.get_all()


@app.get("/categories")
async def get_categories(
    database_manager: DatabaseManager = Depends(get_database_manager),
) -> CategoriesMapping:
    return database_manager.get_categories()


@app.post("/filter/categories")
async def get_by_categories(
    get_by_categories_input: GetByCategoriesInput,
    database_manager: DatabaseManager = Depends(get_database_manager),
) -> AgendaList:
    return database_manager.get_by_categories(get_by_categories_input.categories)


@app.post("/filter/date")
async def get_by_date(
    get_by_date_input: GetByDateInput,
    database_manager: DatabaseManager = Depends(get_database_manager),
) -> AgendaList:
    return database_manager.get_by_date(get_by_date_input.date)


@app.post("/search")
async def search(
    search_input: SearchInput,
    database_manager: DatabaseManager = Depends(get_database_manager),
) -> AgendaList:
    return database_manager.search(
        search_input.query, search_input.in_title, search_input.in_description
    )


@app.get("/reload")
async def reload(
    database_manager: DatabaseManager = Depends(get_database_manager),
):
    database_manager.reload()
    return "ok"


@app.get("/{_id}")
async def get_by_id(
    _id: int,
    database_manager: DatabaseManager = Depends(get_database_manager),
) -> AgendaList:
    return database_manager.get_by_id(_id)
