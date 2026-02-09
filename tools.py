import subprocess
from agno.tools import tool


# ------- CLI Tools -------

@tool
def echo(text: str, args: str = "") -> str:
    """Output text to stdout, optionally piping through other commands.

    Executes: echo {text} {args}

    Args:
        text (str): The text to output.
        args (str): Additional arguments or pipe commands (e.g., "| grep pattern", "| base64").

    Returns:
        str: The echoed text or processed output.
    """
    command = f"echo {text} {args}"
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return f"Error running echo:\n{result.stderr.strip()}"
        return result.stdout.strip()
    except Exception as e:
        return f"Error running echo: {str(e)}"


@tool
def pipe(command: str) -> str:
    """Execute a piped shell command.

    Executes: {command}

    Args:
        command (str): The full command with pipes (e.g., "cat file.txt | grep pattern | sort -u").

    Returns:
        str: Command output.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            return f"Error running command:\n{result.stderr.strip()}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 300 seconds"
    except Exception as e:
        return f"Error running command: {str(e)}"


@tool
def list_dir(path: str, args: str = "") -> str:
    """List the contents of a directory.

    Args:
        path (str): The directory path to list.
        args (str): Additional ls flags (e.g., "-la", "-lh").

    Returns:
        str: Directory listing output.
    """
    command = f"ls {path} {args}"
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return f"Error listing directory:\n{result.stderr.strip()}"
        return result.stdout.strip()
    except Exception as e:
        return f"Error running ls: {str(e)}"


@tool
def cat_file(file_path: str, args: str = "") -> str:
    """Display the contents of a file, optionally piping through other commands.

    Args:
        file_path (str): The path to the file to read.
        args (str): Additional arguments or pipe commands (e.g., "| grep pattern", "| jq .data").

    Returns:
        str: File contents or processed output.
    """
    command = f"cat {file_path} {args}"
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return f"Error reading file:\n{result.stderr.strip()}"
        return result.stdout.strip()
    except Exception as e:
        return f"Error running cat: {str(e)}"


@tool
def pwd_command() -> str:
    """Retrieve the current working directory.

    Returns:
        str: The current working directory path.
    """
    try:
        result = subprocess.run(
            "pwd",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return f"Error running pwd:\n{result.stderr.strip()}"
        return result.stdout.strip()
    except Exception as e:
        return f"Error running pwd: {str(e)}"


@tool
def find_file(file_path: str, args: str = "") -> str:
    """Find files in the filesystem.

    Args:
        file_path (str): The starting directory path for the search.
        args (str): Additional find arguments (e.g., "-name '*.json'", "-type f").

    Returns:
        str: List of matching file paths.
    """
    command = f"find {file_path} {args}"
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return f"Error running find:\n{result.stderr.strip()}"
        return result.stdout.strip()
    except Exception as e:
        return f"Error running find: {str(e)}"


# ---- ASNMap Tool -----

@tool(show_result = True)
def asnmap(target: str, args: str = "") -> str:
    """Map domains, organizations, or IPs to their ASN and IP ranges.

    Executes: echo {target} | asnmap -json -silent

    Args:
        target (str): The domain, organization name, IP address, or ASN to lookup.
        args (str): Additional asnmap flags (e.g., "-org" for org lookup, "-d" for domain, "-i" for IP, "-a" for ASN expansion).

    Returns:
        str: JSON output containing ASN information and CIDR blocks.
    """
    command = f"echo {target} | asnmap  -silent"
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=200
        )
        if result.returncode != 0:
            return f"Error running asnmap:\n{result.stderr.strip()}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: asnmap timed out after 200 seconds"
    except Exception as e:
        return f"Error running asnmap: {str(e)}"


# ---- BBOT Tool -----

@tool
def bbot(target: str, extra_args: str = "") -> str:
    """Run BBOT for recursive subdomain enumeration and attack surface discovery.

    Executes: bbot -t {target} -p subdomain-enum 

    Args:
        target (str): The target domain to enumerate (e.g., "example.com").
        extra_args (str): Additional bbot arguments. (eg. "-p subdomain enum" )

    Returns:
        str: BBOT scan output. Full results are saved to ~/.bbot/scans/<scan_name>/.
    """
    command = f"bbot -t {target} -p subdomain-enum {extra_args}"
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            input="\n",  # Auto-press enter to start scan
            timeout=200
        )
        if result.returncode != 0:
            return f"Error running bbot:\n{result.stderr.strip()}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: bbot scan timed out after 600 seconds"
    except Exception as e:
        return f"Error running bbot: {str(e)}"


# ----- HTTPX Tool -------

@tool(
        show_result=True,
        instructions="pass results from the subdomain enumeration here. Use the command cat {file_path} | httpx -sc -title -tech-detect -t {threads} ")
def httpx(
    file_path: str,
    status_code: bool = True,
    title: bool = True,
    tech_detect: bool = True,
    follow_redirects: bool = False,
    match_codes: str = "",
    filter_codes: str = "",
    threads: int = 50,
    timeout: int = 300,
    extra_args: str = ""
) -> str:
    """Probe a list of subdomains/URLs with httpx for live hosts and technology fingerprinting.

    Executes: cat {file_path} | httpx -sc -title -tech-detect 

    Args:
        file_path (str): Path to file containing subdomains/URLs (one per line).
        status_code (bool): Show HTTP status code (e.g., -sc). Default True.
        title (bool): Show page title (e.g., -title). Default True.
        tech_detect (bool): Detect technologies (e.g., -tech-detect). Default True.
        follow_redirects (bool): Follow HTTP redirects (e.g., -fr). Default False.
        match_codes (str): Only show these status codes (e.g., -mc "200,301").
        filter_codes (str): Hide these status codes (e.g., -fc "404,500").
        threads (int): Number of concurrent threads (e.g., -t 50). Default 50.
        timeout (int): Command timeout in seconds. Default 300.
        extra_args (str): Additional httpx arguments.

    Returns:
        str: httpx results showing live hosts with status codes, titles, and technologies.
    """
    args = []
    if status_code:
        args.append("-sc")
    if title:
        args.append("-title")
    if tech_detect:
        args.append("-tech-detect")
    if follow_redirects:
        args.append("-fr")
    if match_codes:
        args.append(f"-mc {match_codes}")
    if filter_codes:
        args.append(f"-fc {filter_codes}")
    args.append(f"-t {threads}")
    if extra_args:
        args.append(extra_args)

    args_str = " ".join(args)
    command = f"cat {file_path} | /snap/bin/httpx {args_str}"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode != 0:
            return f"Error running httpx:\n{result.stderr.strip()}"
        return result.stdout.strip() or "No live hosts found"
    except subprocess.TimeoutExpired:
        return f"Error: httpx probe timed out after {timeout} seconds"
    except Exception as e:
        return f"Error running httpx: {str(e)}"


# ----- Tool Registry -----

OSINT_TOOLS = [
    # System and file operations
    echo,
    pipe,
    list_dir,
    cat_file,
    pwd_command,
    find_file,

    # Network Recon and ASN Enumeration
    asnmap,

    # Web Fingerprinting
    httpx,

    # Subdomain Enumeration & Asset Discovery
    bbot,
]
