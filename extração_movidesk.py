# Importação das bibliotecas necessárias para automação, manipulação de arquivos e expressões regulares
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import re

# Inicializa o WebDriver do Chrome com as opções padrão
print("🚀 Iniciando o WebDriver...")
options = webdriver.ChromeOptions()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Acessa a página do formulário Movidesk
print("🌐 Acessando a página do Movidesk...")
driver.get("https://grupocasamagalhaes.movidesk.com/kb/form/7426/#")

# Aguarda até que o campo 'Serviço' esteja disponível para clique
print("⏳ Esperando o campo 'Serviço' aparecer...")
espera = WebDriverWait(driver, 15)
dropdown_div = espera.until(
    EC.element_to_be_clickable((By.XPATH, "//div[contains(@id,'jqxWidget') and contains(@class,'jqx-widget')]"))
)

# Clica no campo 'Serviço' para exibir a árvore de opções
print("🖱️ Clicando no campo 'Serviço'...")
dropdown_div.click()
time.sleep(3)

# Orienta o usuário a expandir manualmente todos os grupos da árvore
print("\n🧠 AGORA É COM VOCÊ:")
print("➡️ Expanda todos os grupos no navegador (níveis 1, 2, 3 e 4).")
input("⏸️ Pressione ENTER aqui quando tudo estiver expandido...")

# Coleta todos os itens visíveis da árvore de serviços
print("🔍 Coletando itens visíveis...")
itens = driver.find_elements(By.CLASS_NAME, "jqx-tree-item-li")

# Inicializa listas para armazenar o caminho e a numeração hierárquica
caminho = ["", "", "", ""]
numeracao = ["", "", "", ""]
dados = []

# Inicializa contadores para cada nível da hierarquia
nivel1 = nivel2 = nivel3 = nivel4 = 0

# Percorre cada item coletado da árvore
for item in itens:
    try:
        # Garante que o item está visível na tela
        driver.execute_script("arguments[0].scrollIntoView(true);", item)
        time.sleep(0.05)

        # Extrai o nível do item pela margem esquerda (margin-left)
        estilo = item.get_attribute("style")
        match = re.search(r"margin-left:\s*(\d+)px", estilo)
        if not match:
            continue

        margin = int(match.group(1))
        nivel = margin // 18  # Cada nível aumenta 18px

        # Extrai o texto do item
        div_texto = item.find_element(By.CLASS_NAME, "jqx-tree-item")
        texto = div_texto.get_attribute("innerText").strip()

        if not texto:
            continue

        # Atualiza o caminho hierárquico e reseta níveis inferiores
        caminho[nivel] = texto
        for i in range(nivel + 1, 4):
            caminho[i] = ""

        # Atualiza os contadores de cada nível
        if nivel == 0:
            nivel1 += 1
            nivel2 = nivel3 = nivel4 = 0
        elif nivel == 1:
            nivel2 += 1
            nivel3 = nivel4 = 0
        elif nivel == 2:
            nivel3 += 1
            nivel4 = 0
        elif nivel == 3:
            nivel4 += 1

        # Gera o código hierárquico do item
        if nivel == 0:
            cod = f"{nivel1}"
        elif nivel == 1:
            cod = f"{nivel1}.{nivel2}"
        elif nivel == 2:
            cod = f"{nivel1}.{nivel2}.{nivel3}"
        elif nivel == 3:
            cod = f"{nivel1}.{nivel2}.{nivel3}.{nivel4}"
        else:
            cod = ""

        # Exibe no console o caminho e código do item
        print(f"{cod} -", " > ".join([c for c in caminho if c]))
        # Adiciona o registro à lista de dados
        dados.append([cod] + caminho)

    except Exception as e:
        # Em caso de erro, exibe mensagem e continua
        print(f"⚠️ Erro ao processar item: {e}")

# Salva os dados coletados em um arquivo CSV
print("\n💾 Salvando em 'servicos_hierarquia.csv'...")
with open("servicos_hierarquia.csv", "w", newline="", encoding="utf-8") as arquivo:
    writer = csv.writer(arquivo)
    writer.writerow(["Código", "Nível 1", "Nível 2", "Nível 3", "Nível 4"])
    writer.writerows(dados)

# Exibe mensagem final com o total de registros extraídos e encerra o navegador
print(f"\n✅ Finalizado! Total extraído: {len(dados)} registros")
driver.quit()