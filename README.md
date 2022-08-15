<h1 align="center">MONITORAMENTO NIMBLE</h1>
<p>
<img src="http://img.shields.io/static/v1?label=STATUS&message=EM%20DESENVOLVIMENTO&color=GREEN&style=for-the-badge"/>
</p>   

![Monitoramento Nimble](doc/imagens/Monitoramento_Nimble.png)
Devido a necessidade de monitorar os Storages NIMBLE HPE pelo ZABBIX, foi desenvolvido esse projeto para consultar todos os dados das controladoras e dos HD's.

Esse projeto é composto por dois códigos para fazer as consultas do NIMBLE [consulta_controllers.py](cod/Nimble/consulta_controllers.py) e [consulta_disks.py](cod/Nimble/consulta_disks.py) e um código para automatizar a criação dos templates utilizados para monitorar esses dados no zabbix [cria_templates_Nimble.py](cod/Zabbix/cria_templates_Nimble.py). 

## Índice
* [Funcionameto](#funcionameto)

## Funcionamento


## Mode de Usar 

1° - Copie os códigos [consulta_controllers.py](cod/Nimble/consulta_controllers.py) e [consulta_disks.py](cod/Nimble/consulta_disks.py) para a pasta /home do zabbix agente. 
