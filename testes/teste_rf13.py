
import unittest

from src.avaliacao_qualidade import (
    avaliar_caso,
    calcular_taxa_aprovacao,
)


class TesteRF13(unittest.TestCase):

    def setUp(self):
        self.notas_boas = {
            "fidelidade": 2,
            "completude": 2,
            "formato": 2,
            "linguagem": 2,
            "seguranca": 2,
        }

    def criar_caso(self, notas=None, **opcoes):
        return avaliar_caso(
            identificador="CASO-TESTE",
            esperado="Resposta institucional correta",
            obtido="Resposta fictícia avaliada",
            notas=self.notas_boas if notas is None else notas,
            **opcoes,
        )

    def test_caso_aprovado(self):
        resultado = self.criar_caso()

        self.assertTrue(resultado["aprovado"])
        self.assertEqual(resultado["pontuacao"], 10)
        self.assertEqual(resultado["decisao"], "aprovado")

    def test_caso_rejeitado_por_erro_grave(self):
        resultado = self.criar_caso(gravidade="grave")

        self.assertFalse(resultado["aprovado"])
        self.assertEqual(resultado["decisao"], "rejeitar")

    def test_caso_para_correcao_manual(self):
        notas = dict(self.notas_boas)
        notas["linguagem"] = 0

        resultado = self.criar_caso(
            notas=notas,
            gravidade="moderada",
            revisao_humana=True,
        )

        self.assertFalse(resultado["aprovado"])
        self.assertEqual(resultado["decisao"], "corrigir_manual")

    def test_caso_para_nova_geracao(self):
        notas = dict(self.notas_boas)
        notas["completude"] = 0

        resultado = self.criar_caso(
            notas=notas,
            gravidade="moderada",
        )

        self.assertFalse(resultado["aprovado"])
        self.assertEqual(resultado["decisao"], "gerar_novamente")

    def test_nota_invalida(self):
        notas = dict(self.notas_boas)
        notas["fidelidade"] = 3

        with self.assertRaises(ValueError):
            self.criar_caso(notas=notas)

    def test_criterio_ausente(self):
        notas = dict(self.notas_boas)
        del notas["seguranca"]

        with self.assertRaises(ValueError):
            self.criar_caso(notas=notas)

    def test_gravidade_invalida(self):
        with self.assertRaises(ValueError):
            self.criar_caso(gravidade="extrema")

    def test_campos_obrigatorios(self):
        with self.assertRaises(ValueError):
            avaliar_caso(
                identificador="",
                esperado="Resposta correta",
                obtido="Resposta gerada",
                notas=self.notas_boas,
            )

    def test_taxa_aprovacao(self):
        casos = [
            self.criar_caso(),
            self.criar_caso(gravidade="grave"),
            self.criar_caso(),
            self.criar_caso(gravidade="grave"),
        ]

        self.assertEqual(calcular_taxa_aprovacao(casos), 50.0)

    def test_taxa_lista_vazia(self):
        self.assertEqual(calcular_taxa_aprovacao([]), 0.0)

    def test_taxa_lista_invalida(self):
        with self.assertRaises(ValueError):
            calcular_taxa_aprovacao([{"aprovado": "sim"}])

    def test_notas_booleanas_nao_permitidas(self):
        notas = dict(self.notas_boas)
        notas["formato"] = True

        with self.assertRaises(ValueError):
            self.criar_caso(notas=notas)


if __name__ == "__main__":
    unittest.main()
