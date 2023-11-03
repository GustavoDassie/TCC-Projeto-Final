from database.models import Acesso
from database.models import Veiculo
from sqlalchemy.orm import Session
from sqlalchemy import select
from services import engine


def GetAll():
    session = Session(engine)
    acessos = select(Veiculo).join(Veiculo.funcionario, isouter=True)
    return session.scalars(acessos)


def Save(ehEntrada: bytes, caracteres_detectados: str, veiculo_id: int):
    with Session(engine) as session:
        novo_acesso = Acesso(
            ehEntrada=ehEntrada,
            caracteres_detectados=caracteres_detectados,
            veiculo_id=veiculo_id,
        )
        session.add(novo_acesso)
        session.commit()


def GetByPlaca(id: int):
    session = Session(engine)
    acesso = select(Veiculo).where(Veiculo.id == id)
    return session.scalars(acesso).one()


def GetByPlaca(placa: str):
    session = Session(engine)
    print("*"+placa+"*")
    acesso = select(Veiculo).where(Veiculo.placa == placa)
    return session.scalars(acesso).one_or_none()
