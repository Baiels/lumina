from lexico import Token, Lexer
import sys

# Classe que faz a análise sintática
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = 0
        self.current_token = self.tokens[self.token_index]

    # Avança para o próximo token
    def _advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = Token("EOF", None)

    # Verifica se o token atual é o esperado
    def _eat(self, token_type):
        if self.current_token.type == token_type:
            self._advance()
        else:
            self._error(f"Esperado {token_type}, encontrado {self.current_token.type}")

    # Exibe mensagem de erro com linha e coluna
    def _error(self, message):
        raise Exception(f"Erro sintático na linha {self.current_token.line}, coluna {self.current_token.column}: {message}")

    # Início da análise
    def parse(self):
        self.program()
        print("Análise sintática concluída com sucesso!")

    # Início do programa: lista de funções
    def program(self):
        self.function_declaration_list()
        self._eat("EOF")

    # Pode ter várias funções seguidas
    def function_declaration_list(self):
        while self.current_token.type != "EOF":
            self.function_declaration()

    # Declaração de uma função
    def function_declaration(self):
        if self.current_token.type in ["INT", "FLOAT", "STRING", "BOOL", "VOID"]:
            self._eat(self.current_token.type)
        else:
            self._error(f"Tipo de retorno de função esperado, encontrado {self.current_token.type}")

        self._eat("IDENTIFICADOR")
        self._eat("PARENTESE_ESQ")
        self.parameters()
        self._eat("PARENTESE_DIR")
        self.block()

    # Parâmetros da função (opcional)
    def parameters(self):
        if self.current_token.type in ["INT", "FLOAT", "STRING", "BOOL"]:
            self.parameter()
            while self.current_token.type == "VIRGULA":
                self._eat("VIRGULA")
                self.parameter()

    # Um parâmetro é: tipo + nome
    def parameter(self):
        self._eat(self.current_token.type)
        self._eat("IDENTIFICADOR")

    # Bloco de código entre chaves
    def block(self):
        self._eat("CHAVE_ESQ")
        self.statement_list()
        self._eat("CHAVE_DIR")

    # Lista de comandos (statements)
    def statement_list(self):
        while self.current_token.type != "CHAVE_DIR" and self.current_token.type != "EOF":
            self.statement()
            if self.current_token.type == "PONTO_VIRGULA":
                self._eat("PONTO_VIRGULA")

    # Verifica o tipo de comando e chama o correto
    def statement(self):
        if self.current_token.type in ["INT", "FLOAT", "STRING", "BOOL", "VOID"]:
            self.declaration()
        elif self.current_token.type == "IDENTIFICADOR":
            if self.token_index + 1 < len(self.tokens) and self.tokens[self.token_index + 1].type == "PARENTESE_ESQ":
                self.function_call_statement()
            else:
                self.assignment()
        elif self.current_token.type == "IF":
            self.if_statement()
        elif self.current_token.type == "WHILE":
            self.while_statement()
        elif self.current_token.type == "FOR":
            self.for_statement()
        elif self.current_token.type == "RETURN":
            self.return_statement()
        else:
            self._error(f"Declaração ou instrução inesperada: {self.current_token.type}")

    # Chamada de função (ex: print(x))
    def function_call_statement(self):
        self._eat("IDENTIFICADOR")
        self._eat("PARENTESE_ESQ")
        self.arguments()
        self._eat("PARENTESE_DIR")

    # Argumentos de função (ex: soma(1, 2))
    def arguments(self):
        if self.current_token.type != "PARENTESE_DIR":
            self.expression()
            while self.current_token.type == "VIRGULA":
                self._eat("VIRGULA")
                self.expression()

    # Declaração de variável (ex: int x = 5)
    def declaration(self):
        self._eat(self.current_token.type)
        self._eat("IDENTIFICADOR")
        if self.current_token.type == "ATRIBUIR":
            self._eat("ATRIBUIR")
            self.expression()

    # Atribuição (ex: x = 5)
    def assignment(self):
        self._eat("IDENTIFICADOR")
        self._eat("ATRIBUIR")
        self.expression()

    # Estrutura condicional (if/else)
    def if_statement(self):
        self._eat("IF")
        self._eat("PARENTESE_ESQ")
        self.expression()
        self._eat("PARENTESE_DIR")
        self.block()
        if self.current_token.type == "ELSE":
            self._eat("ELSE")
            self.block()

    # Estrutura de repetição (while)
    def while_statement(self):
        self._eat("WHILE")
        self._eat("PARENTESE_ESQ")
        self.expression()
        self._eat("PARENTESE_DIR")
        self.block()

    # Estrutura de repetição (for)
    def for_statement(self):
        self._eat("FOR")
        self._eat("PARENTESE_ESQ")
        if self.current_token.type in ["INT", "FLOAT", "STRING", "BOOL"]:
            self.declaration()
        elif self.current_token.type == "IDENTIFICADOR":
            self.assignment()
        self._eat("PONTO_VIRGULA")
        self.expression()
        self._eat("PONTO_VIRGULA")
        self.assignment()
        self._eat("PARENTESE_DIR")
        self.block()

    # Retorno de função (return)
    def return_statement(self):
        self._eat("RETURN")
        if self.current_token.type != "PONTO_VIRGULA":
            self.expression()

    # Expressão (ex: x + 5)
    def expression(self):
        self.term()
        while self.current_token.type in ["SOMA", "SUBTRACAO", "IGUAL", "DIFERENTE", "MENOR", "MAIOR", "MENOR_IGUAL", "MAIOR_IGUAL"]:
            self._eat(self.current_token.type)
            self.term()

    # Termo da expressão (multiplicações e divisões)
    def term(self):
        self.factor()
        while self.current_token.type in ["MULTIPLICACAO", "DIVISAO"]:
            self._eat(self.current_token.type)
            self.factor()

    # Fator: número, variável, função ou expressão entre parênteses
    def factor(self):
        token = self.current_token
        if token.type == "NUMERO":
            self._eat("NUMERO")
        elif token.type == "IDENTIFICADOR":
            if self.token_index + 1 < len(self.tokens) and self.tokens[self.token_index + 1].type == "PARENTESE_ESQ":
                self.function_call_statement()
            else:
                self._eat("IDENTIFICADOR")
        elif token.type == "PARENTESE_ESQ":
            self._eat("PARENTESE_ESQ")
            self.expression()
            self._eat("PARENTESE_DIR")
        elif token.type == "STRING":
            self._eat("STRING")
        elif token.type in ["TRUE", "FALSE"]:
            self._eat(token.type)
        else:
            self._error(f"Fator inesperado: {token.type}")

# Parte que roda se o arquivo for executado direto
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python3 sintatico.py <arquivo_fonte>")
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
        parser = Parser(tokens)
        parser.parse()
    except Exception as e:
        print(f"Erro: {e}")
