"""Script para corrigir indentação do dashboard"""

with open('quintoandar_dashboard.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar a linha onde começa "with tab1:"
tab1_index = None
for i, line in enumerate(lines):
    if "with tab1:" in line:
        tab1_index = i
        break

if tab1_index is None:
    print("❌ Não encontrou 'with tab1:'")
    exit(1)

# A partir de tab1_index+1, verificamos se precisa indentar
# Já que esta dentro de with tab1:, tudo que vem depois precisa de 4 espaços adicionais

fixed_lines = lines[:tab1_index+1]  # Manter até "with tab1:"

for i in range(tab1_index+1, len(lines)):
    line = lines[i]
    
    # Skip linhas completamente vazias
    if line.strip() == "":
        fixed_lines.append(line)
        continue
    
    # Se a linha já começa com muitos espaços (já foi indentada), corrigir
    if line.startswith("        "):  # 8 espaços - muito
        # Remover 4 espaços
        fixed_lines.append(line[4:])
    elif line.startswith("    "):  # 4 espaços - certo
        fixed_lines.append(line)
    else:
        # Linha sem indentação - adicionar 4 espaços
        fixed_lines.append("    " + line)

# Salvar
with open('quintoandar_dashboard.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✅ Indentação corrigida!")
