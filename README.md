# Sistema de Baixo Custo para Controle de Acesso de Veículos

Este projeto tem como objetivo desenvolver um sistema acessível e eficiente para o controle de acesso de veículos, utilizando tecnologias de ponta. A arquitetura do sistema integra hardware e software, proporcionando uma solução eficaz para aplicações em controle de acesso veicular, gerenciamento de tráfego e segurança.

## Descrição Geral

O sistema baseia-se em uma arquitetura robusta que utiliza hardware ESP32-CAM para captura de imagens e acionamento da cancela. A parte de processamento de imagem é fundamentada no projeto [Fanghon/lpr](https://github.com/fanghon/lpr), garantindo eficiência na detecção de placas e reconhecimento de caracteres. Além disso, o servidor foi implementado utilizando Flask, com a integração das bibliotecas Alembic e SQLAlchemy para facilitar operações relacionadas ao banco de dados.

---

## Instruções de Uso

1. **Requisitos:**

   * Python (versão 3.11)
   * Bibliotecas necessárias (listadas no arquivo `requirements.txt`)

2. **Instalação:**

    ```powershell
    pip install -r requirements.txt
    ```

3. **Banco de Dados:**

   * Configurar a conexão com o banco de dados:
     * Crie um novo arquivo chamado `.env`.
     * Altere a variável de ambiente `DATABASE_URL` com os dados reais.
       * Exemplo:

          ```dotenv
          DATABASE_URL=mysql+mysqlconnector://user:password@host/database
          ```

     * Aplique as migrações no banco de dados com o Alembic:

          ```powershell
          alembic upgrade head
          ```

   * **Para novas alterações:**

     * Gerar automaticamente uma nova migração

          ```powershell
          alembic revision --autogenerate -m "nome_migracao"
          ```

     * Remover uma migração

          ```powershell
          alembic downgrade -1
          ```

4. **Execução do Servidor:**
     * Execute o servidor Flask:

          ```powershell
          flask run
          ```

5. **Acesso à Interface Web:**

   * Abra um navegador e acesse <http://localhost:5000>
