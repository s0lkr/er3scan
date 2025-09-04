#!/usr/bin/env python3
"""
crt_sh_recon.py - Ferramenta de reconhecimento passivo usando crt.sh
Consulta Certificate Transparency Logs para enumerar subdomínios
"""

import asyncio
import json
import argparse
from typing import List, Set, Dict, Any
from urllib.parse import quote
import httpx
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
import pandas as pd

class CRTShClient:
    """Cliente para consulta assíncrona do crt.sh"""
    
    def __init__(self):
        self.base_url = "https://crt.sh/"
        self.timeout = 30
        self.max_retries = 3
        
    async def query_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        Consulta subdomínios para um domínio específico
        """
        params = {
            'q': f'%.{domain}',
            'output': 'json'
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(self.base_url, params=params)
                    response.raise_for_status()
                    return response.json()
                except httpx.RequestError as e:
                    if attempt == self.max_retries - 1:
                        raise e
                    await asyncio.sleep(2 ** attempt)  # Backoff exponencial
    
    def extract_subdomains(self, data: List[Dict[str, Any]], root_domain: str) -> Set[str]:
        """
        Extrai e filtra subdomínios únicos dos resultados
        """
        subdomains = set()
        
        for entry in data:
            if 'name_value' in entry:
                names = entry['name_value'].split('\n')
                for name in names:
                    name = name.strip().lower()
                    if name.endswith(root_domain) and name != root_domain:
                        subdomains.add(name)
        
        return subdomains

async def process_domains(domains: List[str], output_file: str) -> None:
    """
    Processa múltiplos domínios e gera relatório
    """
    console = Console()
    client = CRTShClient()
    all_results = {}
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Consultando crt.sh...", total=len(domains))
        
        for domain in domains:
            try:
                progress.update(task, description=f"[cyan]Processando {domain}...")
                
                # Consulta o crt.sh
                data = await client.query_domain(domain)
                
                # Extrai subdomínios
                subdomains = client.extract_subdomains(data, domain)
                all_results[domain] = {
                    'subdomains': list(subdomains),
                    'count': len(subdomains)
                }
                
                # Extrai certificados
                certificates = [entry for entry in data if 'id' in entry]
                all_results[domain]['certificates'] = certificates
                all_results[domain]['cert_count'] = len(certificates)
                display_results({domain: all_results[domain]})
                
                
                progress.update(task, advance=1)
                console.print(f"[green]✓[/green] {domain}: {len(subdomains)} subdomínios encontrados")
                
            except Exception as e:
                console.print(f"[red]✗[/red] Erro em {domain}: {str(e)}")
                all_results[domain] = {'error': str(e), 'subdomains': []}
                progress.update(task, advance=1)
    
    # Gera relatórios
    generate_reports(all_results, output_file)
    console.print(f"[green]Relatório salvo em {output_file}.*[/green]")

def generate_reports(results: Dict[str, Any], base_filename: str) -> None:
    """
    Gera relatórios em múltiplos formatos
    """
    # JSON completo
    with open(f"{base_filename}.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # CSV para análise
    csv_data = []
    for domain, data in results.items():
        if 'subdomains' in data:
            for subdomain in data['subdomains']:
                csv_data.append({'domain': domain, 'subdomain': subdomain})
    
    if csv_data:
        df = pd.DataFrame(csv_data)
        df.to_csv(f"{base_filename}.csv", index=False)

def display_results(results: Dict[str, Any]) -> None:
    """
    Exibe resultados formatados no terminal
    """
    console = Console()
    table = Table(title="Resultados do Reconhecimento Passivo", show_header=True)
    
    table.add_column("Domínio", style="cyan")
    table.add_column("Subdomínios", style="green")
    table.add_column("Status", style="magenta")
    
    for domain, data in results.items():
        if 'error' in data:
            table.add_row(domain, "0", f"[red]Erro: {data['error']}[/red]")
        else:
            table.add_row(domain, str(data['count']), "[green]Sucesso[/green]")
    
    console.print(table)

async def main():
    """
    Função principal
    """
    parser = argparse.ArgumentParser(description="Reconhecimento passivo usando crt.sh")
    parser.add_argument("domains", nargs="+", help="Domínios para investigar")
    parser.add_argument("-o", "--output", default="crt_sh_results", 
                       help="Arquivo de saída (sem extensão)")
    
    args = parser.parse_args()
    
    console = Console()
    console.print("[bold blue]🔍 Iniciando reconhecimento passivo no crt.sh[/bold blue]")
    
    try:
        await process_domains(args.domains, args.output)
    except KeyboardInterrupt:
        console.print("[yellow]Interrompido pelo usuário[/yellow]")
    except Exception as e:
        console.print(f"[red]Erro crítico: {str(e)}[/red]")

if __name__ == "__main__":
    asyncio.run(main())