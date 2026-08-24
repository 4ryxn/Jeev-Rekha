"""Validate non-secret production configuration before a release."""

from app.core.config import get_settings


def main() -> None:
    settings = get_settings()
    print(
        "Production configuration is valid: "
        f"environment={settings.app_env}, "
        f"cors_origins={len(settings.cors_origin_list)}, "
        f"trusted_hosts={len(settings.trusted_host_list)}, "
        f"demo_seed_enabled={settings.demo_seed_enabled}."
    )


if __name__ == "__main__":
    main()
