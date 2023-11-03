from database.models import Funcionario
from database.models import Veiculo
from sqlalchemy.orm import Session
from sqlalchemy import select
from services import engine


def GetAll():
    session = Session(engine)
    acessos = select(Funcionario)
    return session.scalars(acessos)


def Save(nome: str, email: str, cpf: str, usuario_id: int):
    with Session(engine) as session:
        novo_acesso = Funcionario(
            usuario_id=usuario_id,
            nome=nome,
            email=email,
            cpf=cpf,
        )
        session.add(novo_acesso)
        session.commit()


def GetById(id: int):
    session = Session(engine)
    acesso = select(Funcionario).where(Funcionario.id == id)
    return session.scalars(acesso).one()
