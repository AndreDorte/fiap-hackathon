import csv
import google.generativeai as genai
import json
import os
import PIL.Image
import resend
import time
from datetime import datetime
from dotenv import load_dotenv
from fpdf import FPDF
from pathlib import Path


class PDFRelatorio(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Relatório de Segurança - Modelo STRIDE', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')


def gerar_pdf(dados_analise,caminho_relatorio_pdf):
    pdf = PDFRelatorio()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Lista de termos para colocar em negrito
    termos_negrito = [
        "S: **Spoofing**", "S: **Spoofing (Falsificação)**"
        "T: Tampering (Adulteração)",
        "R: Repudiation (Não Repúdio)",
        "I: Information Disclosure (Divulgação de Informações)",
        "D: Denial of Service (Negação de Serviço)",
        "E: Elevation of Privilege (Elevação de Privilégio)",
        "S: Ameaça:", "T: Ameaça:", "R: Ameaça:", 
        "I: Ameaça:", "D: Ameaça:", "E: Ameaça:",
        "Ameaça:", "Mitigação:","**Ameaça:**", "**Threat:**"
    ]

    for item in dados_analise:
        # Título do Componente
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, txt=f"Componente: {item['nome']}", ln=1)
        
        # Reset de cor para o corpo do texto
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=10)
        
        texto_corpo = item['analise']
        
        # Aplicando as tags <b> nos termos selecionados
        for termo in termos_negrito:
            if termo in texto_corpo:
                texto_corpo = texto_corpo.replace(termo, f"<b>{termo}</b>")
        
        # Limpeza para evitar erros de caractere no PDF
        texto_html = texto_corpo.replace('\n', '<br>').encode('latin-1', 'replace').decode('latin-1')
        
        # O método write_html interpreta as tags <b> e <br>
        pdf.write_html(texto_html)
        
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

    pdf.output(caminho_relatorio_pdf)


def analisar_arquitetura(nome_arquivo,caminho_arquitetura_analise):
    img = PIL.Image.open(caminho_arquitetura_analise)

    prompt = """
    Analise esta imagem de arquitetura de nuvem. 
    1. Identifique o provedor de nuvem (ex: AWS, Azure, Google Cloud).
    2. Liste todos os componentes e serviços presentes.
    3. Retorne o resultado estritamente no formato CSV com o cabeçalho chamado 'componente' em português.
    Não inclua introduções ou formatação markdown, apenas os dados CSV.
    """

    response = model.generate_content([prompt, img])

    # Exibir o resultado no console e salvar em um arquivo .csv
    print("Componentes identificados:")
    print(response.text)

    # Salvando em um arquivo dataset_xxx.csv
    with open(f'output//{nome_arquivo}', 'w', encoding='utf-8') as f:
        f.write(response.text.replace("```csv","").replace("```",""))

    print(f"\nDataset exportado com sucesso para {nome_arquivo}'.csv'")


def analisar_stride(componente):
    prompt = f"""
    Atue como um Especialista em Segurança de Nuvem AWS.
    Analise o componente AWS '{componente}' usando STRIDE. 
    
    REGRAS OBRIGATÓRIAS:
    1. Responda inteiramente em PORTUGUÊS (Brasil).
    2. Não use introduções ou saudações.
    3. Para cada letra do STRIDE (S, T, R, I, D, E), descreva a ameaça e a mitigação.
    4. Mantenha os termos técnicos da AWS (ex: S3, Lambda), mas a explicação deve ser em português.

    Use o formato:

    S: [Ameaça e Mitigação]
    T: [Ameaça e Mitigação]
    ...
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro ao analisar {componente}: {str(e)}"
    

def analisar_dataset(dataset,caminho_relatorio_pdf,nome_arquivo_cache):
    lista_para_analise = []

    with open(f'output//{dataset}', mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            componente = row['componente']
            if componente:
                lista_para_analise.append(componente)

        if not lista_para_analise:
            print("Nenhum componente encontrado no dataset.")
            return
        
    print(f"Enviando {len(lista_para_analise)} componentes para análise STRIDE...")
    resultado_texto = analisar_todos_componentes(lista_para_analise)
    
    processar_lote_para_pdf(resultado_texto,caminho_relatorio_pdf)

    # Gerando um arquivo de cache para facilitar a reanalise, evitando uma nova chamada 
    # a API gratuita do Gemini que tem limite de consumo.
    with open(f'output//{nome_arquivo_cache}.json', 'w', encoding='utf-8') as f:
        json.dump(resultado_texto, f, ensure_ascii=False, indent=4)

    print(f"\nPDF gerado com sucesso: {caminho_relatorio_pdf}.pdf")
    

def enviar_email_com_anexo(destinatario, caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: O arquivo {caminho_arquivo} não foi encontrado.")
        return

    with open(caminho_arquivo, "rb") as f:
        pdf_data = f.read()
        # O Resend espera o conteúdo como uma lista de inteiros (bytes)
        attachment_content = list(pdf_data)

    params = {
        "from": "onboarding@resend.dev", # Remetente padrão do plano gratuito
        "to": destinatario,
        "subject": "Relatório de Arquitetura - Extração IA",
        "html": """
            <h1>Relatório Gerado com Sucesso</h1>
            <p>Olá! O script de análise de imagem identificou os componentes da sua arquitetura.</p>
            <p>O relatório detalhado das vulnerabilidades segue em anexo em formato PDF.</p>
        """,
        "attachments": [
            {
                "filename": os.path.basename(caminho_arquivo),
                "content": attachment_content,
            }
        ]
    }

    try:
        email = resend.Emails.send(params)
        print(f"E-mail enviado com sucesso! ID da transação: {email['id']}")
    except Exception as e:
        print(f"Falha ao enviar e-mail: {str(e)}")


def analisar_todos_componentes(lista_componentes):
    """
    Envia todos os componentes de uma vez para economizar cota de API.
    """
    # Transforma a lista em uma string formatada
    componentes_str = "\n- ".join(lista_componentes)
    
    prompt = f"""
    Atue como um Especialista em Segurança Cloud.
    Abaixo está uma lista de serviços identificados nesta arquitetura:
    {componentes_str}

    Para CADA item, gere uma análise técnica STRIDE seguindo EXATAMENTE este modelo:
    
    Componente: [Nome do Serviço]
    S: Ameaça: ... | Mitigação: ...
    T: Ameaça: ... | Mitigação: ...
    R: Ameaça: ... | Mitigação: ...
    I: Ameaça: ... | Mitigação: ...
    D: Ameaça: ... | Mitigação: ...
    E: Ameaça: ... | Mitigação: ...
    ---
    
    REGRAS:
    1. Responda em Português (Brasil).
    2. Use o delimitador '---' entre cada componente.
    3. Não inclua introduções ou conclusões.
    """
    
    print(f"Enviando lote de {len(lista_componentes)} componentes para o Gemini...")
    response = model.generate_content(prompt)
    return response.text


def processar_lote_para_pdf(texto_api, nome_arquivo_original):
    # Separa o texto pelo delimitador que pedimos no prompt
    blocos_componentes = texto_api.split('---')
    
    dados_para_pdf = []
    for bloco in blocos_componentes:
        bloco = bloco.strip()
        if not bloco: continue
        
        # Tenta extrair o nome do componente da primeira linha
        linhas = bloco.split('\n')
        nome_comp = linhas[0].replace("Componente:", "").strip()
        corpo_analise = "\n".join(linhas[1:])
        
        dados_para_pdf.append({
            'nome': nome_comp,
            'analise': corpo_analise
        })
    
    gerar_pdf(dados_para_pdf, nome_arquivo_original)


# Carrega as variáveis do arquivo .env
load_dotenv()

# Carrega as variáveis de ambiente
gemini_api_key = os.getenv("GEMINI_API_KEY")
resend_api_key = os.getenv("RESEND_API_KEY")

# Configura as API KEYS carregadas
genai.configure(api_key=gemini_api_key)
resend.api_key = resend_api_key

# Inicializa o modelo 2.5 Flash
model = genai.GenerativeModel(
    model_name='models/gemini-2.5-flash',
    system_instruction="Você é um auditor de segurança brasileiro. Todos os seus relatórios e análises devem ser escritos exclusivamente em português do Brasil, de forma técnica e objetiva."
)

# Caminho da pasta de entrada, que contem os jpgs das arquiteturas a serem analisadas
pasta_entrada = "arquivos"

# Garante que a pasta existe
if not os.path.exists(pasta_entrada):
    os.makedirs(pasta_entrada)

arquivos_imagem = [f for f in os.listdir(pasta_entrada) if f.lower().endswith((".jpg", ".jpeg"))]

# Verifica se a lista está vazia
if not arquivos_imagem:
    print(f"\n[AVISO]: Nenhuma imagem encontrada na pasta '{pasta_entrada}'.")
    print("Por favor, adicione seus diagramas (.jpg, .jpeg) nesta pasta e tente novamente.")
    exit()

print(f"Iniciando análise dos arquivos na pasta '{pasta_entrada}'...")

for arquivo in os.listdir(pasta_entrada):
    if arquivo.lower().endswith((".jpg", ".jpeg")):
        nome_base_arquivo = Path(arquivo).stem
        caminho_completo_arquivo = os.path.join(pasta_entrada, arquivo)
        print(f"Analisando: {arquivo}...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_dataset = f"dataset_{nome_base_arquivo}_{timestamp}.csv"
        nome_arquivo_cache = f"cache_{nome_base_arquivo}_{timestamp}"
        
        # Analisa a arquitetura do arquivo via LLM. 
        # Gera um dataset com o nome de cada componente na pasta output.         
        analisar_arquitetura(nome_dataset, caminho_completo_arquivo)

        time.sleep(30) # Evitar Rate Limit, atraso de 48 segundos segundo retorno da API

        # Informa a pasta e o nome do relatório de vulnerabilidade que será gerado.
        caminho_relatorio_pdf = f"output//Relatorio_STRIDE_{nome_base_arquivo}_{timestamp}.pdf"

        # Analisa o dataset gerado no passo anterior via LLM, criando um relatório 
        # no modelo STRIDE, sinalizando as vulnerabilidades identificadas e as 
        # sugestões para mitigição das mesmas
        analisar_dataset(nome_dataset,caminho_relatorio_pdf,nome_arquivo_cache)