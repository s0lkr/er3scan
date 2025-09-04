#!/usr/bin/env python3
"""
Ferramenta de reconhecimento de subdomínios assíncrona
- Enumerar subdomínios de forma assíncrona
- Realizar resolução DNS e captura básica de banners
- Filtrar apenas subdomínios existentes (HTTP 200/301/302)
- Salvar resultados em JSON
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import httpx
import aiodns
from rich.progress import Progress

# -----------------------------
# Configurações globais
# -----------------------------
HTTP = httpx.AsyncClient(http2=True, timeout=10)  # Cliente HTTP assíncrono
semaphore = asyncio.Semaphore(30)  # Limita conexões simultâneas

# -----------------------------
# Funções
# -----------------------------
async def resolve(host: str, resolver: aiodns.DNSResolver) -> list[str]:
    """Resolve um host para endereços IP (A records)"""
    try:
        ans = await resolver.query(host, "A")
        return [r.host for r in ans]
    except aiodns.error.DNSError:
        return []

async def grab_banner(ip: str, port: int) -> str:
    """Captura banner TCP de IP:porta"""
    try:
        async with semaphore:
            reader, writer = await asyncio.open_connection(ip, port)
            writer.write(b"\r\n")
            await writer.drain()
            data = await asyncio.wait_for(reader.read(128), 4)
            writer.close()
            await writer.wait_closed()
            return data.decode(errors="replace").strip()
    except Exception:
        return ""

async def probe_host(host: str, ports: list[int], resolver: aiodns.DNSResolver) -> dict:
    """Resolve host e captura banners das portas definidas"""
    ips = await resolve(host, resolver)
    tasks = [grab_banner(ip, p) for ip in ips for p in ports]
    banners = await asyncio.gather(*tasks)
    return {"host": host, "ips": ips, "banners": banners}

async def check_subdomain(sub: str) -> bool:
    """
    Verifica se o subdomínio existe via HTTP (status 200, 301 ou 302)
    """
    async with semaphore:
        for scheme in ("http", "https"):
            url = f"{scheme}://{sub}"
            try:
                resp = await HTTP.get(url, follow_redirects=True, timeout=5)
                if resp.status_code in (200, 301, 302):
                    return True
            except Exception:
                pass
    return False

# -----------------------------
# Função principal
# -----------------------------
async def main(wordlist: Path, root_domain: str) -> None:
    resolver = aiodns.DNSResolver()
    ports = [80, 443, 22, 21]

    # Lê wordlist ignorando linhas comentadas
    lines = [line.strip() for line in wordlist.read_text().splitlines() if line.strip() and not line.startswith("#")]
    subs = [f"{line}.{root_domain}" for line in lines]
    total_subs = len(subs)

    # -----------------------------
    # Validação assíncrona dos subdomínios
    # -----------------------------
    print(f"[+] Validando {total_subs} subdomínios para HTTP 200/301/302...")
    valid_flags = await asyncio.gather(*(check_subdomain(sub) for sub in subs))
    valid_subs = [sub for sub, valid in zip(subs, valid_flags) if valid]
    print(f"[+] {len(valid_subs)} subdomínios válidos encontrados")

    # -----------------------------
    # Processamento de hosts válidos
    # -----------------------------
    results = []
    with Progress() as bar:
        task_progress = bar.add_task("Recon", total=len(valid_subs))
        tasks = [probe_host(sub, ports, resolver) for sub in valid_subs]

        for coro in asyncio.as_completed(tasks):
            res = await coro
            results.append(res)
            bar.update(task_progress, advance=1)

    # -----------------------------
    # Salva resultados finais
    # -----------------------------
    def salvar_json_encrementar(base_name: str, data: list):
        """Cria arquivo com numero na frente se o arquivo já existir"""
        je = 0
        while True:
            if je == 0:
                filename = f"{base_name}.json"
            else:
                filename = f"{base_name}_{je}.json"
            path = Path(filename)
            if not path.exists():
                path.write_name(json.dumps(data, indent=2)) # type: ignore
                print(f"[+] Arquivo {filename} salvo com subdomínios válidos")
                break
            je += 1
            salvar_json_encrementar("valid_subdomains", results)

# -----------------------------
# CLI
# -----------------------------
if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Ferramenta assíncrona de reconhecimento de subdomínios")
    ap.add_argument("domain", help="Domínio raiz para escanear (ex: exemplo.com.br)")
    ap.add_argument("wordlist", type=Path, help="Caminho para o arquivo de wordlist")

    args = ap.parse_args()
    asyncio.run(main(args.wordlist, args.domain))
