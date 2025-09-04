# EreScan 🕷️🔮

[![Python](https://img.shields.io/badge/python-3.10+-blueviolet?logo=python\&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-beta-red?style=for-the-badge)](#status)
[![License](https://img.shields.io/badge/license-Personal-darkred?style=for-the-badge)](#licença)
[![GitHub Repo](https://img.shields.io/badge/github-erescan-dark?style=for-the-badge\&logo=github)](https://github.com/seuusuario/erescan)

**EreScan** é uma **ferramenta de reconhecimento de subdomínios**, projetada para **Red Teamers**, pentesters e operações de segurança stealth. Combina técnicas **ativas** (wordlist assíncrona, DNS, banner grabbing) e **passivas** (crt.sh / Certificate Transparency logs).

---

## ⚡ Funcionalidades Nerd/Red Team

* 🔹 **Enumeração assíncrona de subdomínios** usando wordlists personalizadas
* 🔹 **Reconhecimento passivo** via `crt.sh`
* 🔹 **Validação de subdomínios ativos** (HTTP 200, 301, 302)
* 🔹 **Captura de banners TCP** em portas comuns: HTTP, HTTPS, SSH, FTP
* 🔹 **Controle adaptativo de RPS** para stealth operacional
* 🔹 **Exportação de resultados** em JSON/CSV com versionamento automático
* 🔹 **Barras de progresso interativas** no terminal
* 🔹 **Modular e extensível** para pipelines de Red Team

---

## 🛠 Requisitos

* Python 3.10+
* Bibliotecas Python:

```bash
pip install httpx[http2] aiodns rich pandas matplotlib
```

---

## 🚀 Instalação

```bash
git clone https://github.com/seuusuario/erescan.git
cd erescan
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🎛 Uso

### Menu Interativo

Escolha entre **passivo** (`crtsh`) ou **ativo** (`wordlist`):

```bash
python3 erescan.py --method crtsh fictitious-domain.local
python3 erescan.py --method wordlist fictitious-domain.local --wordlist wordlist.txt
```

Parâmetros:

* `--method` : `crtsh` ou `wordlist`
* `--wordlist` : Caminho para a wordlist (obrigatório se `method=wordlist`)
* `--output` : Arquivo base para resultados (default=`results`)

---

### Exemplo Ativo (Wordlist)

```bash
python3 erescan.py --method wordlist corp.fictional.local --wordlist example_wordlist.txt --output scan1
```

* Cria arquivos: `scan1.json` e `scan1.csv`
* Se já existir, adiciona sufixo numérico: `scan1_1.json`, `scan1_2.json`

---

## 📂 Estrutura do Projeto

```
erescan/
├── erescan.py          # Script principal com menu
├── wordlist_scan.py    # Funções de reconhecimento ativo
├── crt_sh_recon.py     # Funções passivas via crt.sh
├── OPSECMonitor.py     # Monitor de RPS (stealth)
├── requirements.txt
└── README.md
```

---

## 🖤 Demonstração

![EreScan Dark Demo](https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif)

---

## 📊 Exemplo de Saída JSON

```json
[
  {
    "host": "admin.fictional.local",
    "ips": ["10.0.0.1"],
    "banners": ["Apache/2.4.41 (Ubuntu)"]
  }
]
```

### CSV

| domain          | subdomain             |
| --------------- | --------------------- |
| fictional.local | admin.fictional.local |

---

## ⚔️ Status de Subdomínios

| Subdomínio            | IPs      | Banner                 | Status HTTP |
| --------------------- | -------- | ---------------------- | ----------- |
| admin.fictional.local | 10.0.0.1 | Apache/2.4.41 (Ubuntu) | 200         |
| dev.fictional.local   | 10.0.0.2 | -                      | 301         |

---

## ⚠️ Status

**Beta** — Use apenas em ambientes autorizados.
Controle RPS para manter **stealth** e não disparar alertas.

---

## 📝 Licença

Uso pessoal, acadêmico.
Para uso corporativo, obtenha permissão adequada.
