from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Pessoa(Base):
    __tablename__ = 'pessoas'

    id = Column(Integer, primary_key=True)
    nome = Column(String(255))
    idade = Column(Integer)


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Substitua 'seu_usuario', 'sua_senha', 'seu_host' e 'seu_banco_de_dados' pelos valores apropriados
engine = create_engine('mysql+mysqlconnector://root:root@localhost/teste')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

nova_pessoa = Pessoa(nome='Alice', idade=30)
session.add(nova_pessoa)
session.commit()

pessoas = session.query(Pessoa).all()
for pessoa  in pessoas:
    print(f'Nome: {pessoa.nome}, Idade: {pessoa.idade}')