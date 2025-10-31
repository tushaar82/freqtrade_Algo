<!--
SYNC IMPACT REPORT
==================
Version Change: [INITIAL] → 1.0.0
Modified Principles: N/A (initial constitution)
Added Sections: 9 core principles + Governance
Removed Sections: N/A
Templates Requiring Updates:
  ✅ plan-template.md - Constitution Check section updated with all 9 principles and validation gates
  ✅ spec-template.md - Added Risk Management Requirements and Testing & Validation Requirements sections
  ✅ tasks-template.md - Added Phase N+1: Trading System Validation with constitution-mandated gates
  N/A checklist-template.md - No updates required (feature-specific checklist generation)
  N/A agent-file-template.md - No updates required (agent guidance file)
Follow-up TODOs: None
-->

# VELOX Algorithmic Trading System Constitution

## Core Principles

### I. Regulatory Compliance & Risk Management

**MUST** adhere to all SEBI (Securities and Exchange Board of India) regulations including:
- Proper risk disclosures in all user-facing components
- Margin requirement validation before order placement
- Trading restriction enforcement (circuit breakers, position limits, banned securities)
- Audit trail maintenance for regulatory review

**MUST** implement multi-layered kill switches:
- Per-strategy emergency stops (hardware-enforced, not software checks)
- Per-account position limits with automatic enforcement
- Overall portfolio-level circuit breakers
- Daily loss limits with automatic trading suspension

**MUST** perform pre-trade risk validation for every order:
- Sufficient margin availability check
- Position limit compliance verification
- Price band and circuit breaker level validation
- Regulatory restriction checks (T2T stocks, GSM list, etc.)

**Rationale**: Non-compliance results in penalties, trading bans, or legal action. Capital preservation through risk management is non-negotiable in live trading environments.

---

### II. System Architecture & Reliability

**MUST** eliminate single points of failure:
- Multiple internet connections (primary + backup ISPs)
- Redundant servers with automatic failover
- Alternative broker API integrations (minimum 2 brokers)
- Backup power supply and hardware redundancy

**MUST** optimize for latency when required:
- Co-location near NSE/MCX data centers for HFT strategies
- Efficient protocols (FIX, binary APIs) over REST where applicable
- Minimize network hops and optimize code paths
- Profile and eliminate bottlenecks ruthlessly

**MUST** ensure data integrity:
- Continuous order and position reconciliation across all brokers
- Checksum validation for all API responses
- Complete audit trails with immutable logging
- Automated detection of discrepancies with immediate alerts

**Rationale**: Trading system downtime or data corruption can result in catastrophic losses. Every microsecond matters in competitive markets.

---

### III. Market Data & Order Management

**MUST** use tick-by-tick live data:
- Never rely on snapshot or delayed data for entry/exit decisions
- Subscribe to live tick streams from NSE/MCX
- Handle corporate actions (splits, bonuses, dividends) correctly
- Maintain data quality monitoring and gap detection

**MUST** track complete order lifecycle:
- Every state transition: pending → submitted → acknowledged → filled → rejected → cancelled
- Precise timestamps (microsecond accuracy) for all events
- Correct handling of partial fills, amendments, and GTT orders
- Order state reconciliation with broker confirmations

**MUST** maintain clock synchronization:
- NTP sync with NSE time servers (mandatory)
- Sub-second accuracy requirements
- Timestamp validation to prevent order rejections
- Monitoring for clock drift with automatic correction

**Rationale**: Inaccurate market data or order tracking leads to incorrect strategy decisions and potential losses. Timestamp mismatches cause order rejections.

---

### IV. Multi-Broker Architecture

**MUST** implement broker abstraction layer:
- Unified API normalizing differences across brokers (Zerodha, ICICI Direct, Upstox, etc.)
- Handle broker-specific quirks: rate limits, order types, response formats
- Consistent error handling and retry logic
- Broker capability detection and adaptation

**MUST** maintain independent position tracking:
- Internal position calculator independent of broker-provided data
- Reconciliation with broker positions every few seconds
- Discrepancy detection and alerting
- Fallback to internal calculations during broker API issues

**MUST** support broker failover:
- Instant order routing to backup brokers during API outages
- Session management across multiple brokers
- Automatic broker health monitoring
- Zero manual intervention for failover during market hours

**Rationale**: Broker API outages are common. Dependency on a single broker creates unacceptable risk during live trading.

---

### V. Strategy Development & Backtesting

**MUST** perform realistic backtesting:
- Include all costs: slippage, impact cost, STT, GST, exchange fees, broker commissions
- Use actual tick data, not just OHLC bars
- Model order rejection scenarios and fill probability
- Account for market microstructure (bid-ask spreads, order book depth)

**MUST** require paper trading validation:
- Minimum 30 days paper trading in live market conditions
- Performance metrics must match backtested expectations (within tolerance)
- All edge cases and error scenarios must be observed
- No real capital deployment without successful paper trading

**MUST** prevent overfitting:
- Walk-forward optimization (never optimize on future data)
- Out-of-sample testing with rolling windows
- Separate training, validation, and test datasets
- Regular strategy degradation monitoring

**Rationale**: Unrealistic backtests lead to false confidence. Paper trading reveals real-world issues before risking capital.

---

### VI. Monitoring & Alerting

**MUST** provide real-time dashboards:
- P&L tracking (realized, unrealized, intraday, overall)
- Position monitoring across all instruments and brokers
- Order flow visualization and execution quality metrics
- System health: API response times, network latency, CPU/memory usage
- Strategy performance with second-level granularity

**MUST** implement multi-channel critical alerts:
- SMS for position limit breaches and system failures
- Email for daily summaries and non-critical issues
- Telegram/WhatsApp for real-time trading alerts
- Phone calls for catastrophic failures (margin shortfall, runaway losses)

**MUST** enable automated emergency responses:
- Automatic position squaring on margin shortfall
- Trading suspension on daily loss limit breach
- Strategy pause on unusual P&L movements
- Broker failover without human intervention

**Rationale**: Human monitoring is insufficient during fast-moving markets. Automated responses prevent small issues from becoming disasters.

---

### VII. Capital Preservation Over Profit Maximization

**MUST** implement conservative position sizing:
- Position size calculation based on volatility and stop-loss
- No overleveraging or margin maximization
- Compound slowly rather than seeking outsized returns

**MUST** enforce loss limits:
- Daily loss limits (e.g., Rs.5000/-) with automatic trading suspension
- Weekly and monthly loss limits
- Drawdown-based position size reduction
- Mandatory trading pause after limit breach until review

**MUST** detect market regime changes:
- Volatility monitoring with automatic position size adjustment
- Liquidity detection (reduce size in illiquid conditions)
- Strategy assumption validation (pause when assumptions break)
- Correlation breakdown detection across instruments

**Rationale**: Preservation of capital is paramount. A single catastrophic loss can eliminate months of gains. Surviving to trade another day is the priority.

---

### VIII. Code Quality & Testing

**MUST** maintain comprehensive test coverage:
- Unit tests for all components: order management, risk checks, strategy logic
- Edge case testing: network failures, partial fills, broker rejections
- Integration tests for broker API interactions
- Chaos engineering: simulate failures regularly

**MUST** implement chaos engineering practices:
- Regular simulation of broker API failures
- Network outage testing
- Bad data injection and handling validation
- Disaster recovery drills

**MUST** enforce deployment discipline:
- Never deploy untested code to production
- Staged rollouts (paper trading → small capital → full deployment)
- Instant rollback capability
- Version control with tagged releases
- Change logs and deployment documentation

**Rationale**: Trading system bugs can cause immediate financial losses. Rigorous testing and deployment discipline are non-negotiable.

---

### IX. Performance Metrics & Analysis

**MUST** track risk-adjusted returns:
- Sharpe ratio (return per unit of risk)
- Maximum drawdown and recovery time
- Win rate and profit factor
- Calmar ratio and Sortino ratio
- Risk-adjusted returns, not just absolute P&L

**MUST** monitor strategy degradation:
- Live performance vs. backtested expectations
- Statistical significance of performance deviation
- Market microstructure change detection
- Strategy parameter drift monitoring

**MUST** analyze transaction costs:
- Break-even win rate calculation given cost structure
- Slippage analysis and optimization
- Impact cost measurement
- Broker comparison and cost optimization
- High-frequency strategies require >50% win rate after costs

**Rationale**: Profitability without risk adjustment is meaningless. Markets evolve constantly; strategies must be monitored for degradation.

---

## Governance

This constitution supersedes all other development practices and trading policies. All code, strategies, and operational procedures MUST comply with these principles.

**Amendment Process**:
- Amendments require documented justification with risk analysis
- Major changes (new principles, removal of safeguards) require MAJOR version bump
- Minor additions or clarifications require MINOR version bump
- Typos and non-semantic changes require PATCH version bump
- All amendments must include migration plan for existing systems

**Compliance Verification**:
- All code reviews MUST verify compliance with constitution principles
- Pre-deployment checklist MUST validate all risk management requirements
- Monthly compliance audits for live trading systems
- Violations must be documented and remediated immediately

**Risk Management Override**:
- Principles I (Regulatory Compliance), II (Reliability), and VII (Capital Preservation) CANNOT be compromised
- Any complexity or technical debt MUST be justified against these principles
- When in doubt, choose the safer, more conservative approach

**Version**: 1.0.0 | **Ratified**: 2025-10-31 | **Last Amended**: 2025-10-31
