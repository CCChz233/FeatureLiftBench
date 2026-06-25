# Task Design: vibe_app__plugin_registry_core__001

Status: oracle-verified

## Why This Task

Extract plugin registry and metaclass discovery from VibeShop where legacy utils shortcuts and GLOBAL_STATE class/name bookkeeping obscure canonical registration.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Metaclass | `plugin_registry/metaclass.py` | `test_metaclass_registers_plugin_classes` |
| Registry | `plugin_registry/registry.py` | `test_register_and_run_plugin` (public) |
| Base plugin | `plugin_registry/base.py` | `test_run_raises_for_disabled_plugin` |
