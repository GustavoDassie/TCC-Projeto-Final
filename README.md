# Sistema de Baixo Custo para Controle de Acesso de Veículos

Este projeto tem como objetivo desenvolver um sistema acessível e eficiente para o controle de acesso de veículos, utilizando tecnologias de ponta. A arquitetura do sistema integra hardware e software, proporcionando uma solução eficaz para aplicações em controle de acesso veicular, gerenciamento de tráfego e segurança.

## Descrição Geral

O sistema baseia-se em uma arquitetura robusta que utiliza hardware ESP32-CAM para captura de imagens e acionamento da cancela. A parte de processamento de imagem é fundamentada no projeto [Fanghon/lpr](https://github.com/fanghon/lpr), garantindo eficiência na detecção de placas e reconhecimento de caracteres. Além disso, o servidor foi implementado utilizando Flask, com a integração das bibliotecas Alembic e SQLAlchemy para facilitar operações relacionadas ao banco de dados.

## Instruções de Uso

1. **Requisitos:**

   * Python (versão 3.11)
   * Tesseract (versão 5.2.0.20220712)
   * Bibliotecas necessárias (listadas no arquivo `requirements.txt`)

2. **Instalação:**

   * Tesseract:
     * Guia para download: [Tessdoc/Downloads](https://github.com/tesseract-ocr/tessdoc/blob/main/Downloads.md)
   * Bibliotecas:

     ```powershell
     pip install -r requirements.txt
     ```

3. **Configurar variáveis de ambiente:**
   * Crie um novo arquivo chamado `.env`.

   * Crie a variável `DATABASE_URL` e a preencha com os dados de conexão com o Banco de dados.
     * Exemplo:

          ```dotenv
          DATABASE_URL=mysql+mysqlconnector://user:password@host/schema
          ```

   * Crie a variável `TESSERACT_CMD` e a preencha com o diretório de instalação do Tesseract.
     * Exemplo:

          ```dotenv
          TESSERACT_CMD="C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
          ```

4. **Banco de Dados:**

   * Configurar a conexão com o banco de dados:
     * Com o arquivo `.env` já configurado, aplique as migrações no banco de dados com o Alembic:

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

5. **Execução do Servidor:**
     * Execute o servidor Flask:

          ```powershell
          flask run
          ```

6. **Acesso à Interface Web:**

   * Abra um navegador e acesse <http://localhost:5000>
