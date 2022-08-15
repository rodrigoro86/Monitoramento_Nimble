<h1 align="center">MONITORAMENTO NIMBLE</h1>
<p>
<img src="http://img.shields.io/static/v1?label=STATUS&message=EM%20DESENVOLVIMENTO&color=GREEN&style=for-the-badge"/>
</p>   

![Monitoramento Nimble](doc/imagens/Monitoramento_Nimble.png)
Devido a necessidade de monitorar os Storages NIMBLE HPE pelo ZABBIX, foi desenvolvido esse projetpo para consultar todos os dados das controladoras e dos HD's dos Storages.

Abaixo um exemplo do Zabbix Server monitorando o Sotarage Nimble.

![Exemplo Zabbix](doc/imagens/ZABBIX_Dados_Nimble.png)

## Índice
* [Funcionameto](#funcionameto)
* [Referências](#referências)

## Funcionamento
Esse projeto é composto por duas partes:
#### 1° Nimble
Para fazer a consulta dos status e informações de todos os periféricos do Nimble é utilizada a biblioteca [nimble-python-sdk](https://github.com/hpe-storage/nimble-python-sdk), com ela foi desenvolvido dois códigos, [consulta_controllers.py](cod/Nimble/consulta_controllers.py) faz a consulta dos status das controladoras e [consulta_disks.py](cod/Nimble/consulta_disks.py) que faz a consulta dos status dos discos SSD e HD. 

#### 2° Zabbix
Para o zabbix conseguir coletar esses dados, foi criado o código [cria_template_Nimble.py](cod/Zabbix/cria_templates_Nimble.py) para automatizar a criação dos templates utilizados para filtrar todos os dados coletados do Nimble.  

## Referências 

- [nimble-python-sdk](https://github.com/hpe-storage/nimble-python-sdk)
- [API Zabbix](https://www.zabbix.com/documentation/current/en/manual/api)