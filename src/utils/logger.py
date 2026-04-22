import logging
import os
from pathlib import Path
from datetime import datetime

class BookBotLogger:
    """Manages system and LLM interaction logs for BookBot_06."""
    
    def __init__(self, log_dir: str = "logs", max_entries: int = 100):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "session.log"
        self.max_entries = max_entries
        
        # Configure standard logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filemode='a',
            encoding='utf-8' # Ensure emojis/special chars don't break it
        )
        self.logger = logging.getLogger("BookBot")

    def log_interaction(self, agent_name: str, prompt: str, response: str):
        """Logs a full LLM interaction."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"--- INTERACTION: {agent_name} @ {timestamp} ---\nPROMPT: {prompt[:200]}...\nRESPONSE: {response[:200]}...\n"
        self.logger.info(log_entry)
        self._prune_logs()

    def log_error(self, message: str):
        """Logs a system error."""
        self.logger.error(message)

    def _prune_logs(self):
        """Ensures the log file doesn't grow indefinitely by keeping only the last few hundred lines."""
        if not self.log_file.exists():
            return
            
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if len(lines) > 500: # Arbitrary threshold for pruning
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines[-500:])
        except Exception:
            pass

    def get_recent_logs(self, n: int = 10) -> str:
        """Returns the last n lines of the log."""
        if not self.log_file.exists():
            return "No logs found."
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return "".join(lines[-n:])

# Singleton instance
bot_logger = BookBotLogger()
