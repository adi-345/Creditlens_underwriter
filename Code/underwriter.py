import fitz  # PyMuPDF
from groq import Groq
import os
import json

pdf_path = None

def get_financial_context(pdf_path):
    # Safely open the document
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Failed to open PDF: {e}")
        return ""

    targets = {
        "BS": ["balance sheet", "current assets", "total liabilities", "stockholders' equity", "consolidated"],
        "PL": ["statement of operations", "income statement", "total revenues", "gross profit", "net income", "operating expenses", "consolidated"]
    }
    
    found_text = ""
    
    try:
        for name, keys in targets.items():
            best_page = ""
            max_score = 0
            for page in doc:
                text = page.get_text()
                score = sum(1 for k in keys if k.lower() in text.lower())
                
                if score > max_score:
                    max_score = score
                    best_page = text
                
                # CRITICAL: Drop the page from memory so the server doesn't crash
                page = None 
                
            found_text += f"\n--- {name} DATA ---\n" + best_page
    finally:
        # CRITICAL: Close the file so Render doesn't throw a 500 Error
        doc.close()

    print(f"Total characters sent to Groq: {len(found_text)}")    
    return found_text

def process_underwriting(pdf_path):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    raw_text = get_financial_context(pdf_path)
    if not raw_text or len(raw_text) < 1500: 
        return {"Error": "PDF is an image or vector graphic. OCR required. Cannot process."}

    # 1. Ask Groq for ALL the keys needed for a full analysis
    prompt = f"""
    Extract the financial values for the TWO MOST RECENT reporting years found in the text.
    Map the most recent year's data to the "_current" keys, and the older year to the "_previous" keys.    

    STRICT RULES:
    1. Return all values as STRINGS wrapped in quotes (e.g., "5000").
    2. If you must combine two numbers, output them as a single string (e.g., "100 + 50"). NEVER output raw unquoted math.
    3. If a value is not explicitly totaled in the text, find the single most relevant line item.
    4. For Revenue, strictly extract "Total revenues", "Total Revenue", "Total Income", or "Revenue from Operations".
    5. Always extract from the "Consolidated" column if both Standalone and Consolidated exist, to match the Balance Sheet.
    6. If a value is missing, use "null".
    
    Return ONLY a JSON object exactly matching this format:
    {{
      "current_assets_current": "value", 
      "current_liabilities_current": "value",
      "total_equity_current": "value", 
      "total_debt_current": "value",
      "net_profit_current": "value", 
      "revenue_current": "value",
      "revenue_previous": "value"
    }}
    
    
    Text: {raw_text}
    """
    # Removed the [:30000] slice above so the P&L doesn't get chopped off!

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0, 
        seed=42        
    )
    
    d = json.loads(completion.choices[0].message.content)
    print("\n--- RAW AI EXTRACTION ---")
    print(json.dumps(d, indent=2))
    print("-------------------------\n")

    def clean(key): 
        val = d.get(key, 0)
        if val is None: return 0
        try:
            if isinstance(val, str):
                cleaned_val = val.replace(",", "").replace("₹", "").replace("$", "").strip()
                if " " in cleaned_val or "+" in cleaned_val or "-" in cleaned_val:
                    return 0 
                return float(cleaned_val)
            return float(val)
        except: 
            return 0

    # 2. CALCULATIONS
    ca25, cl25 = clean('current_assets_current'), clean('current_liabilities_current')
    rev25, rev24 = clean('revenue_current'), clean('revenue_previous')
    profit25 = clean('net_profit_current')
    debt25, equity25 = clean('total_debt_current'), clean('total_equity_current')

    if ca25 == 0 and cl25 == 0:
        return {"Error": "Failed to find standard Current Assets/Liabilities. Document may be a Bank filing or uses unsupported formatting."}
    if rev25 == 0:
        return {"Error": "Failed to find Revenue data. P&L page may be missing or unreadable."}

    current_ratio = ca25 / cl25 if cl25 > 0 else 0
    profit_margin = (profit25 / rev25 * 100) if rev25 > 0 else 0
    debt_equity = debt25 / equity25 if equity25 > 0 else 0
    rev_growth = ((rev25 - rev24) / rev24 * 100) if rev24 > 0 else 0

    # 3. WEIGHTED RISK ENGINE
    points = 0
    if current_ratio > 1.25: points += 30
    if profit_margin > 8: points += 30
    if debt_equity < 1.0: points += 20
    if rev_growth > 0: points += 20

    risk_level = "LOW" if points >= 70 else "MEDIUM" if points >= 40 else "HIGH"

    return {
        "Verdict": f"{risk_level} RISK",
        "Confidence_Score": f"{points}/100",
        "GST_Reconciliation": "Unchecked",
        "Extracted_Data": {
            "Current_Assets": ca25,
            "Current_Liabilities": cl25,
            "Total_Equity": equity25,
            "Total_Debt": debt25,
            "Net_Profit": profit25,
            "Revenue_Current": rev25,
            "Revenue_Previous": rev24
        },
        "Analysis": {
            "Liquidity": f"Current Ratio of {round(current_ratio, 2)}",
            "Profitability": f"Margin of {round(profit_margin, 1)}%",
            "Leverage": f"D/E Ratio of {round(debt_equity, 2)}",
            "Growth": f"Revenue Growth of {round(rev_growth, 1)}%"
        }
    }

if __name__ == "__main__":
    if pdf_path:
        print(process_underwriting(pdf_path))
    else:
        print("No test PDF path provided. Run this via the FastAPI server.")