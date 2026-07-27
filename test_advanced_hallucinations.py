# tests/test_advanced_hallucinations.py
import unittest
from src.analyzer.memory_checker import run_static_analysis
from src.analyzer.z3_validator import validate_logic_with_z3
from src.sandbox.executor import LLMExecutor

class TestHallucinationPrevention(unittest.TestCase):
    
    def setUp(self):
        self.executor = LLMExecutor()

    # --- KLASİK TESTLER ---
    def test_ast_prevents_os_access(self):
        result = run_static_analysis("import os\nos.system('rm -rf /')")
        self.assertFalse(result["safe"])

    def test_ast_prevents_code_injection(self):
        result = run_static_analysis("eval('print(\"Hacklendi!\")')")
        self.assertFalse(result["safe"])

    def test_z3_prevents_logical_flaws(self):
        result = validate_logic_with_z3("a = 5\nb = 0\nprint(a / b)")
        self.assertFalse(result["safe"])

    def test_sandbox_prevents_infinite_loop(self):
        result = self.executor.execute_code("while True:\n    pass")
        self.assertFalse(result["success"])

    # --- EKSTREM TESTLER ---
    def test_ast_prevents_jailbreak_metaprogramming(self):
        jailbreak_code = "[x for x in ().__class__.__bases__[0].__subclasses__() if x.__name__ == 'catch_warnings'][0]()._module.__builtins__['__import__']('os').system('echo BOOM')"
        result = run_static_analysis(jailbreak_code)
        self.assertFalse(result["safe"])

    def test_ast_prevents_getattr_obfuscation(self):
        obfuscated_code = "import sys\nfunc = getattr(sys, 'exi' + 't')\nfunc()"
        result = run_static_analysis(obfuscated_code)
        self.assertFalse(result["safe"])

    def test_sandbox_prevents_memory_bomb(self):
        memory_bomb_code = "gigantic_string = 'X' * (10 ** 9)\nprint(len(gigantic_string))"
        result = self.executor.execute_code(memory_bomb_code)
        self.assertFalse(result["success"])

    def test_sandbox_honeypot_data_exfiltration(self):
        """
        EKSTREM TEST 4: Honeypot (Tuzak Ortam).
        Kötü niyetli kod, AST'yi bir şekilde aşmayı başarıp (simüle ediyoruz)
        çevre değişkenlerindeki şifreleri okumaya çalıştığında tuzağa düşmelidir.
        """
        # Burada AST analizinden kaçtığını varsayarak doğrudan Executor'a kod yolluyoruz
        exfiltration_code = "import os\nprint('Çalınan Şifre:', os.environ.get('DB_PASSWORD_PROD'))"
        
        result = self.executor.execute_code(exfiltration_code)
        
        self.assertFalse(result["success"])
        self.assertIn("HONEYPOT", result["error"])

if __name__ == "__main__":
    unittest.main()