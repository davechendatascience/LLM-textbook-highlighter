#!/usr/bin/env python3
"""
Test script to check MCP connection with ArXiv server
"""

import asyncio
import sys
import traceback

try:
    from mcp import StdioServerParameters
    from mcp.client.stdio import stdio_client
    print("✅ MCP library imported successfully")
except ImportError as e:
    print(f"❌ Failed to import MCP library: {e}")
    sys.exit(1)

async def test_mcp_connection():
    """Test MCP connection to ArXiv server"""
    print("\n🔍 Testing MCP connection...")
    
    try:
        # Create server parameters
        server_params = StdioServerParameters(
            command="uv",
            args=["tool", "run", "arxiv-mcp-server", "--storage-path", "/Users/davidchen/GitHub/mcps/arxiv-mcp-server"],
            env={}
        )
        print("✅ Server parameters created")
        
        # Try to connect
        print("🔄 Attempting to connect to ArXiv MCP server...")
        async with stdio_client(server_params) as (read_stream, write_stream):
            print("✅ Connected to MCP server")
            
            # Create client session
            from mcp import ClientSession
            client = ClientSession(read_stream, write_stream)
            
            # Wait a moment for server initialization
            print("🔄 Waiting for server initialization...")
            await asyncio.sleep(1)
            
            # List available tools
            print("🔄 Listing available tools...")
            tools_result = await client.list_tools()
            print(f"✅ Found {len(tools_result.tools)} tools:")
            for tool in tools_result.tools:
                print(f"   - {tool.name}: {tool.description}")
            
            # Test search_papers tool
            if any(tool.name == "search_papers" for tool in tools_result.tools):
                print("\n🔄 Testing search_papers tool...")
                result = await client.call_tool(
                    "search_papers",
                    {
                        "query": "machine learning",
                        "max_results": 2,
                        "categories": []
                    }
                )
                print(f"✅ Search successful, found {len(result.content)} papers")
                if result.content:
                    print(f"   First paper: {result.content[0].get('title', 'No title')}")
            else:
                print("❌ search_papers tool not found")
                
    except Exception as e:
        print(f"❌ MCP connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()
        return False
    
    return True

async def test_simple_connection():
    """Test a simpler connection approach"""
    print("\n🔍 Testing simple MCP connection...")
    
    try:
        # Try with just the basic command
        server_params = StdioServerParameters(
            command="uv",
            args=["tool", "run", "arxiv-mcp-server"],
            env={}
        )
        
        async with stdio_client(server_params) as (read_stream, write_stream):
            print("✅ Simple connection successful")
            from mcp import ClientSession
            client = ClientSession(read_stream, write_stream)
            tools_result = await client.list_tools()
            print(f"✅ Found {len(tools_result.tools)} tools")
            return True
            
    except Exception as e:
        print(f"❌ Simple connection failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting MCP Connection Test")
    print("=" * 50)
    
    # Test 1: Full connection
    success1 = asyncio.run(test_mcp_connection())
    
    # Test 2: Simple connection
    success2 = asyncio.run(test_simple_connection())
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Full connection: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Simple connection: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 or success2:
        print("\n🎉 MCP connection is working!")
    else:
        print("\n⚠️  MCP connection failed, will use fallback mode")

if __name__ == "__main__":
    main()
