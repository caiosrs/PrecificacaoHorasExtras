#registros/views.py

import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from .forms import RegistroHorasExtrasForm
import os
import tempfile
import logging
from django.views.decorators.csrf import csrf_exempt
from openpyxl import load_workbook
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from datetime import datetime
from io import BytesIO

logger = logging.getLogger(__name__)

def autocomplete_funcionarios(request):
    if request.method == 'GET':
        term = request.GET.get('term', '')
        # Caminho absoluto para o arquivo Excel
        excel_path = os.path.join(os.path.dirname(__file__), r'D:\1Desktop\Documentos\My Web Sites\App py\ProjetoCastan\Funcionários.xlsx')
        
        # Carregar dados dos funcionários do arquivo Excel
        funcionarios_df = pd.read_excel(excel_path)
        # Filtrar nomes que comecem com o termo
        nomes = funcionarios_df[funcionarios_df['Nome do funcionário'].str.startswith(term, na=False)]['Nome do funcionário'].tolist()
        
        # Retornar sugestões como JSON
        return JsonResponse(nomes, safe=False)
    
def formatar_numero(numero):
    """
    Formata um número como string com máscara de milhar e decimal (1.000,00).
    """
    if isinstance(numero, (int, float)):
        return f"{numero:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return numero

def desenhar_tabela(pdf_canvas, dados):
    # Obtém a data e hora atual
    agora = datetime.now()
    data_hora = agora.strftime('%d/%m/%Y às %H:%M')

    # Define os estilos
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1,
        spaceAfter=12
    )

    # Cria o título e o subtítulo
    title = Paragraph('Cálculo do valor de Horas Extras', title_style)
    subtitle = Paragraph(f'Gerado em: {data_hora}', subtitle_style)

    # Dados da tabela
    data = [['Descrição', 'Valor']]
    data += [[chave, formatar_numero(valor)] if isinstance(valor, (int, float)) else [chave, valor] for chave, valor in dados.items()]

    table = Table(data, colWidths=[2.5 * inch, 2.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (-1, -1), (-1, -1), colors.yellow)
    ]))

    elements = [title, subtitle, table]
    pdf_canvas.build(elements)

@csrf_exempt
def registro_horas_extras(request):
    if request.method == 'POST':
        form = RegistroHorasExtrasForm(request.POST)
        if form.is_valid():
            nome_funcionario = form.cleaned_data['nome_funcionario']

            # Caminho absoluto para o arquivo Excel
            excel_path = os.path.join(os.path.dirname(__file__), r'D:\1Desktop\Documentos\My Web Sites\App py\ProjetoCastan\Funcionários.xlsx')

            # Carregar dados dos funcionários do arquivo Excel
            funcionarios_df = pd.read_excel(excel_path)

            # Buscar informações da pessoa selecionada
            pessoa_selecionada = funcionarios_df[funcionarios_df['Nome do funcionário'] == nome_funcionario]

            if not pessoa_selecionada.empty:
                salario = pessoa_selecionada.iloc[0]['Salário']
                carga_horaria = pessoa_selecionada.iloc[0]['Carga Horária']

                salario = float(salario)
                carga_horaria = float(carga_horaria)
                
                salario_por_hora = salario / carga_horaria
                dias_uteis = int(form.cleaned_data["dias_uteis"])
                dsr = int(form.cleaned_data["dsr"])

                he60_qtde = float(form.cleaned_data["he60_qtde"])
                he80_qtde = float(form.cleaned_data["he80_qtde"])
                he80_qtde_noturno = float(form.cleaned_data["he80_qtde_noturno"])
                he100_qtde = float(form.cleaned_data["he100_qtde"])

                he60_valor = 1.0
                he80_valor = salario_por_hora * 1.8 * he80_qtde
                he80_valor_noturno = (salario_por_hora * 1.8 * 1.3) * (he80_qtde_noturno * 1.1428571)
                he100_valor = salario_por_hora * 2 * he100_qtde

                refl_dsr = ((he60_valor + he80_valor + he80_valor_noturno + he100_valor) / dias_uteis) * dsr
                total_he = he60_valor + he80_valor + he80_valor_noturno + he100_valor + refl_dsr
                
                decimo_terceiro = (salario_por_hora * total_he) / 12
                ferias = (salario_por_hora * total_he) / 12
                um_terco_ferias = ferias / 3
                fgts = (total_he + decimo_terceiro + ferias + um_terco_ferias) * 0.08

                ferias_faturado = total_he / 12 * 1.333333
                decimo_terceiro_faturado = total_he / 12
                inss = (total_he + ferias_faturado + decimo_terceiro_faturado) * 0.28
                fgts_faturado = (total_he + ferias_faturado + decimo_terceiro_faturado) * 0.08
                total_faturado = total_he + ferias_faturado + decimo_terceiro_faturado + inss + fgts_faturado
                fgst_40 = fgts_faturado * 0.4
                total_absoluto = total_faturado + fgst_40
                valor_nota = total_absoluto / 0.8

                dados = {
                    'Nome do Funcionário': nome_funcionario,
                    'Salário': round(salario, 2),
                    'Carga Horária': round(carga_horaria, 2),
                    'Salário por Hora': round(salario_por_hora, 2),
                    'Décimo Terceiro': round(decimo_terceiro, 2),
                    'Férias': round(ferias, 2),
                    '1/3 de Férias': round(um_terco_ferias, 2),
                    'FGTS': round(fgts, 2),
                    'Reflexo DSR': round(refl_dsr, 2),
                    'Total de Horas Extras': round(total_he, 2),
                    'Férias Faturado': round(ferias_faturado, 2),
                    'Décimo Terceiro Faturado': round(decimo_terceiro_faturado, 2),
                    'INSS': round(inss, 2),
                    'FGTS Faturado': round(fgts_faturado, 2),
                    'Total Faturado': round(total_faturado, 2),
                    'FGTS 40%': round(fgst_40, 2),
                    'Total Absoluto': round(total_absoluto, 2),
                    'Valor da Nota': round(valor_nota, 2)
                }

                if 'download_pdf' in request.POST:
                    # Criar buffer de memória para o PDF
                    buffer = BytesIO()
                    pdf_canvas = SimpleDocTemplate(buffer, pagesize=letter)

                    desenhar_tabela(pdf_canvas, dados)
                    
                    # Preparar a resposta
                    buffer.seek(0)
                    response = HttpResponse(buffer, content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="horas_extras.pdf"'
                    return response

                if 'download_excel' in request.POST:
                    df_resultados = pd.DataFrame(list(dados.items()), columns=['Atributo', 'Valor'])
                    
                    # Aplicar a formatação diretamente no DataFrame
                    df_resultados['Valor'] = df_resultados['Valor'].apply(formatar_numero)
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
                        df_resultados.to_excel(temp_file.name, index=False)
                        temp_file_path = temp_file.name

                    with open(temp_file_path, 'rb') as excel_file:
                        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                        response['Content-Disposition'] = 'attachment; filename="resultados_calculos.xlsx"'

                    os.remove(temp_file_path)
                    return response

                # Caso contrário, retorne os dados como JSON
                return JsonResponse(dados)
            else:
                return JsonResponse({'error': 'Funcionário não encontrado.'}, status=404)
        else:
            return JsonResponse({'error': 'Formulário inválido.'}, status=400)
    else:
        excel_path = os.path.join(os.path.dirname(__file__), r'D:\1Desktop\Documentos\My Web Sites\App py\ProjetoCastan\Funcionários.xlsx')
        funcionarios_df = pd.read_excel(excel_path)
        nomes_funcionarios = funcionarios_df['Nome do funcionário'].tolist()
        
        choices = [(nome, nome) for nome in nomes_funcionarios]
        
        form = RegistroHorasExtrasForm()
        form.fields['nome_funcionario'].choices = choices
    
    return render(request, 'registro_horas_extras.html', {'form': form, 'names': nomes_funcionarios})

def sucesso(request):
    return render(request, 'sucesso.html')