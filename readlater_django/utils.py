import logging
import os


def load_env(env, default=None, enforce=True):
    """Load value from environment or raise exception/use default."""
    if not enforce:
        value = os.environ.get(env, default)
    else:
        if default is not None:
            logging.warning(f'Default {default} ignored for env {env}'
                            'since enforce=True.')
        value = os.environ.get(env, None)
        if value is None:
            raise ValueError(f'Env {env} not set!')
    return value
