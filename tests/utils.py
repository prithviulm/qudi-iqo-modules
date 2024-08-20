def add_modules(module_manager, config):
    for base in ['logic', 'hardware']:
        for module_name, module_cfg in list(config[base].items()):
            module_manager.add_module(module_name, base, module_cfg, allow_overwrite=False, emit_change=True )
    return module_manager