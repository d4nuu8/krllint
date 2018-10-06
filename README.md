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

Create a configuration file at the current working directory:
```bash
$ krllint --generate-config
```

krllint tries to load configuration files with the following sequence:
```krllint.conf.py```:
1. Explicitly defined as argument
2. Current working directory
3. ```~/.config/```
4. Default configuration of krllint

Explicitly loading of a configuration file:
```bash
$ krllint --config krllint.config.py
```