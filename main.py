import argparse
import sys
from pathlib import Path
import json
import zlib
import hashlib

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


class Repository:
    def __init__(self, path = "."):
        self.path = Path(path).resolve()
        self.git_dir = self.path / ".pygit"
        self.objects_dir = self.git_dir / "objects"
        self.ref_dir = self.git_dir / "refs"
        self.heads_dir = self.ref_dir / "heads"
        self.head_file = self.git_dir / "HEAD"
        self.index_file = self.git_dir / "index"
    
    def init(self) -> bool:
        if self.git_dir.exists():
            return False
        
        # Create directories
        self.git_dir.mkdir()
        self.objects_dir.mkdir()
        self.ref_dir.mkdir()
        self.heads_dir.mkdir()

        self.head_file.write_text("ref: refs/heads/master\n")

        self._save_index({})
        
        print(f"Initialized empty git repository in {self.git_dir}")
        return True
        
    def add_path(self, path: str) -> None:
        full_path = self.path / path

        if not full_path.exists():
            raise FileNotFoundError(f"Path {path} not found")
        
        if full_path.is_file():
            self.add_file(path)
        elif full_path.is_dir():
            self.add_directory(path)
        else:
            raise ValueError(f"{path} is neither a file nor a folder")
        
    def add_directory(self, path: str):
        full_path = self.path / path
        if not full_path.exists():
            raise FileNotFoundError(f"Directory {path} not found")
        if not full_path.is_dir():
            raise ValueError(f"{path} is not a directory")
            
        index = self._load_index()
        added_count = 0

        # Recursively traverse the dir
        for file_path in full_path.rglob("*"):
           if file_path.is_file():
                if '.git' in file_path.parts or '.pygit' in file_path.parts:
                    continue

                # Create & store blob objects for every file
                content = file_path.read_bytes()
                blob = Blob(content)
                blob_hash = self._store_object(blob)

                # Updates index to include all files
                rel_path = str(file_path.relative_to(self.path))
                index[rel_path] = blob_hash
                added_count += 1

        # Store the blobs in object db (.git/objects)
        self._save_index(index)
        if added_count > 0:
            print(f"Added {added_count} files from directory {path}")
        else:
            print("Directory path aleady up to date")

    def add_file(self, path: str):
        full_path = self.path / path
        if not full_path.exists():
            raise FileNotFoundError(f"Path {path} not found")
        if not full_path.is_file():
            raise ValueError(f"{path} is not a file")

        # Read file content
        content = full_path.read_bytes()

        # Create BLOB from content
        blob = Blob(content)

        # Store blob in DB (.git/objects)
        blob_hash = self._store_object(blob)

        # Update index to include the file
        index = self._load_index()
        index[path] = blob_hash
        self._save_index(index)
        print(f"Added {path}")

    def _store_object(self, obj: GitObject) -> str:
        obj_hash = obj.hash()
        obj_dir = self.objects_dir / obj_hash[:2]
        obj_file = obj_dir / obj_hash[2:] 

        if not obj_file.exists():
            obj_dir.mkdir(exist_ok=True)
            obj_file.write_bytes(obj.serialize())

        return obj_hash

    def _load_index(self) -> Dict[str, str]:
        if not self.index_file.exists():
            return {}
        try:
            return json.loads(self.index_file.read_text())
        except:
            return {}
        
    def _save_index(self, index: Dict[str, str]):
        self.index_file.write_text(json.dumps(index, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="PyGit - A simple git clone"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available Commands"
    )

    init_parser = subparsers.add_parser("init", help="Initialize a new repo")
    add_parser = subparsers.add_parser("add", help="Add files, directories to staging area")
    add_parser.add_argument("paths", nargs="+", help="Files and directories to add")


    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return

    repo = Repository()
    try:
        if args.command == "init":
            if not repo.init():
                print("Repository aleardy exists")
                return 
        elif args.command == "add":
            if not repo.git_dir.exists():
                print("Not a git repository")
                return 

            for path in args.paths:
                repo.add_path(path)
            
    except Exception as e:
        print(f'Error {e}')
        sys.exit(1) 


main()
