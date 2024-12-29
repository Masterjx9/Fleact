
# Global registry for components
component_registry = {}

def register_component(component):
    """
    Register a component in the global registry by its fleact-id.
    """
    component_registry[component.fleact_id] = component

def find_element_by_fleact_id(fleact_id):
    """
    Retrieve a component by its fleact-id.
    """
    print(fleact_id)
    print(fleact_id)
    print(fleact_id)
    print(fleact_id)
    print(fleact_id)
    print(fleact_id)
    print(fleact_id)
    print(fleact_id)
    print(fleact_id)
    print(fleact_id)
    print(fleact_id)
    print(fleact_id)
    return component_registry.get(fleact_id)
