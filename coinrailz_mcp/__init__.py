#!/usr/bin/env python3
"""
Coin Railz MCP Server - Claude/Anthropic Model Context Protocol Integration

This MCP server exposes ALL 63 Coin Railz x402 micropayment services as tools for Claude.
It enables AI agents running in Claude to access blockchain data, trading signals,
prediction markets, satellite data, IoT sensor feeds, and AI inference through the
Coin Railz payment infrastructure.

Payment Methods:
1. API Key (prepaid credits) - RECOMMENDED: Purchase credits at https://coinrailz.com/credits
2. x402 USDC payments - For blockchain-native agents

Usage:
1. Install: pip install coinrailz-mcp
2. Configure in Claude Desktop config
3. Set COINRAILZ_API_KEY environment variable (or use first-call-free on select services)

QUICK START (No API key needed!):
- gas-price-oracle and token-metadata are FREE
- Run once to auto-get a demo key with $1 trial credits
"""

__version__ = "1.1.0"

import os
import asyncio
import json
import uuid
import hashlib
from typing import Any, Optional, List
from pathlib import Path
import httpx

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("MCP SDK not installed. Run: pip install mcp")
    raise

COINRAILZ_BASE_URL = os.getenv("COINRAILZ_BASE_URL", "https://coinrailz.com")
COINRAILZ_API_KEY = os.getenv("COINRAILZ_API_KEY", "")

FREE_TIER_SERVICES = {"gas-price-oracle", "token-metadata"}

_telemetry_sent = False
_install_id = None

def _get_install_id() -> str:
    """Get or create a persistent install ID for this SDK instance."""
    global _install_id
    if _install_id:
        return _install_id
    
    config_dir = Path.home() / ".coinrailz"
    config_dir.mkdir(exist_ok=True)
    install_file = config_dir / "install_id"
    
    if install_file.exists():
        _install_id = install_file.read_text().strip()
    else:
        _install_id = f"mcp-{uuid.uuid4().hex[:16]}"
        install_file.write_text(_install_id)
    
    return _install_id

async def _send_telemetry(event: str = "usage"):
    """Send anonymous telemetry to help improve the SDK."""
    global _telemetry_sent
    if _telemetry_sent and event == "install":
        return
    
    try:
        install_id = _get_install_id()
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{COINRAILZ_BASE_URL}/api/sdk/telemetry",
                json={
                    "installId": install_id,
                    "sdkType": "python-mcp",
                    "sdkVersion": __version__,
                    "event": event,
                    "environment": {
                        "hasApiKey": bool(COINRAILZ_API_KEY),
                        "baseUrl": COINRAILZ_BASE_URL
                    }
                },
                headers={"User-Agent": f"CoinRailz-MCP-Server/{__version__}"}
            )
        _telemetry_sent = True
    except Exception:
        pass

async def _get_demo_key() -> Optional[str]:
    """Automatically fetch a demo API key with $1 trial credits."""
    try:
        install_id = _get_install_id()
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{COINRAILZ_BASE_URL}/api/sdk/demo-key",
                json={
                    "installId": install_id,
                    "sdkType": "python-mcp"
                },
                headers={"User-Agent": f"CoinRailz-MCP-Server/{__version__}"}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("api_key")
    except Exception:
        pass
    return None

mcp = FastMCP("coinrailz")

async def call_coinrailz_service(
    service: str, 
    payload: dict = None,
    method: str = "POST"
) -> dict:
    """
    Call a Coin Railz x402 service with smart payment handling.
    
    Features:
    - Automatically tries free tier services without API key
    - Auto-fetches demo key if service requires payment
    - Sends anonymous telemetry to improve SDK experience
    """
    global COINRAILZ_API_KEY
    
    await _send_telemetry("usage")
    
    url = f"{COINRAILZ_BASE_URL}/x402/{service}"
    is_free_service = service in FREE_TIER_SERVICES
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": f"CoinRailz-MCP-Server/{__version__}"
    }
    
    api_key = COINRAILZ_API_KEY
    if api_key:
        headers["X-API-KEY"] = api_key
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            if method == "POST":
                response = await client.post(url, json=payload or {}, headers=headers)
            else:
                response = await client.get(url, headers=headers)
            
            if response.status_code == 402:
                data = response.json()
                price = data.get("accepts", [{}])[0].get("maxAmountRequiredUSD", "Unknown")
                
                if not api_key:
                    demo_key = await _get_demo_key()
                    if demo_key:
                        headers["X-API-KEY"] = demo_key
                        if method == "POST":
                            retry_response = await client.post(url, json=payload or {}, headers=headers)
                        else:
                            retry_response = await client.get(url, headers=headers)
                        
                        if retry_response.status_code == 200:
                            result = retry_response.json()
                            result["_sdk_note"] = f"Used auto-fetched demo key. Set COINRAILZ_API_KEY env var to use your own credits."
                            return result
                
                return {
                    "error": "Payment required",
                    "service": service,
                    "price_usd": price,
                    "message": f"This service costs ${price}. You need an API key with credits.",
                    "quick_fix": {
                        "step_1": "Get FREE demo key: Run any free service first (gas-price-oracle, token-metadata)",
                        "step_2": "Or buy credits: https://coinrailz.com/credits ($10 minimum)",
                        "step_3": "Set env var: export COINRAILZ_API_KEY=your_key_here"
                    },
                    "free_services": list(FREE_TIER_SERVICES),
                    "sdk_info": {
                        "get_demo_key": "POST https://coinrailz.com/api/sdk/demo-key with your install ID",
                        "credits_page": "https://coinrailz.com/credits",
                        "documentation": "https://coinrailz.com/docs/sdk"
                    }
                }
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}", "message": str(e)}
        except Exception as e:
            return {"error": "Request failed", "message": str(e)}


# =============================================================================
# CATEGORY 1: DISCOVERY & TESTING (1 service)
# =============================================================================

@mcp.tool()
async def ping_coinrailz(message: str = "Hello from Claude") -> str:
    """
    Test connectivity to Coin Railz x402 payment infrastructure.
    
    Args:
        message: Optional message to include in ping
    
    Returns:
        Platform status, version, and available services count.
    
    Price: $0.25
    """
    result = await call_coinrailz_service("ping", {"message": message})
    return json.dumps(result, indent=2)


# =============================================================================
# CATEGORY 2: TRADING INTELLIGENCE (14 services)
# =============================================================================

@mcp.tool()
async def get_gas_prices(chains: List[str] = None) -> str:
    """
    Get real-time gas prices across multiple blockchain networks.
    
    Args:
        chains: List of chains to query. Options: ethereum, base, polygon, bsc, arbitrum, optimism.
                Defaults to all supported chains.
    
    Returns:
        Gas prices in gwei with USD cost estimates for each chain.
    
    Price: $0.10 (FIRST CALL FREE for new users!)
    """
    payload = {"chains": chains or ["ethereum", "base", "polygon", "arbitrum", "optimism"]}
    result = await call_coinrailz_service("gas-price-oracle", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_token_metadata(token_address: str, chain: str = "ethereum") -> str:
    """
    Get metadata for any ERC-20 token including name, symbol, decimals, and total supply.
    
    Args:
        token_address: The token contract address (0x...)
        chain: Blockchain network. Options: ethereum, base, polygon, bsc, arbitrum, optimism
    
    Returns:
        Token metadata including name, symbol, decimals, total supply.
    
    Price: $0.10 (FIRST CALL FREE for new users!)
    """
    payload = {"tokenAddress": token_address, "chain": chain}
    result = await call_coinrailz_service("token-metadata", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_token_price(token_address: str, chain: str = "ethereum") -> str:
    """
    Get real-time token price from multiple DEX sources.
    
    Args:
        token_address: The token contract address (0x...)
        chain: Blockchain network. Options: ethereum, base, polygon, bsc
    
    Returns:
        Token price in USD with source information.
    
    Price: $0.25
    """
    payload = {"tokenAddress": token_address, "chain": chain}
    result = await call_coinrailz_service("token-price", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_token_sentiment(token_address: str, chain: str = "ethereum") -> str:
    """
    Get AI-powered social sentiment analysis for a token.
    
    Args:
        token_address: The token contract address (0x...)
        chain: Blockchain network
    
    Returns:
        Sentiment score, social volume, and trending topics related to the token.
    
    Price: $0.25
    """
    payload = {"tokenAddress": token_address, "chain": chain}
    result = await call_coinrailz_service("token-sentiment", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_trending_tokens(chain: str = "ethereum", limit: int = 10) -> str:
    """
    Get trending tokens across DeFi platforms.
    
    Args:
        chain: Blockchain network. Options: ethereum, base, polygon, bsc
        limit: Number of tokens to return (max 50)
    
    Returns:
        List of trending tokens with volume, price change, and social metrics.
    
    Price: $0.50
    """
    payload = {"chain": chain, "limit": min(limit, 50)}
    result = await call_coinrailz_service("trending-tokens", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_whale_alerts(chains: List[str] = None, min_value_usd: int = 100000) -> str:
    """
    Get real-time whale transaction alerts across chains.
    
    Args:
        chains: List of chains to monitor. Defaults to all major chains.
        min_value_usd: Minimum transaction value in USD to alert on
    
    Returns:
        Recent large transactions with sender, receiver, and token details.
    
    Price: $0.35
    """
    payload = {
        "chains": chains or ["ethereum", "base", "polygon"],
        "minValueUsd": min_value_usd
    }
    result = await call_coinrailz_service("whale-alerts", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_dex_liquidity(token_address: str, chain: str = "ethereum") -> str:
    """
    Get DEX liquidity analysis for a token across major exchanges.
    
    Args:
        token_address: The token contract address (0x...)
        chain: Blockchain network. Options: ethereum, base, polygon, bsc
    
    Returns:
        Liquidity depth, top pools, and slippage estimates.
    
    Price: $0.20
    """
    payload = {"tokenAddress": token_address, "chain": chain}
    result = await call_coinrailz_service("dex-liquidity", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_trade_signals(token: str = None, chain: str = "ethereum") -> str:
    """
    Get AI-powered trading signals and market recommendations.
    
    Args:
        token: Optional token address or symbol to focus on
        chain: Blockchain network. Options: ethereum, base, polygon
    
    Returns:
        Trading signals with entry/exit recommendations and confidence scores.
    
    Price: $0.75
    """
    payload = {"token": token, "chain": chain} if token else {"chain": chain}
    result = await call_coinrailz_service("trade-signals", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_trading_signal(symbol: str, timeframe: str = "1h") -> str:
    """
    Get trading signal for a specific symbol and timeframe.
    
    Args:
        symbol: Trading pair symbol (e.g., ETH/USDC, BTC/USDT)
        timeframe: Chart timeframe. Options: 1m, 5m, 15m, 1h, 4h, 1d
    
    Returns:
        Buy/sell signal with indicators, confidence, and target prices.
    
    Price: $1.00
    """
    payload = {"symbol": symbol, "timeframe": timeframe}
    result = await call_coinrailz_service("trading-signal", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_sentiment_analysis(query: str, sources: List[str] = None) -> str:
    """
    Get AI-powered sentiment analysis for crypto topics.
    
    Args:
        query: Topic to analyze (token name, project, or keyword)
        sources: List of sources. Options: twitter, reddit, news, telegram
    
    Returns:
        Sentiment score, volume trends, and key narratives.
    
    Price: $0.50
    """
    payload = {
        "query": query,
        "sources": sources or ["twitter", "reddit", "news"]
    }
    result = await call_coinrailz_service("sentiment-analysis", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_arbitrage_opportunities(chains: List[str] = None, min_profit_pct: float = 0.5) -> str:
    """
    Scan for cross-chain arbitrage opportunities.
    
    Args:
        chains: List of chains to scan for arbitrage
        min_profit_pct: Minimum profit percentage to report
    
    Returns:
        List of arbitrage opportunities with routes and expected profit.
    
    Price: $1.25
    """
    payload = {
        "chains": chains or ["ethereum", "base", "polygon", "arbitrum"],
        "minProfitPct": min_profit_pct
    }
    result = await call_coinrailz_service("arbitrage-scanner", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_correlation_matrix(tokens: List[str], timeframe: str = "7d") -> str:
    """
    Get correlation matrix between multiple tokens.
    
    Args:
        tokens: List of token addresses or symbols to analyze
        timeframe: Analysis period. Options: 1d, 7d, 30d, 90d
    
    Returns:
        Correlation coefficients between all token pairs.
    
    Price: $0.75
    """
    payload = {"tokens": tokens, "timeframe": timeframe}
    result = await call_coinrailz_service("correlation-matrix", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_risk_metrics(token_address: str, chain: str = "ethereum") -> str:
    """
    Get comprehensive risk metrics for a token.
    
    Args:
        token_address: The token contract address (0x...)
        chain: Blockchain network
    
    Returns:
        Volatility, VaR, max drawdown, and other risk metrics.
    
    Price: $1.00
    """
    payload = {"tokenAddress": token_address, "chain": chain}
    result = await call_coinrailz_service("risk-metrics", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_batch_quote(tokens: List[str], chain: str = "ethereum") -> str:
    """
    Get quotes for multiple tokens in a single request.
    
    Args:
        tokens: List of token addresses to quote
        chain: Blockchain network
    
    Returns:
        Prices and metadata for all requested tokens.
    
    Price: $0.40
    """
    payload = {"tokens": tokens, "chain": chain}
    result = await call_coinrailz_service("batch-quote", payload)
    return json.dumps(result, indent=2)


# =============================================================================
# CATEGORY 3: EXECUTION & INFRASTRUCTURE (4 services)
# =============================================================================

@mcp.tool()
async def get_multi_chain_balance(wallet_address: str, chains: List[str] = None, include_tokens: bool = True) -> str:
    """
    Get multi-chain wallet balance across 7+ EVM networks.
    
    Args:
        wallet_address: The wallet address to check (0x...)
        chains: List of chains to query. Defaults to all supported chains.
        include_tokens: Whether to include ERC-20 token balances.
    
    Returns:
        Wallet balances for native tokens and ERC-20 tokens across all specified chains.
    
    Price: $0.50
    """
    payload = {
        "walletAddress": wallet_address,
        "chains": chains or ["ethereum", "base", "polygon", "bsc", "arbitrum", "optimism"],
        "includeTokens": include_tokens
    }
    result = await call_coinrailz_service("multi-chain-balance", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def build_transaction(
    from_address: str,
    to_address: str,
    value: str,
    chain: str = "ethereum",
    token_address: str = None
) -> str:
    """
    Build a transaction object ready for signing.
    
    Args:
        from_address: Sender wallet address
        to_address: Recipient wallet address
        value: Amount to send (in token units or wei)
        chain: Blockchain network
        token_address: Optional ERC-20 token address (native token if not provided)
    
    Returns:
        Unsigned transaction object with gas estimates.
    
    Price: $0.30
    """
    payload = {
        "from": from_address,
        "to": to_address,
        "value": value,
        "chain": chain
    }
    if token_address:
        payload["tokenAddress"] = token_address
    result = await call_coinrailz_service("transaction-builder", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def manage_approvals(wallet_address: str, chain: str = "ethereum", action: str = "list") -> str:
    """
    Manage token approvals for a wallet.
    
    Args:
        wallet_address: The wallet address to check
        chain: Blockchain network
        action: Action to perform. Options: list, revoke_risky
    
    Returns:
        List of token approvals with risk assessment.
    
    Price: $0.20
    """
    payload = {
        "walletAddress": wallet_address,
        "chain": chain,
        "action": action
    }
    result = await call_coinrailz_service("approval-manager", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def bridge_tokens(
    from_chain: str,
    to_chain: str,
    token_address: str,
    amount: str,
    recipient: str = None
) -> str:
    """
    Get bridge quote and route for cross-chain token transfer.
    
    Args:
        from_chain: Source blockchain
        to_chain: Destination blockchain
        token_address: Token to bridge
        amount: Amount to bridge
        recipient: Optional different recipient address
    
    Returns:
        Bridge route, fees, and estimated time.
    
    Price: $2.00
    """
    payload = {
        "fromChain": from_chain,
        "toChain": to_chain,
        "tokenAddress": token_address,
        "amount": amount
    }
    if recipient:
        payload["recipient"] = recipient
    result = await call_coinrailz_service("seamless-chain-bridge", payload)
    return json.dumps(result, indent=2)


# =============================================================================
# CATEGORY 4: PREMIUM SERVICES (4 services)
# =============================================================================

@mcp.tool()
async def scan_smart_contract(contract_address: str, chain: str = "ethereum") -> str:
    """
    Perform security analysis on a smart contract.
    
    Args:
        contract_address: The contract address to scan (0x...)
        chain: Blockchain network. Options: ethereum, base, polygon
    
    Returns:
        Security analysis including vulnerabilities, rug pull risk, and audit score.
    
    Price: $1.00
    """
    payload = {"contractAddress": contract_address, "chain": chain}
    result = await call_coinrailz_service("contract-scan", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_wallet_risk_score(wallet_address: str, chain: str = "ethereum") -> str:
    """
    Get risk analysis and security scoring for any wallet address.
    
    Args:
        wallet_address: The wallet address to analyze (0x...)
        chain: Primary chain for analysis. Options: ethereum, base, polygon
    
    Returns:
        Risk score, transaction patterns, and security recommendations.
    
    Price: $0.50
    """
    payload = {"walletAddress": wallet_address, "chain": chain}
    result = await call_coinrailz_service("wallet-risk", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def track_portfolio(wallet_address: str, chains: List[str] = None) -> str:
    """
    Get comprehensive portfolio tracking and analytics.
    
    Args:
        wallet_address: The wallet address to track
        chains: List of chains to include in portfolio
    
    Returns:
        Portfolio value, allocation, P&L, and historical performance.
    
    Price: $0.50
    """
    payload = {
        "walletAddress": wallet_address,
        "chains": chains or ["ethereum", "base", "polygon", "arbitrum"]
    }
    result = await call_coinrailz_service("portfolio-tracker", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def optimize_portfolio(holdings: List[dict], risk_tolerance: str = "medium") -> str:
    """
    Get AI-powered portfolio optimization recommendations.
    
    Args:
        holdings: List of current holdings [{"token": "...", "amount": "...", "chain": "..."}]
        risk_tolerance: Risk level. Options: low, medium, high
    
    Returns:
        Rebalancing recommendations and optimal allocation.
    
    Price: $2.00
    """
    payload = {
        "holdings": holdings,
        "riskTolerance": risk_tolerance
    }
    result = await call_coinrailz_service("portfolio-optimization", payload)
    return json.dumps(result, indent=2)


# =============================================================================
# CATEGORY 5: REAL ESTATE (3 services)
# =============================================================================

@mcp.tool()
async def get_property_valuation(address: str = None, property_id: str = None) -> str:
    """
    Get AI-powered property valuation estimate.
    
    Args:
        address: Property street address
        property_id: Or property ID if known
    
    Returns:
        Estimated value, comparable sales, and market trends.
    
    Price: $0.75
    """
    payload = {}
    if address:
        payload["address"] = address
    if property_id:
        payload["propertyId"] = property_id
    result = await call_coinrailz_service("property-valuation", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def analyze_lease(lease_terms: dict) -> str:
    """
    Analyze commercial lease terms and market comparison.
    
    Args:
        lease_terms: Lease details including rent, term, location, size
    
    Returns:
        Lease analysis with market comparison and recommendations.
    
    Price: $1.00
    """
    result = await call_coinrailz_service("lease-analysis", lease_terms)
    return json.dumps(result, indent=2)

@mcp.tool()
async def track_construction_progress(project_id: str) -> str:
    """
    Track construction project progress and milestones.
    
    Args:
        project_id: The construction project ID
    
    Returns:
        Progress updates, timeline, and budget status.
    
    Price: $1.50
    """
    payload = {"projectId": project_id}
    result = await call_coinrailz_service("construction-progress", payload)
    return json.dumps(result, indent=2)


# =============================================================================
# CATEGORY 6: BANKING/FINANCE (3 services)
# =============================================================================

@mcp.tool()
async def get_credit_risk_score(entity_id: str, entity_type: str = "individual") -> str:
    """
    Get credit risk assessment for individuals or businesses.
    
    Args:
        entity_id: Identifier for the entity (wallet, business ID, etc.)
        entity_type: Type of entity. Options: individual, business, dao
    
    Returns:
        Credit score, risk factors, and lending recommendations.
    
    Price: $1.25
    """
    payload = {"entityId": entity_id, "entityType": entity_type}
    result = await call_coinrailz_service("credit-risk-score", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def detect_fraud(transaction_data: dict) -> str:
    """
    AI-powered fraud detection for transactions.
    
    Args:
        transaction_data: Transaction details to analyze
    
    Returns:
        Fraud score, risk indicators, and recommendations.
    
    Price: $0.75
    """
    result = await call_coinrailz_service("fraud-detection", transaction_data)
    return json.dumps(result, indent=2)

@mcp.tool()
async def run_compliance_check(entity_id: str, check_type: str = "aml") -> str:
    """
    Run AML/KYC compliance checks.
    
    Args:
        entity_id: Identifier for the entity (wallet address, etc.)
        check_type: Type of check. Options: aml, kyc, sanctions, pep
    
    Returns:
        Compliance status, flags, and required actions.
    
    Price: $1.75
    """
    payload = {"entityId": entity_id, "checkType": check_type}
    result = await call_coinrailz_service("compliance-check", payload)
    return json.dumps(result, indent=2)


# =============================================================================
# CATEGORY 7: POLYMARKET PREDICTION MARKETS (4 services)
# =============================================================================

@mcp.tool()
async def get_polymarket_events(category: str = None, limit: int = 20) -> str:
    """
    Get active Polymarket prediction market events.
    
    Args:
        category: Optional category filter (politics, crypto, sports, etc.)
        limit: Number of events to return
    
    Returns:
        List of active prediction markets with current odds.
    
    Price: $0.25
    """
    payload = {"limit": limit}
    if category:
        payload["category"] = category
    result = await call_coinrailz_service("polymarket-events", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_polymarket_odds(event_id: str) -> str:
    """
    Get current odds for a specific Polymarket event.
    
    Args:
        event_id: The Polymarket event ID
    
    Returns:
        Current odds, volume, and price history.
    
    Price: $0.50
    """
    payload = {"eventId": event_id}
    result = await call_coinrailz_service("polymarket-odds", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def search_polymarket(query: str, limit: int = 10) -> str:
    """
    Search Polymarket events by keyword.
    
    Args:
        query: Search query
        limit: Number of results to return
    
    Returns:
        Matching prediction markets with current odds.
    
    Price: $0.25
    """
    payload = {"query": query, "limit": limit}
    result = await call_coinrailz_service("polymarket-search", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_prediction_market_odds(event_id: str = None, query: str = None) -> str:
    """
    Get prediction market odds (aggregated from multiple sources).
    
    Args:
        event_id: Optional specific event ID
        query: Optional search query for events
    
    Returns:
        Current odds, volume, and market details for prediction events.
    
    Price: $0.50
    """
    payload = {}
    if event_id:
        payload["eventId"] = event_id
    if query:
        payload["query"] = query
    result = await call_coinrailz_service("prediction-market-odds", payload)
    return json.dumps(result, indent=2)


# =============================================================================
# CATEGORY 8: AI AGENT INFRASTRUCTURE (3 services)
# =============================================================================

@mcp.tool()
async def create_agent_wallet(agent_name: str, agent_type: str = "trading") -> str:
    """
    Create a new persistent wallet for an AI agent via Coinbase CDP.
    
    Args:
        agent_name: Name identifier for the agent
        agent_type: Type of agent. Options: trading, payment, defi, general
    
    Returns:
        New wallet address and management details.
    
    Price: $2.00
    """
    payload = {"agentName": agent_name, "agentType": agent_type}
    result = await call_coinrailz_service("agent-create-wallet", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def create_instant_agent_wallet(purpose: str = "general") -> str:
    """
    Instantly create a temporary agent wallet for quick operations.
    
    Args:
        purpose: Purpose of the wallet. Options: trading, testing, payment
    
    Returns:
        Temporary wallet address with 24-hour validity.
    
    Price: $1.00
    """
    payload = {"purpose": purpose}
    result = await call_coinrailz_service("instant-agent-wallet", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def verify_agent_identity(agent_address: str, proof: str = None) -> str:
    """
    Verify and register an AI agent's on-chain identity (ERC-8004).
    
    Args:
        agent_address: The agent's wallet address
        proof: Optional identity proof or attestation
    
    Returns:
        Verification status and on-chain identity NFT details.
    
    Price: $5.00
    """
    payload = {"agentAddress": agent_address}
    if proof:
        payload["proof"] = proof
    result = await call_coinrailz_service("verified-agent-identity", payload)
    return json.dumps(result, indent=2)


# =============================================================================
# CATEGORY 9: ENTERPRISE SERVICES (3 services)
# =============================================================================

@mcp.tool()
async def request_smart_contract_audit(contract_address: str, chain: str = "ethereum", scope: str = "full") -> str:
    """
    Request comprehensive smart contract security audit.
    
    Args:
        contract_address: Contract to audit
        chain: Blockchain network
        scope: Audit scope. Options: quick, standard, full
    
    Returns:
        Audit request confirmation and estimated delivery time.
    
    Price: $10.00
    """
    payload = {
        "contractAddress": contract_address,
        "chain": chain,
        "scope": scope
    }
    result = await call_coinrailz_service("smart-contract-audit", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def request_payment_processing(
    merchant_id: str,
    payment_type: str = "one-time",
    currencies: List[str] = None
) -> str:
    """
    Set up multi-chain payment processing for merchants.
    
    Args:
        merchant_id: Merchant identifier
        payment_type: Type of payment. Options: one-time, subscription, escrow
        currencies: Accepted cryptocurrencies
    
    Returns:
        Payment processing setup details and integration instructions.
    
    Price: $0.50
    """
    payload = {
        "merchantId": merchant_id,
        "paymentType": payment_type,
        "currencies": currencies or ["USDC", "ETH", "USDT"]
    }
    result = await call_coinrailz_service("payment-processing", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def request_compliance_consultation(
    entity_type: str,
    jurisdictions: List[str],
    services: List[str]
) -> str:
    """
    Request AML/KYC compliance consultation.
    
    Args:
        entity_type: Type of entity. Options: exchange, defi, nft, payment
        jurisdictions: List of jurisdictions to cover (US, EU, UK, etc.)
        services: Services requiring compliance (custody, trading, payments)
    
    Returns:
        Consultation request confirmation and preliminary assessment.
    
    Price: $5.00
    """
    payload = {
        "entityType": entity_type,
        "jurisdictions": jurisdictions,
        "services": services
    }
    result = await call_coinrailz_service("compliance-consultation", payload)
    return json.dumps(result, indent=2)


# =============================================================================
# CATEGORY 10: TRADITIONAL MARKETS (2 services)
# =============================================================================

@mcp.tool()
async def get_stock_sentiment(
    symbol: str,
    include_news: bool = True,
    include_technicals: bool = True,
    include_institutional: bool = True
) -> str:
    """
    Get AI-powered stock market sentiment analysis.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, TSLA, MSFT, NVDA)
        include_news: Include recent news and headlines analysis
        include_technicals: Include technical analysis and chart patterns
        include_institutional: Include institutional and insider activity
    
    Returns:
        Sentiment analysis with overall rating, confidence score, key drivers, and trading recommendation.
    
    Price: $0.40
    """
    payload = {
        "symbol": symbol.upper(),
        "includeNews": include_news,
        "includeTechnicals": include_technicals,
        "includeInstitutional": include_institutional
    }
    result = await call_coinrailz_service("stock-sentiment", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_forex_sentiment(
    pair: str,
    include_economic: bool = True,
    include_central_bank: bool = True,
    include_geopolitical: bool = True
) -> str:
    """
    Get AI-powered forex currency pair sentiment analysis.
    
    Args:
        pair: Currency pair (e.g., EURUSD, GBPJPY, USDJPY, AUDUSD)
        include_economic: Include economic factors analysis
        include_central_bank: Include central bank policy outlook
        include_geopolitical: Include geopolitical factors
    
    Returns:
        Sentiment analysis with overall rating, confidence score, key drivers, and trading recommendation.
    
    Price: $0.40
    """
    payload = {
        "pair": pair.upper(),
        "includeEconomic": include_economic,
        "includeCentralBank": include_central_bank,
        "includeGeopolitical": include_geopolitical
    }
    result = await call_coinrailz_service("forex-sentiment", payload)
    return json.dumps(result, indent=2)


# =============================================================================
# CATEGORY 11: KALSHI PREDICTION MARKETS (3 services)
# =============================================================================

@mcp.tool()
async def get_kalshi_markets(category: str = None, limit: int = 20) -> str:
    """
    Get active markets from Kalshi, a CFTC-regulated prediction exchange.
    
    Args:
        category: Optional category filter (politics, economics, weather, sports, etc.)
        limit: Number of markets to return
    
    Returns:
        Active Kalshi markets with current odds, volume, and resolution criteria.
    
    Price: $0.25
    """
    payload = {"limit": limit}
    if category:
        payload["category"] = category
    result = await call_coinrailz_service("kalshi-markets", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_kalshi_odds(market_ticker: str) -> str:
    """
    Get current odds and orderbook for a specific Kalshi market.
    
    Args:
        market_ticker: The Kalshi market ticker (e.g., PRES-2024-DJT)
    
    Returns:
        Current yes/no prices, volume, open interest, and order book depth.
    
    Price: $0.25
    """
    payload = {"marketTicker": market_ticker}
    result = await call_coinrailz_service("kalshi-odds", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def search_kalshi(query: str, limit: int = 10) -> str:
    """
    Search Kalshi prediction markets by keyword.
    
    Args:
        query: Search query (e.g., "bitcoin", "fed rate", "election")
        limit: Number of results to return
    
    Returns:
        Matching Kalshi markets with current status and odds.
    
    Price: $0.25
    """
    payload = {"query": query, "limit": limit}
    result = await call_coinrailz_service("kalshi-search", payload)
    return json.dumps(result, indent=2)


# =============================================================================
# CATEGORY 12: SATELLITE & EARTH OBSERVATION (12 services)
# =============================================================================

@mcp.tool()
async def get_fire_alerts(
    latitude: float = None,
    longitude: float = None,
    radius_km: float = 100,
    hours: int = 24
) -> str:
    """
    Get real-time active fire detection data from NASA FIRMS satellites.
    
    Args:
        latitude: Center latitude for area search (-90 to 90)
        longitude: Center longitude for area search (-180 to 180)
        radius_km: Search radius in kilometers
        hours: Look-back period in hours (max 168)
    
    Returns:
        Active fire detections with confidence, FRP (fire radiative power), and coordinates.
    
    Price: $0.15
    """
    payload = {"radiusKm": radius_km, "hours": hours}
    if latitude is not None:
        payload["latitude"] = latitude
    if longitude is not None:
        payload["longitude"] = longitude
    result = await call_coinrailz_service("fire-alerts", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_weather_imagery(
    latitude: float,
    longitude: float,
    layer: str = "GOES_East_ABI_Band13_Clean_Infrared"
) -> str:
    """
    Get high-resolution weather satellite imagery from NASA GIBS.
    
    Args:
        latitude: Center latitude (-90 to 90)
        longitude: Center longitude (-180 to 180)
        layer: Imagery layer. Options: GOES_East_ABI_Band13_Clean_Infrared,
               MODIS_Terra_CorrectedReflectance_TrueColor, VIIRS_SNPP_DayNightBand_ENCC
    
    Returns:
        Satellite imagery tile URL, metadata, and current weather pattern description.
    
    Price: $0.15
    """
    payload = {"latitude": latitude, "longitude": longitude, "layer": layer}
    result = await call_coinrailz_service("weather-imagery", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_vegetation_health(
    latitude: float,
    longitude: float,
    date: str = None
) -> str:
    """
    Get NDVI vegetation health indices from satellite data.
    
    Args:
        latitude: Center latitude (-90 to 90)
        longitude: Center longitude (-180 to 180)
        date: Optional date (YYYY-MM-DD). Defaults to most recent available.
    
    Returns:
        NDVI values, vegetation health classification, and trend vs prior period.
    
    Price: $0.15
    """
    payload = {"latitude": latitude, "longitude": longitude}
    if date:
        payload["date"] = date
    result = await call_coinrailz_service("vegetation", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def detect_floods(
    latitude: float,
    longitude: float,
    date: str = None
) -> str:
    """
    Detect flood extent from ESA Sentinel-1 SAR satellite data.
    
    Args:
        latitude: Center latitude (-90 to 90)
        longitude: Center longitude (-180 to 180)
        date: Optional date (YYYY-MM-DD). Defaults to most recent available.
    
    Returns:
        Flood extent mapping, affected area estimate, and change vs baseline.
    
    Price: $0.25
    """
    payload = {"latitude": latitude, "longitude": longitude}
    if date:
        payload["date"] = date
    result = await call_coinrailz_service("flood-detection", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_air_quality(
    latitude: float,
    longitude: float
) -> str:
    """
    Get atmospheric pollutant concentrations from ESA Sentinel-5P satellite.
    
    Args:
        latitude: Latitude (-90 to 90)
        longitude: Longitude (-180 to 180)
    
    Returns:
        NO2, SO2, CO, O3, and aerosol concentrations with AQI classification.
    
    Price: $0.15
    """
    payload = {"latitude": latitude, "longitude": longitude}
    result = await call_coinrailz_service("air-quality", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_land_use(
    latitude: float,
    longitude: float
) -> str:
    """
    Get land cover classification from ESA WorldCover satellite data.
    
    Args:
        latitude: Latitude (-90 to 90)
        longitude: Longitude (-180 to 180)
    
    Returns:
        Land use classification (cropland, forest, urban, water, etc.) with percentages.
    
    Price: $0.15
    """
    payload = {"latitude": latitude, "longitude": longitude}
    result = await call_coinrailz_service("land-use", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_satellite_earthdata(
    dataset: str,
    latitude: float = None,
    longitude: float = None,
    date: str = None
) -> str:
    """
    NASA Earthdata gateway — access precipitation, SST, soil moisture, and ocean data.
    
    Args:
        dataset: Dataset to query. Options: precipitation, sst, soil_moisture, ocean_color, granules
        latitude: Optional latitude filter (-90 to 90)
        longitude: Optional longitude filter (-180 to 180)
        date: Optional date (YYYY-MM-DD)
    
    Returns:
        NASA satellite data for the requested dataset and location.
    
    Price: $0.25
    """
    payload = {"dataset": dataset}
    if latitude is not None:
        payload["latitude"] = latitude
    if longitude is not None:
        payload["longitude"] = longitude
    if date:
        payload["date"] = date
    result = await call_coinrailz_service("satellite-earthdata", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def search_earthdata_granules(
    short_name: str,
    latitude: float = None,
    longitude: float = None,
    date_start: str = None,
    date_end: str = None,
    limit: int = 10
) -> str:
    """
    Search 1B+ NASA satellite granules in the Earthdata catalog.
    
    Args:
        short_name: Dataset short name (e.g., GPM_3IMERGHH, MODIS_Terra_L2, SMAP_L3)
        latitude: Optional center latitude for spatial filter
        longitude: Optional center longitude for spatial filter
        date_start: Start date (YYYY-MM-DD)
        date_end: End date (YYYY-MM-DD)
        limit: Maximum results to return
    
    Returns:
        Granule metadata including download URLs, coverage, and file sizes.
    
    Price: $0.25
    """
    payload = {"shortName": short_name, "limit": limit}
    if latitude is not None:
        payload["latitude"] = latitude
    if longitude is not None:
        payload["longitude"] = longitude
    if date_start:
        payload["dateStart"] = date_start
    if date_end:
        payload["dateEnd"] = date_end
    result = await call_coinrailz_service("earthdata-granules", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_precipitation_data(
    latitude: float,
    longitude: float,
    date: str = None
) -> str:
    """
    Get real-time observed rain rate and accumulated precipitation from NASA GPM.
    
    Args:
        latitude: Latitude (-90 to 90)
        longitude: Longitude (-180 to 180)
        date: Optional date (YYYY-MM-DD). Defaults to most recent.
    
    Returns:
        Precipitation rate (mm/hr), accumulation, and storm tracking data.
    
    Price: $0.25
    """
    payload = {"latitude": latitude, "longitude": longitude}
    if date:
        payload["date"] = date
    result = await call_coinrailz_service("earthdata-precipitation", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_sea_surface_temperature(
    latitude: float,
    longitude: float,
    date: str = None
) -> str:
    """
    Get sea surface temperature from NASA MODIS satellite data.
    
    Args:
        latitude: Latitude (-90 to 90)
        longitude: Longitude (-180 to 180)
        date: Optional date (YYYY-MM-DD). Defaults to most recent.
    
    Returns:
        SST in Celsius/Fahrenheit, anomaly vs climatological mean, and trend.
    
    Price: $0.25
    """
    payload = {"latitude": latitude, "longitude": longitude}
    if date:
        payload["date"] = date
    result = await call_coinrailz_service("earthdata-sst", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_soil_moisture(
    latitude: float,
    longitude: float,
    date: str = None
) -> str:
    """
    Get soil moisture granule data from NASA SMAP satellite.
    
    Args:
        latitude: Latitude (-90 to 90)
        longitude: Longitude (-180 to 180)
        date: Optional date (YYYY-MM-DD). Defaults to most recent.
    
    Returns:
        Volumetric soil moisture content, freeze/thaw state, and agricultural relevance.
    
    Price: $0.25
    """
    payload = {"latitude": latitude, "longitude": longitude}
    if date:
        payload["date"] = date
    result = await call_coinrailz_service("earthdata-soil-moisture", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_ocean_color(
    latitude: float,
    longitude: float,
    date: str = None
) -> str:
    """
    Get MODIS Aqua ocean chlorophyll-a concentration and water quality data.
    
    Args:
        latitude: Latitude (-90 to 90)
        longitude: Longitude (-180 to 180)
        date: Optional date (YYYY-MM-DD). Defaults to most recent.
    
    Returns:
        Chlorophyll-a concentration (mg/m³), ocean color index, and phytoplankton activity.
    
    Price: $0.25
    """
    payload = {"latitude": latitude, "longitude": longitude}
    if date:
        payload["date"] = date
    result = await call_coinrailz_service("earthdata-ocean-color", payload)
    return json.dumps(result, indent=2)


# =============================================================================
# CATEGORY 13: IoT & DePIN DATA (5 services)
# =============================================================================

@mcp.tool()
async def get_fleet_telematics(
    device_id: str = None,
    fleet_id: str = None,
    limit: int = 10
) -> str:
    """
    Get real-time fleet data: GPS location, fuel, speed, and diagnostics from IoT devices.
    
    Args:
        device_id: Specific device ID to query
        fleet_id: Or query all devices in a fleet
        limit: Maximum number of device records to return
    
    Returns:
        GPS coordinates, speed, fuel level, engine diagnostics, and last-seen timestamp.
    
    Price: $0.10
    """
    payload = {"limit": limit}
    if device_id:
        payload["deviceId"] = device_id
    if fleet_id:
        payload["fleetId"] = fleet_id
    result = await call_coinrailz_service("fleet-telematics", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_weather_station_data(
    station_id: str = None,
    latitude: float = None,
    longitude: float = None,
    radius_km: float = 10
) -> str:
    """
    Get hyperlocal weather data from IoT weather station network.
    
    Args:
        station_id: Specific weather station ID
        latitude: Or find nearest station by coordinates
        longitude: Longitude for nearest-station search
        radius_km: Search radius in kilometers
    
    Returns:
        Temperature, humidity, pressure, wind speed/direction, and precipitation.
    
    Price: $0.10
    """
    payload = {"radiusKm": radius_km}
    if station_id:
        payload["stationId"] = station_id
    if latitude is not None:
        payload["latitude"] = latitude
    if longitude is not None:
        payload["longitude"] = longitude
    result = await call_coinrailz_service("weather-station-data", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def read_iot_sensor(device_id: str, sensor_type: str = "all") -> str:
    """
    Get a single sensor reading from a registered IoT device.
    
    Args:
        device_id: The registered IoT device ID
        sensor_type: Sensor type to read. Options: temperature, humidity, pressure,
                     co2, motion, light, vibration, all
    
    Returns:
        Current sensor value(s) with unit, timestamp, and device metadata.
    
    Price: $0.05
    """
    payload = {"deviceId": device_id, "sensorType": sensor_type}
    result = await call_coinrailz_service("iot-sensor-reading", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def stream_iot_device(device_id: str, duration_seconds: int = 60) -> str:
    """
    Get real-time data stream from an IoT device.
    
    Args:
        device_id: The registered IoT device ID
        duration_seconds: Duration to collect data (max 300 seconds)
    
    Returns:
        Time-series sensor readings for the requested duration.
    
    Price: $0.10
    """
    payload = {"deviceId": device_id, "durationSeconds": min(duration_seconds, 300)}
    result = await call_coinrailz_service("iot-device-stream", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def export_iot_bulk_data(
    device_id: str,
    start_date: str,
    end_date: str,
    format: str = "json"
) -> str:
    """
    Export historical bulk data from an IoT device.
    
    Args:
        device_id: The registered IoT device ID
        start_date: Start date for export (YYYY-MM-DD)
        end_date: End date for export (YYYY-MM-DD)
        format: Export format. Options: json, csv
    
    Returns:
        Historical sensor data export with download URL and record count.
    
    Price: $0.25
    """
    payload = {
        "deviceId": device_id,
        "startDate": start_date,
        "endDate": end_date,
        "format": format
    }
    result = await call_coinrailz_service("iot-bulk-data", payload)
    return json.dumps(result, indent=2)


# =============================================================================
# CATEGORY 14: AI INFERENCE & YIELD (2 services)
# =============================================================================

@mcp.tool()
async def run_ai_inference(
    prompt: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 500,
    system_prompt: str = None
) -> str:
    """
    Pay-per-call GPT-4o-mini inference via x402 USDC micropayments.
    Ideal for agents that need AI capabilities without managing OpenAI API keys.
    
    Args:
        prompt: The user prompt / question
        model: Model to use. Options: gpt-4o-mini, gpt-4o, gpt-4-turbo
        max_tokens: Maximum tokens in response (max 4000)
        system_prompt: Optional system prompt to set context
    
    Returns:
        AI-generated text response with token usage and cost breakdown.
    
    Price: $0.05
    """
    payload = {
        "prompt": prompt,
        "model": model,
        "maxTokens": min(max_tokens, 4000)
    }
    if system_prompt:
        payload["systemPrompt"] = system_prompt
    result = await call_coinrailz_service("ai-inference", payload)
    return json.dumps(result, indent=2)

@mcp.tool()
async def find_solana_yield(
    min_apy: float = 0.0,
    max_risk: str = "medium",
    asset: str = "USDC"
) -> str:
    """
    Get real-time Solana lending and yield opportunities from Kamino and other protocols.
    
    Args:
        min_apy: Minimum APY filter (percentage, e.g., 3.0 for 3%)
        max_risk: Maximum risk level. Options: low, medium, high
        asset: Asset to find yield for. Options: USDC, SOL, USDT, mSOL
    
    Returns:
        Ranked yield opportunities with current APY, TVL, protocol, and risk rating.
    
    Price: $0.25
    """
    payload = {"minApy": min_apy, "maxRisk": max_risk, "asset": asset}
    result = await call_coinrailz_service("solana-yield-finder", payload)
    return json.dumps(result, indent=2)


def main():
    """Run the MCP server (synchronous entry point for CLI)."""
    mcp.run()


if __name__ == "__main__":
    main()
