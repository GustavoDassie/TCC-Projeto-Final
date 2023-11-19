from database.models import Funcionario
from sqlalchemy.orm import Session
from sqlalchemy import select
from services import engine
from datetime import datetime


def GetAll():
    session = Session(engine)
    funcionarios = select(Funcionario)
    return session.scalars(funcionarios)


def Save(nome: str, email: str, cpf: str, prontuario: str, usuario_id: int):
    with Session(engine) as session:
        novo_funcionario = Funcionario(
            usuario_id=usuario_id,
            nome=nome,
            email=email,
            cpf=cpf,
            prontuario=prontuario,
            ativo=True,
        )
        session.add(novo_funcionario)
        session.commit()


def GetById(id: int):
    session = Session(engine)
    funcionario = select(Funcionario).where(Funcionario.id == id)
    return session.scalars(funcionario).one()


def ToggleAtivo(id: int):
    session = Session(engine)
    funcionario_select = select(Funcionario).where(Funcionario.id == id)
    funcionario = session.scalars(funcionario_select).one()
    if funcionario:
        funcionario.ativo = not funcionario.ativo
        novaData = datetime.now()
        funcionario.atualizado_em = novaData
        session.commit()
        return True
    return False


def Delete(id: int):
    session = Session(engine)
    funcionario_select = select(Funcionario).where(Funcionario.id == id)
    funcionario = session.scalars(funcionario_select).one()
    if funcionario:
        session.delete(funcionario)
        session.commit()
        return True
    return False


def Update(id: int, nome: str, email: str):
    session = Session(engine)
    funcionario_select = select(Funcionario).where(Funcionario.id == id)
    funcionario = session.scalars(funcionario_select).one()
    if funcionario:
        funcionario.nome = nome
        funcionario.email = email
        novaData = datetime.now()
        funcionario.atualizado_em = novaData
        session.commit()
        return True
    return False
