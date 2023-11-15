from database import Base
from sqlalchemy import *
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing import Optional
from typing import List


class Acesso(Base):
    __tablename__ = "acesso"

    id = Column(Integer, primary_key=True)
    inserido_em = Column(DATETIME, server_default=func.now(), nullable=False)
    eh_entrada = Column(Boolean, nullable=False)
    caracteres_detectados = Column(String(255))
    veiculo_id: Mapped[Optional[int]] = mapped_column(ForeignKey("veiculo.id"))
    veiculo: Mapped[Optional["Veiculo"]] = relationship(back_populates="acessos")

    def to_json(self, depth=1):
        data = {
            "id": self.id,
            "inserido_em": self.inserido_em.strftime("%Y-%m-%d %H:%M:%S"),
            "eh_entrada": self.eh_entrada,
            "caracteres_detectados": self.caracteres_detectados,
        }
        if depth > 0:
            data["veiculo"] = (
                self.veiculo.to_json(depth=depth - 1) if self.veiculo else None
            )
        return data


class Veiculo(Base):
    __tablename__ = "veiculo"

    id = Column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    usuario: Mapped["Usuario"] = relationship(back_populates="veiculos")
    funcionario_id: Mapped[int] = mapped_column(ForeignKey("funcionario.id"))

    funcionario: Mapped["Funcionario"] = relationship(back_populates="veiculos")
    acessos: Mapped[List["Acesso"]] = relationship(back_populates="veiculo")

    placa = Column(String(255))
    modelo = Column(String(255))
    ano = Column(String(255))
    inserido_em = Column(DATETIME, server_default=func.now(), nullable=False)
    atualizado_em = Column(DATETIME, server_default=func.now(), nullable=False)
    ativo = Column(Boolean, nullable=False)

    def to_json(self, depth=1):
        data = {
            "id": self.id,
            "placa": self.placa,
            "modelo": self.modelo,
            "ano": self.ano,
            "inserido_em": self.inserido_em.strftime("%Y-%m-%d %H:%M:%S"),
            "atualizado_em": self.atualizado_em.strftime("%Y-%m-%d %H:%M:%S"),
            "ativo": self.ativo,
        }
        if depth > 0:
            data["usuario"] = (
                self.usuario.to_json(depth=depth - 1) if self.usuario else None
            )
            data["funcionario"] = (
                self.funcionario.to_json(depth=depth - 1) if self.funcionario else None
            )
            data["acessos"] = (
                [acesso.to_json(depth=depth - 1) for acesso in self.acessos]
                if self.acessos
                else None
            )
        return data


class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True)
    funcionarios: Mapped[List["Funcionario"]] = relationship(back_populates="usuario")
    veiculos: Mapped[List["Veiculo"]] = relationship(back_populates="usuario")
    nome = Column(String(255))
    email = Column(String(255))
    senha = Column(String(255))
    inserido_em = Column(DATETIME, server_default=func.now(), nullable=False)
    ativo = Column(Boolean, nullable=False)

    def to_json(self, depth=1):
        data = {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "senha": self.senha,
            "inserido_em": self.inserido_em.strftime("%Y-%m-%d %H:%M:%S"),
            "ativo": self.ativo,
        }
        if depth > 0:
            data["funcionarios"] = (
                [
                    funcionario.to_json(depth=depth - 1)
                    for funcionario in self.funcionarios
                ]
                if self.funcionarios
                else None
            )
            data["veiculos"] = (
                [veiculo.to_json(depth=depth - 1) for veiculo in self.veiculos]
                if self.veiculos
                else None
            )
        return data


class Funcionario(Base):
    __tablename__ = "funcionario"

    id = Column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    usuario: Mapped["Usuario"] = relationship(back_populates="funcionarios")
    veiculos: Mapped[List["Veiculo"]] = relationship(back_populates="funcionario")
    nome = Column(String(255))
    email = Column(String(255))
    cpf = Column(String(255))
    prontuario = Column(String(255))
    inserido_em = Column(DATETIME, server_default=func.now(), nullable=False)
    atualizado_em = Column(DATETIME, server_default=func.now(), nullable=False)
    ativo = Column(Boolean, nullable=False)

    def to_json(self, depth=1):
        data = {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "cpf": self.cpf,
            "prontuario": self.prontuario,
            "inserido_em": self.inserido_em.strftime("%Y-%m-%d %H:%M:%S"),
            "atualizado_em": self.atualizado_em.strftime("%Y-%m-%d %H:%M:%S"),
            "ativo": self.ativo,
        }
        if depth > 0:
            data["usuario"] = (
                self.usuario.to_json(depth=depth - 1) if self.usuario else None
            )
            data["veiculos"] = (
                [veiculo.to_json(depth=depth - 1) for veiculo in self.veiculos]
                if self.veiculos
                else None
            )
        return data
