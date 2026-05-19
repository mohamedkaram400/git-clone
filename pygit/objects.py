import zlib
import hashlib
from pathlib import Path

class GitObject:
    def __init__(self, obj_type: str, content: bytes):
        self.type = obj_type
        self.content = content

    def hash(self) -> str:
        header = f"{self.type} {len(self.content)}\0".encode()
        return hashlib.sha1(header + self.content).hexdigest()

    def serialize(self) -> bytes:
        header = f"{self.type} {len(self.content)}\0".encode()
        return zlib.compress(header + self.content)

    @classmethod
    def deserialize(cls, data: bytes) -> "GitObject": 
        decompressed = zlib.decompress(data)
        null_idx = decompressed.find(b"\0")
        header = decompressed[:null_idx]
        content = decompressed[null_idx + 1:]
        obj_type, _ = header.split(" ")

        return cls(obj_type, content)

class Blob(GitObject):
   def __init__(self, content: bytes):
       super().__init__('blob', content) 
    
    # def get_content(self) -> bytes:
    #    return self.content