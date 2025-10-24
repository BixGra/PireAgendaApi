from datetime import datetime
import re

from sqlalchemy import (
    Column,
    Date,
    Integer,
    Text,
)
from sqlalchemy import create_engine
from sqlalchemy import or_, extract
from sqlalchemy.orm import declarative_base, sessionmaker

from app.schemas.database_schemas import (
    AgendaItem,
    AgendaList,
    Categories,
    CategoriesMapping,
    CategoryMapping,
)
from app.utils.google_sheet import get_google_sheet_data

engine = create_engine(f"sqlite:///./app/data/pireagenda.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Agenda(Base):
    __tablename__ = "AGENDA"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    title = Column(Text)
    description = Column(Text)
    category1 = Column(Text, default="sans_categorie")
    category2 = Column(Text, default=None)
    category3 = Column(Text, default=None)
    link = Column(Text, default=None)
    link_title = Column(Text, default=None)


Base.metadata.create_all(bind=engine)


class DatabaseManager:
    def __init__(self):
        self._db = SessionLocal()

    def reload(self):
        data = get_google_sheet_data(
            "https://docs.google.com/spreadsheets/d/161ygk8Gyjn4JXMcP_fSjTJB776P0uZUsG7K8TTCYYV4/edit#gid=0"
        )
        existing_ids = {
            _id[0]
            for _id in self._db.query(Agenda.id).filter(
                Agenda.id.in_([row["id"] for row in data])
            )
        }
        self._db.add_all(
            [
                Agenda(
                    id=row["id"],
                    date=row["date"],
                    title=row["title"],
                    description=row["description"],
                    category1=Categories[row["category1"]].value,
                    category2=Categories[
                        row["category2"] if row["category2"] else "none"
                    ].value,  #  TODO clean
                    category3=Categories[
                        row["category3"] if row["category3"] else "none"
                    ].value,  #  TODO clean
                    link=row["link"],
                    link_title=row["link_title"],
                )
                for row in data
                if row["id"] not in existing_ids
            ]
        )
        self._db.commit()

    def close(self):
        self._db.close()

    @staticmethod
    def to_item(row) -> AgendaItem:
        return AgendaItem(
            id=row.id,
            date=row.date,
            title=row.title,
            description=row.description,
            category1=Categories(row.category1).name,
            category2=Categories(row.category2).name,
            category3=Categories(row.category3).name,
            link=row.link,
            link_title=row.link_title,
        )

    def wrap(self, query) -> AgendaList:
        return AgendaList(items=[self.to_item(row) for row in query])

    def get_all(self) -> AgendaList:
        return self.wrap(self._db.query(Agenda))

    @staticmethod
    def get_categories() -> CategoriesMapping:
        return CategoriesMapping(
            items=[
                CategoryMapping(name=category.name, value=category.value)
                for category in Categories
                if category.name != "none"
            ]
        )

    def get_by_id(self, _id: int) -> AgendaList:
        return self.wrap(self._db.query(Agenda).filter(Agenda.id == _id).first())

    def get_by_categories(self, categories: list[Categories]) -> AgendaList:
        _categories = [category.value for category in categories]
        return self.wrap(
            self._db.query(Agenda).filter(
                or_(
                    Agenda.category1.in_(_categories),
                    Agenda.category2.in_(_categories),
                    Agenda.category3.in_(_categories),
                )
            )
        )

    def get_by_date(self, date: datetime) -> AgendaList:
        target_month = date.month
        target_day = date.day
        return self.wrap(
            self._db.query(Agenda).filter(
                extract("month", Agenda.date) == target_month,
                extract("day", Agenda.date) == target_day,
            )
        )

    def search(self, query: str, in_title: bool, in_description: bool) -> AgendaList:
        pattern = f"(?i)({query})"
        criterion = []
        if in_title:
            criterion.append(Agenda.title.regexp_match(pattern, "i"))
        if in_description:
            criterion.append(Agenda.description.regexp_match(pattern, "i"))

        rows = self._db.query(Agenda).filter(*criterion)

        def highlight(text: str) -> str:
            return re.sub(
                pattern,
                r'<span class="highlight">\1</span>',
                text,
            )

        if in_title:
            for row in rows:
                row.title = highlight(row.title)

        if in_description:
            for row in rows:
                row.description = highlight(row.description)

        return self.wrap(rows)
