# Calendário da Copa 2026

## Nome do projeto

**Calendário da Copa 2026**

## Objetivo

O objetivo do projeto é desenvolver um sistema para acompanhamento dos jogos da Copa do Mundo 2026, permitindo consultar partidas por data, fase, grupo e estádio.

O sistema também permite visualizar detalhes das partidas, favoritar jogos, acessar um calendário interativo e exportar os jogos para um arquivo de calendário no formato `.ics`.

## Contexto

Este projeto foi desenvolvido como atividade acadêmica, com foco em organização de dados, interface gráfica, manipulação de arquivos locais e melhoria do sistema a partir de feedbacks recebidos.

Após apresentação e análise do projeto, foi sugerida a implementação de uma funcionalidade de calendário automático. A melhoria foi aplicada por meio da exportação dos jogos em formato `.ics`, permitindo que o usuário importe os jogos em aplicativos de calendário, como Outlook, Google Calendar, Calendário do Windows ou calendário do celular.

## Funcionamento do sistema

O sistema utiliza uma base local em JSON com os jogos da Copa 2026. A partir desses dados, o usuário pode:

* visualizar o dashboard inicial;
* consultar todos os jogos;
* pesquisar partidas por seleção, cidade ou estádio;
* filtrar por fase, grupo e status;
* acessar detalhes de cada partida;
* favoritar jogos;
* visualizar jogos em um calendário mensal;
* exportar partidas para calendário `.ics`;
* exportar dados em `.csv`;
* alterar preferências de visualização.

## Funcionalidade implementada após feedback

Durante o desenvolvimento, foi recebida a sugestão de implementar uma integração com calendário.

A melhoria foi aplicada com a criação da exportação em formato `.ics`.

Com essa função, o usuário pode gerar um arquivo de calendário contendo os jogos e abrir/importar esse arquivo em aplicativos compatíveis.

Importante: o sistema não atualiza jogos em tempo real pela internet. Ele utiliza dados locais do arquivo JSON. Caso os dados sejam atualizados, o arquivo JSON deve ser substituído ou recarregado no sistema.

## Tecnologias utilizadas

* Python 3.11+
* PySide6
* QtAwesome
* JSON
* HTML5
* CSS3
* JavaScript
* localStorage
* Exportação ICS
* Exportação CSV

## Como executar a versão Python

### Opção 1 — Abrir pelo arquivo BAT

No Windows, dê dois cliques em:

```txt
abrir_app.bat
```

Esse arquivo cria o ambiente virtual, instala as dependências e abre o sistema.

### Opção 2 — Rodar pelo terminal

```bash
pip install -r requirements.txt
python main.py
```

## Como abrir a versão HTML

A versão HTML foi criada para permitir visualização rápida do projeto no navegador, sem instalar Python.

Dê dois cliques em:

```txt
abrir_html_v4.bat
```

Ou abra manualmente:

```txt
calendario_copa_2026_html_v4.html
```

## Estrutura do projeto

```txt
Calendario-da-Copa-2026/
│
├── main.py
├── abrir_app.bat
├── requirements.txt
├── README.md
│
├── calendario_copa_2026_html_v4.html
├── abrir_html_v4.bat
│
├── data/
│   ├── dados_copa.json
│   ├── favoritos.json
│   └── preferencias.json
│
├── cache/
│   └── flags/
│
├── scripts/
│   └── validate_data.py
│
├── src/
│   ├── data_store.py
│   ├── default_data.py
│   ├── exporters.py
│   ├── icons.py
│   ├── main_window.py
│   ├── models.py
│   ├── pages.py
│   ├── paths.py
│   ├── theme.py
│   ├── validators.py
│   └── widgets.py
│
└── evidencias/
    ├── dashboard.png
    ├── jogos.png
    ├── calendario.png
    ├── detalhes.png
    ├── favoritos.png
    └── configuracoes.png
```

## Evidências do sistema funcionando

As evidências devem ser registradas por meio de prints das telas principais:

* Dashboard;
* Jogos;
* Calendário;
* Detalhes do jogo;
* Favoritos;
* Configurações;
* Exportação de calendário `.ics`.

Os prints ficam na pasta:

```txt
evidencias/
```

## Testes recomendados

Antes da entrega, execute:

```bash
python -m compileall .
python scripts/validate_data.py
python main.py
```

Também teste manualmente:

1. Abrir o sistema.
2. Acessar a tela inicial.
3. Abrir a tela de jogos.
4. Pesquisar uma seleção.
5. Abrir detalhes de uma partida.
6. Favoritar um jogo.
7. Verificar a tela de favoritos.
8. Abrir o calendário.
9. Clicar em dias com jogos.
10. Exportar calendário `.ics`.
11. Exportar tabela `.csv`.
12. Abrir a versão HTML.

## Link do repositório

Cole aqui o link do GitHub:

```txt
https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO
```

## Consideração sobre feedbacks

O projeto foi atualizado após os feedbacks recebidos na apresentação. A principal melhoria considerada foi a implementação da exportação automática para calendário por meio de arquivo `.ics`, permitindo maior utilidade prática para o usuário acompanhar as partidas.

## Observação

O sistema trabalha com uma base local de dados. Ele não consulta a internet automaticamente e não atualiza resultados em tempo real.
