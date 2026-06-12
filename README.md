# Coin Railz MCP Server

<!-- mcp-name: io.github.tdnupe3/coinrailz -->

[![PyPI version](https://badge.fury.io/py/coinrailz-mcp.svg)](https://pypi.org/project/coinrailz-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server exposing **63 Coin Railz x402 micropayment services** to Claude and other LLMs. Access blockchain analytics, trading signals, satellite/earth data (NASA & ESA), IoT sensor feeds, AI inference, prediction markets, and more — all paid with USDC credits or native x402 on-chain payments.

## Features

- **63 Tools for Claude**: Complete coverage across 14 service categories
- **First-Call Free**: `gas-price-oracle` and `token-metadata` are FREE for first-time users
- **API Key Authentication**: Simple prepaid credits system — no blockchain knowledge required
- **x402 Protocol Support**: Native USDC micropayments on Base for crypto-native agents
- **Coinbase AgentKit Compatible**: Works with AgentKit MCP Extension out of the box
- **14 Service Categories**: From trading intelligence to NASA satellite data

## Quick Start

### Installation

```bash
pip install coinrailz-mcp
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

## Available Tools (63)

### Category 1: Discovery & Testing (1)
| Tool | Description | Price |
|------|-------------|-------|
| `ping_coinrailz` | Test platform connectivity | $0.25 |

### Category 2: Trading Intelligence (14)
| Tool | Description | Price |
|------|-------------|-------|
| `get_gas_prices` | Real-time gas across 6 chains | $0.10 (FREE first) |
| `get_token_metadata` | Token name, symbol, decimals | $0.10 (FREE first) |
| `get_token_price` | Real-time DEX prices | $0.25 |
| `get_token_sentiment` | AI social sentiment | $0.25 |
| `get_trending_tokens` | Trending by volume | $0.50 |
| `get_whale_alerts` | Large transaction alerts | $0.35 |
| `get_dex_liquidity` | DEX liquidity depth | $0.20 |
| `get_trade_signals` | AI trading signals | $0.75 |
| `get_trading_signal` | Symbol-specific signals | $1.00 |
| `get_sentiment_analysis` | Multi-source sentiment | $0.50 |
| `get_arbitrage_opportunities` | Cross-chain arb scanner | $1.25 |
| `get_correlation_matrix` | Token correlations | $0.75 |
| `get_risk_metrics` | Volatility, VaR, drawdown | $1.00 |
| `get_batch_quote` | Multi-token quotes | $0.40 |

### Category 3: Execution & Infrastructure (4)
| Tool | Description | Price |
|------|-------------|-------|
| `get_multi_chain_balance` | Wallet balances across chains | $0.50 |
| `build_transaction` | Build unsigned transactions | $0.30 |
| `manage_approvals` | Token approval manager | $0.20 |
| `bridge_tokens` | Cross-chain bridge quotes | $2.00 |

### Category 4: Premium Services (4)
| Tool | Description | Price |
|------|-------------|-------|
| `scan_smart_contract` | Contract security scan | $1.00 |
| `get_wallet_risk_score` | Wallet risk analysis | $0.50 |
| `track_portfolio` | Portfolio analytics | $0.50 |
| `optimize_portfolio` | AI portfolio optimization | $2.00 |

### Category 5: Real Estate (3)
| Tool | Description | Price |
|------|-------------|-------|
| `get_property_valuation` | AI property valuation | $0.75 |
| `analyze_lease` | Lease term analysis | $1.00 |
| `track_construction_progress` | Construction tracking | $1.50 |

### Category 6: Banking/Finance (3)
| Tool | Description | Price |
|------|-------------|-------|
| `get_credit_risk_score` | Credit risk assessment | $1.25 |
| `detect_fraud` | AI fraud detection | $0.75 |
| `run_compliance_check` | AML/KYC checks | $1.75 |

### Category 7: Polymarket Prediction Markets (4)
| Tool | Description | Price |
|------|-------------|-------|
| `get_polymarket_events` | Active prediction markets | $0.25 |
| `get_polymarket_odds` | Event odds | $0.50 |
| `search_polymarket` | Search events | $0.25 |
| `get_prediction_market_odds` | Aggregated odds | $0.50 |

### Category 8: AI Agent Infrastructure (3)
| Tool | Description | Price |
|------|-------------|-------|
| `create_agent_wallet` | Create Coinbase CDP agent wallet | $2.00 |
| `create_instant_agent_wallet` | Instant temp wallet | $1.00 |
| `verify_agent_identity` | ERC-8004 on-chain identity | $5.00 |

### Category 9: Enterprise Services (3)
| Tool | Description | Price |
|------|-------------|-------|
| `request_smart_contract_audit` | Full security audit | $10.00 |
| `request_payment_processing` | Merchant payment setup | $0.50 |
| `request_compliance_consultation` | AML/KYC consulting | $5.00 |

### Category 10: Traditional Markets (2)
| Tool | Description | Price |
|------|-------------|-------|
| `get_stock_sentiment` | AI stock market sentiment (AAPL, TSLA, etc.) | $0.40 |
| `get_forex_sentiment` | AI forex pair sentiment (EURUSD, GBPJPY, etc.) | $0.40 |

### Category 11: Kalshi Prediction Markets (3)
| Tool | Description | Price |
|------|-------------|-------|
| `get_kalshi_markets` | Active CFTC-regulated markets | $0.25 |
| `get_kalshi_odds` | Market odds and orderbook | $0.25 |
| `search_kalshi` | Search markets by keyword | $0.25 |

### Category 12: Satellite & Earth Observation (12) — NEW
| Tool | Description | Price |
|------|-------------|-------|
| `get_fire_alerts` | NASA FIRMS real-time fire detection | $0.15 |
| `get_weather_imagery` | NASA GIBS satellite weather imagery | $0.15 |
| `get_vegetation_health` | NDVI vegetation health (satellite) | $0.15 |
| `detect_floods` | ESA Sentinel-1 SAR flood mapping | $0.25 |
| `get_air_quality` | ESA Sentinel-5P atmospheric pollutants | $0.15 |
| `get_land_use` | ESA WorldCover land classification | $0.15 |
| `get_satellite_earthdata` | NASA Earthdata gateway | $0.25 |
| `search_earthdata_granules` | Search 1B+ NASA satellite granules | $0.25 |
| `get_precipitation_data` | NASA GPM rain rate data | $0.25 |
| `get_sea_surface_temperature` | NASA MODIS sea surface temp | $0.25 |
| `get_soil_moisture` | NASA SMAP soil moisture | $0.25 |
| `get_ocean_color` | MODIS Aqua chlorophyll-a | $0.25 |

### Category 13: IoT & DePIN Data (5) — NEW
| Tool | Description | Price |
|------|-------------|-------|
| `get_fleet_telematics` | GPS, fuel, speed from fleet devices | $0.10 |
| `get_weather_station_data` | Hyperlocal IoT weather data | $0.10 |
| `read_iot_sensor` | Single IoT sensor reading | $0.05 |
| `stream_iot_device` | Real-time IoT device stream | $0.10 |
| `export_iot_bulk_data` | Historical IoT data export | $0.25 |

### Category 14: AI Inference & Yield (2) — NEW
| Tool | Description | Price |
|------|-------------|-------|
| `run_ai_inference` | Pay-per-call GPT-4o-mini via USDC | $0.05 |
| `find_solana_yield` | Solana yield opportunities (Kamino) | $0.25 |

## Example Usage in Claude

After configuring the MCP server, try asking Claude:

- "What are the current gas prices on Ethereum and Base?"
- "Get the wallet balance for 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
- "Are there any active wildfires within 100km of 37.7749° N, 122.4194° W?"
- "What is the current sea surface temperature near the Maldives?"
- "Get soil moisture data for latitude 41.8, longitude -87.6"
- "What are the trending tokens on Base right now?"
- "Get trading signals for ETH"
- "Search Polymarket for Bitcoin events"
- "Scan this smart contract for vulnerabilities: 0x..."
- "Run AI inference: summarize the latest DeFi news"
- "Find the best USDC yield on Solana right now"

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `COINRAILZ_API_KEY` | Your API key from coinrailz.com/credits | Recommended |
| `COINRAILZ_BASE_URL` | Override base URL (default: https://coinrailz.com) | No |

## Pricing

Credits are deducted per service call:
- IoT sensors: $0.05
- Most data services: $0.10 - $0.50
- Analytics & AI: $0.50 - $2.00
- Enterprise services: $5.00 - $10.00

Purchase credits at https://coinrailz.com/credits

## Supported Blockchains

- Ethereum
- Base (Coinbase L2)
- Polygon
- BNB Chain (BSC)
- Arbitrum
- Optimism
- Solana

## Contributing

Contributions welcome! Please open an issue or submit a PR.

## Support

- Documentation: https://coinrailz.com/developers
- Issues: https://github.com/tdnupe3/mcp-server-coinrailz/issues
- Email: support@coinrailz.com

## License

MIT License - see LICENSE file
