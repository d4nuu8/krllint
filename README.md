# krlcodestyle
krlcodestyle checks and automatically fixes KRL (KUKA Robot Language) code.

## Installation
Youe can download ```krlcodestyle.py``` either from github or with these command:
```bash
$ pip install krlcodestyle
```

### Exmaple usage
Show help:
```bash
$ krlcodestyle --help
```

Check files or folders:
```bash
$ krlcodestyle example.src
$ krlcodestyle example.src furhter_example.src
$ krlcodestyle source_dir
```

Automatically fix code:
```bash
$ krlcodestyle --fix example.src
```