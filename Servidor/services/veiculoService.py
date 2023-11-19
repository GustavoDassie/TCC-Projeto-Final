from database.models import Veiculo
from sqlalchemy.orm import Session
from sqlalchemy import select
from services import engine
from datetime import datetime
from lpr import LPR


def GetAll():
    session = Session(engine)
    veiculos = select(Veiculo).join(Veiculo.funcionario, isouter=True)
    return session.scalars(veiculos)


def Save(placa: str, funcionario_id: str, modelo: str, ano: str, usuario_id: int):
    with Session(engine) as session:
        novo_veiculo = Veiculo(
            placa=placa,
            funcionario_id=funcionario_id,
            modelo=modelo,
            ano=ano,
            usuario_id=usuario_id,
            ativo=True,
        )
        session.add(novo_veiculo)
        session.commit()


def GetById(id: int):
    session = Session(engine)
    veiculo = select(Veiculo).where(Veiculo.id == id)
    return session.scalars(veiculo).one()


def GetByPlaca(placa: str):
    session = Session(engine)
    veiculo = select(Veiculo).where(Veiculo.placa == placa)
    return session.scalars(veiculo).one_or_none()


def GetOneInPlacas(placas: list[str]):
    session = Session(engine)
    veiculo = select(Veiculo).where(Veiculo.placa.in_(placas))
    return session.scalars(veiculo).one_or_none()


def ToggleAtivo(id: int):
    session = Session(engine)
    veiculo_select = select(Veiculo).where(Veiculo.id == id)
    veiculo = session.scalars(veiculo_select).one()
    if veiculo:
        veiculo.ativo = not veiculo.ativo
        novaData = datetime.now()
        veiculo.atualizado_em = novaData
        session.commit()
        return True
    return False


def Delete(id: int):
    session = Session(engine)
    veiculo_select = select(Veiculo).where(Veiculo.id == id)
    veiculo = session.scalars(veiculo_select).one()
    if veiculo:
        session.delete(veiculo)
        session.commit()
        return True
    return False


def Update(id: int, placa: str, funcionario_id: str, modelo: str, ano: str):
    session = Session(engine)
    veiculo_select = select(Veiculo).where(Veiculo.id == id)
    veiculo = session.scalars(veiculo_select).one()
    if veiculo:
        veiculo.modelo = modelo
        veiculo.ano = ano
        veiculo.funcionario_id = funcionario_id
        veiculo.placa = placa
        novaData = datetime.now()
        veiculo.atualizado_em = novaData
        session.commit()
        return True
    return False


def verify_access(detects: list[str], LPR_MODEL: LPR) -> tuple[bool, str, int | None]:
    if len(detects) > 0:
        for detect in detects:
            charset = detect.replace(" ", "").replace("\n", "")

            veiculo = GetByPlaca(charset)

            if veiculo is not None:
                return veiculo.ativo, charset, veiculo.id
            else:
                placas = LPR_MODEL.all_correcoes_placa(charset)
                veiculo = GetOneInPlacas(placas)
                if veiculo is not None:
                    return veiculo.ativo, charset, veiculo.id

    return (
        False,
        ", ".join([detect.replace(" ", "").replace("\n", "") for detect in detects]),
        None,
    )
