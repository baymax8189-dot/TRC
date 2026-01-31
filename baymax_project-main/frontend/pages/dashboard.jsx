import { useEffect, useState } from 'react';

export default function Dashboard() {
  const [stocks, setStocks] = useState([]);
  const [stats, setStats] = useState(null);
  const [gainers, setGainers] = useState([]);
  const [momentum, setMomentum] = useState([]);
  const [breakouts, setBreakouts] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [loading, setLoading] = useState(true);
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://chartlink-api.onrender.com';

  const fetchData = async () => {
    try {
      setLoading(true);
      const [latestRes, statsRes, gainersRes, momentumRes, breakoutsRes] = await Promise.all([
        fetch(`${API_URL}/api/dashboard/latest`),
        fetch(`${API_URL}/api/dashboard/stats`),
        fetch(`${API_URL}/api/analytics/top-gainers`),
        fetch(`${API_URL}/api/analytics/momentum`),
        fetch(`${API_URL}/api/analytics/breakouts`)
      ]);

      if (latestRes.ok) setStocks(await latestRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
      if (gainersRes.ok) setGainers(await gainersRes.json());
      if (momentumRes.ok) setMomentum(await momentumRes.json());
      if (breakoutsRes.ok) setBreakouts(await breakoutsRes.json());
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Load data immediately and auto-refresh every 5 minutes
  useEffect(() => {
    fetchData(); // Initial load
    const interval = setInterval(fetchData, 300000); // Auto-refresh every 5 min
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial', background: '#f5f5f5', minHeight: '100vh' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ margin: 0 }}>📊 Stock Screener Dashboard</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '12px', color: '#666' }}>🔴 LIVE</span>
          <button 
            onClick={fetchData}
            style={{
              padding: '10px 20px',
              background: '#333',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            🔄 Refresh Now
          </button>
        </div>
      </div>
      <p style={{ color: '#666' }}>
        Last loaded: {lastUpdate?.toLocaleTimeString() || 'Loading...'} 
        <br/>
        <small>✓ Auto-refreshes every 5 minutes | Data pulled every 1 minute</small>
      </p>

      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginBottom: '20px' }}>
          <div style={{ background: 'white', padding: '15px', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <strong>Total Symbols</strong><br/><span style={{ fontSize: '24px', color: '#333' }}>{stats.total_symbols}</span>
          </div>
          <div style={{ background: 'white', padding: '15px', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <strong>Market Avg</strong><br/>
            <span style={{ fontSize: '24px', color: stats.market_avg > 0 ? 'green' : 'red' }}>
              {stats.market_avg}%
            </span>
          </div>
          <div style={{ background: '#e8f5e9', padding: '15px', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <strong>Gainers (>5%)</strong><br/><span style={{ fontSize: '24px', color: 'green' }}>{stats.gainers_5pct}</span>
          </div>
          <div style={{ background: '#ffebee', padding: '15px', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <strong>Losers (<-5%)</strong><br/><span style={{ fontSize: '24px', color: 'red' }}>{stats.losers_5pct}</span>
          </div>
        </div>
      )}

      <h2>🚀 Top Gainers (Last Hour)</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', background: 'white', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <thead>
          <tr style={{ background: '#333', color: 'white' }}>
            <th style={{ padding: '12px', textAlign: 'left' }}>Symbol</th>
            <th style={{ padding: '12px' }}>Avg Gain</th>
            <th style={{ padding: '12px' }}>Price</th>
            <th style={{ padding: '12px' }}>Volume</th>
            <th style={{ padding: '12px' }}>Count</th>
          </tr>
        </thead>
        <tbody>
          {gainers.length > 0 ? (
            gainers.map((g, i) => (
              <tr key={i} style={{ background: i % 2 === 0 ? '#f9f9f9' : 'white', borderBottom: '1px solid #ddd' }}>
                <td style={{ padding: '12px' }}><strong>{g.symbol}</strong></td>
                <td style={{ padding: '12px', color: 'green', textAlign: 'center', fontWeight: 'bold' }}>+{g.avg_gain}%</td>
                <td style={{ padding: '12px', textAlign: 'center' }}>₹{g.max_price}</td>
                <td style={{ padding: '12px', textAlign: 'center' }}>{g.max_volume.toLocaleString()}</td>
                <td style={{ padding: '12px', textAlign: 'center' }}>{g.occurrences}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="5" style={{ padding: '20px', textAlign: 'center', color: '#999' }}>No data available</td>
            </tr>
          )}
        </tbody>
      </table>

      <h2 style={{ marginTop: '30px' }}>📈 Latest Data (Last 5 min)</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', background: 'white', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <thead>
          <tr style={{ background: '#333', color: 'white' }}>
            <th style={{ padding: '12px', textAlign: 'left' }}>Symbol</th>
            <th style={{ padding: '12px' }}>% Change</th>
            <th style={{ padding: '12px' }}>Price</th>
            <th style={{ padding: '12px' }}>Volume</th>
            <th style={{ padding: '12px' }}>Time</th>
          </tr>
        </thead>
        <tbody>
          {stocks.length > 0 ? (
            stocks.slice(0, 50).map((stock, i) => (
              <tr key={i} style={{ background: i % 2 === 0 ? '#f9f9f9' : 'white', borderBottom: '1px solid #ddd' }}>
                <td style={{ padding: '12px' }}>{stock.symbol}</td>
                <td style={{ padding: '12px', color: stock.pct_chg > 0 ? 'green' : 'red', textAlign: 'center', fontWeight: 'bold' }}>
                  {stock.pct_chg > 0 ? '+' : ''}{stock.pct_chg}%
                </td>
                <td style={{ padding: '12px', textAlign: 'center' }}>₹{stock.price}</td>
                <td style={{ padding: '12px', textAlign: 'center' }}>{stock.volume.toLocaleString()}</td>
                <td style={{ padding: '12px', textAlign: 'center' }}>
                  {new Date(stock.created_at).toLocaleTimeString()}
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="5" style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                {loading ? 'Loading...' : 'No data available'}
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <h2 style={{ marginTop: '30px' }}>⚡ Momentum Stocks (Strong Upward Trend)</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', background: 'white', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <thead>
          <tr style={{ background: '#333', color: 'white' }}>
            <th style={{ padding: '12px', textAlign: 'left' }}>Symbol</th>
            <th style={{ padding: '12px' }}>Avg Gain</th>
            <th style={{ padding: '12px' }}>Appearances</th>
            <th style={{ padding: '12px' }}>Volatility</th>
            <th style={{ padding: '12px' }}>Last Updated</th>
          </tr>
        </thead>
        <tbody>
          {momentum.length > 0 ? (
            momentum.slice(0, 15).map((m, i) => (
              <tr key={i} style={{ background: i % 2 === 0 ? '#f9f9f9' : 'white', borderBottom: '1px solid #ddd' }}>
                <td style={{ padding: '12px' }}><strong>{m.symbol}</strong></td>
                <td style={{ padding: '12px', color: 'green', textAlign: 'center', fontWeight: 'bold' }}>+{m.avg_gain}%</td>
                <td style={{ padding: '12px', textAlign: 'center' }}>{m.appearances}</td>
                <td style={{ padding: '12px', textAlign: 'center' }}>{m.volatility}%</td>
                <td style={{ padding: '12px', textAlign: 'center' }}>
                  {new Date(m.last_updated).toLocaleTimeString()}
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="5" style={{ padding: '20px', textAlign: 'center', color: '#999' }}>No momentum data</td>
            </tr>
          )}
        </tbody>
      </table>

      <h2 style={{ marginTop: '30px' }}>🚀 Breakout Stocks (High Volatility)</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', background: 'white', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <thead>
          <tr style={{ background: '#333', color: 'white' }}>
            <th style={{ padding: '12px', textAlign: 'left' }}>Symbol</th>
            <th style={{ padding: '12px' }}>Max Gain</th>
            <th style={{ padding: '12px' }}>Price Range</th>
            <th style={{ padding: '12px' }}>Avg Volume</th>
            <th style={{ padding: '12px' }}>Last Updated</th>
          </tr>
        </thead>
        <tbody>
          {breakouts.length > 0 ? (
            breakouts.slice(0, 15).map((b, i) => (
              <tr key={i} style={{ background: i % 2 === 0 ? '#f9f9f9' : 'white', borderBottom: '1px solid #ddd' }}>
                <td style={{ padding: '12px' }}><strong>{b.symbol}</strong></td>
                <td style={{ padding: '12px', color: 'green', textAlign: 'center', fontWeight: 'bold' }}>+{b.max_gain}%</td>
                <td style={{ padding: '12px', textAlign: 'center' }}>₹{b.price_range}</td>
                <td style={{ padding: '12px', textAlign: 'center' }}>{b.avg_volume.toLocaleString()}</td>
                <td style={{ padding: '12px', textAlign: 'center' }}>
                  {new Date(b.last_updated).toLocaleTimeString()}
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="5" style={{ padding: '20px', textAlign: 'center', color: '#999' }}>No breakout data</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
