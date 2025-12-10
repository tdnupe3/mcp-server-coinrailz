# Coin Railz MCP Server

<!-- mcp-name: io.github.tdnupe3/coinrailz -->

[![PyPI version](https://badge.fury.io/py/coinrailz-mcp.svg)](https://pypi.org/project/coinrailz-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that exposes **38 Coin Railz x402 micropayment services** to Claude and other LLMs. Access blockchain data, trading signals, prediction markets, stock/forex sentiment, and crypto analytics directly from Claude.

## What is MCP?

MCP (Model Context Protocol) is Anthropic's open standard for connecting AI models to external tools and data sources. This server lets Claude access real-time blockchain and crypto data through Coin Railz's x402 payment infrastructure.

## Features

- **38 Crypto Tools for Claude**: Complete coverage of blockchain analytics, trading, DeFi, and traditional markets
- **First-Call Free**: `gas-price-oracle` and `token-metadata` are FREE for first-time users
- **API Key Authentication**: Simple prepaid credits system - no blockchain knowledge required
- **x402 Protocol Support**: Native USDC payments on Base chain for crypto-native agents
- **10 Service Categories**: From trading intelligence to traditional markets sentiment

## Quick Start

### Installation

```bash
# Using pip
pip install coinrailz-mcp

# Or from source
git clone https://github.com/coinrailz/mcp-server-coinrailz.git
cd mcp-server-coinrailz
pip install -e .
```

### Configure Claude Desktop

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "coinrailz": {
      "command": "python",
      "args": ["-m", "coinrailz_mcp"],
      "env": {
        "COINRAILZ_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Get an API Key

1. Visit https://coinrailz.com/credits
2. Purchase credits with Stripe (credit card) or USDC
3. Generate an API key
4. Set the `COINRAILZ_API_KEY` environment variable

**Free Trial**: `gas-price-oracle` and `token-metadata` are FREE for your first call!

## Available Tools (38)

### Category 1: Discovery & Testing (1)
| Tool | Description | Price |
|------|-------------|-------|
| `ping_coinrailz` | Test platform connectivity | $0.25 |

### Category 2: Trading Intelligence (14)
| Tool | Description | Price |
|------|-------------|-------|
| `get_gas_prices` | Real-time gas across 6 chains | $0.10 (FREE first) |
| `get_token_metadata` | Token name, symbol, decimals | $0.10 (FREE first) |
| `get_token_price` | Real-time DEX prices | $0.15 |
| `get_token_sentiment` | AI social sentiment | $0.25 |
| `get_trending_tokens` | Trending by volume | $0.50 |
| `get_whale_alerts` | Large transaction alerts | $0.35 |
| `get_dex_liquidity` | DEX liquidity depth | $0.20 |
| `get_trade_signals` | AI trading signals | $0.75 |
| `get_trading_signal` | Symbol-specific signals | $0.50 |
| `get_sentiment_analysis` | Multi-source sentiment | $0.30 |
| `get_arbitrage_opportunities` | Cross-chain arb scanner | $1.00 |
| `get_correlation_matrix` | Token correlations | $0.50 |
| `get_risk_metrics` | Volatility, VaR, drawdown | $0.40 |
| `get_batch_quote` | Multi-token quotes | $0.25 |

### Category 3: Execution & Infrastructure (4)
| Tool | Description | Price |
|------|-------------|-------|
| `get_multi_chain_balance` | Wallet balances across chains | $0.50 |
| `build_transaction` | Build unsigned transactions | $0.15 |
| `manage_approvals` | Token approval manager | $0.30 |
| `bridge_tokens` | Cross-chain bridge quotes | $0.50 |

### Category 4: Premium Services (4)
| Tool | Description | Price |
|------|-------------|-------|
| `scan_smart_contract` | Contract security audit | $2.00 |
| `get_wallet_risk_score` | Wallet risk analysis | $0.50 |
| `track_portfolio` | Portfolio analytics | $0.75 |
| `optimize_portfolio` | AI portfolio optimization | $1.00 |

### Category 5: Real Estate (3)
| Tool | Description | Price |
|------|-------------|-------|
| `get_property_valuation` | AI property valuation | $5.00 |
| `analyze_lease` | Lease term analysis | $3.00 |
| `track_construction_progress` | Construction tracking | $2.00 |

### Category 6: Banking/Finance (3)
| Tool | Description | Price |
|------|-------------|-------|
| `get_credit_risk_score` | Credit risk assessment | $2.00 |
| `detect_fraud` | AI fraud detection | $0.50 |
| `run_compliance_check` | AML/KYC checks | $1.00 |

### Category 7: Prediction Markets (4)
| Tool | Description | Price |
|------|-------------|-------|
| `get_polymarket_events` | Active prediction markets | $0.25 |
| `get_polymarket_odds` | Event odds | $0.15 |
| `search_polymarket` | Search events | $0.20 |
| `get_prediction_market_odds` | Aggregated odds | $0.50 |

### Category 8: AI Agent Infrastructure (3)
| Tool | Description | Price |
|------|-------------|-------|
| `create_agent_wallet` | Create managed agent wallet | $1.00 |
| `create_instant_agent_wallet` | Instant temp wallet | $0.50 |
| `verify_agent_identity` | ERC-8004 identity NFT | $2.00 |

### Category 9: Enterprise Services (3)
| Tool | Description | Price |
|------|-------------|-------|
| `request_smart_contract_audit` | Full security audit | $1000 |
| `request_payment_processing` | Merchant payment setup | $50/hr |
| `request_compliance_consultation` | AML/KYC consulting | $500 |

### Category 10: Traditional Markets (2) - NEW!
| Tool | Description | Price |
|------|-------------|-------|
| `get_stock_sentiment` | AI stock market sentiment (AAPL, TSLA, etc.) | $0.40 |
| `get_forex_sentiment` | AI forex pair sentiment (EURUSD, GBPJPY, etc.) | $0.40 |

## Example Usage in Claude

After configuring the MCP server, try asking Claude:

- "What are the current gas prices on Ethereum and Base?"
- "Get the wallet balance for 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
- "Analyze the risk score for this wallet address"
- "What are the trending tokens on Base right now?"
- "Get trading signals for ETH"
- "Search Polymarket for Bitcoin events"
- "Scan this smart contract for vulnerabilities: 0x..."

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `COINRAILZ_API_KEY` | Your API key from coinrailz.com/credits | Recommended |
| `COINRAILZ_BASE_URL` | Override base URL (default: https://coinrailz.com) | No |

## Pricing

Credits are deducted per service call:
- Most services: $0.10 - $1.00
- Premium services: $2.00 - $5.00  
- Enterprise services: $50 - $1000

Purchase credits at https://coinrailz.com/credits

## Supported Blockchains

- Ethereum
- Base
- Polygon
- BNB Chain (BSC)
- Arbitrum
- Optimism
- PulseChain

## Contributing

Contributions welcome! Please open an issue or submit a PR.

## Support

- Documentation: https://coinrailz.com/developers
- Issues: https://github.com/coinrailz/mcp-server-coinrailz/issues
- Email: support@coinrailz.com

## License

MIT License - see LICENSE file
