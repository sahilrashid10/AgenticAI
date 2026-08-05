from fastmcp import FastMCP

mcp = FastMCP("Procurement Server")

APPROVED_VENDORS = [
    "Dell",
    "HP",
    "Lenovo",
]

@mcp.tool()
def get_approved_vendors():

    return APPROVED_VENDORS

if __name__ == "__main__":
    mcp.run()