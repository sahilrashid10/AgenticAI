from langgraph.graph import StateGraph, START, END

from graph.state import CustomerState

from graph.nodes import (
    validate_node,
    validation_error_node,
    exists_node,
    exists_error_node,
    save_node,
    email_node,
    checklist_node,
)


def route_after_validate(state: CustomerState):
    return "exists" if state["valid"] else "validation_error"


def route_after_exists(state: CustomerState):
    return "save" if not state["exists"] else "exists_error"


builder = StateGraph(CustomerState)

builder.add_node("validate", validate_node)
builder.add_node("validation_error", validation_error_node)
builder.add_node("exists", exists_node)
builder.add_node("exists_error", exists_error_node)
builder.add_node("save", save_node)
builder.add_node("email", email_node)
builder.add_node("checklist", checklist_node)

builder.add_edge(START, "validate")

builder.add_conditional_edges(
    "validate",
    route_after_validate,
    {
        "exists": "exists",
        "validation_error": "validation_error",
        END: END,
    },
)
builder.add_conditional_edges(
    "exists",
    route_after_exists,
    {
        "save": "save",
        "exists_error": "exists_error",
        END: END,
    },
)

builder.add_edge("validation_error", END)
builder.add_edge("exists_error", END)
builder.add_edge("save", "email")
builder.add_edge("email", "checklist")
builder.add_edge("checklist", END)

graph = builder.compile()