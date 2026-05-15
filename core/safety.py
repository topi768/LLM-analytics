import re

BANNED_PATTERNS = [
    r"\bimport\s+os\b",
    r"\bimport\s+sys\b",
    r"\bimport\s+subprocess\b",
    r"\bimport\s+socket\b",
    r"\bimport\s+shutil\b",
    r"\bimport\s+pathlib\b",
    r"\bimport\s+pickle\b",
    r"\bimport\s+ctypes\b",
    r"\bimport\s+threading\b",
    r"\bimport\s+multiprocessing\b",
    r"\bimport\s+requests\b",
    r"\bimport\s+urllib\b",
    r"\bimport\s+http\b",
    r"\bopen\s*\(",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"\bcompile\s*\(",
    r"__\w+__",
    r"\bglobals\s*\(",
    r"\blocals\s*\(",
    r"\binput\s*\(",
    r"\bos\.",
    r"\bsys\.",
    r"\bsubprocess\.",
    r"\bsocket\.",
    r"\bshutil\.",
    r"\bpickle\.",
]

def is_safe_code(code: str) -> bool:
    for pattern in BANNED_PATTERNS:
        if re.search(pattern, code, flags=re.IGNORECASE):
            return False
    return True