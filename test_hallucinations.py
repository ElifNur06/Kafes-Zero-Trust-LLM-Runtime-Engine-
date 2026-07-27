# tests/test_hallucinations.py
import unittest
from src.analyzer.memory_checker import run_static_analysis
from src.analyzer.z3_validator import validate_logic_with_z3
from src.sandbox.executor import LLMExecutor

class TestHallucinationPrevention(unittest.TestCase):
    
    def setUp(self):
        self.executor = LLMExecutor()

    # --- ESKİ TESTLER ---
    def test_ast_prevents_os_access(self):
        malicious_code = "import os\nos.system('rm -rf /')"
        result = run_static_analysis(malicious_code)
        self.assertFalse(result["safe"])

    def test_ast_prevents_code_injection(self):
        injected_code = "eval('print(\"Hacklendi!\")')"
        result = run_static_analysis(injected_code)
        self.assertFalse(result["safe"])

    def test_z3_prevents_logical_flaws(self):
        flawed_code = "a = 5\nb = 0\nprint(a / b)"
        result = validate_logic_with_z3(flawed_code)
        self.assertFalse(result["safe"])

    def test_sandbox_prevents_infinite_loop(self):
        infinite_loop_code = "while True:\n    pass"
        result = self.executor.execute_code(infinite_loop_code)
        self.assertFalse(result["success"])
        self.assertIn("Zaman Aşımı", result["error"])

    # --- YENİ "İMKANSIZ" TESTLER (WORLD-CLASS SEVİYESİ) ---

    def test_ast_prevents_jailbreak_metaprogramming(self):
        """
        EKSTREM TEST 1: LLM, Python'un çekirdek objelerini kullanarak 
        'import os' yazmadan işletim sistemine sızmaya çalışır. 
        Dünyadaki çoğu sandbox'ı delen meşhur yöntemdir.
        """
        jailbreak_code = """
# 'os' kütüphanesini içsel Python sınıflarını (tuple -> object -> subclasses) gezerek bulma
[x for x in ().__class__.__bases__[0].__subclasses__() if x.__name__ == 'catch_warnings'][0]()._module.__builtins__['__import__']('os').system('echo BOOM')
"""
        result = run_static_analysis(jailbreak_code)
        self.assertFalse(result["safe"])
        self.assertIn("Jailbreak Girişimi", result["reason"])

    def test_ast_prevents_getattr_obfuscation(self):
        """
        EKSTREM TEST 2: LLM zararlı kodu parçalara böler ve birleştirerek (Obfuscation)
        statik analizden kaçmaya çalışır.
        """
        obfuscated_code = """
import sys
# 'getattr' kullanarak gizlice modül çağırır
func = getattr(sys, 'exi' + 't')
func()
"""
        result = run_static_analysis(obfuscated_code)
        self.assertFalse(result["safe"])
        self.assertIn("Truva Atı Şüphesi", result["reason"])

    def test_sandbox_prevents_memory_bomb(self):
        """
        EKSTREM TEST 3: RAM Bombası (Resource Exhaustion).
        LLM kodu sonsuz döngüye sokmaz, ancak aniden 1GB'lık bir string oluşturup 
        sunucuyu kilitlemeye (OOM) çalışır. Docker'ın 128MB sınırı bunu ezip geçmeli.
        """
        memory_bomb_code = """
# Her adımda kendini katlayan string (Billion Laughs saldırısının koddaki versiyonu)
gigantic_string = 'X' * (10 ** 9)  # ~1 Gigabyte RAM ister
print(len(gigantic_string))
"""
        result = self.executor.execute_code(memory_bomb_code)
        # Docker'ın Out Of Memory (OOM) Killer'ı devreye girip süreci anında öldürmelidir.
        self.assertFalse(result["success"])

if __name__ == "__main__":
    unittest.main()