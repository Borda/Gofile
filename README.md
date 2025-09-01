# gofile

🚀 Python wrapper for gofile.io Upload API[^1].

[![Build](https://github.com/Alyetama/gofile/actions/workflows/poetry-build.yml/badge.svg)](https://github.com/Alyetama/gofile/actions/workflows/poetry-build.yml) [![PyPI version](https://badge.fury.io/py/gofilepy.svg)](https://pypi.org/project/gofilepy) [![Supported Python versions](https://img.shields.io/badge/Python-%3E=3.7-blue.svg)](https://www.python.org/downloads/) [![PEP8](https://img.shields.io/badge/Code%20style-PEP%208-orange.svg)](https://www.python.org/dev/peps/pep-0008/)

## ⬇️ Installation

```bash
pip install gofilepy
```

## ⬆️  Upgrade Existing Installation

```bash
pip install -U gofilepy
```


## ⌨️ Usage

```
usage: gofilepy [-h] [-s] [-o] [-e] [-vv] [-v] path [path ...]

Example: gofile <file/folder_path>

positional arguments:
  path                  Path to the file(s) and/or folder(s)

options:
  -h, --help            show this help message and exit
  -s, --to-single-folder
                        Upload multiple files to the same folder. All files
                        will share the same URL. This option requires a valid
                        token exported as: `GOFILE_TOKEN`
  -o, --open-urls       Open the URL(s) in the browser when the upload is
                        complete (macOS-only)
  -e, --export          Export upload response(s) to a JSON file
  -vv, --verbose        Show more information
```

## 📕 Examples

### Example 1: Uploading one file

```bash
➜ gofile foo.txt
╭───────────────────────────────────────────╮
│ File: foo.txt                             │
│ Download page: https://gofile.io/d/PkdZP5 │
╰───────────────────────────────────────────╯
Uploading progress: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
```

### Example 2: Uploading multiple files/directories

```bash
➜ gofile foo.txt bar.txt foobar.txt foo/
╭───────────────────────────────────────────╮
│ File: foo.txt                             │
│ Download page: https://gofile.io/d/rLwQVZ │
╰───────────────────────────────────────────╯
╭───────────────────────────────────────────╮
│ File: bar.txt                             │
│ Download page: https://gofile.io/d/DdS7mZ │
╰───────────────────────────────────────────╯
╭───────────────────────────────────────────╮
│ File: foobar.txt                          │
│ Download page: https://gofile.io/d/C1VicP │
╰───────────────────────────────────────────╯
╭───────────────────────────────────────────╮
│ File: foo/foo_1.txt                       │
│ Download page: https://gofile.io/d/CkYw18 │
╰───────────────────────────────────────────╯
Uploading progress: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
```

### Example 3: Uploading multiple files to the same URL

This option requires a Gofile token (see: [## Misc.](#misc)).

```bash
➜ gofile -s foo.txt bar.txt
╭───────────────────────────────────────────╮
│ Files:                                    │
│ foo.txt                                   │
│ bar.txt                                   │
│ Download page: https://gofile.io/d/bFwawd │
╰───────────────────────────────────────────╯
Uploading progress: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
```

### Example 4: Verbose output

```bash
➜ gofile -vv foo.txt
╭──────────────────────────────────────────────────────────────────────────────╮
│ {                                                                            │
│   "foo.txt": {                                                               │
│     "timestamp": "30-05-2022 18:42:15",                                      │
│     "response": {                                                            │
│       "status": "ok",                                                        │
│       "data": {                                                              │
│         "guestToken": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",                    │
│         "downloadPage": "https://gofile.io/d/sU4hV1",                        │
│         "code": "sU4hV1",                                                    │
│         "parentFolder": "7ad2d249-96a1-4675-b185-05665fbc9a46",              │
│         "fileId": "0e93e093-d122-4e42-a1be-2e7d34d78ffb",                    │
│         "fileName": "foo.txt",                                               │
│         "md5": "d41d8cd98f00b204e9800998ecf8427e"                            │
│       }                                                                      │
│     }                                                                        │
│   }                                                                          │
│ }                                                                            │
╰──────────────────────────────────────────────────────────────────────────────╯
Uploading progress: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
```

### Example 5: Exporting the API response to a JSON file

```bash
➜ gofile -e foo.txt
╭───────────────────────────────────────────╮
│ File: foo.txt                             │
│ Download page: https://gofile.io/d/8t79Lz │
╰───────────────────────────────────────────╯
Uploading progress: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
Exported data to: gofile_export_1653950555.json
```

<details>
  <summary>Content of <code>gofile_export_1653950555.json</code></summary>
  
```json
[
    {
        "foo.txt": {
            "timestamp": "30-05-2022 18:42:35",
            "response": {
                "status": "ok",
                "data": {
                    "guestToken": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                    "downloadPage": "https://gofile.io/d/8t79Lz",
                    "code": "8t79Lz",
                    "parentFolder": "05xd4cb-8965-417f-ae34-a116et99b798",
                    "fileId": "d1fc3a97-8xe3-486a-bc0d-edb1rb103040",
                    "fileName": "foo.txt",
                    "md5": "d41d8cd99f00b204e9810998ecf8427e"
                }
            }
        }
    }
]
```
</details>

## Misc.

### 🔑 Optional: Saving uploads to your Gofile account

If you want the files to be uploaded to a specific account, you can export your gofile token, which can be retrieved from the [profile page](https://gofile.io/myProfile), as an environment variable `GOFILE_TOKEN`.

```bash
export GOFILE_TOKEN='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```


[^1]: **Disclaimer: This tool is not associated with Gofile, WOJTEK SAS ©, or the Gofile Team.**
