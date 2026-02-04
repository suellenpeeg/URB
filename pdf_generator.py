from fpdf import FPDF
import pandas as pd
from datetime import datetime

# ============================================================
# FUNÇÃO DE LIMPEZA DE TEXTO (CRUCIAL PARA ACENTOS)
# ============================================================
def clean_text(text):
    """Limpa o texto para evitar erros de codificação no PDF (Latin-1)."""
    if text is None: 
        return ""
    # Converte para string e substitui caracteres problemáticos
    text = str(text).replace("–", "-").replace("“", '"').replace("”", '"').replace("’", "'")
    try:
        return text.encode('latin-1', 'replace').decode('latin-1')
    except:
        return text

# ============================================================
# CLASSE E FUNÇÃO GERADORA
# ============================================================
def gerar_pdf_os(dados):
    """
    Gera o PDF da Ordem de Serviço baseado no dicionário de dados (linha do banco).
    Retorna os bytes do PDF.
    """
    try:
        class PDF(FPDF):
            def header(self):
                # Tenta inserir o logo, se não existir, segue sem ele
                try:
                    self.image('logo.png', x=90, y=8, w=30) 
                    self.ln(22)
                except:
                    self.ln(5)
                
                self.set_font('Arial', 'B', 14)
                self.cell(0, 6, clean_text("Autarquia de Urbanização e Meio Ambiente de Caruaru"), 0, 1, 'C')
                self.set_font('Arial', 'B', 12)
                self.cell(0, 6, clean_text("Central de Atendimento"), 0, 1, 'C')
                self.ln(5)
        
        # Instancia o PDF
        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=25) 
        pdf.add_page()
        pdf.set_line_width(0.3)

        # Função auxiliar interna para células cinzas
        def celula_cinza(texto):
            pdf.set_fill_color(220, 220, 220) # Cinza claro
            pdf.set_font("Arial", 'B', 9)
            pdf.cell(0, 6, clean_text(texto), 1, 1, 'L', fill=True)

        # --- 1. TÍTULO DA SEÇÃO ---
        celula_cinza("ORDEM DE SERVIÇO - SETOR DE FISCALIZAÇÃO")
        
        # Tratamento de Data e Hora (Vindo do Banco SQL ou Pandas)
        raw_date = dados.get('created_at', '')
        data_fmt, hora_fmt = "", ""
        
        if raw_date:
            try:
                # Se já for objeto datetime (comum em SQL)
                if isinstance(raw_date, (datetime, pd.Timestamp)):
                    dt_obj = raw_date
                else:
                    dt_obj = pd.to_datetime(str(raw_date))
                
                data_fmt = dt_obj.strftime('%d/%m/%Y')
                hora_fmt = dt_obj.strftime('%H:%M')
            except:
                data_fmt = str(raw_date)

        # Linha 1: Nº, DATA, HORA, ORIGEM
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(8, 8, "N", 1, 0, 'C') # Simbolo de numero
        pdf.set_font("Arial", '', 9)
        pdf.cell(25, 8, clean_text(dados.get('external_id', '')), 1, 0, 'C')
        
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(12, 8, "DATA:", 1, 0, 'C')
        pdf.set_font("Arial", '', 9)
        pdf.cell(22, 8, data_fmt, 1, 0, 'C')

        pdf.set_font("Arial", 'B', 8)
        pdf.cell(12, 8, "HORA:", 1, 0, 'C')
        pdf.set_font("Arial", '', 9)
        pdf.cell(15, 8, hora_fmt, 1, 0, 'C')

        # Tratamento de Origem e Encaminhamento (se existir no banco)
        origem = dados.get('origem', '')
        # Se você tiver coluna num_encaminhamento no banco, adicione aqui
        # num_encaminhamento = dados.get('num_encaminhamento', '') 
        origem_texto = origem

        pdf.set_font("Arial", 'B', 8)
        pdf.cell(18, 8, "ORIGEM:", 1, 0, 'L')
        pdf.set_font("Arial", '', 8)
        pdf.cell(0, 8, clean_text(origem_texto), 1, 1, 'L')

        # Linha 2: Bairro e Zona (TGS)
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(35, 8, "BAIRRO OU DISTRITO:", 1, 0, 'L')
        pdf.set_font("Arial", '', 9)
        pdf.cell(120, 8, clean_text(dados.get('bairro', '')), 1, 0, 'L')
        
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(10, 8, "TGS:", 1, 0, 'C')
        pdf.set_font("Arial", '', 9)
        pdf.cell(0, 8, clean_text(dados.get('zona', '')), 1, 1, 'C')

        # --- 2. DESCRIÇÃO ---
        celula_cinza("DESCRIÇÃO DA ORDEM DE SERVIÇO")
        pdf.set_font("Arial", '', 9)
        # Multi cell para quebra de linha automática na descrição
        pdf.multi_cell(0, 5, clean_text(dados.get('descricao', '')), 1, 'L')
        
        # --- 3. ENDEREÇO, GEOLOCALIZAÇÃO E PONTO DE REFERÊNCIA ---
        # Garante alinhamento após multi_cell
        # pdf.set_y(pdf.get_y()) 
        
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(30, 8, "LOGRADOURO:", "LTB", 0, 'L') # Bordas Esquerda, Topo, Baixo
        pdf.set_font("Arial", '', 9)
        pdf.cell(0, 8, clean_text(dados.get('rua', '')), "RB", 1, 'L') # Bordas Direita, Baixo
        
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(30, 8, clean_text("Nº:"), "LB", 0, 'L')
        pdf.set_font("Arial", '', 9)
        pdf.cell(0, 8, clean_text(dados.get('numero', '')), "RB", 1, 'L')

        # Geolocalização
        lat = str(dados.get('latitude', ''))
        lon = str(dados.get('longitude', ''))
        geo_texto = f"Lat: {lat} | Lon: {lon}" if (lat and lon and lat != '0.0') else "Não informada"

        pdf.set_font("Arial", 'B', 8)
        pdf.cell(35, 8, clean_text("GEOLOCALIZAÇÃO:"), 1, 0, 'L')
        pdf.set_font("Arial", '', 8)
        pdf.cell(0, 8, clean_text(geo_texto), 1, 1, 'L')

        # Ponto de Referência (se existir no banco)
        # pdf.set_font("Arial", 'B', 8)
        # pdf.cell(35, 8, clean_text("PONTO DE REFERÊNCIA: "), 1, 0, 'L')
        # pdf.set_font("Arial", '', 8)
        # pdf.cell(0, 8, clean_text(dados.get('ponto_referencia', '')), 1, 1, 'L')

        # --- 4. ASSINATURAS (Mantendo o layout exato) ---
        pdf.ln(5)
        y_sig = pdf.get_y()
        # Verifica se cabe na página, senão cria nova
        if y_sig > 230: 
            pdf.add_page()
            y_sig = pdf.get_y()

        # Retângulos de assinatura
        pdf.rect(10, y_sig, 130, 18) # Caixa esquerda
        pdf.rect(140, y_sig, 60, 18) # Caixa direita (Rubrica)
        
        pdf.set_fill_color(220, 220, 220) 
        pdf.set_xy(140, y_sig)
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(60, 6, "Rubrica", 1, 0, 'C', fill=True)

        pdf.set_xy(12, y_sig + 2)
        pdf.set_font("Arial", 'B', 7)
        pdf.cell(0, 4, "RECEBIDO POR:", 0, 1)
        
        pdf.set_x(12)
        pdf.set_font("Arial", '', 9)
        # Se tiver campo 'quem_recebeu' ou usuario logado
        pdf.cell(125, 8, clean_text(dados.get('quem_recebeu', '')), 0, 0, 'L')
                
        # --- 5. INFORMAÇÕES DA FISCALIZAÇÃO (CAMPO EM BRANCO) ---
        pdf.set_xy(10, y_sig + 22)
        celula_cinza("INFORMAÇÕES DA FISCALIZAÇÃO")
        
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(90, 10, clean_text("DATA DA VISTORIA:            "), 1, 0, 'L')
        pdf.cell(0, 10, "HORA:             ", 1, 1, 'L')

        # Cabeçalho do quadro
        pdf.set_font("Arial", '', 7)
        pdf.cell(0, 5, clean_text("OBSERVAÇÕES E DESCRIÇÃO DA OCORRÊNCIA"), "LR", 1, 'C')
        
        # Espaço em branco para escrita manual
        pdf.cell(0, 65, "", "LR", 1, 'L') # Altura do quadro branco

        # Linha da Rubrica no rodapé do quadro
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 5, clean_text("  RUBRICA:                       "), "LR", 1, 'L')
        
        # Fecha o quadro
        pdf.cell(0, 10, "", "LRB", 1, 'L') 

        # --- 6. OBSERVAÇÕES ADMINISTRATIVAS (DO SISTEMA) ---
        pdf.ln(5)
        obs_texto = dados.get('observacoes', '')
        if obs_texto:
            celula_cinza("OBSERVAÇÕES ADMINISTRATIVAS / DE CAMPO")
            pdf.set_font("Arial", '', 9)
            pdf.multi_cell(0, 6, clean_text(obs_texto), 1, 'L')

        # Retorna o binário
        return bytes(pdf.output(dest='S'))

    except Exception as e:
        return str(e).encode()
