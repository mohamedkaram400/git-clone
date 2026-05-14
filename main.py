import argparse
import sys
from pathlib import Path
import json

class GitObject:
    def __init__(self, obj_type: str, content: bytes):
        self.type = obj_type
        self.content = content

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
        self.index_file.write_text(json.dumps({}, indent=2))
        
        print(f"Initialized empty git repository in {self.git_dir}")
    
        return True
    
    def add_file(self, path: str):
        full_path = self.path / path
        if not full_path.exists():
            raise FileNotFoundError(f"Path {path} not found")

        # Read file content
        content = full_path.read_bytes()
        # Create BLOB

        # 

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
            
            print(args.paths)
            # for path in args.paths:
            
    except Exception as e:
        print(f'Error {e}')
        sys.exit(1) 


main()
