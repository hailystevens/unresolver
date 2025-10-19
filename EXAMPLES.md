# Unresolver Examples

This document provides practical examples of using Unresolver to find broken links in HTML files.

## Example 1: Quick Check

Check all HTML files in the current directory:

```bash
python3 unresolver.py .
```

**Output:**
```
======================================================================
Link Check Results
======================================================================
Files checked: 2
Total links: 17
Broken links: 6
======================================================================

📄 test/test.html
   ❌ Broken links: 6
      Line 10: <link href="css/missing.css">
      → Local file not found
      Line 19: <a href="missing.html">
      → Local file not found
```

## Example 2: Check Without External URLs

Skip external URL checking for faster results:

```bash
python3 unresolver.py --no-external ./docs
```

This is useful when you only want to verify local file references.

## Example 3: Detailed Report with Valid Links

Show both broken and valid links:

```bash
python3 unresolver.py --show-valid index.html
```

**Output:**
```
📄 index.html
   ❌ Broken links: 2
      Line 15: <a href="missing.html">
      → Local file not found
   ✓ Valid links: 5
      Line 8: <link href="css/styles.css">
      Line 16: <a href="about.html">
```

## Example 4: JSON Output for CI/CD

Generate JSON output for automated processing:

```bash
python3 unresolver.py --json . > link-report.json
```

**Output (link-report.json):**
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
      },
      {
        "tag": "link",
        "attr": "href",
        "url": "styles.css",
        "line": 8,
        "status": "valid",
        "reason": "Local file exists"
      }
    ]
  }
]
```

## Example 5: Custom Timeout for External URLs

Set a longer timeout for slow external sites:

```bash
python3 unresolver.py --timeout 10 ./website
```

## Example 6: CI/CD Integration

Use in a CI/CD pipeline to fail builds on broken links:

```bash
#!/bin/bash
python3 unresolver.py --no-external ./public
if [ $? -ne 0 ]; then
  echo "Found broken links! Build failed."
  exit 1
fi
echo "All links are valid!"
```

## Example 7: Using the Web Interface

Start the web server and view results in your browser:

```bash
python3 server.py
```

Then open http://localhost:8000/index.html to see the interactive interface.

## Tag Coverage

Unresolver checks all these HTML tags:

| Tag | Attribute | Example |
|-----|-----------|---------|
| `<a>` | `href` | `<a href="page.html">Link</a>` |
| `<link>` | `href` | `<link href="style.css" rel="stylesheet">` |
| `<img>` | `src` | `<img src="logo.png" alt="Logo">` |
| `<script>` | `src` | `<script src="app.js"></script>` |
| `<iframe>` | `src` | `<iframe src="embed.html"></iframe>` |
| `<area>` | `href` | `<area href="target.html" shape="rect">` |

## Special Cases Handled

Unresolver intelligently handles:

- **Fragments**: `#section` - Skipped (page anchors)
- **mailto**: `mailto:test@example.com` - Skipped
- **tel**: `tel:+1234567890` - Skipped
- **javascript**: `javascript:void(0)` - Skipped
- **data URIs**: `data:image/png;base64,...` - Skipped
- **Relative paths**: `../images/logo.png` - Resolved correctly
- **Absolute paths**: `/assets/style.css` - Resolved from base

## Tips

1. **Fast Checks**: Use `--no-external` to skip slow external URL checks
2. **Detailed Reports**: Use `--show-valid` to see what's working
3. **Automation**: Use `--json` for machine-readable output
4. **Exit Codes**: The script returns 1 if broken links are found, 0 otherwise
5. **Performance**: External URLs are cached, so checking the same URL multiple times is fast
