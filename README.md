# 🛡️ Auditoria STRIDE com IA

Este projeto foi desenvolvido para o **Hackathon FIAP - Fase 5**, com o objetivo de automatizar a análise de segurança de arquiteturas cloud. Utilizando a multimodalidade do **Google Gemini 2.5 Flash**, transformamos um diagrama de arquitetura (JPG) em um dataset de componentes e, sequencialmente, em um relatório detalhado de vulnerabilidades baseado no modelo **STRIDE**.



## 🚀 Fluxo de Funcionamento

1.  **Visão Computacional**: O Gemini analisa o diagrama `.jpg`.
2.  **Extração de Dados**: Identificação automática de cada serviço (S3, EC2, etc).
3.  **Análise de Segurança**: Processamento de cada componente usando o framework **STRIDE** (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege).
4.  **Relatório Profissional**: Exportação automática para um PDF formatado e objetivo, com notificação via e-mail.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.11+
* **IA:** Google Gemini 2.5 Flash (API `google-generativeai`)
* **Processamento de Imagem:** Pillow (PIL)
* **Geração de PDF:** FPDF2
* **Persistência:** JSON (Cache local para economia de tokens e testes)

## 📁 Estrutura do Projeto

```text
├── arquivos/                    # Pasta onde salvamos o jpg da arquitetura a ser analisada
│   ├── arquitetura_aws_01.jpg     
├── output/                      # Pasta onde os relatórios finais são salvos, datasets auxiliares, etc.
├── src/
│   ├── hackathon.py             # Script principal (Visão, Análise e Geração de Relatório de Vulnerabilidades)
├── .env.example                 # Modelo para configuração da API Key
├── requirements.txt             # Dependências do projeto
└── .gitignore                   # Proteção contra upload de venv e chaves
``` 
---

## 💻 Como Executar

Siga os passos abaixo para configurar o ambiente e rodar a análise em sua máquina. Em nosso roteiro via Windows, executamos todos os comandos via **Windows PowerShell**, com a versão do Python **3.11**.

### 1. Preparar o Diretório de Trabalho

Escolha ou crie uma pasta de sua preferência para organizar o projeto:

```
# Criar uma pasta para seus projetos (exemplo)
mkdir MeusProjetos

cd MeusProjetos
```

### 2. Clonar o Repositório


```bash
git clone [https://github.com/AndreDorte/fiap-hackathon.git](https://github.com/AndreDorte/fiap-hackathon.git)

cd fiap-hackathon
``` 
### 3. Configurar o Ambiente Virtual (venv)
No Windows (PowerShell):

```PowerShell
py -m venv .venv

.\.venv\Scripts\Activate.ps1 # outra alternativa seria .\.venv\Scripts\Activate.bat
``` 
No Linux ou macOS:

```Bash
python3 -m venv .venv

source venv/bin/activate
``` 

### 4. Instalar as Dependências
Com o ambiente virtual ativo, execute:

```Bash
pip install -r requirements.txt
```

### 5. Configurar a API Key

1. Obtenha sua chave gratuita no [Google AI Studio](https://aistudio.google.com/api-keys).
2. Edite o arquivo *.env* na raiz do projeto , e atualize a chave GEMINI_API_KEY com o valor obtido.
3. Obtenha sua chave gratuita no [Resend](https://resend.com/api-keys)
4. Edite novamente o arquivo *.env*, e atualize a chave RESEND_API_KEY com o valor obtido.

### 6. Executar a Análise

Certifique-se de que sua imagem de arquitetura está na pasta **arquivos** raiz com extensão `jpg`. Em seguida, rode:

```Bash
python .\src\hackathon.py
```
### 📂 Estrutura de Arquivos

```
├── arquivos/                    # Pasta com o jpg da arquitetura analisada
│   ├── arquivo.jpg     
├── output/                      # Pasta onde os PDFs finais e arquivos auxiliares são gerados
├── src/
│   ├── hackathon.py             # Script principal (Orquestração da IA e PDF)
├── .env                         # Arquivo de credenciais
├── .gitignore                   # Proteção de arquivos sensíveis e venv
├── requirements.txt             # Bibliotecas necessárias (fpdf2, pillow, google-generativeai, python-dotenv)
```

### 📊 Saída Esperada

O script gera um relatório PDF profissional na pasta /outputs. Para cada componente identificado, o Gemini detalha a ameaça específica (conforme o modelo STRIDE) e a respectiva mitigação técnica recomendada pelas melhores práticas da AWS.

Desenvolvido por: <LISTAR  O NOME DOS INTEGRANTES>

