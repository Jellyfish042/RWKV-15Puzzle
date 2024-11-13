import json


class DataLogger:
    def __init__(self, print_to_console=True):
        self.log = ""
        self.print_to_console = print_to_console

    def print_and_log(self, text: str, end="\n"):
        if self.print_to_console:
            print(text)
        self.log += text + end

    def print_all(self, max_length=2000):
        print("=" * 100)
        if max_length is None:
            print(self.log)
        else:
            print(self.log[:max_length])
        print("=" * 100)
        print(f"Total Length: {len(self.log)}")
        

    def clear(self):
        self.log = ""

    def append_to_jsonl(self, filename: str):
        with open(filename, "a", encoding="utf-8") as f:
            json_entry = json.dumps({"text": self.log.strip()}, ensure_ascii=False)
            f.write(json_entry + "\n")
