from fastmcp import FastMCP

mcp = FastMCP("Procurement MCP Server")


@mcp.tool
def get_company_policy(policy: str | None = None):
    # my data base is this return statement
    return {
        "laptop_limit": 10,
        "software_limit": 5000,
        "approved_vendors": [
            "Dell",
            "HP",
            "Lenovo"
        ]
    }


if __name__ == "__main__":
    mcp.run()