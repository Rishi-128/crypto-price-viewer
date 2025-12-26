import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime
import time
import os


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_KEY = os.getenv("COINGECKO_API_KEY", "") or st.secrets.get("COINGECKO_API_KEY", "")



st.set_page_config(
    page_title="Crypto Price Viewer",
    page_icon="🪙",
    layout="wide"
)

COINS = {
    "Bitcoin": {"id": "bitcoin", "symbol": "BTC", "icon": "₿", "color": "#F7931A"},
    "Ethereum": {"id": "ethereum", "symbol": "ETH", "icon": "Ξ", "color": "#627EEA"},
    "Tether": {"id": "tether", "symbol": "USDT", "icon": "💵", "color": "#26A17B"},
    "XRP": {"id": "ripple", "symbol": "XRP", "icon": "✕", "color": "#00AAE4"},
    "BNB": {"id": "binancecoin", "symbol": "BNB", "icon": "🔶", "color": "#F3BA2F"},
    "Solana": {"id": "solana", "symbol": "SOL", "icon": "◎", "color": "#9945FF"},
    "USD Coin": {"id": "usd-coin", "symbol": "USDC", "icon": "💲", "color": "#2775CA"},
    "Cardano": {"id": "cardano", "symbol": "ADA", "icon": "🔵", "color": "#0033AD"},
    "Dogecoin": {"id": "dogecoin", "symbol": "DOGE", "icon": "🐕", "color": "#C2A633"},
    "TRON": {"id": "tron", "symbol": "TRX", "icon": "⚡", "color": "#FF0013"}
}

st.markdown("""
    <style>
    /* Main price display */
    .big-price {
        font-size: 52px;
        font-weight: 700;
        background: linear-gradient(90deg, #f7931a, #ffab40);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 10px 0;
    }
    
    /* Price change colors */
    .price-up {
        color: #00c853;
        font-size: 18px;
        font-weight: 600;
    }
    .price-down {
        color: #ff5252;
        font-size: 18px;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    .coin-card {
         width: 100%;
        text-align: left;
        padding: 12px 16px;
        margin: 4px 0;
        border-radius: 10px;
        border: none;
        border-left: 4px solid #444;
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        color: white;
        font-weight: 500;
        transition: all 0.2s;
       
    }
    .coin-card:hover {
        transform: translateX(5px);
    }
    .coin-name {
        font-size: 14px;
        font-weight: 600;
        color: #ffffff;
    }
    .coin-symbol {
        font-size: 12px;
        color: #888;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 20px 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Coin buttons - green hover effect */
    div[data-testid="stButton"] > button:not([kind="primary"]) {
        width: 100%;
        text-align: left;
        padding: 12px 16px;
        margi   n: 4px 0;
        border-radius: 10px;
        border: none;
        border-left: 4px solid transparent;
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        color: white;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    div[data-testid="stButton"] > button:not([kind="primary"]):hover {
        transform: translateX(5px);
        border-left: 4px solid #00c853;
        background: linear-gradient(90deg, rgba(0, 200, 83, 0.15) 0%, transparent 50%, #2d2d44 100%);
        box-shadow: 0 0 15px rgba(0, 200, 83, 0.2);
    }
    
    /* Refresh button - neutral default, red on hover */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%) !important;
        border: none !important;
        border-left: 4px solid transparent !important;
        color: white !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateX(5px);
        border-left: 4px solid #ff5252 !important;
        background: linear-gradient(90deg, rgba(255, 82, 82, 0.2) 0%, transparent 50%, #2d2d44 100%) !important;
        box-shadow: 0 0 15px rgba(255, 82, 82, 0.3);
    }
    </style>
""", unsafe_allow_html=True)


st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("🪙 Crypto Price Viewer")
st.caption("Real-time cryptocurrency prices powered by CoinGecko")
st.markdown('</div>', unsafe_allow_html=True)

if 'selected_coin' not in st.session_state:
    st.session_state.selected_coin = "Bitcoin"

with st.sidebar:
    st.markdown("## 🎯 Select Coin")
    st.caption("Click any coin below to view its data")
    
    st.markdown("---")
  
    for coin_name, coin_info in COINS.items():
        is_selected = coin_name == st.session_state.selected_coin
        
        # Create button with custom styling
        if is_selected:
            button_label = f"{coin_info['icon']} {coin_name} ({coin_info['symbol']}) ✓"
        else:
            button_label = f"{coin_info['icon']} {coin_name} ({coin_info['symbol']})"
        
        if st.button(button_label, key=f"btn_{coin_name}", use_container_width=True):
            st.session_state.selected_coin = coin_name
            st.rerun()
    
    st.markdown("---")
  
   
    if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    st.caption("Data updates every 30 seconds")


selected_coin_name = st.session_state.selected_coin
selected_coin = COINS[selected_coin_name]

st.session_state.api_key = API_KEY

@st.cache_data(ttl=30)  
def get_coin_price(coin_id, api_key=""):
    
    if api_key:
        url = "https://api.coingecko.com/api/v3/simple/price"
        headers = {"x-cg-demo-api-key": api_key}
    else:
        url = "https://api.coingecko.com/api/v3/simple/price"
        headers = {}
    
    params = {
        "ids": coin_id,
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_last_updated_at": "true",
        "include_market_cap": "true",
        "include_24hr_vol": "true"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None


@st.cache_data(ttl=120)  # Cache for 2 minutes
def get_weekly_data(coin_id, api_key=""):
    
    if api_key:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        headers = {"x-cg-demo-api-key": api_key}
    else:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        headers = {}
    
    params = {
        "vs_currency": "u  sd",
        "days": "7",
        "interval": "daily"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None

st.markdown(f"## {selected_coin['icon']} {selected_coin_name} ({selected_coin['symbol']})")


col1, col2, col3 = st.columns([2, 2, 1])

price_data = get_coin_price(selected_coin["id"], st.session_state.api_key)

if price_data:
    coin_info = price_data.get(selected_coin["id"], {})
    current_price = coin_info.get("usd", 0)
    price_change_24h = coin_info.get("usd_24h_change", 0) or 0
    last_updated = coin_info.get("last_updated_at", 0)
    market_cap = coin_info.get("usd_market_cap", 0) or 0
    volume_24h = coin_info.get("usd_24h_vol", 0) or 0
    
    with col1:
        st.subheader("💰 Current Price")
        st.markdown(f'<p class="big-price">${current_price:,.2f}</p>', unsafe_allow_html=True)
        
       
        change_class = "price-up" if price_change_24h >= 0 else "price-down"
        change_symbol = "▲" if price_change_24h >= 0 else "▼"
        st.markdown(
            f'<span class="{change_class}">{change_symbol} {abs(price_change_24h):.2f}% (24h)</span>',
            unsafe_allow_html=True
        )
        
  
        if last_updated:
            update_time = datetime.fromtimestamp(last_updated)
            st.caption(f"🕐 Updated: {update_time.strftime('%H:%M:%S')}")

    with col2:
        st.subheader("📊 Market Stats")
        st.metric(
            label="💎 Market Cap",
            value=f"${market_cap/1e9:.2f}B" if market_cap >= 1e9 else f"${market_cap/1e6:.2f}M"
        )
        st.metric(
            label="📈 24h Volume",
            value=f"${volume_24h/1e9:.2f}B" if volume_24h >= 1e9 else f"${volume_24h/1e6:.2f}M"
        )

    with col3:
        st.subheader("⚡ Quick View")
        st.metric(
            label=selected_coin["symbol"],
            value=f"${current_price:,.2f}",
            delta=f"{price_change_24h:.2f}%"
        )
else:
    st.warning("⏳ Loading data... If this persists, add your FREE API key in the sidebar for better reliability.")


st.markdown("---")
st.subheader(f"📈 {selected_coin['symbol']} Weekly Price Trend")

weekly_data = get_weekly_data(selected_coin["id"], st.session_state.api_key)

if weekly_data:
    prices = weekly_data.get("prices", [])
    
    if prices:
     
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
        
      
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date"],
            y=df["price"],
            mode='lines+markers',
            name=selected_coin["symbol"],
            line=dict(color=selected_coin["color"], width=3, shape='spline'),
            marker=dict(size=8, color=selected_coin["color"]),
            fill='tozeroy',
            fillcolor=f'rgba{tuple(list(bytes.fromhex(selected_coin["color"][1:])) + [0.1])}',
            hovertemplate='%{x|%b %d}<br><b>$%{y:,.2f}</b><extra></extra>'
        ))
        
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Price (USD)",
            hovermode='x unified',
            template="plotly_dark",
            height=400,
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0),
            yaxis=dict(tickprefix="$", tickformat=",.0f", gridcolor='rgba(128,128,128,0.2)'),
            xaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
       
        st.markdown("### 📊 Weekly Statistics")
        col3, col4, col5, col6 = st.columns(4)
        
        week_high = df["price"].max()
        week_low = df["price"].min()
        week_change = ((df["price"].iloc[-1] - df["price"].iloc[0]) / df["price"].iloc[0]) * 100
        week_avg = df["price"].mean()
        
        with col3:
            st.metric("🔺 Week High", f"${week_high:,.2f}")
        
        with col4:
            st.metric("🔻 Week Low", f"${week_low:,.2f}")
        
        with col5:
            st.metric("📊 Week Change", f"{week_change:+.2f}%")
        
        with col6:
            st.metric("📈 Week Avg", f"${week_avg:,.2f}")
        
    
        with st.expander("📋 View Price History"):
            display_df = df.copy()
            display_df = display_df.sort_values("date", ascending=False)  # Most recent first
            display_df["Price"] = display_df["price"].apply(lambda x: f"${x:,.2f}")
            display_df["Date"] = display_df["date"].dt.strftime("%b %d, %Y %H:%M")
            st.dataframe(display_df[["Date", "Price"]], use_container_width=True, hide_index=True, height=300)
else:
    st.info("⏳ Loading chart data...")


time.sleep(60)
st.rerun()
