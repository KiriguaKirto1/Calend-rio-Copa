# Calendário da Copa 2026

## Nome do projeto

**Calendário da Copa 2026**

## Objetivo

O objetivo do projeto é desenvolver um sistema para acompanhamento dos jogos da Copa do Mundo 2026, permitindo que o usuário consulte partidas, datas, horários, grupos, fases, estádios e informações gerais dos confrontos.

O sistema também permite favoritar jogos, visualizar partidas em formato de calendário, exportar dados e gerar um arquivo de calendário no formato `.ics`, facilitando a importação dos jogos em aplicativos de calendário.

## Proposta do projeto

O projeto foi criado como um sistema de organização e consulta para a Copa do Mundo 2026. A ideia principal é oferecer uma interface simples e funcional para que o usuário consiga acompanhar os jogos de forma mais prática, sem precisar consultar manualmente uma tabela externa a todo momento.

A aplicação trabalha com uma base local de dados em JSON, exibindo as partidas no sistema por meio de telas como dashboard, lista de jogos, calendário, detalhes das partidas, favoritos e configurações.

## Atualização após feedbacks

Durante o desenvolvimento, foi recebida a sugestão de implementar uma forma de integração com calendário.

A melhoria considerada no projeto foi a exportação dos jogos no formato `.ics`. Esse formato permite que o usuário baixe um arquivo de calendário e importe as partidas em aplicativos compatíveis, como Outlook, Google Calendar, Calendário do Windows ou calendário do celular.

Essa funcionalidade não significa atualização em tempo real pela internet. O sistema continua usando dados locais. A exportação `.ics` serve para facilitar o acompanhamento dos jogos em outros aplicativos.

## Funcionamento do sistema

O sistema utiliza dados armazenados localmente em arquivos JSON. A partir desses dados, a aplicação organiza e exibe as partidas da Copa 2026 em diferentes telas.

O usuário pode:

* visualizar um painel inicial com resumo dos jogos;
* consultar a lista completa de partidas;
* pesquisar jogos por seleção, cidade, estádio ou fase;
* filtrar partidas por grupo, fase ou status;
* abrir detalhes de cada confronto;
* marcar partidas como favoritas;
* visualizar jogos em um calendário mensal;
* exportar jogos em formato `.ics`;
* exportar dados em `.csv`;
* alterar preferências de visualização nas configurações.

## Tecnologias utilizadas

* Python 3.11+
* PySide6
* JSON
* HTML5
* CSS3
* JavaScript
* localStorage
* Exportação ICS
* Exportação CSV

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
└── src/
    ├── data_store.py
    ├── default_data.py
    ├── exporters.py
    ├── icons.py
    ├── main_window.py
    ├── models.py
    ├── pages.py
    ├── paths.py
    ├── theme.py
    ├── validators.py
    └── widgets.py
```

## Arquivo principal do sistema

O arquivo principal da versão Python é:

```txt
main.py
```

Ele é responsável por iniciar a aplicação e carregar a interface principal do sistema.

## Como executar a versão Python

### Opção 1 — Abrir pelo arquivo BAT

No Windows, dê dois cliques em:

```txt
abrir_app.bat
```

Esse arquivo cria o ambiente virtual, instala as dependências e abre o sistema.

### Opção 2 — Executar pelo terminal

Instale as dependências:

```bash
pip install -r requirements.txt
```

Depois execute:

```bash
python main.py
```

## Como abrir a versão HTML

A versão HTML foi criada como uma alternativa para visualização rápida do projeto diretamente no navegador.

Para abrir, dê dois cliques em:

```txt
index.html
```

## Principais telas do sistema

O sistema possui as seguintes telas principais:

### Início

Tela inicial com resumo geral do calendário, próximos jogos e informações rápidas sobre o sistema.

### Jogos

Tela com a lista de partidas, busca, filtros e acesso aos detalhes de cada jogo.

### Calendário

Tela em formato de calendário mensal, permitindo visualizar os dias com partidas e selecionar jogos por data.

### Detalhes

Tela com informações específicas de uma partida, como seleções, horário, estádio, cidade, fase e opções de favorito ou exportação.

### Favoritos

Tela que reúne os jogos marcados pelo usuário como favoritos.

### Configurações

Tela para ajustar preferências de visualização, tema, formato de data, fuso horário e opções relacionadas à exportação.

## Exportação para calendário

Uma das melhorias do projeto é a exportação dos jogos para o formato `.ics`.

Esse tipo de arquivo pode ser utilizado em aplicativos de calendário. Ao gerar o arquivo, o usuário pode importá-lo em serviços ou programas compatíveis.

Exemplos de aplicativos compatíveis:

* Google Calendar;
* Outlook;
* Calendário do Windows;
* calendário do celular.

Importante: dependendo do sistema operacional e do aplicativo de calendário instalado, a importação pode exigir confirmação manual do usuário.

## Exportação CSV

O sistema também permite exportar dados em formato `.csv`, facilitando a abertura das informações em programas de planilha, como Excel, Google Sheets ou LibreOffice Calc.

## Sobre os dados

O projeto utiliza uma base local de jogos armazenada em JSON.

Isso significa que:

* os dados são carregados a partir dos arquivos do próprio projeto;
* o sistema não consulta uma API externa automaticamente;
* o sistema não atualiza resultados em tempo real;
* caso os dados mudem, o arquivo JSON precisa ser atualizado.

## Conclusão

O projeto Calendário da Copa 2026 apresenta uma solução para consultar, organizar e acompanhar partidas da competição por meio de uma interface gráfica em Python e uma versão HTML de apoio.

A atualização após feedback trouxe a exportação em formato `.ics`, tornando o sistema mais útil para quem deseja acompanhar os jogos em aplicativos de calendário.
