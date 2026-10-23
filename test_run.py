import json
import tempfile
from pathlib import Path
import subprocess
import requests
import time


def wait_for_server(url, timeout=30, interval=2):
    """Wait for the server to be ready by polling the URL."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            requests.get(url, timeout=5)
            return True
        except requests.ConnectionError:
            time.sleep(interval)
    return False


def test_run():
    cmd = ["docker", "build", "-t", "akretion/boleto_cnab_api", "."]
    result = subprocess.run(
        cmd, check=False, capture_output=True, text=True, cwd=Path(__file__).parent
    )
    assert result.returncode == 0, result.stderr + "\n" + result.stdout

    cmd = [
        "docker",
        "run",
        "-d",
        "-p",
        "9292:9292",
        "--name=boleto_cnab_api",
        "akretion/boleto_cnab_api",
    ]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr + "\n" + result.stdout

    assert wait_for_server("http://localhost:9292"), "Server did not start within 30s"

    boleto_values = [
        {
            "valor": 5.0,
            "cedente": "Kivanio Barbosa",
            "documento_cedente": "12345678912",
            "sacado": "Claudio Pozzebom",
            "sacado_documento": "12345678900",
            "agencia": "0810",
            "conta_corrente": "53678",
            "convenio": 12387,
            "nosso_numero": "12345678",
            "bank": "itau",
        },
        {
            "valor": 10.00,
            "cedente": "PREFEITURA MUNICIPAL DE VILHENA",
            "documento_cedente": "04092706000181",
            "sacado": "João Paulo Barbosa",
            "sacado_documento": "77777777777",
            "agencia": "1825",
            "conta_corrente": "0000528",
            "convenio": "245274",
            "nosso_numero": "000000000000001",
            "bank": "caixa",
        },
    ]
    content = json.dumps(boleto_values)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        file_name = f.name
        f.write(content)
    for template in ("boleto", "carne"):
        with open(file_name, "rb") as data_file:
            result = requests.post(
                "http://localhost:9292/api/boleto/multi",
                data={
                    "type": "pdf",
                    "template": template,
                },
                files={"data": data_file},
            )
        assert result.ok, (
            f"{template}: expected 2xx, got {result.status_code}. Body: {result.text[:500]}"
        )
        assert result.content.startswith(b"%PDF"), f"{template}: response is not a PDF"

    cmd = ["docker", "rm", "-f", "boleto_cnab_api"]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr + "\n" + result.stdout
