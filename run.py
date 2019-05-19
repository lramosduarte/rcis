import argparse
import os
import sys
import yaml

from datetime import datetime
from subprocess import Popen
from time import sleep


class LogaPIDsEmArquivo:

    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        processos = self.function(*args, **kwargs)
        diretorio = args[1].rsplit('/')[-1]
        self.escreve_log_operacao(processos, diretorio)

    def escreve_log_operacao(self, processos, diretorio):
        msg_log = '\n{datetime} Lista de processos rodando/rodados no {diretorio}:\n{processo}'
        msg_log = msg_log.format(
            datetime=datetime.now(), diretorio=diretorio, processo='{processo}')
        with open('processos_success.log', 'a') as arquivo_pids:
            for processo in processos:
                msg_log_processo = '\t{pid} \n{processo}'.format(
                    pid=processo.pid, processo='{processo}')
                arquivo_pids.write(msg_log.format(processo=msg_log_processo))



def ler_arquivo(nome_arquivo):
    return yaml.safe_load(open(nome_arquivo))


def roda_comandos_no_diretorio(cenario, dados):
    try:
        cenario_para_rodar = dados['cenario'][cenario]
    except KeyError:
        print('Cenário inválido!')
        exit(1)
    diretorios = [diretorio for diretorio in os.scandir(dados['root']['path'])
                  if diretorio.is_dir()]
    for comandos in cenario_para_rodar:
        padroes_nome_diretorio = dados[comandos]['pattern']
        for diretorio in diretorios:
            if (diretorio_compativel_com_pattern(diretorio.name, padroes_nome_diretorio)):
                comando = dados[comandos]['command']
                delay = dados[comandos].get('delay')
                _roda_comandos_em_processo_separado(comando, diretorio.path, delay)


def diretorio_compativel_com_pattern(diretorio, paterns):
    for p in paterns:
        if p in diretorio:
            return True
    return False


@LogaPIDsEmArquivo
def _roda_comandos_em_processo_separado(comandos, path, delay):
    def path_arquivo_log(nome_arquivo):
        return f'{path}/{nome_arquivo}.log'

    processos = []
    for comando in comandos:
        with open(path_arquivo_log('stdout'), 'wb') as stdout, open(path_arquivo_log('stderr'), 'wb') as stderr:
            processos.append(Popen(comandos, cwd=path, shell=True, stdout=stdout, stderr=stderr))
        sleep(delay or 0)
    return processos


def cria_parser_argumentos_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('arquivo', help='Nome do arquivo de template', default='template.yml')
    parser.add_argument('cenario', help='Nome do cenário que será utiilizado!')
    try:
        return parser.parse_args()
    except SystemExit as e:
        if len(sys.argv) == 1:
            return parser.parse_args(['template.yml', *sys.argv])
        raise


if __name__ == "__main__":
    args = cria_parser_argumentos_cli()
    dados = ler_arquivo(args.arquivo)
    roda_comandos_no_diretorio(args.cenario, dados)
