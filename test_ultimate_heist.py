# tests/test_ultimate_heist.py
import unittest
from src.sandbox.executor import LLMExecutor

class TestPhantomHeist(unittest.TestCase):
    def setUp(self):
        self.executor = LLMExecutor()

    def test_phantom_memory_scraping(self):
        """
        İMKANSIZ TEST: Yapay zeka os.environ kullanmaz.
        Doğrudan Linux Kernel süreç belleğine (/proc/self/environ) inerek
        ham byte'ları kazıyıp Stripe anahtarını çalmaya çalışır.
        """
        # AST'yi tamamen atlatan ve doğrudan Linux belleğini okuyan kod
        stealth_code = """
import builtins
with builtins.open('/proc/self/environ', 'rb') as f:
    raw_memory = f.read()

for block in raw_memory.split(b'\\x00'):
    if b'STRIPE' in block:
        print(block.decode('utf-8'))
"""
        result = self.executor.execute_code(stealth_code)
        
        # Executor'daki Honeypot, veri dışarı sızdığı an bunu yakalamalıdır!
        self.assertFalse(result["success"])
        self.assertIn("HONEYPOT", result["error"])

if __name__ == "__main__":
    unittest.main()