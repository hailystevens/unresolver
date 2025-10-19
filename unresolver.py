#!/usr/bin/env python3
"""
Unresolver: A minimal Python script to find broken links in HTML files.
Checks <a href>, <link>, <img>, <script>, <iframe>, and <area> tags.
Uses only standard library for minimal dependencies.
"""

import argparse
import json
import os
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import socket


class LinkExtractor(HTMLParser):
    """Extract links from HTML content."""
    
    # Tags and their link attributes to check
    LINK_TAGS = {
        'a': 'href',
        'link': 'href',
        'img': 'src',
        'script': 'src',
        'iframe': 'src',
        'area': 'href',
    }
    
    def __init__(self):
        super().__init__()
        self.links = []
        
    def handle_starttag(self, tag, attrs):
        """Extract links from relevant tags."""
        if tag in self.LINK_TAGS:
            attr_name = self.LINK_TAGS[tag]
            attrs_dict = dict(attrs)
            if attr_name in attrs_dict:
                link = attrs_dict[attr_name]
                if link:  # Ignore empty links
                    self.links.append({
                        'tag': tag,
                        'attr': attr_name,
                        'url': link,
                        'line': self.getpos()[0]
                    })


class LinkChecker:
    """Check if links are valid."""
    
    def __init__(self, timeout=5, check_external=True):
        self.timeout = timeout
        self.check_external = check_external
        self.checked_urls = {}  # Cache for external URLs
        
    def is_external(self, url):
        """Check if URL is external."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    
    def is_special_protocol(self, url):
        """Check if URL uses special protocol (mailto, tel, etc.)."""
        parsed = urlparse(url)
        special_protocols = ['mailto', 'tel', 'javascript', 'data', '#']
        return parsed.scheme in special_protocols or url.startswith('#')
    
    def check_local_file(self, url, base_path):
        """Check if local file exists."""
        # Remove query string and fragment
        url_path = urlparse(url).path
        
        # Handle absolute vs relative paths
        if url_path.startswith('/'):
            # Absolute path from web root - treat as relative to parent directory
            # This works for most common scenarios where HTML files are in a subdirectory
            file_path = Path(base_path).parent / url_path.lstrip('/')
        else:
            # Relative path - resolve relative to the HTML file's directory
            file_path = Path(base_path).parent / url_path
            
        return file_path.exists()
    
    def check_external_url(self, url):
        """Check if external URL is reachable."""
        if url in self.checked_urls:
            return self.checked_urls[url]
        
        try:
            # Create request with user agent to avoid blocks
            req = Request(url, headers={'User-Agent': 'Unresolver/1.0'})
            response = urlopen(req, timeout=self.timeout)
            result = response.getcode() < 400
            self.checked_urls[url] = result
            return result
        except (HTTPError, URLError, socket.timeout, OSError, ValueError):
            self.checked_urls[url] = False
            return False
    
    def check_link(self, link_info, file_path):
        """Check if a link is valid."""
        url = link_info['url']
        
        # Skip special protocols
        if self.is_special_protocol(url):
            return {
                'status': 'skipped',
                'reason': 'Special protocol or fragment'
            }
        
        # Check external URLs
        if self.is_external(url):
            if not self.check_external:
                return {
                    'status': 'skipped',
                    'reason': 'External URL check disabled'
                }
            is_valid = self.check_external_url(url)
            return {
                'status': 'valid' if is_valid else 'broken',
                'reason': 'External URL reachable' if is_valid else 'External URL not reachable'
            }
        
        # Check local file
        is_valid = self.check_local_file(url, file_path)
        return {
            'status': 'valid' if is_valid else 'broken',
            'reason': 'Local file exists' if is_valid else 'Local file not found'
        }


def find_html_files(path):
    """Find all HTML files in the given path."""
    path = Path(path)
    if path.is_file():
        if path.suffix.lower() in ['.html', '.htm']:
            return [path]
        return []
    
    html_files = []
    for pattern in ['**/*.html', '**/*.htm']:
        html_files.extend(path.glob(pattern))
    return html_files


def check_file(file_path, checker):
    """Check all links in a single HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return {
            'file': str(file_path),
            'error': f'Failed to read file: {str(e)}',
            'links': []
        }
    
    # Extract links
    parser = LinkExtractor()
    try:
        parser.feed(content)
    except Exception as e:
        return {
            'file': str(file_path),
            'error': f'Failed to parse HTML: {str(e)}',
            'links': []
        }
    
    # Check each link
    results = []
    for link_info in parser.links:
        check_result = checker.check_link(link_info, file_path)
        results.append({
            **link_info,
            **check_result
        })
    
    return {
        'file': str(file_path),
        'links': results
    }


def format_text_output(results, show_valid=False):
    """Format results as text output."""
    output = []
    total_files = len(results)
    total_links = sum(len(r['links']) for r in results)
    total_broken = sum(len([l for l in r['links'] if l['status'] == 'broken']) for r in results)
    
    output.append(f"\n{'='*70}")
    output.append(f"Link Check Results")
    output.append(f"{'='*70}")
    output.append(f"Files checked: {total_files}")
    output.append(f"Total links: {total_links}")
    output.append(f"Broken links: {total_broken}")
    output.append(f"{'='*70}\n")
    
    for result in results:
        if 'error' in result:
            output.append(f"\n❌ {result['file']}")
            output.append(f"   Error: {result['error']}")
            continue
        
        broken_links = [l for l in result['links'] if l['status'] == 'broken']
        if broken_links or show_valid:
            output.append(f"\n📄 {result['file']}")
            
            if broken_links:
                output.append(f"   ❌ Broken links: {len(broken_links)}")
                for link in broken_links:
                    output.append(f"      Line {link['line']}: <{link['tag']} {link['attr']}=\"{link['url']}\">")
                    output.append(f"      → {link['reason']}")
            
            if show_valid:
                valid_links = [l for l in result['links'] if l['status'] == 'valid']
                if valid_links:
                    output.append(f"   ✓ Valid links: {len(valid_links)}")
                    for link in valid_links:
                        output.append(f"      Line {link['line']}: <{link['tag']} {link['attr']}=\"{link['url']}\">")
    
    return '\n'.join(output)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Find broken links in HTML files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s .                      # Check all HTML files in current directory
  %(prog)s index.html             # Check a single file
  %(prog)s --no-external .        # Skip external URL checks
  %(prog)s --json . > results.json  # Output as JSON
        """
    )
    parser.add_argument('path', help='Path to HTML file or directory')
    parser.add_argument('--no-external', action='store_true',
                        help='Skip checking external URLs')
    parser.add_argument('--timeout', type=int, default=5,
                        help='Timeout for external URL checks (seconds, default: 5)')
    parser.add_argument('--show-valid', action='store_true',
                        help='Show valid links in addition to broken ones')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON')
    
    args = parser.parse_args()
    
    # Find HTML files
    html_files = find_html_files(args.path)
    if not html_files:
        print(f"No HTML files found in: {args.path}", file=sys.stderr)
        return 1
    
    # Check links
    checker = LinkChecker(
        timeout=args.timeout,
        check_external=not args.no_external
    )
    
    results = []
    for file_path in html_files:
        result = check_file(file_path, checker)
        results.append(result)
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text_output(results, args.show_valid))
    
    # Return error code if broken links found
    broken_count = sum(len([l for l in r['links'] if l['status'] == 'broken']) for r in results)
    return 1 if broken_count > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
