#!/usr/bin/env python3
"""Trava da publicação: falha se o portal tiver endereço IP privado, tabela de logins de teste ou pasta que não pode sair.
Roda no workflow do Pages, antes de publicar. Não conhece os logins (eles ficam só na fonte privada); a conferência deles
é feita pelo gerador, que só entrega o portal se não houver nenhum.
Uso: python3 ferramentas/verificar_portal.py [pasta do portal]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import higiene  # noqa: E402

pasta = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
achados = higiene.verificar(pasta)
for arq, o_que, n in achados:
    print(f"BLOQUEADO: {arq}: {o_que} (x{n})")
if achados:
    raise SystemExit(f"Publicação bloqueada: {len(achados)} problema(s). Nenhum valor é impresso.")
print("Verificação ok: nenhum endereço IP privado, tabela de logins ou pasta proibida.")
