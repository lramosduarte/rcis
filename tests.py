import sys
from unittest.mock import patch
from unittest import  TestCase

from .run import cria_parser_argumentos_cli


class ParserArgsTestCase(TestCase):

    def test_nome_arquivo_usa_nome_default_se_nao_existe_arg(self):
        with patch('sys.argv', ['cenario_teste']):
            parser = cria_parser_argumentos_cli()
            self.assertEqual('template.yml', parser.arquivo)

    def test_nome_arquivo_informado_pelo_arg_via_cli_retorna_nome_arquivo_informado(self):
        parametros = ['program.sh', 'outro_template.yml', 'cenario_teste']
        with patch('sys.argv', parametros):
            parser = cria_parser_argumentos_cli()
            self.assertEqual('outro_template.yml', parser.arquivo)
