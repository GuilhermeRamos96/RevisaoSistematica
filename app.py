# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
from typing import Dict, List, Optional
import pandas as pd

# Import custom modules
from reference_manager import ReferenceManager
from prisma_diagram import PRISMADiagram
from export_utils import ExportUtils
from ai_utils import AIUtils

# Configure page
st.set_page_config(
    page_title="PRISMA Writer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PRISMA 2020 Section Tips and Structure
SECTION_TIPS = {
    "Título": "Identifique o relatório como uma revisão sistemática, meta-análise ou ambos.",
    "Resumo": "Forneça um resumo estruturado incluindo, conforme aplicável: antecedentes, objetivos, fontes de dados, critérios de elegibilidade, participantes e intervenções, avaliação de risco de viés, métodos de síntese, resultados, limitações, conclusões e implicações das principais descobertas; registro da revisão sistemática.",
    "Introdução - Justificativa": "Descreva a justificativa para a revisão no contexto do que já é conhecido.",
    "Introdução - Objetivos": "Forneça uma declaração explícita das questões que estão sendo abordadas com referência a participantes, intervenções, comparações, resultados e desenho do estudo (PICOS).",
    "Métodos - Critérios de Elegibilidade": "Especifique as características do estudo (por exemplo, PICOS, duração do acompanhamento) e características do relatório (por exemplo, anos considerados, idioma, status da publicação) usadas como critérios de elegibilidade, fornecendo justificativa.",
    "Métodos - Fontes de Informação": "Descreva todas as fontes de informação (por exemplo, bancos de dados com datas de cobertura, contato com autores para identificar estudos adicionais) na busca e a data da última busca.",
    "Métodos - Estratégia de Busca": "Apresente a estratégia de busca completa para pelo menos um banco de dados, incluindo quaisquer limites usados, de forma que possa ser reproduzível.",
    "Métodos - Processo de Seleção": "Declare o processo de seleção de estudos (ou seja, triagem, elegibilidade, inclusão na revisão sistemática e, se aplicável, inclusão na meta-análise).",
    "Métodos - Coleta de Dados": "Descreva o método de extração de dados dos relatórios (por exemplo, formulários piloto, independentemente, em duplicata) e quaisquer processos para obter e confirmar dados dos investigadores.",
    "Métodos - Itens de Dados": "Liste e defina todas as variáveis para as quais os dados foram buscados (por exemplo, PICOS, fontes de financiamento) e quaisquer suposições e simplificações feitas.",
    "Métodos - Avaliação do Risco de Viés": "Descreva os métodos usados para avaliar o risco de viés de estudos individuais (incluindo especificação se isso foi feito no nível do estudo ou do resultado) e como essa informação deve ser usada na síntese dos dados.",
    "Métodos - Medidas de Efeito": "Declare as principais medidas de resultado (por exemplo, razão de risco, diferença média).",
    "Métodos - Métodos de Síntese": "Descreva os métodos de tratamento de dados e combinação dos resultados dos estudos, se houver, incluindo medidas de consistência (por exemplo, I²) para cada meta-análise.",
    "Métodos - Viés de Publicação": "Especifique quaisquer métodos usados para avaliar o risco de viés devido a resultados não relatados (viés de publicação).",
    "Métodos - Avaliação da Certeza": "Descreva quaisquer métodos usados para avaliar a certeza ou confiança nos resultados gerais (por exemplo, GRADE).",
    "Resultados": "Forneça o número de estudos selecionados, avaliados quanto à elegibilidade e incluídos na revisão, com motivos para exclusões em cada estágio, idealmente com um fluxograma.",
    "Discussão": "Forneça uma interpretação geral dos resultados no contexto de outras evidências e discuta as limitações da revisão.",
    "Registro e Protocolo": "Forneça informações de registro para a revisão (por exemplo, número de registro) e onde o protocolo da revisão pode ser acessado.",
    "Financiamento": "Descreva as fontes de financiamento para a revisão sistemática e outras formas de apoio (por exemplo, fornecimento de dados); papel dos financiadores na revisão sistemática.",
    "Conflitos de Interesse": "Declare quaisquer conflitos de interesse dos autores da revisão.",
    "Disponibilidade dos Dados": "Declare que todos os dados relevantes estão dentro do artigo e seus arquivos de Informações de Apoio, ou forneça detalhes sobre como acessar os dados."
}

SECTIONS = list(SECTION_TIPS.keys())

class PRISMAApp:
    """Main PRISMA 2020 Systematic Review Writing Tool"""
    
    def __init__(self):
        """Initialize the application with session state management"""
        self.init_session_state()
        
    def init_session_state(self):
        """Initialize session state variables"""
        if 'section_content' not in st.session_state:
            st.session_state.section_content = {section: "" for section in SECTIONS}
        
        if 'reference_manager' not in st.session_state:
            st.session_state.reference_manager = ReferenceManager()
            
        if 'prisma_diagram' not in st.session_state:
            st.session_state.prisma_diagram = PRISMADiagram()
            
        if 'export_utils' not in st.session_state:
            st.session_state.export_utils = ExportUtils()
            
        if 'ai_utils' not in st.session_state:
            st.session_state.ai_utils = AIUtils()
            
        if 'current_section' not in st.session_state:
            st.session_state.current_section = SECTIONS[0]
            
        if 'show_citation_modal' not in st.session_state:
            st.session_state.show_citation_modal = False
            
    def render_sidebar(self):
        """Render the navigation sidebar"""
        st.sidebar.title("📊 Ferramenta PRISMA 2020")
        
        # Botão biblioparser
        st.sidebar.link_button(
            "Ir para BiblioParser",
            "https://biblioparser.streamlit.app/",
            help="Abre a aplicação BiblioParser em uma nova aba"
         )

        st.sidebar.markdown("---")
        
        # AI Configuration Section
        st.sidebar.subheader("🤖 Configuração de IA")
        
        # Get current API key
        current_api_key = st.session_state.get('groq_api_key', '')
        
        api_key = st.sidebar.text_input(
            "Chave API Groq (opcional):",
            type="password",
            value=current_api_key,
            help="Para habilitar melhoramento de texto com IA. Obtenha em: https://console.groq.com/keys"
        )
        
        # Update API key if changed
        if api_key != current_api_key:
            st.session_state.groq_api_key = api_key
            # Update AI utils with new key
            st.session_state.ai_utils.update_api_key(api_key)
        
        # Show AI status
        if api_key:
            validation_result = st.session_state.ai_utils.validate_api_connection()
            if validation_result["available"]:
                st.sidebar.success("✅ IA conectada e disponível")
            else:
                error_msg = validation_result.get("error", "Erro desconhecido")
                st.sidebar.error(f"❌ Erro na IA: {error_msg}")
        else:
            st.sidebar.info("ℹ️ IA desabilitada - insira a chave API")
        
        st.sidebar.markdown("---")
        
        # Project Management Section
        st.sidebar.subheader("📁 Gerenciamento de Projeto")
        
        # Load JSON project
        uploaded_file = st.sidebar.file_uploader(
            "Carregar projeto salvo (.json):",
            type=['json'],
            help="Carregue um projeto PRISMA salvo anteriormente",
            key="json_uploader"
        )
        
        if uploaded_file is not None:
            file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            
            if st.session_state.get('last_uploaded_file_id') != file_id:
                try:
                    json_data = uploaded_file.read().decode('utf-8')
                    imported_data = st.session_state.export_utils.import_from_json(json_data)
                    
                    if imported_data:
                        # Load sections
                        st.session_state.section_content = imported_data.get('sections', {})
                        
                        # Load references
                        ref_data = imported_data.get('references', [])
                        citations_data = imported_data.get('citations', {})
                        
                        # Restore reference manager state
                        st.session_state.reference_manager.references = ref_data
                        st.session_state.reference_manager.citations = citations_data
                        
                        # Mark file as processed
                        st.session_state.last_uploaded_file_id = file_id
                        
                        st.sidebar.success("Projeto carregado com sucesso!")
                        st.rerun()
                    else:
                        st.sidebar.error("Erro ao carregar projeto")
                except Exception as e:
                    st.sidebar.error(f"Erro ao processar arquivo: {str(e)}")
        
        st.sidebar.markdown("---")
        
        # Navigation tabs
        tab_selection = st.sidebar.radio(
            "Navegar para:",
            ["Escrita", "Referências", "Diagrama de Fluxo", "Exportar"],
            key="main_navigation"
        )
        
        if tab_selection == "Escrita":
            st.sidebar.markdown("### Seções")
            selected_section = st.sidebar.selectbox(
                "Escolha a seção:",
                SECTIONS,
                index=SECTIONS.index(st.session_state.current_section),
                key="section_selector"
            )
            st.session_state.current_section = selected_section
            
        return tab_selection
        
    def render_writing_tab(self):
        """Render the main writing interface"""
        st.title("🔬 Editor de Revisão Sistemática PRISMA 2020")
        
        current_section = st.session_state.current_section
        
        # Section header
        st.header(f"📝 {current_section}")
        
        # Display section tip
        if current_section in SECTION_TIPS:
            st.info(f"**Dica:** {SECTION_TIPS[current_section]}")
        
        # Text editor with inline citation support
        col_main, col_side = st.columns([3, 1])
        
        with col_main:
            content = st.text_area(
                f"Escreva sua seção {current_section}:",
                value=st.session_state.section_content[current_section],
                height=400,
                key=f"editor_{current_section}",
                help="Digite seu texto. Use o painel lateral para inserir citações rapidamente."
            )
        
        with col_side:
            st.markdown("**Citações Rápidas**")
            refs = st.session_state.reference_manager.get_all_references()
            
            if refs:
                # Show reference count
                st.caption(f"{len(refs)} referência(s) disponível(is)")
                
                # Compact dropdown for reference selection
                ref_options = {}
                for ref in refs:
                    ref_preview = ref['formatted'][:30] + "..." if len(ref['formatted']) > 30 else ref['formatted']
                    ref_options[f"[{ref['id']}] {ref_preview}"] = ref['id']
                
                selected_ref = st.selectbox(
                    "Selecionar referência:",
                    options=["Escolha..."] + list(ref_options.keys()),
                    key=f"quick_ref_select_{current_section}"
                )
                
                # Insert button
                if selected_ref != "Escolha..." and st.button("➕ Inserir Citação", key=f"quick_insert_{current_section}"):
                    ref_id = ref_options[selected_ref]
                    citation_text = f"[{ref_id}]"
                    new_content = content + " " + citation_text if content else citation_text
                    st.session_state.section_content[current_section] = new_content
                    st.session_state.reference_manager.add_citation(current_section, ref_id)
                    st.success(f"Citação [{ref_id}] inserida!")
                    st.rerun()
                
                # Show recently used references for quick access
                if hasattr(st.session_state.reference_manager, 'citation_order') and st.session_state.reference_manager.citation_order:
                    st.markdown("**Últimas usadas:**")
                    recent_refs = st.session_state.reference_manager.citation_order[-3:]  # Last 3 used
                    for ref_id in recent_refs:
                        ref = st.session_state.reference_manager.get_reference_by_id(ref_id)
                        if ref:
                            ref_short = ref['formatted'][:25] + "..." if len(ref['formatted']) > 25 else ref['formatted']
                            if st.button(f"[{ref_id}] {ref_short}", key=f"recent_{ref_id}_{current_section}", help="Clique para inserir"):
                                citation_text = f"[{ref_id}]"
                                new_content = content + " " + citation_text if content else citation_text
                                st.session_state.section_content[current_section] = new_content
                                st.session_state.reference_manager.add_citation(current_section, ref_id)
                                st.success(f"Citação [{ref_id}] inserida!")
                                st.rerun()
            else:
                st.caption("Nenhuma referência\ndisponível")
        
        # Update content in session state
        st.session_state.section_content[current_section] = content
        
        # AI Enhancement and Citation buttons
        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            if st.button("🤖 Melhorar com IA", key=f"ai_improve_{current_section}"):
                if content and content.strip():
                    if st.session_state.ai_utils.is_available():
                        with st.spinner("Melhorando texto com IA..."):
                            improved_text = st.session_state.ai_utils.improve_text(
                                content, 
                                context=f"PRISMA 2020 {current_section} section"
                            )
                            if improved_text:
                                st.session_state.section_content[current_section] = improved_text
                                st.success("Texto melhorado! Atualizando...")
                                st.rerun()
                            else:
                                st.error("Falha ao melhorar o texto. Verifique sua configuração da API.")
                    else:
                        st.warning("Funcionalidade de IA não disponível. Configure sua chave API Groq.")
                else:
                    st.warning("Por favor, escreva algum conteúdo primeiro.")
        
        with col2:
            if st.button("📚 Inserir Citação", key=f"cite_{current_section}"):
                refs = st.session_state.reference_manager.get_all_references()
                if refs:
                    st.session_state.show_citation_modal = True
                else:
                    st.info("Nenhuma referência disponível. Adicione referências na aba Referências primeiro.")
        
        # Citation modal
        if st.session_state.show_citation_modal:
            self.render_citation_modal(current_section)
        
        # Progress indicator
        completed_sections = sum(1 for content in st.session_state.section_content.values() if content.strip())
        progress_percentage = completed_sections / len(SECTIONS)
        
        st.markdown("---")
        st.subheader("📊 Progresso da Revisão")
        st.progress(progress_percentage)
        st.write(f"Seções concluídas: {completed_sections}/{len(SECTIONS)} ({progress_percentage:.1%})")
        
    def render_citation_modal(self, section_name: str):
        """Render citation insertion modal"""
        st.markdown("### 📚 Inserir Citação")
        
        refs = st.session_state.reference_manager.get_all_references()
        
        # Create reference selection
        ref_options = {}
        for ref in refs:
            preview = ref['formatted'][:100] + "..." if len(ref['formatted']) > 100 else ref['formatted']
            ref_options[f"[{ref['id']}] {preview}"] = ref['id']
        
        if ref_options:
            selected_refs = st.multiselect(
                "Selecione as referências para citar:",
                options=list(ref_options.keys()),
                key="citation_multiselect"
            )
            
            # Insertion position options
            st.markdown("**Posição da citação:**")
            insertion_option = st.radio(
                "Onde inserir?",
                ["No final do texto", "Na posição do cursor", "Posição específica"],
                key="insertion_position"
            )
            
            cursor_position = None
            if insertion_option == "Posição específica":
                current_text = st.session_state.section_content[section_name]
                cursor_position = st.number_input(
                    "Posição do caractere (0 = início):",
                    min_value=0,
                    max_value=len(current_text),
                    value=len(current_text),
                    key="cursor_position"
                )
                
                # Show text preview with position indicator
                if current_text:
                    preview_text = current_text[:cursor_position] + "█" + current_text[cursor_position:]
                    st.text_area(
                        "Visualização (█ = posição da citação):",
                        value=preview_text[:200] + "..." if len(preview_text) > 200 else preview_text,
                        height=100,
                        disabled=True
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Inserir Citações") and selected_refs:
                    for selected in selected_refs:
                        ref_id = ref_options[selected]
                        st.session_state.reference_manager.add_citation(section_name, ref_id)
                    
                    # Generate citation text
                    citation_ids = [ref_options[selected] for selected in selected_refs]
                    citation_text = "[" + ",".join(map(str, sorted(citation_ids))) + "]"
                    
                    # Insert citation at appropriate position
                    current_content = st.session_state.section_content[section_name]
                    
                    if insertion_option == "No final do texto":
                        new_content = current_content + " " + citation_text
                    elif insertion_option == "Posição específica" and cursor_position is not None:
                        new_content = current_content[:cursor_position] + citation_text + current_content[cursor_position:]
                    else:  # Na posição do cursor - default to end for now
                        new_content = current_content + " " + citation_text
                    
                    st.session_state.section_content[section_name] = new_content
                    st.session_state.show_citation_modal = False
                    st.success(f"Citação {citation_text} inserida!")
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancelar"):
                    st.session_state.show_citation_modal = False
                    st.rerun()
        else:
            st.warning("Nenhuma referência disponível.")
            if st.button("❌ Fechar"):
                st.session_state.show_citation_modal = False
                st.rerun()
        
    def render_references_tab(self):
        """Render the reference management interface"""
        st.title("📚 Gerenciamento de Referências")
        
        # Add new reference section
        st.subheader("➕ Adicionar Nova Referência")
        
        # Method selection
        add_method = st.radio(
            "Método:",
            ["DOI", "Manual"],
            horizontal=True
        )
        
        if add_method == "DOI":
            doi_input = st.text_input(
                "Digite o DOI:",
                placeholder="10.1000/xyz123 ou https://doi.org/10.1000/xyz123",
                help="Cole o DOI completo ou URL do DOI"
            )
            
            if st.button("🔍 Buscar por DOI"):
                if doi_input.strip():
                    with st.spinner("Buscando metadados..."):
                        ref_id = st.session_state.reference_manager.add_reference_from_doi(doi_input.strip())
                        if ref_id:
                            st.success(f"Referência adicionada com ID: {ref_id}")
                            st.rerun()
                        else:
                            st.error("Falha ao buscar metadados. Verifique o DOI e tente novamente.")
                else:
                    st.warning("Por favor, digite um DOI.")
        
        else:  # Manual
            with st.form("manual_reference_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    authors = st.text_input(
                        "Autores:",
                        placeholder="Silva JA, Santos MB, Costa LC",
                        help="Separe os autores por vírgula"
                    )
                    title = st.text_input(
                        "Título:",
                        placeholder="Título do artigo"
                    )
                    journal = st.text_input(
                        "Revista:",
                        placeholder="Nome da revista"
                    )
                    year = st.text_input(
                        "Ano:",
                        placeholder="2023"
                    )
                
                with col2:
                    volume = st.text_input(
                        "Volume (opcional):",
                        placeholder="42"
                    )
                    issue = st.text_input(
                        "Número (opcional):",
                        placeholder="3"
                    )
                    pages = st.text_input(
                        "Páginas (opcional):",
                        placeholder="123-145"
                    )
                    doi = st.text_input(
                        "DOI (opcional):",
                        placeholder="10.1000/xyz123"
                    )
                
                submitted = st.form_submit_button("➕ Adicionar Referência")
                
                if submitted:
                    if authors and title and journal and year:
                        ref_id = st.session_state.reference_manager.add_manual_reference(
                            authors, title, journal, year, volume, issue, pages, doi
                        )
                        if ref_id:
                            st.success(f"Referência manual adicionada com ID: {ref_id}")
                            st.rerun()
                        else:
                            st.error("Erro ao adicionar referência manual.")
                    else:
                        st.error("Por favor, preencha todos os campos obrigatórios (autores, título, revista, ano).")
        
        st.markdown("---")
        
        # Display references
        st.subheader("📖 Referências Cadastradas")
        
        refs = st.session_state.reference_manager.get_all_references()
        
        if refs:
            # Reorder button
            if st.button("🔄 Reordenar por Citações"):
                # Get current sections content for reordering analysis
                sections_content = st.session_state.section_content
                
                # Reorder references based on actual text appearance
                id_mapping = st.session_state.reference_manager.reorder_references_by_citation(sections_content)
                
                if id_mapping:
                    # Update citation numbers in all text content
                    updated_content = st.session_state.reference_manager.update_citations_in_text(
                        sections_content, id_mapping
                    )
                    
                    # Update session state with corrected text
                    st.session_state.section_content.update(updated_content)
                    
                    st.success("Referências reordenadas e citações atualizadas no texto!")
                else:
                    st.warning("Nenhuma citação encontrada no texto para reordenar.")
                st.rerun()
            
            for ref in refs:
                with st.expander(f"[{ref['id']}] {ref['formatted'][:100]}..."):
                    st.write(f"**ID:** {ref['id']}")
                    st.write(f"**Tipo:** {ref.get('type', 'manual')}")
                    st.write(f"**Formatação completa:**")
                    st.write(ref['formatted'])
                    
                    if ref.get('doi'):
                        st.write(f"**DOI:** {ref['doi']}")
                    
                    if st.button(f"🗑️ Remover", key=f"remove_ref_{ref['id']}"):
                        if st.session_state.reference_manager.remove_reference(ref['id']):
                            st.success("Referência removida!")
                            st.rerun()
                        else:
                            st.error("Erro ao remover referência.")
        else:
            st.info("Nenhuma referência cadastrada. Adicione referências usando os métodos acima.")
        
    def render_diagram_tab(self):
        """Render the PRISMA flow diagram interface"""
        st.title("📊 Diagrama de Fluxo PRISMA 2020")
        
        st.markdown("""
        Configure os dados para gerar o diagrama de fluxo conforme as diretrizes PRISMA 2020.
        """)
        
        # Initialize diagram data in session state
        if 'diagram_data' not in st.session_state:
            st.session_state.diagram_data = {
                'databases': 0,
                'registers': 0,
                'duplicates_removed': 0,
                'automation_excluded': 0,
                'other_removed': 0,
                'records_screened': 0,
                'records_excluded': 0,
                'reports_sought': 0,
                'reports_not_retrieved': 0,
                'reports_assessed': 0,
                'exclusion_reasons': [],
                'studies_included': 0,
                'reports_included': 0
            }
        
        # Form for diagram data
        with st.form("diagram_data_form"):
            st.subheader("📋 Dados de Identificação")
            col1, col2 = st.columns(2)
            
            with col1:
                databases = st.number_input(
                    "Artigos identificados em bases de dados:",
                    min_value=0,
                    value=st.session_state.diagram_data['databases']
                )
                registers = st.number_input(
                    "Artigos identificados em registros:",
                    min_value=0,
                    value=st.session_state.diagram_data['registers']
                )
            
            with col2:
                duplicates_removed = st.number_input(
                    "Artigos duplicados removidos:",
                    min_value=0,
                    value=st.session_state.diagram_data['duplicates_removed']
                )
                automation_excluded = st.number_input(
                    "Artigos excluídos por ferramentas automatizadas:",
                    min_value=0,
                    value=st.session_state.diagram_data['automation_excluded']
                )
                other_removed = st.number_input(
                    "Artigos removidos por outras razões:",
                    min_value=0,
                    value=st.session_state.diagram_data['other_removed']
                )
            
            st.subheader("🔍 Dados de Triagem")
            col3, col4 = st.columns(2)
            
            with col3:
                records_screened = st.number_input(
                    "Artigos triados:",
                    min_value=0,
                    value=st.session_state.diagram_data['records_screened']
                )
                reports_sought = st.number_input(
                    "Artigos buscados para recuperação:",
                    min_value=0,
                    value=st.session_state.diagram_data['reports_sought']
                )
            
            with col4:
                records_excluded = st.number_input(
                    "Artigos excluídos:",
                    min_value=0,
                    value=st.session_state.diagram_data['records_excluded']
                )
                reports_not_retrieved = st.number_input(
                    "Artigos não recuperados:",
                    min_value=0,
                    value=st.session_state.diagram_data['reports_not_retrieved']
                )
            
            st.subheader("✅ Dados de Elegibilidade e Inclusão")
            col5, col6 = st.columns(2)
            
            with col5:
                reports_assessed = st.number_input(
                    "Artigos avaliados para elegibilidade:",
                    min_value=0,
                    value=st.session_state.diagram_data['reports_assessed']
                )
                studies_included = st.number_input(
                    "Estudos incluídos na revisão:",
                    min_value=0,
                    value=st.session_state.diagram_data['studies_included']
                )
            
            with col6:
                reports_included = st.number_input(
                    "Relatórios de estudos incluídos:",
                    min_value=0,
                    value=st.session_state.diagram_data['reports_included']
                )
            
            st.subheader("❌ Motivos de Exclusão")
            st.markdown("**Configure os motivos de exclusão na avaliação de elegibilidade:**")
            
            # Initialize exclusion reasons if not present
            if 'exclusion_reasons' not in st.session_state.diagram_data:
                st.session_state.diagram_data['exclusion_reasons'] = []
            
            # Display current exclusion reasons
            exclusion_reasons = st.session_state.diagram_data['exclusion_reasons'].copy()
            
            # Add new exclusion reason
            new_reason = st.text_input(
                "Novo motivo de exclusão:",
                placeholder="Ex: Não atendeu aos critérios PICOS"
            )
            new_count = st.number_input(
                "Número de estudos excluídos por este motivo:",
                min_value=0,
                key="new_exclusion_count"
            )
            
            if st.form_submit_button("💾 Salvar Dados do Diagrama"):
                # Update diagram data
                st.session_state.diagram_data.update({
                    'databases': databases,
                    'registers': registers,
                    'duplicates_removed': duplicates_removed,
                    'automation_excluded': automation_excluded,
                    'other_removed': other_removed,
                    'records_screened': records_screened,
                    'records_excluded': records_excluded,
                    'reports_sought': reports_sought,
                    'reports_not_retrieved': reports_not_retrieved,
                    'reports_assessed': reports_assessed,
                    'studies_included': studies_included,
                    'reports_included': reports_included
                })
                
                # Add new exclusion reason if provided
                if new_reason.strip() and new_count > 0:
                    exclusion_reasons.append({
                        'reason': new_reason.strip(),
                        'count': new_count
                    })
                
                st.session_state.diagram_data['exclusion_reasons'] = exclusion_reasons
                st.success("Dados salvos com sucesso!")
                st.rerun()
        
        # Display current exclusion reasons
        if st.session_state.diagram_data['exclusion_reasons']:
            st.subheader("📋 Motivos de Exclusão Configurados")
            for i, reason_data in enumerate(st.session_state.diagram_data['exclusion_reasons']):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {reason_data['reason']}: **{reason_data['count']} estudos**")
                with col2:
                    if st.button("🗑️", key=f"remove_reason_{i}"):
                        st.session_state.diagram_data['exclusion_reasons'].pop(i)
                        st.rerun()
        
        st.markdown("---")
        
        # Generate diagram
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Gerar Diagrama"):
                with st.spinner("Gerando diagrama PRISMA..."):
                    diagram_path = st.session_state.prisma_diagram.generate_diagram(
                        st.session_state.diagram_data
                    )
                    if diagram_path:
                        st.success("Diagrama gerado com sucesso!")
                        st.session_state.diagram_generated = True
                        st.session_state.diagram_path = diagram_path
                    else:
                        st.error("Erro ao gerar diagrama.")
        
        with col2:
            if st.button("🎨 Gerar Diagrama de Exemplo"):
                with st.spinner("Gerando diagrama de exemplo..."):
                    diagram_path = st.session_state.prisma_diagram.create_sample_diagram()
                    if diagram_path:
                        st.success("Diagrama de exemplo gerado!")
                        st.session_state.diagram_generated = True
                        st.session_state.diagram_path = diagram_path
                    else:
                        st.error("Erro ao gerar diagrama de exemplo.")
        
        # Display generated diagram
        if st.session_state.get('diagram_generated') and st.session_state.get('diagram_path'):
            if os.path.exists(st.session_state.diagram_path):
                st.subheader("📊 Diagrama PRISMA Gerado")
                st.image(st.session_state.diagram_path, caption="Diagrama de Fluxo PRISMA 2020")
                
                # Download button
                with open(st.session_state.diagram_path, "rb") as file:
                    st.download_button(
                        label="📥 Baixar Diagrama",
                        data=file.read(),
                        file_name="prisma_diagram.png",
                        mime="image/png"
                    )
        
    def render_export_tab(self):
        """Render the export interface"""
        st.title("📤 Exportar Revisão Sistemática")
        
        st.markdown("""
        Exporte sua revisão sistemática em diferentes formatos.
        """)
        
        # Prepare export data
        export_data = {
            'sections': st.session_state.section_content,
            'references': st.session_state.reference_manager.get_all_references(),
            'citations': st.session_state.reference_manager.citations
        }
        
        # Export options
        st.subheader("📋 Opções de Exportação")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Exportar DOCX"):
                with st.spinner("Gerando documento DOCX..."):
                    docx_path = st.session_state.export_utils.export_to_docx(export_data)
                    if docx_path and os.path.exists(docx_path):
                        with open(docx_path, "rb") as file:
                            st.download_button(
                                label="📥 Baixar DOCX",
                                data=file.read(),
                                file_name=docx_path,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        st.success("Documento DOCX gerado!")
                    else:
                        st.error("Erro ao gerar DOCX. Verifique se o python-docx está instalado.")
        
        with col2:
            if st.button("📕 Exportar PDF"):
                with st.spinner("Gerando documento PDF..."):
                    pdf_path = st.session_state.export_utils.export_to_pdf(export_data)
                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as file:
                            st.download_button(
                                label="📥 Baixar PDF",
                                data=file.read(),
                                file_name=pdf_path,
                                mime="application/pdf"
                            )
                        st.success("Documento PDF gerado!")
                    else:
                        st.error("Erro ao gerar PDF. Verifique se o reportlab está instalado.")
        
        with col3:
            if st.button("💾 Exportar JSON"):
                json_data = st.session_state.export_utils.export_to_json(export_data)
                if json_data:
                    st.download_button(
                        label="📥 Baixar JSON",
                        data=json_data,
                        file_name=f"prisma_project_{st.session_state.export_utils.timestamp}.json",
                        mime="application/json"
                    )
                    st.success("Projeto JSON gerado!")
                else:
                    st.error("Erro ao gerar JSON.")
        
        st.markdown("---")
        
        # Generate PRISMA checklist
        st.subheader("📋 Checklist PRISMA 2020")
        
        if st.button("📋 Gerar Checklist PRISMA"):
            with st.spinner("Gerando checklist..."):
                checklist_path = st.session_state.export_utils.generate_checklist_docx()
                if checklist_path and os.path.exists(checklist_path):
                    with open(checklist_path, "rb") as file:
                        st.download_button(
                            label="📥 Baixar Checklist",
                            data=file.read(),
                            file_name=checklist_path,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    st.success("Checklist PRISMA gerado!")
                else:
                    st.error("Erro ao gerar checklist.")
        
        # Preview statistics
        st.subheader("📊 Estatísticas da Revisão")
        
        completed_sections = sum(1 for content in st.session_state.section_content.values() if content.strip())
        total_words = sum(len(content.split()) for content in st.session_state.section_content.values() if content.strip())
        total_references = len(st.session_state.reference_manager.get_all_references())
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Seções Concluídas", f"{completed_sections}/{len(SECTIONS)}")
        
        with col2:
            st.metric("Total de Palavras", total_words)
        
        with col3:
            st.metric("Referências", total_references)
        
    def run(self):
        """Run the main application"""
        try:
            # Render sidebar and get selected tab
            selected_tab = self.render_sidebar()
            
            # Render main content based on selected tab
            if selected_tab == "Escrita":
                self.render_writing_tab()
            elif selected_tab == "Referências":
                self.render_references_tab()
            elif selected_tab == "Diagrama de Fluxo":
                self.render_diagram_tab()
            elif selected_tab == "Exportar":
                self.render_export_tab()
                
        except Exception as e:
            st.error(f"Erro na aplicação: {str(e)}")
            import traceback
            st.text(traceback.format_exc())

# Run the application
if __name__ == "__main__":
    app = PRISMAApp()
    app.run()
