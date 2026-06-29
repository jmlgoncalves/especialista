import fitz  # PyMuPDF
import os

def pdf_to_markdown(pdf_path, md_path):
    # Abre o documento PDF
    doc = fitz.open(pdf_path)
    md_content = ""

    for page_num in range(len(doc)):
        page = doc[page_num]
        # Extrai texto mantendo a estrutura básica
        text = page.get_text("blocks")

        # Adiciona um separador de página no markdown
        md_content += f"## Página {page_num + 1}\n\n"

        for _, _, _, _, content, _, _ in text:
            if content.strip():
                md_content += content + "\n\n"

    # Salva o conteúdo no arquivo .md
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Sucesso! Arquivo convertido para: {md_path}")

# Camininhos baseados no seu prompt
pdf_file = r".\pdfs\Consolidação Decreto-Lei n.º 169_2012  - Diário da República n.º 148_2012, Série I de 2012-08-01.pdf"
md_file = r".\docs\Consolidação Decreto-Lei n.º 169_2012  - Diário da República n.º 148_2012, Série I de 2012-08-01.md"

if os.path.exists(pdf_file):
    pdf_to_markdown(pdf_file, md_file)
else:
    print("Arquivo não encontrado no caminho especificado.")