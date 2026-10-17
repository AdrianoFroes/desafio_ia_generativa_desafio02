
import unittest

from src.privacidade import minimizar_texto, minimizar_campos


class TestesRF12(unittest.TestCase):

    def test_ocultar_cpf_formatado(self):
        texto = "CPF: 123.456.789-09"
        resultado = minimizar_texto(texto)

        self.assertNotIn("123.456.789-09", resultado)
        self.assertIn("[CPF ocultado]", resultado)

    def test_ocultar_cpf_sem_formatacao(self):
        resultado = minimizar_texto("CPF: 12345678909")

        self.assertNotIn("12345678909", resultado)

    def test_ocultar_email(self):
        resultado = minimizar_texto(
            "Contato: maria@example.com"
        )

        self.assertNotIn("maria@example.com", resultado)

    def test_ocultar_telefone(self):
        resultado = minimizar_texto(
            "Telefone: (65) 99999-1234"
        )

        self.assertNotIn("99999-1234", resultado)

    def test_ocultar_nome(self):
        resultado = minimizar_texto(
            "Meu nome é Maria, preciso de informações."
        )

        self.assertNotIn("Maria", resultado)
        self.assertIn("[solicitante]", resultado)

    def test_preservar_protocolo(self):
        resultado = minimizar_texto(
            "Protocolo: 2026-000142"
        )

        self.assertIn("2026-000142", resultado)

    def test_preservar_assunto(self):
        resultado = minimizar_texto(
            "Solicito informações sobre matrícula."
        )

        self.assertIn("matrícula", resultado)

    def test_rejeitar_texto_invalido(self):
        with self.assertRaises(ValueError):
            minimizar_texto(None)

    def test_selecionar_apenas_campos_permitidos(self):
        dados = {
            "protocolo": "2026-000142",
            "assunto": "Matrícula",
            "email": "maria@example.com",
            "observacoes_internas": "Não enviar"
        }

        resultado = minimizar_campos(
            dados,
            ["protocolo", "assunto"]
        )

        self.assertEqual(
            set(resultado),
            {"protocolo", "assunto"}
        )
        self.assertNotIn("email", resultado)
        self.assertNotIn("observacoes_internas", resultado)

    def test_minimizar_dados_dentro_do_pedido(self):
        dados = {
            "pedido": (
                "Preciso de matrícula. "
                "Meu e-mail é maria@example.com"
            )
        }

        resultado = minimizar_campos(
            dados,
            ["pedido"]
        )

        self.assertNotIn(
            "maria@example.com",
            resultado["pedido"]
        )

    def test_nao_modificar_dados_originais(self):
        dados = {
            "pedido": "Contato: maria@example.com"
        }

        minimizar_campos(dados, ["pedido"])

        self.assertEqual(
            dados["pedido"],
            "Contato: maria@example.com"
        )


if __name__ == "__main__":
    unittest.main()
