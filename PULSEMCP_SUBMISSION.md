# PulseMCP Registry Submission Guide

## Overview
This guide documents the submission process for registering `coinrailz-mcp` on the PulseMCP directory - the curated Model Context Protocol server registry.

## Pre-Submission Checklist

- [x] PyPI package published (`coinrailz-mcp v1.0.4`)
- [x] `server.json` validated against MCP schema
- [x] GitHub repository exists with README
- [x] 38 production MCP tools documented
- [x] Uses proper stdio transport
- [x] No security vulnerabilities in code

## server.json Location

The `server.json` file is ready at: `mcp-server-coinrailz/server.json`

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-10-17/server.schema.json",
  "name": "io.github.tdnupe3/coinrailz",
  "description": "38 crypto micropayment services: trading intelligence, DEX analytics, prediction markets, stock/forex sentiment via x402 protocol",
  "repository": {
    "url": "https://github.com/tdnupe3/mcp-server-coinrailz",
    "source": "github"
  },
  "version": "1.0.4",
  "packages": [
    {
      "registryType": "pypi",
      "identifier": "coinrailz-mcp",
      "version": "1.0.4",
      "transport": {
        "type": "stdio"
      },
      "environmentVariables": [
        {
          "description": "Your Coin Railz API key for authenticated access to paid services",
          "isRequired": false,
          "format": "string",
          "isSecret": true,
          "name": "COINRAILZ_API_KEY"
        }
      ]
    }
  ]
}
```

## Submission Steps

### Option 1: PulseMCP Website Submission

1. **Visit PulseMCP**: Go to https://pulsemcp.com/submit
2. **Enter GitHub URL**: `https://github.com/tdnupe3/mcp-server-coinrailz`
3. **Fill Details**:
   - Name: `Coin Railz MCP`
   - Description: `38 crypto micropayment services: trading intelligence, DEX analytics, prediction markets, stock/forex sentiment via x402 protocol on Base Chain`
   - Category: `Finance` or `Cryptocurrency`
   - Package: `pip install coinrailz-mcp`
4. **Submit**: Click submit and wait for review

### Option 2: Official MCP Registry (modelcontextprotocol/servers)

1. **Fork Repository**: https://github.com/modelcontextprotocol/servers
2. **Add Server Entry**: Add to `servers.json`:
   ```json
   {
     "name": "coinrailz",
     "description": "38 crypto micropayment services via x402 protocol",
     "pypi": "coinrailz-mcp"
   }
   ```
3. **Create PR**: Submit pull request with description

## Key Selling Points (for submission descriptions)

- **38 Production MCP Tools**: Comprehensive crypto/DeFi toolkit
- **x402 Protocol Integration**: HTTP 402-based micropayments
- **Multi-Chain Support**: 7 blockchains (Ethereum, Base, Polygon, BSC, Arbitrum, Optimism, PulseChain)
- **Categories Covered**:
  - Trading Intelligence (5 tools)
  - DEX Analytics (5 tools)  
  - Wallet Management (5 tools)
  - Cross-Chain Operations (4 tools)
  - Smart Contract Tools (3 tools)
  - Risk Assessment (4 tools)
  - Real Estate (3 tools)
  - Financial Analytics (3 tools)
  - Prediction Markets (4 tools)
  - Traditional Markets (2 tools)

## Expected Timeline

- **Submission**: Immediate (self-service)
- **PulseMCP Review**: 1-3 days
- **Official MCP Registry**: 1-2 weeks (PR review)
- **Listing Active**: Within 1 week of approval

## Verification After Listing

After listing, verify discoverability:
1. Search for "coinrailz" on PulseMCP
2. Check GitHub stars and traffic
3. Monitor PyPI download stats

## Contact

- **GitHub Issues**: https://github.com/tdnupe3/mcp-server-coinrailz/issues
- **Platform Support**: partners@coinrailz.com

---

**Status**: Ready for submission
**Last Updated**: December 28, 2025
