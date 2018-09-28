# krllint
krllint checks and automatically fixes KRL (KUKA Robot Language) code.

## Installation
Youe can download ```krllint.py``` either from github or with this command:
```bash
$ pip install krllint
```

### Exmaple usage
Show help:
```bash
$ krllint --help
```

Check files or folders:
```bash
$ krllint example.src
$ krllint example.src furhter_example.src
$ krllint source_dir
```

Automatically fix code:
```bash
$ krllint --fix example.src
```