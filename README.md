# Unresolver 🔗

A minimal Python script to find broken links in HTML files. Checks `<a href>`, `<link>`, `<img>`, `<script>`, `<iframe>`, and `<area>` tags with minimal dependencies (uses only Python standard library).

## Features

- ✅ **Minimal dependencies** - Uses only Python standard library
- 🔍 **Comprehensive link checking** - Checks all common HTML link tags
- 🌐 **External URL validation** - Verifies external links are reachable
- 📁 **Local file validation** - Ensures local resources exist
- 🎨 **Multiple output formats** - Text and JSON output
- 🖥️ **Serverless web interface** - Standalone HTML file that works offline
- ⚡ **Fast** - Caches external URL checks
- 🎯 **Flexible** - Check single files or entire directories
- 🌍 **Site root support** - Properly resolve absolute URLs with `--site-root`
- 📑 **Configurable index files** - Check directories with custom index filenames
- 🔤 **Fragment decoding** - Decodes URL-encoded fragments for better validation

## Checked Tags

The tool checks links in the following HTML tags:
- `<a href="...">` - Hyperlinks
- `<link href="...">` - Stylesheets and resources
- `<img src="...">` - Images
- `<script src="...">` - JavaScript files
- `<iframe src="...">` - Embedded content
- `<area href="...">` - Image map areas

## Installation

No installation required! Just clone and run:

```bash
git clone https://github.com/hailystevens/unresolver.git
cd unresolver
chmod +x unresolver.py
```

## Usage

### Command Line Interface

**Basic usage:**
```bash
python3 unresolver.py .
```

**Check a single file:**
```bash
python3 unresolver.py index.html
```

**Check a directory:**
```bash
python3 unresolver.py ./docs
```

**Skip external URL checks (faster):**
```bash
python3 unresolver.py --no-external .
```

**Show valid links too:**
```bash
python3 unresolver.py --show-valid .
```

**Output as JSON:**
```bash
python3 unresolver.py --json . > results.json
```

**Custom timeout for external URLs:**
```bash
python3 unresolver.py --timeout 10 .
```

**Specify site root for absolute URLs:**
```bash
python3 unresolver.py --site-root /path/to/site/root .
```

**Custom index filenames:**
```bash
python3 unresolver.py --index-files index.html,default.html,home.html .
```

### Serverless Web Interface

The web interface is now completely serverless! Simply open `index.html` in any web browser:

1. **Open directly:** Double-click `index.html` to open it in your browser
2. **Works offline:** No server or internet connection required (except for checking external URLs)
3. **Upload HTML files:** Use the file upload feature to select HTML files to check
4. **Get instant results:** See broken links, valid links, and warnings immediately

**Features:**
- File upload for checking multiple HTML files
- External URL validation (with internet connection)
- Configurable index filenames
- URL fragment decoding
- No localhost or server required!

**Note:** For checking local file references (relative paths, absolute paths), use the CLI version which has full filesystem access.

## Command Line Options

```
usage: unresolver.py [-h] [--no-external] [--timeout TIMEOUT] [--show-valid] [--json] 
                     [--site-root SITE_ROOT] [--index-files INDEX_FILES] path

Find broken links in HTML files

positional arguments:
  path                     Path to HTML file or directory

optional arguments:
  -h, --help               show this help message and exit
  --no-external            Skip checking external URLs
  --timeout TIMEOUT        Timeout for external URL checks (seconds, default: 5)
  --show-valid             Show valid links in addition to broken ones
  --json                   Output results as JSON
  --site-root SITE_ROOT    Site root directory for resolving absolute URLs (starting with /)
  --index-files INDEX_FILES
                           Comma-separated list of index filenames to check in directories 
                           (default: index.html,index.htm)
```

## Examples

**Example 1: Quick check of current directory**
```bash
python3 unresolver.py .
```

**Example 2: Check documentation folder without external links**
```bash
python3 unresolver.py --no-external ./docs
```

**Example 3: Generate JSON report**
```bash
python3 unresolver.py --json . > link-report.json
```

**Example 4: Comprehensive check with all details**
```bash
python3 unresolver.py --show-valid --timeout 10 .
```

## Output

### Text Output

```
======================================================================
Link Check Results
======================================================================
Files checked: 2
Total links: 15
Broken links: 3
======================================================================

📄 index.html
   ❌ Broken links: 2
      Line 15: <a href="missing.html">
      → Local file not found
      Line 42: <img src="images/404.png">
      → Local file not found

📄 about.html
   ❌ Broken links: 1
      Line 8: <link href="https://example.com/gone.css">
      → External URL not reachable
```

### JSON Output

```json
[
  {
    "file": "index.html",
    "links": [
      {
        "tag": "a",
        "attr": "href",
        "url": "missing.html",
        "line": 15,
        "status": "broken",
        "reason": "Local file not found"
      }
    ]
  }
]
```

## How It Works

1. **HTML Parsing** - Uses Python's built-in `html.parser` to extract links
2. **Link Classification** - Determines if links are local files, external URLs, or special protocols
3. **Local File Checking** - Verifies files exist on the filesystem
4. **External URL Checking** - Makes HTTP requests to verify external links are reachable
5. **Result Reporting** - Outputs findings in text or JSON format

## Special Cases

The tool intelligently handles:
- **Fragments** (`#section`) - Skipped
- **Special protocols** (`mailto:`, `tel:`, `javascript:`) - Skipped
- **Data URIs** (`data:image/png;base64,...`) - Skipped
- **Relative paths** - Resolved relative to the HTML file location
- **Absolute paths** - Resolved from site root (use `--site-root` to specify)
- **Directory URLs** - Automatically checks for index files (`index.html`, `index.htm`, or custom)
- **URL-encoded fragments** - Decoded properly for accurate validation

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Author

Created with ❤️ for finding broken links easily