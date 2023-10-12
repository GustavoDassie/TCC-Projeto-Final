from database.Image import Image
from sqlalchemy.orm import Session
from services import engine


def GetAll():
    with Session(engine) as session:
        images = session.query(Image).all()
        return images


def Save(raw_data: bytes, charset: str, filename: str, file_ext: str = None):
    with Session(engine) as session:
        ext = file_ext
        name = filename

        if ext is None:
            ext = filename.split(".")[1].lower()
            name = filename.split(".")[0].lower()

        nova_imagem = Image(
            file_name=name,
            file_ext=ext,
            raw_data=raw_data,
            charset=charset,
            treated_data=raw_data,
        )
        session.add(nova_imagem)
        session.commit()

def GetById(id: int):
    with Session(engine) as session:
        image = session.query(Image).where(Image.id == id).one()
        return image
