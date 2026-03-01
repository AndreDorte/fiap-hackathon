# 🛡️ AWS Architecture Sentinel: Auditoria STRIDE com IA

Este projeto foi desenvolvido para o **Hackathon FIAP - Fase 5**, com o objetivo de automatizar a análise de segurança de arquiteturas AWS. Utilizando a multimodalidade do **Google Gemini 2.5 Flash**, transformamos um diagrama de arquitetura (JPG) em um dataset de componentes e, sequencialmente, em um relatório detalhado de vulnerabilidades baseado no modelo **STRIDE**.



## 🚀 Fluxo de Funcionamento

1.  **Visão Computacional**: O Gemini analisa o diagrama `.jpg` da AWS.
2.  **Extração de Dados**: Identificação automática de cada serviço (S3, EC2, etc).
3.  **Análise de Segurança**: Processamento individual de cada componente usando o framework **STRIDE** (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege).
4.  **Relatório Profissional**: Exportação automática para um PDF formatado e objetivo, com notificação via e-mail.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
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

Siga os passos abaixo para configurar o ambiente e rodar a análise em sua máquina.

### 1. Clonar o Repositório
```bash
git clone [https://github.com/AndreDorte/fiap-hackathon.git](https://github.com/AndreDorte/fiap-hackathon.git)
cd fiap-hackathon
``` 
### 2. Configurar o Ambiente Virtual (venv)
No Windows (PowerShell):

```PowerShell
python -m venv venv
.\venv\Scripts\activate
``` 
No Linux ou macOS:

```Bash
python3 -m venv venv
source venv/bin/activate
``` 

### 3. Instalar as Dependências
Com o ambiente virtual ativo, execute:

```Bash
pip install -r requirements.txt
```

### 4. Configurar a API Key

1. Obtenha sua chave gratuita no [Google AI Studio](https://aistudio.google.com/api-keys).
2. Obtenha sua chave gratuita no [Resend](https://resend.com/api-keys)
3. Na raiz do projeto, crie um arquivo chamado .env.
4. Adicione suas chaves no arquivo seguindo exatamente este formato:

```Plaintext
GEMINI_API_KEY=sua_chave_aqui
RESEND_API_KEY=sua_chave_aqui
```

### 5. Executar a Análise

Certifique-se de que sua imagem de arquitetura está na pasta **arquivos** raiz com o nome **arquitetura_aws_01.jpg**. Em seguida, rode:

```Bash
python main.py
```
### 📂 Estrutura de Arquivos

```
├── arquivos/                    # Pasta com o jpg da arquitetura analisada
│   ├── arquitetura_aws_01.jpg     
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

