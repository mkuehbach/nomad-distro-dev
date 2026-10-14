import os, re, secrets, subprocess, sys

def main():
    args = os.environ.get("POE_EXTRA_ARGS", "").strip()
    command = args.split() if args else []

    if command == ["setup"]:
        import yaml

        if os.path.exists(".env.north"):
            print(".env.north already exists, leaving it as is")
            sys.exit(0)

        with open("nomad.yaml") as f:
            config = yaml.safe_load(f) or {}

        keycloak = config.get("keycloak", {})
        north = config.get("north", {})
        services = config.get("services", {})

        server_url = keycloak.get(
            "server_url",
            "https://nomad-lab.eu/fairdi/keycloak/auth",
        )
        keycloak_url = re.sub(r"/auth/?$", "", server_url)

        hub_port = north.get("hub_port", 9000)
        base_path = services.get("api_base_path", "/nomad-oasis")

        with open(".env.north", "w") as fp:
            lines = [
                f'KEYCLOAK_URL="{keycloak_url}"',
                f'KEYCLOAK_REALM="{keycloak.get("realm_name", "fairdi_nomad_prod")}"',
                f'OAUTH_CLIENT_ID="nomad_public"',
                f'OAUTH_CLIENT_SECRET=""',
                f'OAUTH_CALLBACK_URL="http://localhost:{hub_port}{base_path}/north/hub/oauth_callback"',
                f'SERVICE_API_TOKEN="secret-token"',
                f'JUPYTERHUB_CRYPT_KEY="{secrets.token_hex(32)}"',
            ]
            fp.write("\n".join(lines) + "\n")
        print("Created .env.north")
    elif command == ["start"]:
        subprocess.run(["docker", "compose", "up", "north"], check=True)
    else:
        sys.exit("Usage: uv run poe north setup|start")
