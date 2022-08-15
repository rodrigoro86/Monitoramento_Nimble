import json
from pydoc import visiblename
from pip._vendor import requests
from logging import debug, info, warning, error, critical, DEBUG, WARNING, INFO, ERROR, basicConfig
from argparse import ArgumentParser

basicConfig(level=INFO)

parser = ArgumentParser(description="Cria os templates NIMBLE no Zabbix Server",
                        usage="python cria_templates_Nimble.py --usuario <Nome_Usuário> --senha <Senha usada no Nimble> --url <URL_Zabbix>  --ip_Nimble <IP do Nimble> --usr_Nimble <Usuario Nimble> --pas_Nimble <Senha Nimble>")

parser.add_argument('--usuario', help='Nome do usuário cadastrado no Zabbix')
parser.add_argument('--senha', help='Senha do usário cadastrado no Zabbix')
parser.add_argument('--url', type=str, help="url do Zabbix")

parser.add_argument('--ip_Nimble', help='Ip do Nimble')
parser.add_argument('--usr_Nimble', help='Usuário cadastrado no Nimble')
parser.add_argument('--pas_Nimble', help='Senha cadastrada no Nimble')

class GERA_TOKEN():
    def __init__(self, user:str, password:str, endereco_url:str) -> None:
        """
        Gera o token da api do zabbix, esse token é utilizado pelas outras funções
        
        Entrada: user              Nome do Usuário
                 password          Senha do Usuário
                 endereco_url      Endereço do zabbix

        Atributos:  self.url       Endereço do zabbix
                    self.token     Token gerado pelo zabbix

        Retorno: Se ocorrer algum erro, o programa é finalizado
                 Se funcionar o token será gravado no atributo self.token

        Exemplo: api = API_ZABBIX('Admin','zabbix',"http://192.168.15.8/api_jsonrpc.php")
        
        """
        comando = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
            "user": user,
            "password": password
            },
            'auth':None,
            "id": 1
        }
        self.url = endereco_url
        #self.header = {'Content-Type': 'application/json'}
        self.header = {'content-type': 'application/json'}
        
        res = requests.post(self.url, data=json.dumps(comando), headers=self.header)
        resposta = json.dumps(res.json(), indent=4, sort_keys=True)
        resposta_zbx = json.loads(resposta)
  
        if "error" in resposta_zbx:
            result = resposta_zbx["error"]["data"]
            critical(f'Erro de conexão com o servidor zabbix: {result}')
            quit()
        else:
            info(f'Api conectada com o servidor Zabbix {self.url}')
            token = resposta_zbx["result"]
            self.token = token

    def _envia_comando_json(self, comando:dict) -> dict:
        """
        Função utilizada para transformar o comando em dict para json e enviar para o zabbix
        
        Entrada: comando            Comando que será enviado para o zabbix 

        Atributos: None

        Retorno: Resposta do zabbix no formato dict

        Exemplo: 
        
        """
        res = requests.post(self.url, data=json.dumps(comando), headers=self.header) #Envia o comando e aguarda a resposta
        resposta = json.dumps(res.json(), indent=4, sort_keys=True)                  #Transforma em str a reposta
        resultado = json.loads(resposta)                                             #Transforma em lista de dict 
        return resultado                                                             

class Consulta_Elementos(GERA_TOKEN):
    def __init__(self, user: str, password: str, endereco_url: str) -> None:
        super().__init__(user, password, endereco_url)
    
    def consulta_id_template(self, nome_template:str) -> str:
        """
        Consulta o id do template
        
        Entrada: nome_template  Nome do template do zabbix

        Retorno: id_template:     None -> Se o template não existir
                                  str -> id do template                                

        Exemplo: 
                    api = API_ZABBIX('Admin','zabbix',"http://192.168.15.5/api_jsonrpc.php")
                    id_template = api.consulta_id_template(nome_template='Template OS Linux'))        
        """
        cmd_template_get = {
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": "templateid",
                "filter": {
                    "host": [
                        nome_template,
                    ]
                }
            },
            "auth": self.token,
            "id": 1
        }
        resposta_zbx = self._envia_comando_json(cmd_template_get)
        if not resposta_zbx['result']:
            id_template = None
            info(f'Não foi possível consultar o id do Template {nome_template} -> {resposta_zbx}')
        else:
            debug(f'Consultado o id do template {nome_template}')
            id_template = resposta_zbx['result'][0]['templateid']
        
        return id_template

    def consulta_id_application(self, id_template, nome_aplicacao):
        cmd_application_get = {
            "jsonrpc": "2.0",
            "method": "application.get",
            "params": {
                "output": "applicationid",
                "templateids": id_template,
                "sortfield": "name",
                "filter": {
                    "name": nome_aplicacao
                }
            },
            "auth": self.token,
            "id": 1
        }
        resposta_zbx = self._envia_comando_json(cmd_application_get)
        print(resposta_zbx)
        if not resposta_zbx['result']:
            id_application = None
            info(f'Não foi possível consultar o id da aplicação {id_template} -> {resposta_zbx}')
        else:
            debug(f'Consultado o id do host {visiblename}')
            id_application = resposta_zbx['result'][0]['applicationid']
        
        return id_application

    def consulta_id_template_group(self, nome_template:str) -> str:
        """
        Consulta o id do Hosts groups
        
        Entrada: nome_Grupo            Nome do Grupo que será consultado o id 

        Retorno: id_group: str ->   Se não existir retorna None
                                    Se o grupo existe retorna o ID do Hosts groups encontrado

        Exemplo: 
                    api = API_ZABBIX('Admin','zabbix',"http://192.168.15.5/api_jsonrpc.php")
                    id_grupoServidores = api.consulta_id_Hosts_groups('Servidores'))        
        """
        cmd_hostgroup_get = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": "groupid",
                "filter": {
                    "name": [nome_template]
                }
            },
            "auth": self.token,
            "id": 1
        },
        resposta_zbx = self._envia_comando_json(cmd_hostgroup_get)
        resposta_zbx = resposta_zbx[0]
        if not resposta_zbx['result']:
            resultado = resposta_zbx
            info(f'Não foi possível consultar o id do grupo {nome_template} -> {resultado}')
            result = None
        else:
            debug(f'Consultado o id do grupo {nome_template}')
            result = resposta_zbx['result'][0]['groupid']
        return result
            
class ZABBIX(Consulta_Elementos):
    def __init__(self, user: str, password: str, endereco_url: str, ip_Nimble:str, usuario_Nimble:str, senha_Nimble:str) -> None:
        super().__init__(user, password, endereco_url)

        self.servidores_nimble = [1]  
        self.itens_temperature_sensors = ['inlet-temp', 'outlet-temp', 'LeftEar', 'bp-temp', 'RightEar']
        self.itens_power_suplay = ['power-supply1', 'power-supply2']
        self.itens_fans = {'fan1':'fan1a', 'fan2':'fan1b', 'fan3':'fan2a', 'fan4':'fan2b', 'fan5':'fan3a', 'fan6':'fan3b'}
        self.itens_controllers = ['A', 'B']
        self.ip_nimble = ip_Nimble
        self.usuario = usuario_Nimble
        self.senha = senha_Nimble

    def cria_itens_controllers(self):

        nome_template = 'NIMBLE_Controllers'
        id_template = self._cria_template(nome_template)
        id_template = self.consulta_id_template(nome_template)
        id_aplicacao_controllers = self.cria_applicacao('Controladora', id_template)   
        for n_nimble in self.servidores_nimble:
            nome_nimble = f'NIMBLE-N{n_nimble}'
            id_nimble = self.cria_applicacao(nome_nimble, id_template) 
            nome_arquivo = f'controllers_NIMBLE-N{n_nimble}.txt'

            id_aplicacao = self.cria_applicacao('Conteúdo Arquivos', id_template) 

            nome_item = f'{nome_nimble} - Consulta Dados Controllers'
            key = f'system.run["python3 /home/consulta_controllers.py --ip \'{self.ip_nimble}\' --usuario \'{self.usuario}\' --senha \'{self.senha}\' > /tmp/{nome_arquivo}",nowait]'
            self._cria_item(nome_item, id_template, key, 3, [id_aplicacao, id_nimble])

            nome_item = f'{nome_nimble} - Conteudo Dados Controllers'
            key = f'vfs.file.contents[/tmp/{nome_arquivo}]'
            self._cria_item(nome_item, id_template, key, 4, [id_aplicacao, id_nimble])

            id_aplicacao = self.cria_applicacao('FAN', id_template) 
            for k_fan, v_fan in self.itens_fans.items():       
                for controladora in self.itens_controllers:
                    print(nome_nimble, k_fan, v_fan, controladora)
                    # Cria item Status FAN
                    nome_item_fan = f'{nome_nimble} - Status {k_fan} - Controladora {controladora}'
                    key = f'vfs.file.regexp[/tmp/{nome_arquivo},"{k_fan};\s{v_fan};\scontroller\s{controladora};\s{controladora};\s([a-z].*);\s[0-9]*;",,,,"\\1"]'
                    self._cria_item(nome_item_fan, id_template, key, 4, [id_aplicacao_controllers, id_aplicacao, id_nimble])

                    nome_item_fan = f'{nome_nimble} - Velocidade {k_fan} - Controladora {controladora}'
                    key = f'vfs.file.regexp[/tmp/{nome_arquivo},"{k_fan};\s{v_fan};\scontroller\s{controladora};\s{controladora};.*;\s([0-9]*);",,,,\\1]'
                    self._cria_item(nome_item_fan, id_template, key, 3, [id_aplicacao_controllers, id_aplicacao, id_nimble])
     
            id_aplicacao = self.cria_applicacao('Temperatura', id_template)
            for sensor_temperatura in self.itens_temperature_sensors:
                for controladora in self.itens_controllers:
                    print(nome_nimble, k_fan, v_fan, controladora)
                    # Cria item Status FAN
                    nome_item = f'{nome_nimble} - Temperatura Sensor {sensor_temperatura} - Controladora {controladora}'
                    key = f'vfs.file.regexp[/tmp/{nome_arquivo},"{sensor_temperatura}.*([0-9]' + '{2}' + f');\s{controladora};\spd_temperature_sensors",,,,\\1]'
                    self._cria_item(nome_item, id_template, key, 3, [id_aplicacao_controllers, id_aplicacao, id_nimble], '°C')
                    
                    nome_item = f'{nome_nimble} - Status Sensor Temperatura {sensor_temperatura} - Controladora {controladora}'
                    key = f'vfs.file.regexp[/tmp/{nome_arquivo},"{sensor_temperatura}.*;\s([a-z].*);\s[0-9]' + '{2}' + f';\s{controladora};\spd_temperature_sensors",,,,"\\1"]'
                    self._cria_item(nome_item, id_template, key, 4, [id_aplicacao_controllers, id_aplicacao, id_nimble])
                     
            id_aplicacao = self.cria_applicacao('Fonte', id_template)
            for power_suplay in self.itens_power_suplay:       
                for controladora in self.itens_controllers:
                    print(nome_nimble, k_fan, v_fan, controladora)
                    # Cria item Status FAN
                    nome_item = f'{nome_nimble} - Status Fonte  {power_suplay} - Controladora {controladora}'
                    key = f'vfs.file.regexp[/tmp/{nome_arquivo},"{power_suplay}.*;\s([a-z].*);\s[0-9];.*",,,,"\\1"]'
                    self._cria_item(nome_item, id_template, key, 4, [id_aplicacao_controllers, id_aplicacao, id_nimble])

            id_aplicacao = self.cria_applicacao('Status_Geral', id_template)
            for controladora in self.itens_controllers:
                print(nome_nimble, controladora)
                nome_item = f'{nome_nimble} - Status Controladora - Controladora {controladora}'
                key = f'vfs.file.regexp[/tmp/{nome_arquivo},"{controladora};\s([a-z].*);\s{controladora};\scontrollers",,,,"\\1"]'
                self._cria_item(nome_item, id_template, key, 4, [id_aplicacao_controllers, id_aplicacao, id_nimble])

                #Status Temperatura
                nome_item = f'{nome_nimble} - Status Sensores de Temperatura - Controladora {controladora}'
                key = f'vfs.file.regexp[/tmp/{nome_arquivo},"([0-9]);\s{controladora};\s[a-z].*;\s{controladora};\scontrollers",,,,\\1]'
                self._cria_item(nome_item, id_template, key, 3, [id_aplicacao_controllers, id_aplicacao, id_nimble])                           
                
                descricao = f'Problema com a temperatura da Controladora {controladora}'
                comments = f'Verique os sensores de temperatura'
                exprecao = '{' + f'{nome_template}:{key}.last()' + '}<>1'
                prioridade = 3
                self._cria_trigger(descricao, exprecao, prioridade, comments)

                #Status FAN
                nome_item = f'{nome_nimble} - Status Fan - Controladora {controladora}'
                key = f'vfs.file.regexp[/tmp/{nome_arquivo},"([0-9]);\s[0-9];\s{controladora};\s[a-z].*;\s{controladora};\scontrollers",,,,\\1]'
                self._cria_item(nome_item, id_template, key, 3, [id_aplicacao_controllers, id_aplicacao, id_nimble])    

                descricao = f'Problema com a fan da Controladora {controladora}'
                exprecao = '{' + f'{nome_template}:{key}.last()' + '}<>1'
                comments = f'Verique os sensores de temperatura'
                prioridade = 3
                self._cria_trigger(descricao, exprecao, prioridade, comments)

                #Status Fonte
                nome_item = f'{nome_nimble} - Status da Fonte - Controladora {controladora}'
                key = f'vfs.file.regexp[/tmp/{nome_arquivo},"([0-9]);\s[0-9];\s[0-9];\s{controladora};\s[a-z].*;\s{controladora};\scontrollers",,,,\\1]'
                self._cria_item(nome_item, id_template, key, 3, [id_aplicacao_controllers, id_aplicacao, id_nimble])    

                descricao = f'Problema com a fonte da Controladora {controladora}'
                exprecao = '{' + f'{nome_template}:{key}.last()' + '}<>1'
                comments = f'Verique os sensores de temperatura'
                prioridade = 3
                self._cria_trigger(descricao, exprecao, prioridade, comments)

    def cria_itens_disk(self):
        
        nome_template = 'NIMBLE_Disks'
        id_template = self._cria_template(nome_template)
        id_template = self.consulta_id_template(nome_template)
        id_aplicacao_disk = self.cria_applicacao('disks', id_template)   
        for n_nimble in self.servidores_nimble:
            nome_nimble = f'NIMBLE-N{n_nimble}'
            id_nimble = self.cria_applicacao(nome_nimble, id_template) 
            nome_arquivo = f'disks_NIMBLE-N{n_nimble}.txt'


            id_aplicacao = self.cria_applicacao('Conteúdo Arquivos', id_template) 

            nome_item = f'{nome_nimble} - Consulta Dados Disks'
            key = f'system.run["python3 /home/consulta_disks.py --ip \'{self.ip_nimble}\' --usuario \'{self.usuario}\' --senha \'{self.senha}\' > /tmp/{nome_arquivo}",nowait]'
            self._cria_item(nome_item, id_template, key, 3, [id_aplicacao, id_nimble])

            # Cria item Conteudo arquivo
            nome_item = f'{nome_nimble} - Conteudo Dados Disks'
            key = f'vfs.file.contents[/tmp/{nome_arquivo}]'
            self._cria_item(nome_item, id_template, key, 4, [id_aplicacao, id_nimble])


            id_aplicacao = self.cria_applicacao('Dados Disks', id_template)
            for n_ssd in range(1, 4):
                for n_bank in range(0, 2):

                    id_aplicacao = self.cria_applicacao('Status Disks', id_template)
                    nome_item = f'{nome_nimble} - Status SSD Slot {n_ssd} Bank {n_bank}'
                    key = f'vfs.file.regexp[/tmp/{nome_arquivo},"ssd;\s{n_ssd};\s{n_bank};\s[0-9];\s(([a-z]*\s[a-z]*)|([a-z]*))",,,,"\\1"]'
                    self._cria_item(nome_item, id_template, key, 4, [id_aplicacao_disk, id_aplicacao, id_nimble])
                    
                    nome_item = f'{nome_nimble} - Valor Status SSD Slot {n_ssd} Bank {n_bank}'
                    key = f'vfs.file.regexp[/tmp/{nome_arquivo},"ssd;\s{n_ssd};\s{n_bank};\s([0-9]);",,,,\\1]'
                    self._cria_item(nome_item, id_template, key, 3, [id_aplicacao_disk, id_aplicacao, id_nimble])

                    descricao = f'{nome_nimble} - Problema com o SSD Slot {n_ssd} Bank {n_bank} '
                    exprecao = '{' + f'{nome_template}:{key}.last()' + '}<>1'
                    comments = f'Verique os sensores de temperatura'
                    prioridade = 3
                    self._cria_trigger(descricao, exprecao, prioridade, comments)

                    id_aplicacao = self.cria_applicacao('Volume Disks', id_template)
                    nome_item = f'{nome_nimble} - Total Volume {n_ssd} Bank {n_bank}'
                    key = f'vfs.file.regexp[/tmp/{nome_arquivo},"ssd;\s{n_ssd};\s{n_bank};\s[0-9];\s([a-z]*\s[a-z]*|[a-z]*);\s([0-9]*)",,,,\\2]'
                    self._cria_item(nome_item, id_template, key, 3, [id_aplicacao_disk, id_aplicacao, id_nimble], 'GB')
            
            for n_hdd in range(4, 25):
                
                id_aplicacao = self.cria_applicacao('Status Disks', id_template)
                nome_item = f'{nome_nimble} - Status HDD Slot {n_hdd}'
                key = f'vfs.file.regexp[/tmp/{nome_arquivo},"hdd;\s{n_hdd};\s0;\s[0-9];\s(([a-z]*\s[a-z]*)|([a-z]*))",,,,"\\1"]'
                self._cria_item(nome_item, id_template, key, 4, [id_aplicacao_disk, id_aplicacao, id_nimble])
                
                nome_item = f'{nome_nimble} - Valor Status HDD Slot {n_hdd}'
                key = f'vfs.file.regexp[/tmp/{nome_arquivo},"hdd;\s{n_hdd};\s0;\s([0-9]);",,,,\\1]'
                self._cria_item(nome_item, id_template, key, 3, [id_aplicacao_disk, id_aplicacao, id_nimble])

                descricao = f'{nome_nimble} - Problema com o HDD Slot {n_hdd}'
                exprecao = '{' + f'{nome_template}:{key}.last()' + '}<>1'
                comments = f'Verique o HDD Slot {n_hdd}'
                prioridade = 3
                self._cria_trigger(descricao, exprecao, prioridade, comments)
        
                id_aplicacao = self.cria_applicacao('Volume Disks', id_template)
                nome_item = f'{nome_nimble} - Total Volume {n_hdd}'
                key = f'vfs.file.regexp[/tmp/{nome_arquivo},"hdd;\s{n_hdd};\s0;\s[0-9];\s([a-z]*\s[a-z]*|[a-z]*);\s([0-9]*)",,,,\\2]'
                self._cria_item(nome_item, id_template, key, 3, [id_aplicacao_disk, id_aplicacao, id_nimble], 'GB')
            
            list_ssd = ['slot_1_A', 'slot_1_B', 'slot_2_A', 'slot_2_B', 'slot_3_A', 'slot_3_B']
            for n_ssd in range(0, 6):

                id_aplicacao = self.cria_applicacao('Volume Disks', id_template)
                nome_item = f'{nome_nimble} - Total LBAs written SSD {list_ssd[n_ssd]}'
                key = f'vfs.file.regexp[/tmp/{nome_arquivo},"{n_ssd};\sslot_[0-9]*;\s([0-9]*)",,,,\\1]'
                self._cria_item(nome_item, id_template, key, 3, [id_aplicacao_disk, id_aplicacao, id_nimble], 'Mb')

                nome_item = f'{nome_nimble} - Total LBAs flash writes SSD {list_ssd[n_ssd]}'
                key = f'vfs.file.regexp[/tmp/{nome_arquivo},"{n_ssd};\sslot_[0-9]*;\s[0-9]*.[0-9];\s([0-9]*)",,,,\\1]'
                self._cria_item(nome_item, id_template, key, 3, [id_aplicacao_disk, id_aplicacao, id_nimble], 'Mb')

                id_aplicacao = self.cria_applicacao('Power on', id_template)
                nome_item = f'{nome_nimble} - Power on hours SSD {list_ssd[n_ssd]}'
                key = f'vfs.file.regexp[/tmp/{nome_arquivo},"^{n_ssd};.*;\s([0-9]*)",,,,\\1]'
                self._cria_item(nome_item, id_template, key, 3, [id_aplicacao_disk, id_aplicacao, id_nimble], 'h')
            
            for n_hdd in range(6, 27):
                id_aplicacao = self.cria_applicacao('Volume Disks', id_template)
                nome_item = f'{nome_nimble} - Total Write Bytes Processed HDD {n_hdd - 2}'
                key = f'vfs.file.regexp[/tmp/{nome_arquivo},"{n_hdd};\sslot_[0-9]*;\s[a-z]*;\s[a-s]*;\s([0-9]*)",,,,\\1]'
                self._cria_item(nome_item, id_template, key, 3, [id_aplicacao_disk, id_aplicacao, id_nimble], 'Gb')

                id_aplicacao = self.cria_applicacao('Temperature C', id_template)
                nome_item = f'{nome_nimble} - Temperature C HDD {n_hdd - 2}'
                key = f'vfs.file.regexp[/tmp/{nome_arquivo},"{n_hdd};\sslot_[0-9]*;\s[a-z]*;\s[a-s]*;\s[0-9]*.[0-9]*;\s([0-9]*)",,,,\\1]'
                self._cria_item(nome_item, id_template, key, 3, [id_aplicacao_disk, id_aplicacao, id_nimble], '°C')

                id_aplicacao = self.cria_applicacao('Power on', id_template)
                nome_item = f'{nome_nimble} - Power on hours HDD {n_hdd - 2}'
                key = f'vfs.file.regexp[/tmp/{nome_arquivo},"^{n_hdd};.*;\s([0-9]*)",,,,\\1]'
                self._cria_item(nome_item, id_template, key, 3, [id_aplicacao_disk, id_aplicacao, id_nimble], 'h')
      
    def cria_applicacao(self, nome_aplication, id_template):
        id_aplicacao = self.consulta_id_application(id_template, nome_aplication)
        cmd_application_create = {
            "jsonrpc": "2.0",
            "method": "application.create",
            "params": {
                "name": nome_aplication,
                "hostid": id_template
            },
            "auth": self.token,
            "id": 1
        }
        if id_aplicacao == None:
            resposta_zbx = self._envia_comando_json(cmd_application_create)
            if "error" in resposta_zbx:
                resultado = resposta_zbx['error']
                warning(f'Não foi possível criar a aplicação {nome_aplication} -> {resultado}')
                id_aplicacao = None
            else:
                info(f'Aplicação {nome_aplication} criada com sucesso !!!')
                result = resposta_zbx['result']['applicationids'][0]
                id_aplicacao = result
        return id_aplicacao

    def _cria_template(self, nome_template):
        cmd_template_create = {
            "jsonrpc": "2.0",
            "method": "template.create",
            "params": {
                "host": nome_template,
                "name": nome_template,
                "groups": {
                    "groupid": None
                }
            },
            "auth": self.token,
            "id": 1
        }
        id_template = self.consulta_id_template(nome_template)
        if id_template == None:
            id_templategroup = self._cria_template_group(nome_template)
            cmd_template_create['params']['groups']['groupid'] = id_templategroup

            resposta_zbx = self._envia_comando_json(cmd_template_create)
            if "error" in resposta_zbx:
                resultado = resposta_zbx['error']
                warning(f'Não foi possível criar o template {nome_template}-> {resultado}')
                id_template = None
            else:
                info(f'Template {nome_template} criados com sucesso !!!')
                result = resposta_zbx['result']
                id_template = result
        return id_template

    def _cria_template_group(self, nome_template_group):
        cmd_templategroup_create = {
            "jsonrpc": "2.0",
            "method": "hostgroup.create",
            "params": {
                "name": nome_template_group
            },
            "auth": self.token,
            "id": 1
        }
        id_template_group = self.consulta_id_template_group(nome_template_group)
        if id_template_group == None:
            resposta_zbx = self._envia_comando_json(cmd_templategroup_create)
            if "error" in resposta_zbx:
                resultado = resposta_zbx['error']
                warning(f'Não foi possível criar o grupo do template {nome_template_group}-> {resultado}')
                id_template_group = None
            else:
                info(f'Grupo Template {nome_template_group} criados com sucesso !!!')
                result = resposta_zbx['result']['groupids'][0]
                id_template_group = result

        return id_template_group

    def _cria_trigger(self, descricao, exprecao, prioridade, comments) -> list:
        cmd_trigger_create = {
            "jsonrpc": "2.0",
            "method": "trigger.create",
            "params": {'description': descricao,
                        'expression': exprecao,
                        'priority': prioridade,
                        'comments': comments},
            "auth": self.token,
            "id": 1
        }
        resposta_zbx = self._envia_comando_json(cmd_trigger_create)
        if "error" in resposta_zbx:
            resultado = resposta_zbx['error']
            warning(f'Não foi possível criar as triggers do item {descricao}-> {resultado}')
            id_triggers = None
        else:
            info(f'Triggers do item {descricao} criados com sucesso !!!')
            result = resposta_zbx['result']['triggerids']
            id_triggers = result

        return id_triggers

    def _cria_item(self, item_name, id_template, key, tipo_valor, aplicacoes:list, unidade=None):
        cmd_item_create = {
            "jsonrpc": "2.0",
            "method": "item.create",
            "params": {
                "name": item_name,
                "key_": key,
                "hostid": id_template,
                "type":0,
                "value_type":tipo_valor,
                "delay":"60s",
                #"history":"30",
                "applications": aplicacoes,
                "units": unidade,
            },
            "auth":self.token,
            "id":1
        }

        resposta_zbx = self._envia_comando_json(cmd_item_create)
        if "error" in resposta_zbx:
            resultado = resposta_zbx['error']
            warning(f'Não foi possível criar o item master {item_name}-> {resultado}')
            id_item = None
        else:
            info(f'Item master {item_name} criados com sucesso !!!')
            result = resposta_zbx['result']['itemids'][0]
            id_item = result
        return id_item

if __name__ == '__main__':
    """
    Exemplo: python cria_templates_Nimble.py --usuario 'Admin' --senha 'zabbix' --url 'http://192.168.100.244/api_jsonrpc.php' 
                                             --ip_Nimble '10.10.10.10' --usr_Nimble 'admin' --pas_Nimble 'admin'
    """
    args = parser.parse_args()
    zabbix = ZABBIX(args.usuario, args.senha, args.url, args.ip_Nimble, args.usr_Nimble, args.pas_Nimble)
    #zabbix = ZABBIX('Admin', 'zabbix', "http://192.168.100.244/api_jsonrpc.php", '10.10.10.10', 'admin', 'admin')
    zabbix.cria_itens_controllers()
    zabbix.cria_itens_disk()