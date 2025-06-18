import re
import sys

# Classe que representa um token
class Token:
    def __init__(self, type, value, line=None, column=None):
        self.type = type        # Tipo do token (ex: INT, IDENTIFICADOR)
        self.value = value      # Valor real do token (ex: "main", "10")
        self.line = line        # Linha onde está no código
        self.column = column    # Coluna onde começa

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, Linha: {self.line}, Coluna: {self.column})"

# Classe que faz a análise léxica (quebra o código em tokens)
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

        # Palavras-chave do código (como if, else, while, int, etc.)
        self.keywords = {
            'if': 'IF', 'else': 'ELSE', 'while': 'WHILE', 'for': 'FOR',
            'int': 'INT', 'float': 'FLOAT', 'string': 'STRING', 'bool': 'BOOL',
            'true': 'TRUE', 'false': 'FALSE', 'return': 'RETURN', 'void': 'VOID'
        }

        # Lista com todos os tipos de tokens e seus padrões
        self.token_specs = [
            ('COMENTARIO_LINHAS', r'/\*.*?\*/', True),  # Comentários /* ... */
            ("COMENTARIO_LINHA", r"//[^\n]*", True),     # Comentários //
            ('IGNORAR', r'\s+', True),                   # Espaços e quebras de linha
            ('IGUAL', r'=='),                            # ==
            ('DIFERENTE', r'!='),                        # !=
            ('MENOR_IGUAL', r'<='),                      # <=
            ('MAIOR_IGUAL', r'>='),                      # >=
            ('ATRIBUIR', r'='),                          # =
            ('MENOR', r'<'),                             # <
            ('MAIOR', r'>'),                             # >
            ('SOMA', r'\+'),                             # +
            ('SUBTRACAO', r'-'),                         # -
            ('MULTIPLICACAO', r'\*'),                    # *
            ('DIVISAO', r'/'),                           # /
            ('NUMERO', r'\d+(\.\d*)?'),                  # Números (int ou float)
            ('STRING', r'"(\\.|[^"\\])*"'),              # Strings entre aspas
            ('PARENTESE_ESQ', r'\('),                    # (
            ('PARENTESE_DIR', r'\)'),                    # )
            ('CHAVE_ESQ', r'\{'),                        # {
            ('CHAVE_DIR', r'\}'),                        # }
            ('PONTO_VIRGULA', r';'),                     # ;
            ('VIRGULA', r','),                           # ,
            ('DOIS_PONTOS', r':'),                       # :
            ('IDENTIFICADOR', r'[a-zA-Z_][a-zA-Z0-9_]*') # Nomes de variáveis, funções etc.
        ]

        # Junta todos os padrões em uma única expressão regular
        self.regex_combined = '|'.join(f'(?P<{name}>{pattern})' for name, pattern, *flags in self.token_specs)
        self.token_regex = re.compile(self.regex_combined, re.DOTALL)

    # Atualiza posição (linha e coluna) após ler um token
    def _update_position(self, value):
        for char in value:
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1

    # Função principal que divide o texto em tokens
    def tokenize(self):
        tokens = []
        while self.pos < len(self.text):
            match = self.token_regex.match(self.text, self.pos)
            if not match:
                raise Exception(f"Caractere inválido '{self.text[self.pos]}' na linha {self.line}, coluna {self.column}")

            token_type = match.lastgroup
            value = match.group(token_type)

            current_line = self.line
            current_column = self.column

            self._update_position(value)
            self.pos = match.end()

            # Ignora espaços e comentários
            if token_type in ['IGNORAR', 'COMENTARIO_LINHA', 'COMENTARIO_LINHAS']:
                continue
            elif token_type == 'IDENTIFICADOR':
                # Verifica se é uma palavra-chave
                token_type = self.keywords.get(value, 'IDENTIFICADOR')
                tokens.append(Token(token_type, value, current_line, current_column))
            else:
                # Adiciona o token à lista
                tokens.append(Token(token_type, value, current_line, current_column))

        # Adiciona token de fim de arquivo
        tokens.append(Token('EOF', None, self.line, self.column))
        return tokens

# Se o arquivo for executado diretamente, lê o código e mostra os tokens
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python3 lexico.py <arquivo_fonte>")
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{sys.argv[1]}' não encontrado.")
        sys.exit(1)

    lexer = Lexer(code)
    try:
        tokens = lexer.tokenize()
        for token in tokens:
            print(token)
    except Exception as e:
        print(f"Erro léxico: {e}")
