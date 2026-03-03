import google.generativeai as genai
import csv
import json
import time
import os
import PIL.Image
import resend
from dotenv import load_dotenv
from fpdf import FPDF


class PDFRelatorio(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Relatório de Segurança AWS - Modelo STRIDE', 0, 1, 'C')
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


def analisar_arquitetura():
    # 3. Carregar a imagem da arquitetura AWS
    img = PIL.Image.open('arquivos/arquitetura_aws_01.jpg')

    # 4. Criar o prompt específico para extração de componentes
    prompt = """
    Analise esta imagem de arquitetura AWS e identifique todos os componentes e serviços presentes.
    Gere uma lista estruturada contendo apenas o nome do componente/serviço.
    Retorne o resultado estritamente no formato CSV, com o cabeçalho 'componente'.
    """

    # 5. Gerar a resposta enviando a imagem e o texto
    response = model.generate_content([prompt, img])

    # 6. Exibir o resultado no console e salvar em um arquivo .csv
    print("Componentes identificados:")
    print(response.text)

    # Salvando em um arquivo dataset.csv
    with open('output/aws_components_dataset.csv', 'w', encoding='utf-8') as f:
        f.write(response.text.replace("```csv","").replace("```",""))

    print("\nDataset exportado com sucesso para 'aws_components_dataset.csv'")


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
    

def analisar_dataset(caminho_relatorio_pdf):
    resultados = []

    with open('output/aws_components_dataset.csv', mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            componente = row['componente']
            print(f"Analisando {componente}...")
            
            response = analisar_stride(componente)

            resultados.append({'nome': componente, 'analise': response})
            time.sleep(2) # Evitar Rate Limit

    with open('output/cache_gemini.json', 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)

    # Gerar o arquivo final
    gerar_pdf(resultados,caminho_relatorio_pdf)
    print("\nPDF gerado com sucesso: Relatorio_Seguranca_AWS.pdf")
    

def enviar_email_com_anexo(destinatario, caminho_arquivo):
    # Verificando se o arquivo existe localmente
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: O arquivo {caminho_arquivo} não foi encontrado.")
        return

    with open(caminho_arquivo, "rb") as f:
        pdf_data = f.read()
        # O Resend espera o conteúdo como uma lista de inteiros (bytes)
        attachment_content = list(pdf_data)

    # Configurando os parâmetros do e-mail
    params = {
        "from": "onboarding@resend.dev", # Remetente padrão do plano gratuito
        "to": destinatario,
        "subject": "Relatório de Arquitetura AWS - Extração IA",
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
        # Realizando o envio
        email = resend.Emails.send(params)
        print(f"E-mail enviado com sucesso! ID da transação: {email['id']}")
    except Exception as e:
        print(f"Falha ao enviar e-mail: {str(e)}")


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

analisar_arquitetura()

caminho_relatorio_pdf = f"output//Relatorio_Seguranca_AWS.pdf"

analisar_dataset(caminho_relatorio_pdf)