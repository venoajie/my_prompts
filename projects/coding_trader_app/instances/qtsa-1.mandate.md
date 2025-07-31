---
domain: coding_trader_app
persona_alias: qsa-1
---

<Mandate>
As the Quantitative Strategy Analyst, I need your help to develop a new trading strategy.

My high-level goal is to create a mean-reversion strategy for BTC/USDT on the 1-hour timeframe. I want to "buy the dip" and "sell the rip" when the market is moving sideways.

My available data inputs are: open, high, low, close, volume, and real-time order book snapshots.

Please begin by following your operational protocol. Start with Step 1 to help me frame the strategic goal more precisely.
</Mandate>


### **The Two-Persona Workflow: A Best Practice**

The process of turning a strategy idea into production code should be a clear handoff between two of your expert agents:

1.  **`QSA-1` (The Designer):** Its sole job is to produce a platform-agnostic `StrategyBlueprint` document. This artifact is its final output.
2.  **`CSA-1` (The Implementer):** Its job is to take the `StrategyBlueprint` as input and translate it into production-quality Python code that is perfectly integrated with your existing architecture.

Here is the detailed breakdown of this workflow.

#### **Step 1: `QSA-1` Creates the Blueprint**

After you complete an interactive session with the `QSA-1` persona, its final output (as per its Step 5) will be a structured Markdown file. This file becomes a new artifact in your `knowledge_base`.

**Example Artifact: `knowledge_base/strategies/mean_reversion_v1.md`**
```markdown
# Strategy Blueprint: Mean Reversion V1

**Metadata:**
- **Strategy ID:** MR-V1
- **Author:** QSA-1
- **Target Market:** BTC/USDT (1-hour timeframe)
- **Market Condition:** Range-bound / Sideways

---
**Indicators Used:**
- **Bollinger Bands:** Period=20, Standard Deviations=2
- **Relative Strength Index (RSI):** Period=14

---
**Entry Logic (Long):**
```pseudocode
IF (Price crosses BELOW the Lower Bollinger Band) 
AND (RSI is BELOW 30)
THEN ENTER LONG
```

**Entry Logic (Short):**
```pseudocode
IF (Price crosses ABOVE the Upper Bollinger Band) 
AND (RSI is ABOVE 70)
THEN ENTER SHORT
```

---
**Exit Logic:**
- **Take Profit (Long):** Price touches the middle Bollinger Band (20-period SMA).
- **Take Profit (Short):** Price touches the middle Bollinger Band (20-period SMA).
- **Stop Loss:** A hard stop is placed 1.5 * Average True Range (ATR-14) from the entry price.

---
**Risk Management:**
- **Position Sizing:** Fixed 1.5% of account equity risked per trade.
- **Max Concurrent Positions:** 1
```

This document is perfectly clear, but it contains zero Python code. It is pure logic.

#### **Step 2: `CSA-1` Implements the Blueprint**

Now, you activate your **Collaborative Systems Architect (CSA-1)**, whose expertise is writing code that fits your architecture. You give it the `StrategyBlueprint` as its primary input.

Here is the instance prompt you would use for this handoff:

```markdown
---
domain: coding_trader_app
persona_alias: csa-1
---

<Mandate>
As the Collaborative Systems Architect, your task is to implement the trading strategy defined in the provided `StrategyBlueprint`.

Your implementation must adhere to our existing application architecture.
- Use the data models defined in `MODELS_PY_SOURCE_BASIC`.
- Leverage the centralized constants from `CONSTANTS_PY_SOURCE`.
- The final output should be a new Python file that can be loaded by our `StrategyEngine`.

First, state your implementation plan as per your operational protocol, then await my confirmation before generating the code.
</Mandate>

<h3>Strategy Definition:</h3>
<Inject src="strategies/mean_reversion_v1.md" />

<h3>Architectural Context:</h3>
<Inject src="src/shared/models.py" />
<Inject src="src/shared/config/constants.py" />
```

### **Why This Workflow is Superior**

This two-persona approach is more robust and effective for several reasons:

1.  **Architectural Awareness is Placed Correctly:** The `CSA-1` is the agent that is aware of your architecture. By providing it with your existing `models.py` and `constants.py`, you give it the necessary context to write code that "fits in" perfectly, preventing it from inventing new data structures or hardcoding values.
2.  **Enforces Modularity:** The strategy logic (`StrategyBlueprint`) remains a clean, independent module. You can give this same blueprint to another developer, or even a different AI persona, and they could implement it in a different programming language without ambiguity.
3.  **Reduces Errors:** This process separates the "what" from the "how." `QSA-1` focuses on creating logically sound trading rules. `CSA-1` focuses on writing clean, efficient, and well-integrated code. This division of labor reduces the cognitive load on each agent, leading to higher-quality output at each step.
4.  **Creates an Audit Trail:** You now have a clear, auditable link between a formal strategy document and the code that implements it. If a strategy underperforms, you can go back to the blueprint to see if the flaw was in the original logic or in its implementation.

By using this workflow, you leverage the specialized strengths of each persona to create a system that is both strategically sound and architecturally robust.