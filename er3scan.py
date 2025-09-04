#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menu de Reconhecimento de Subdom�nios
"""

import asyncio
from pathlib import Path
from rich.console import Console

# Importa as fun��es dos outros scripts
from kushkush_subs import main as wordlist_main
from crth_sh_recon import process_domains as crtsh_main
from OPSECMonitor import OPSECCheck, OPSECMonitor

console = Console()

async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Menu de Reconhecimento de Subdomínios")
    parser.add_argument("domain", help="Domínio raiz para reconhecimento")
    parser.add_argument("--method", choices=["crtsh", "wordlist"], required=True, 
                        help="Método de reconhecimento: crtsh ou wordlist")
    parser.add_argument("--wordlist", type=Path, 
                        help="Caminho para a wordlist (necessário se method for wordlist)")
    parser.add_argument("--output", default="results", 
                        help="Arquivo base para salvar resultados (sem extensão)")

    args = parser.parse_args()

    # Validação de argumentos
    if args.method == "wordlist":
        if not args.wordlist or not args.wordlist.exists():
            console.print("[red]Erro: Wordlist é obrigatória e deve existir quando o método é 'wordlist'[/red]")
            return
        await wordlist_main(args.wordlist, args.domain)  # chama a função principal do seu script de wordlist

    elif args.method == "crtsh":
        console.print(f"[blue]Iniciando reconhecimento passivo usando crt.sh para {args.domain}[/blue]")
        await crtsh_main([args.domain], args.output)  # chama process_domains do crt_sh_recon

if __name__ == "__main__":
    asyncio.run(main())
