import jsonpickle
from database.models import Acesso
from database.models import Veiculo
from sqlalchemy.orm import Session
from sqlalchemy import select
from services import engine


def GetAll():
    session = Session(engine)
    acessos = select(Acesso).join(Acesso.veiculo, isouter=True).join(Veiculo.funcionario, isouter=True)
    return session.scalars(acessos)

def GetAllAsJson():
    session = Session(engine)
    acessos = select(Acesso).join(Acesso.veiculo, isouter=True).join(Veiculo.funcionario, isouter=True)
    acessos = session.scalars(acessos)
    # Converter os resultados em uma lista de dicionários
    dados = [resultado.to_json(depth=2) for resultado in acessos]
    # Converter a lista de dicionários em JSON
    json_data = jsonpickle.encode(dados)
    return json_data


def Save(ehEntrada: bool, caracteres_detectados: str, veiculo_id: int):
    with Session(engine) as session:
        novo_acesso = Acesso(
            eh_entrada=ehEntrada,
            caracteres_detectados=caracteres_detectados,
            veiculo_id=veiculo_id,
        )
        session.add(novo_acesso)
        session.commit()


def GetById(id: int):
    session = Session(engine)
    acesso = (
        select(Acesso)
        .join(Veiculo, Veiculo.id == Acesso.veiculo_id, isouter=True)
        .where(Acesso.id == id)
    )
    return session.scalars(acesso).one()
