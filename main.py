import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import ImageFont
import numpy as np

# Configurações
FONT_PATH = "C:/Windows/Fonts/LCALLIG.TTF"  # Caminho da fonte Arial
FONT_SIZE_NAME = 105  
FONT_SIZE_OTHER = 50 
SPREADSHEET = "nomes.csv"  # Planilha com os nomes

def generate_badge(name, output_path, staff, numero_grupo):

    if staff == True:
        img = Image.open("cracha_staff.png")
    else:
        img = Image.open("cracha.png")

    draw = ImageDraw.Draw(img)
    
    # Carregar a fonte
    font_name = ImageFont.truetype(FONT_PATH, FONT_SIZE_NAME)
    font_other = ImageFont.truetype(FONT_PATH, FONT_SIZE_OTHER)
    
    # Definir posição do texto
    img_width, img_height = img.size

    # Remover espaço no final do nome, se houver
    name = name.rstrip()
    name_parts = name.split(" ")
    if len(name_parts) > 1:
        name2use = "{} {}".format(name_parts[0], name_parts[-1])
    else:
        name2use = name_parts[0]
    
    del name, name_parts
    
    text_bbox = draw.textbbox((0, 0), name2use, font=font_name)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (img_width / 2) - (text_width / 2)  # Centralizar
    text_y = img_height - text_height - int(img_height * 0.11)  # Ajuste vertical

    # Adicionar nome ao crachá
    draw.text((text_x, text_y), name2use, font=font_name, fill="black")


    if not np.isnan(numero_grupo):
        # Adicionar texto "Grupo: X: " no canto inferior esquerdo
        camp_text = "Grupo: {}".format(int(numero_grupo))
        camp_bbox = draw.textbbox((0, 0), camp_text, font=font_other)
        text_width = camp_bbox[2] - camp_bbox[0]
        text_height = camp_bbox[3] - camp_bbox[1]
        camp_x = int(img_width * 0.95) - text_width  # Margem direita
        camp_y = img_height - text_height - int(img_height * 0.05)  # Ajuste vertical

        draw.text((camp_x, camp_y), camp_text, font=font_other, fill="black")

    # Adicionar texto "Acampamento: " no canto inferior esquerdo
    camp_text = "Acampamento: "
    camp_bbox = draw.textbbox((0, 0), camp_text, font=font_other)
    text_width = camp_bbox[2] - camp_bbox[0]
    text_height = camp_bbox[3] - camp_bbox[1]
    camp_x = int(img_width * 0.04)  # Margem esquerda
    camp_y = img_height - text_height - int(img_height * 0.05)  # Ajuste vertical

    draw.text((camp_x, camp_y), camp_text, font=font_other, fill="black")
    
    # Salvar imagem
    img.save(output_path)

def create_pdf(df):

    ################################################################
    df = df[~df["Participante"].isna()].reset_index(drop=True)

    # Filtrar apenas os participantes que estão em grupo
    df_grupo = df[df["Grupo"] == True].reset_index(drop=True)

    # Embaralhar os índices dos participantes
    shuffled_indices = np.random.permutation(df_grupo.index)

    # Dividir os participantes em seis grupos de forma aleatória
    df_grupo["Grupo_Numero"] = (shuffled_indices % 6) + 1

    # Atualizar o dataframe original com os números dos grupos
    df = df.merge(df_grupo[["Participante", "Grupo_Numero"]], on="Participante", how="left")
    ################################################################

    names = df["Participante"].astype(str).tolist()
    staffs = df["Staff"].tolist()
    numero_grupos = df["Grupo_Numero"].tolist()

    crachas_por_pagina = []
    
    for idx in range(len(names)):

        if idx < len(names) - 1:
            continue

        name = names[idx]
        staff = staffs[idx]
        numero_grupo = numero_grupos[idx]

        output_img_path = f"outputs/cracha_{idx}.png"

        generate_badge(name, output_img_path, staff, numero_grupo)
        crachas_por_pagina.append(output_img_path)
        
        # A cada 4 crachás, adiciona uma página
        if len(crachas_por_pagina) == 4 or idx == len(names) - 1:

            if idx == len(names) - 1:
                # Adicionar crachás em branco para completar a página
                while len(crachas_por_pagina) < 4:
                    output_img_path = "cracha.png"
                    crachas_por_pagina.append(output_img_path)

            """Cria um PDF com quatro crachás por página."""
            pdf = canvas.Canvas("outputs/cracha_{}.pdf".format(idx), pagesize=A4)

            for i, img_path in enumerate(crachas_por_pagina):

                # Tamanho da página A4
                PAGE_WIDTH, PAGE_HEIGHT = A4

                # Posições para quatro crachás por página
                POSITIONS = [
                    (0, PAGE_HEIGHT // 2),
                    (0, 0),
                    (PAGE_WIDTH // 2, PAGE_HEIGHT // 2),
                    (PAGE_WIDTH // 2, 0),
                ]

                pdf.drawInlineImage(img_path, *POSITIONS[i], width=PAGE_WIDTH // 2, height=PAGE_HEIGHT // 2)
            
            pdf.showPage()    
            pdf.save()

            crachas_por_pagina = []

if __name__ == "__main__":

    # Ler planilha e gerar crachás
    df = pd.read_csv(SPREADSHEET)
    create_pdf(df)

    print("Crachás gerados com sucesso!")
